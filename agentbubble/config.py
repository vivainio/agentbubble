"""Load agentbubble config from TOML files."""

import os
from dataclasses import dataclass, field
from pathlib import Path

if hasattr(__builtins__, "__import__"):
    import tomllib
else:
    import tomllib


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
    """
    global_path = Path(_expand_path("~/.config/agentbubble/config.toml"))
    global_cfg = _parse_sandbox_section(_load_toml(global_path))

    if project_dir is None:
        project_dir = os.getcwd()
    project_path = Path(project_dir) / CONFIG_FILENAME
    project_cfg = _parse_sandbox_section(_load_toml(project_path))

    return SandboxConfig(
        ro_bind=global_cfg.ro_bind + project_cfg.ro_bind,
        rw_bind=global_cfg.rw_bind + project_cfg.rw_bind,
        mask=global_cfg.mask + project_cfg.mask,
    )
