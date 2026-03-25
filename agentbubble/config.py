"""Load agentbubble config from TOML files."""

import os
from dataclasses import dataclass, field
from pathlib import Path

import tomllib

from agentbubble.profiles import ALL_PROFILE_NAMES, resolve_profiles


CONFIG_FILENAME = ".agentbubble.toml"


@dataclass
class SandboxConfig:
    ro_bind: list[str] = field(default_factory=list)
    rw_bind: list[str] = field(default_factory=list)
    mask: list[str] = field(default_factory=list)


def _expand_path(p: str) -> str:
    return os.path.expanduser(os.path.expandvars(p))


def _parse_sandbox_section(data: dict) -> SandboxConfig:
    section = data.get("sandbox", {})
    return SandboxConfig(
        ro_bind=[_expand_path(p) for p in section.get("ro_bind", [])],
        rw_bind=[_expand_path(p) for p in section.get("rw_bind", [])],
        mask=list(section.get("mask", [])),
    )


def _load_toml(path: Path) -> dict:
    if not path.is_file():
        return {}
    with open(path, "rb") as f:
        return tomllib.load(f)


def load_config(project_dir: str | None = None) -> SandboxConfig:
    """Load and merge global + project config.

    Global: ~/.config/agentbubble/config.toml
    Project: <project_dir>/.agentbubble.toml

    Project values are appended to global values.

    Profiles are resolved from the top-level ``profiles`` key in either config
    file.  If neither config file specifies ``profiles``, all built-in profiles
    are active (preserving out-of-the-box behaviour).  When at least one config
    specifies ``profiles``, the union of both lists is used.
    """
    global_path = Path(_expand_path("~/.config/agentbubble/config.toml"))
    global_data = _load_toml(global_path)
    global_cfg = _parse_sandbox_section(global_data)

    project_path = Path(project_dir or os.getcwd()) / CONFIG_FILENAME
    project_data = _load_toml(project_path)
    project_cfg = _parse_sandbox_section(project_data)

    global_profiles: list[str] | None = global_data.get("profiles")
    project_profiles: list[str] | None = project_data.get("profiles")

    if global_profiles is None and project_profiles is None:
        active_profiles = ALL_PROFILE_NAMES
    else:
        seen: dict[str, None] = {}
        for name in (global_profiles or []) + (project_profiles or []):
            seen[name] = None
        active_profiles = list(seen)

    profile_ro, profile_rw = resolve_profiles(active_profiles, Path.home())

    return SandboxConfig(
        ro_bind=global_cfg.ro_bind + project_cfg.ro_bind + profile_ro,
        rw_bind=global_cfg.rw_bind + project_cfg.rw_bind + profile_rw,
        mask=global_cfg.mask + project_cfg.mask,
    )
