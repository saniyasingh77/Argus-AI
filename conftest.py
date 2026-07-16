"""Ensure the project root is on sys.path so `import backend...` works under
pytest no matter how it is launched (bare `pytest`, `python -m pytest`, any CI).
pytest imports this file automatically before collecting tests."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
