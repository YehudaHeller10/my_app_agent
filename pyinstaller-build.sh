#!/usr/bin/env bash
set -euo pipefail

if ! command -v pyinstaller >/dev/null 2>&1; then
  echo "PyInstaller not found. Installing..."
  pip install pyinstaller
fi

pyinstaller --noconfirm --onefile --windowed \
  --name AndroidAppGenerator \
  --add-data "templates:templates" \
  --add-data "core:core" \
  --add-data "gui:gui" \
  main.py

echo "Build complete: dist/AndroidAppGenerator (or .exe on Windows)"
