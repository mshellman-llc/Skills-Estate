"""Resolve the packaged shared brand runtime without a company filesystem."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
CANDIDATES = (HERE.parent / "_runtime/brand-renderer/brand",
              HERE.parent.parent / "brand-renderer/brand")
selected = next((p for p in CANDIDATES if (p / "html_profile.py").is_file()), None)
if selected is None:
    raise RuntimeError("Brand runtime is missing. Rebuild this skill with its declared dependencies.")
sys.path.insert(0, str(selected))
from html_profile import apply_profile, resources
