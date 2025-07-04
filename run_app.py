#!/usr/bin/env python3
"""Run the CV Check application."""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import using absolute imports after path modification
import app

if __name__ == "__main__":
    app.main()