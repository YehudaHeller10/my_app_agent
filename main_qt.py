#!/usr/bin/env python3

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui_qt.main_window import run_qt_app


def main():
    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)
    run_qt_app()


if __name__ == "__main__":
    main()

