"""Entry point for `akta-pro` and `python -m akta_pro_cli`.

Lazily imports the Typer app so a broken/partial install prints a helpful hint
instead of an ImportError traceback.
"""

from __future__ import annotations

import sys


def main() -> None:
    try:
        from akta_pro_cli.app import app
    except ModuleNotFoundError as exc:  # e.g. a broken install missing typer/rich
        sys.stderr.write(
            f"The akta.pro CLI is missing a dependency ({exc.name}).\n"
            "Reinstall with:  pipx install akta-pro-cli\n"
        )
        raise SystemExit(1) from exc
    app()


if __name__ == "__main__":
    main()
