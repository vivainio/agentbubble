"""Built-in sandbox profiles for common agent toolchains."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ProfileDef:
    home_ro: list[str] = field(default_factory=list)  # home-relative, ro-bind-try
    home_rw: list[str] = field(default_factory=list)  # home-relative, bind-try
    abs_ro: list[str] = field(default_factory=list)   # absolute, ro-bind-try


BUILTIN_PROFILES: dict[str, ProfileDef] = {
    "copilot": ProfileDef(
        home_rw=[".copilot", ".config/.copilot", ".config/gh", ".cache/Microsoft", ".cache/gh"],
    ),
    "claude": ProfileDef(
        home_ro=[".claude"],
    ),
    "skills": ProfileDef(home_ro=[".cache/skillset/repos"]),  # + dynamic symlink targets
    "gh": ProfileDef(
        home_rw=[".config/gh", ".cache/gh"],
    ),
    "node": ProfileDef(
        home_ro=[".nvm", ".local/share/fnm"],
        abs_ro=["/run/user/1000/fnm_multishells"],
    ),
}

ALL_PROFILE_NAMES: list[str] = list(BUILTIN_PROFILES)


def _claude_skill_targets(home: Path) -> list[str]:
    """Return unique real paths of symlink targets in ~/.claude/skills/."""
    skills_dir = home / ".claude" / "skills"
    if not skills_dir.is_dir():
        return []
    seen: dict[str, None] = {}
    for entry in skills_dir.iterdir():
        try:
            target = entry.resolve()
            if target.exists():
                seen[str(target)] = None
        except OSError:
            pass
    return list(seen)


def resolve_profiles(names: list[str], home: Path) -> tuple[list[str], list[str]]:
    """Resolve profile names to (ro_binds, rw_binds) as absolute paths.

    Unknown profile names emit a warning and are skipped.
    """
    import warnings

    ro: list[str] = []
    rw: list[str] = []
    for name in names:
        if name not in BUILTIN_PROFILES:
            warnings.warn(f"agentbubble: unknown profile {name!r}", stacklevel=2)
            continue
        p = BUILTIN_PROFILES[name]
        ro += [str(home / rel) for rel in p.home_ro] + p.abs_ro
        if name == "skills":
            ro += _claude_skill_targets(home)
        rw += [str(home / rel) for rel in p.home_rw]
    # Preserve order while deduplicating
    ro = list(dict.fromkeys(ro))
    rw = list(dict.fromkeys(rw))
    return ro, rw
