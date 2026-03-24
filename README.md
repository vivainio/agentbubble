# agentbubble

Agent wrapper for [bubblewrap](https://github.com/containers/bubblewrap). Run AI coding agents (Copilot, Claude, etc.) in a sandboxed environment with controlled filesystem access.

## Install

```bash
pip install agentbubble
```

## Usage

```bash
agentbubble -- copilot
agentbubble -- claude
agentbubble --mask-file .env --mask-file .env.local -- copilot
agentbubble --no-network -- python script.py
agentbubble --project-dir /path/to/project -- claude
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

## Credits

Inspired by [Jussi Heikkilä's bubblewrap_copilot script](https://github.com/jussih/dotfiles/blob/master/stow/scripts/.local/bin/bubblewrap_copilot).
