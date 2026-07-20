"""Shared Rich consoles.

`out` writes machine/primary output to stdout; `err` writes human status,
credit lines, and errors to stderr — so `akta-pro ... --json | jq` stays clean.
"""

from rich.console import Console

out = Console()
err = Console(stderr=True)
