
from main import app

if __name__ == '__main__':
    app.run()
from __future__ import annotations

"""WSGI entrypoint for Render.

This module prefers the MVP application defined in `main_mvp.py` which
exposes the `/api/*` endpoints used by the frontend. If `main_mvp` is not
available, it falls back to the legacy `main.py` application for
backwards-compatibility.
"""

try:
    # Prefer the MVP app
    from main_mvp import app  # type: ignore
except Exception:
    # Fallback to legacy app
    from main import app  # type: ignore


if __name__ == '__main__':
    app.run()
