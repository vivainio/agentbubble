"""Compose bubblewrap (bwrap) commands for sandboxed execution."""

from pathlib import Path

from agentbubble.config import CONFIG_FILENAME


# System directories to bind read-only
SYSTEM_RO_BINDS = [
    "/usr",
    "/lib",
    "/lib64",
    "/bin",
    "/etc/resolv.conf",
    "/etc/hosts",
    "/etc/ssl",
    "/etc/passwd",
    "/etc/group",
]

# Paths relative to $HOME to bind read-only (using --ro-bind-try)
HOME_RO_BINDS = [
    ".config/git/config",
    ".config/git/config.local",
    ".config/uv",
    ".local/share/uv",
    ".local/bin",
    ".ssh/known_hosts",
]

# Paths relative to $HOME to bind read-write (using --bind-try)
HOME_RW_BINDS = [
    ".cache/uv",
    ".cache/pip",
    ".npm",
]

# Absolute paths to try binding read-only
ABSOLUTE_RO_TRY_BINDS: list[str] = []


def build_bwrap_command(
    command: list[str],
    project_dir: str | Path | None = None,
    network: bool = True,
    mask_files: list[str] | None = None,
    extra_ro_binds: list[str] | None = None,
    extra_rw_binds: list[str] | None = None,
) -> list[str]:
    """Build a bwrap command line.

    Args:
        command: The command and arguments to run inside the sandbox.
        project_dir: Project directory to bind read-write. Defaults to cwd.
        network: Whether to allow network access.
        mask_files: List of file paths to mask with /dev/null.
        extra_ro_binds: Additional paths to bind read-only.
        extra_rw_binds: Additional paths to bind read-write.

    Returns:
        Complete bwrap command as a list of strings.
    """
    project = Path(project_dir) if project_dir else Path.cwd()
    home = Path.home()
    cmd: list[str] = ["bwrap"]

    # System read-only binds
    for path in SYSTEM_RO_BINDS:
        cmd.extend(["--ro-bind", path, path])

    # Home directory read-only binds (try, so missing paths don't fail)
    for rel_path in HOME_RO_BINDS:
        full = str(home / rel_path)
        cmd.extend(["--ro-bind-try", full, full])

    # Absolute read-only try binds
    for path in ABSOLUTE_RO_TRY_BINDS:
        cmd.extend(["--ro-bind-try", path, path])

    # Extra read-only binds
    for path in extra_ro_binds or []:
        cmd.extend(["--ro-bind-try", path, path])

    # Project directory read-write
    cmd.extend(["--bind", str(project), str(project)])

    # Home directory read-write binds
    for rel_path in HOME_RW_BINDS:
        full = str(home / rel_path)
        cmd.extend(["--bind-try", full, full])

    # Extra read-write binds
    for path in extra_rw_binds or []:
        cmd.extend(["--bind-try", path, path])

    # Filesystem setup
    cmd.extend([
        "--tmpfs", "/tmp",
        "--proc", "/proc",
        "--dev", "/dev",
    ])

    # Namespace and lifecycle
    if network:
        cmd.append("--share-net")
    cmd.extend([
        "--unshare-pid",
        "--die-with-parent",
        "--chdir", str(project),
    ])

    # Mask config files so the agent can't read them
    project_config = project / CONFIG_FILENAME
    global_config = home / ".config/agentbubble/config.toml"
    for cfg in [project_config, global_config]:
        cmd.extend(["--ro-bind-try", "/dev/null", str(cfg)])

    # Mask files (bind /dev/null over them)
    for mask in mask_files or []:
        p = Path(mask)
        mask_path = p if p.is_absolute() else project / mask
        cmd.extend(["--ro-bind", "/dev/null", str(mask_path)])

    # The command to execute
    cmd.extend(command)

    return cmd
