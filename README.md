# agentbubble

Agent wrapper for [bubblewrap](https://github.com/containers/bubblewrap). Run AI coding agents (Copilot, Claude, etc.) in a sandboxed environment with controlled filesystem access.

## Install

```bash
uv tool install agentbubble
```

## Usage

```bash
agentbubble copilot
agentbubble claude
agentbubble yolopilot                          # copilot --allow-all
agentbubble --mask-file .env --mask-file .env.local copilot
agentbubble --no-network python script.py
agentbubble --project-dir /path/to/project claude
agentbubble --verbose copilot                  # print bwrap command before running
```

## Configuration

Create `.agentbubble.toml` in your project root or `~/.config/agentbubble/config.toml` for global defaults:

```toml
[sandbox]
ro_bind = [
    "~/.config/some-agent",
]
rw_bind = [
    "~/.cache/some-agent",
]
mask = [".env", ".env.local"]
```

Project config is merged with global config. Paths support `~` and `$ENV_VAR` expansion.

Config files are automatically masked inside the sandbox.

## Profiles

Profiles are named sets of bind mounts for common agent toolchains. All profiles are active by default when no config file is present. To enable only specific profiles, set the top-level `profiles` key in either config file:

```toml
profiles = ["copilot", "claude"]
```

The union of profiles listed in the global and project configs is used.

### Built-in profiles

| Profile | Binds |
|---------|-------|
| `copilot` | `~/.copilot`, `~/.config/.copilot`, `~/.config/gh`, `~/.cache/Microsoft`, `~/.cache/gh` (rw) |
| `claude` | `~/.claude` (ro) |
| `skills` | `~/.cache/skillset/repos` (ro) + resolves symlink targets in `~/.claude/skills/` (ro) |
| `gh` | `~/.config/gh`, `~/.cache/gh` (rw) |
| `node` | `~/.nvm`, `~/.local/share/fnm`, `/run/user/1000/fnm_multishells` (ro) |

## Credits

Inspired by [Jussi Heikkilä's bubblewrap_copilot script](https://github.com/jussih/dotfiles/blob/master/stow/scripts/.local/bin/bubblewrap_copilot).
