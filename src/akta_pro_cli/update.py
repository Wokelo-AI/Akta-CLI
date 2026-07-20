"""Update checking for the CLI.

Discovers the latest released version from PyPI (the `akta-pro-cli` project's
JSON API). Results are cached in the config dir so `akta-pro --version` can show
a hint without hitting the network on every call.
"""

from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

from akta_pro_cli.config import config_dir

PACKAGE = "akta-pro-cli"
PYPI_URL = f"https://pypi.org/pypi/{PACKAGE}/json"
PROJECT_URL = f"https://pypi.org/project/{PACKAGE}/"
_CACHE_TTL = 24 * 3600  # re-check at most once a day for the --version hint


def _cache_path() -> Path:
    return config_dir() / "update-check.json"


def parse_version(v: str) -> tuple[int, ...]:
    """Lenient version tuple: '1.2.3' -> (1, 2, 3); non-numeric parts -> 0."""
    parts: list[int] = []
    for chunk in v.split("."):
        digits = ""
        for ch in chunk:
            if ch.isdigit():
                digits += ch
            else:
                break
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def is_newer(latest: str, current: str) -> bool:
    return parse_version(latest) > parse_version(current)


def latest_version(timeout: float = 5.0) -> str | None:
    """Latest version of the package on PyPI, or None on any failure."""
    try:
        with urllib.request.urlopen(PYPI_URL, timeout=timeout) as resp:  # noqa: S310 (https only)
            data = json.load(resp)
        version = data.get("info", {}).get("version")
        return version or None
    except (OSError, ValueError):
        return None


def cached_latest(*, timeout: float = 2.0, ttl: int = _CACHE_TTL, force: bool = False) -> str | None:
    """Latest version string, using a time-boxed cache. Best-effort; None on failure.

    With `force`, always re-checks (used by `akta-pro update`). Otherwise reads
    the cache and only re-checks once `ttl` has elapsed (used by the `--version`
    hint, so it stays fast and offline most of the time).
    """
    path = _cache_path()
    now = int(time.time())
    if not force:
        try:
            data = json.loads(path.read_text())
            if now - int(data.get("checked_at", 0)) < ttl:
                return data.get("latest")
        except (OSError, ValueError):
            pass
    latest = latest_version(timeout=timeout)
    if latest is not None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"checked_at": now, "latest": latest}))
        except OSError:
            pass
    return latest
