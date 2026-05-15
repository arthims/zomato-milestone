import sys
from pathlib import Path

# add src/ to path so imports work without pip install -e .
sys.path.insert(0, str(Path(__file__).parent / "src"))

from milestone1.phase9_streamlit.app import main

main()
