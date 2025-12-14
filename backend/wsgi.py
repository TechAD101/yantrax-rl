# wsgi.py - YantraX WSGI entry
import sys
import os
import importlib
import importlib.util

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Prefer enhanced main when explicitly enabled and available. This is
# non-destructive: fallback to legacy `main` if `main_enhanced` is absent
# or the AI_FIRM_ENABLED env var is not truthy.
def _str2bool(s: str) -> bool:
    return str(s).lower() in ("1", "true", "yes", "on")

ai_firm_enabled = _str2bool(os.environ.get("AI_FIRM_ENABLED", "false"))

app = None
# Prefer `main` (newer entrypoint with diagnostics). If it's available, use it.
try:
    if importlib.util.find_spec("main") is not None:
        mod_main = importlib.import_module("main")
        app = getattr(mod_main, "app", None)
except Exception:
    app = None

# If `main` wasn't available or didn't provide an app, try the enhanced AI entrypoint
if app is None and ai_firm_enabled:
    try:
        if importlib.util.find_spec("main_enhanced") is not None:
            mod = importlib.import_module("main_enhanced")
            app = getattr(mod, "app", None)
    except Exception:
        app = None

# Final fallback: try to import `main` again (or raise if neither present)
if app is None:
    try:
        from main import app  # type: ignore
    except Exception:
        raise

if __name__ == "__main__":
    app.run()
