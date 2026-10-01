"""Pytest conftest: make the repository root importable.

Many test modules import the `backend` package; running pytest from the repo
root requires the root on sys.path. Without this, CI (fresh interpreter, no
prior sys.path mutation) fails collection with "No module named 'backend'".
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
