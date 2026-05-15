"""
streamlit_app.py
----------------
Repo-root entrypoint for Streamlit Community Cloud.
Set this as the main file path in the Cloud dashboard.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from milestone1.phase9_streamlit.app import main

main()
