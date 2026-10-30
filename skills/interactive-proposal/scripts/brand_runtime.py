"""Resolve the packaged brand and roadmap runtimes without a company filesystem."""
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
from brand_profile import load_profile, resolve_profile

KIT = next((p for p in (HERE.parent / "_runtime/roadmap-artifacts/scripts",
                        HERE.parent.parent / "roadmap-artifacts/scripts")
            if (p / "rk_embed.py").is_file()), None)
if KIT is None:
    raise RuntimeError("Roadmap runtime is missing. Rebuild this skill with its declared dependencies.")
sys.path.insert(0, str(KIT))
import rk_embed


def roadmap_assets(explicit=None):
    """Inline roadmap component CSS and JS, with text-on-color pairs chosen for the selected profile."""
    return rk_embed.assets(load_profile(resolve_profile(explicit))["colors"])
