#!/usr/bin/env python3
"""Список всех файлов в директории OpenCode."""

from pathlib import Path

p = Path.home() / "AppData" / "Roaming" / "ai.opencode.desktop"

print("=== Все файлы ===")
for f in sorted(p.iterdir()):
    if f.is_file():
        print(f"{f.name:55s} {f.stat().st_size:>8d} bytes")
    elif f.is_dir():
        print(f"{f.name:55s} {'<DIR>':>8s}")
