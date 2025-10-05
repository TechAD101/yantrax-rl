# wsgi.py - YantraX WSGI entry
import sys
import os
import importlib

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Prefer enhanced main when explicitly enabled and available. This is
# non-destructive: fallback to legacy `main` if `main_enhanced` is absent
# or the AI_FIRM_ENABLED env var is not truthy.
def _str2bool(s: str) -> bool:
    return str(s).lower() in ("1", "true", "yes", "on")

ai_firm_enabled = _str2bool(os.environ.get("AI_FIRM_ENABLED", "false"))

app = None
if ai_firm_enabled:
    try:
        # Only import main_enhanced if module is present to avoid ImportError
        if importlib.util.find_spec("main_enhanced") is not None:
            mod = importlib.import_module("main_enhanced")
            app = getattr(mod, "app", None)
    except Exception:
        # If anything goes wrong, we'll fall back to legacy main below
        app = None

if app is None:
    # Fallback to legacy `main` app
    try:
        from main import app  # type: ignore
    except Exception:
        raise


if __name__ == "__main__":
    app.run()
