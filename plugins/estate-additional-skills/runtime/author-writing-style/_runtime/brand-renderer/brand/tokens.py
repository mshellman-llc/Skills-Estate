#!/usr/bin/env python3
"""Renderer-compatible tokens derived from the selected Markdown brand profile.

Set SKILLS_BRAND_PROFILE for an explicit profile; otherwise the current project's
brand.md wins over the packaged neutral policy. Existing semantic keys remain
available so renderers keep their layout and calculation behavior.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class TokensNotFound(RuntimeError):
    pass




class _Tokens:
    def __init__(self) -> None:
        from brand_profile import selected_tokens
        try:
            self.path, raw = selected_tokens()
        except (ValueError, OSError) as exc:
            raise TokensNotFound(str(exc)) from exc
        self.raw = raw
        self.provenance = raw.get("provenance", {})
        self.colors = raw["colors"]
        self.rules = raw["rules"]
        self.type = raw.get("type", {})
        self.blocked = raw.get("blocked", {})

        self.hex = {k: v["hex"] for k, v in self.colors.items()}
        self.bare = {k: v["hex"].lstrip("#") for k, v in self.colors.items()}
        # Semantic aliases. The CSS owns the values; these own the names the
        # producers say out loud, so a CSS variable rename touches only the
        # alias map instead of every renderer.
        self.aliases = {k: v for k, v in (raw.get("aliases") or {}).items()
                        if not k.startswith("$")}
        for name, target in self.aliases.items():
            if target in self.colors:
                self.hex[name] = self.colors[target]["hex"]
                self.bare[name] = self.colors[target]["hex"].lstrip("#")
        self.by_hex = {v["hex"].lower(): {"key": k, **v}
                       for k, v in self.colors.items()}
        self.allowed_hexes = set(self.by_hex)

        self.blocked_hexes: dict[str, dict[str, Any]] = {}
        for group, spec in (self.blocked or {}).items():
            if not isinstance(spec, dict) or "hexes" not in spec:
                continue
            repl = {k.lower(): v for k, v in (spec.get("replacedBy") or {}).items()}
            for h in spec["hexes"]:
                self.blocked_hexes[h.lower()] = {
                    "group": group,
                    "replacedBy": repl.get(h.lower()),
                    "reason": spec.get("reason", ""),
                }

    def rgb(self, key_or_hex: str) -> tuple[int, int, int]:
        h = self.hex.get(key_or_hex, key_or_hex).lstrip("#")
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

    def brand_group(self, hex_value: str) -> str | None:
        t = self.by_hex.get(str(hex_value).lower())
        return t["group"] if t and t.get("brand") else None

    def is_warm(self, hex_value: str) -> bool:
        """Warm means the red channel leads the blue channel by a visible
        margin. The profile decides whether warmth is restricted."""
        if self.rules.get("warmAccentsAllowed", True):
            return False
        r, g, b = self.rgb(hex_value)
        allowed = {a.lower() for a in self.rules.get("warmSurfacesAllowed", [])}
        if str(hex_value).lower() in allowed:
            return False
        if max(r, g, b) - min(r, g, b) < 12:
            return False          # effectively neutral
        return r > b + 12

    @property
    def is_authoritative(self) -> bool:
        return self.provenance.get("mode") == "authoritative"


T = _Tokens()

if __name__ == "__main__":
    print(f"tokens: {T.path}")
    print(f"mode:   {T.provenance.get('mode')} ({T.provenance.get('guidelines')})")
    for k, v in T.colors.items():
        flag = "brand" if v.get("brand") else "neutral"
        print(f"  {v['hex']}  {k:<14} {flag:<8} {v['role']}")
    print(f"known off-brand hexes the linter blocks: {len(T.blocked_hexes)}")
