"""CLI entry point for agentbubble."""

import argparse
import os

from agentbubble.config import load_config
from agentbubble.sandbox import build_bwrap_command


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run commands in a bubblewrap sandbox",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print the bwrap command before executing",
    )
    parser.add_argument(
        "--project-dir",
        default=os.getcwd(),
        help="Project directory to bind read-write (default: cwd)",
    )
    parser.add_argument(
        "--no-network",
        action="store_true",
        help="Disable network access in sandbox",
    )
    parser.add_argument(
        "--mask-file",
        action="append",
        default=[],
        metavar="FILE",
        help="Mask file by binding /dev/null over it (e.g. .env)",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command to run inside the sandbox",
    )
    args = parser.parse_args()

    if not args.command:
        parser.error("No command specified")

    # Strip leading '--' if present
    command = args.command
    if command[0] == "--":
        command = command[1:]

    # Convenience aliases
    if command[0] == "yolopilot":
        command = ["copilot", "--allow-all"] + command[1:]

    cfg = load_config(args.project_dir)

    cmd = build_bwrap_command(
        command=command,
        project_dir=args.project_dir,
        network=not args.no_network,
        mask_files=args.mask_file + cfg.mask,
        extra_ro_binds=cfg.ro_bind,
        extra_rw_binds=cfg.rw_bind,
    )

    if args.verbose:
        import shlex
        mask_files = args.mask_file + cfg.mask

        def _yaml_list(label: str, items: list[str]) -> None:
            print(f"{label}:")
            if items:
                for item in items:
                    print(f"  - {item}")
            else:
                print("  []")

        _yaml_list("ro_bind", cfg.ro_bind)
        _yaml_list("rw_bind", cfg.rw_bind)
        _yaml_list("mask", mask_files)
        _yaml_list("command", command)
        print(f"network: {not args.no_network}")
        print(f"project_dir: {args.project_dir}")
        print()

    os.execvp(cmd[0], cmd)
