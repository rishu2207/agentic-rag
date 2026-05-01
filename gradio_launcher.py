"""Launcher for the optional Gradio interface.

Run this script to start a lightweight web UI that talks to the FastAPI backend.
The production frontend is the Next.js app in ``frontend/`` — this launcher is
kept for quick notebook-style demos and internal testing.
"""

import sys
from pathlib import Path

# Ensure the project root is on the Python path so ``backend`` is importable.
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.gradio_app import main

if __name__ == "__main__":
    main()
