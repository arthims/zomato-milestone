import sys, os
from pathlib import Path

# Streamlit Cloud mounts repo at /mount/src/<repo-name>/
# This ensures src/ is always on the path regardless of mount point
root = Path(__file__).parent.resolve()
sys.path.insert(0, str(root / "src"))

from milestone1.phase9_streamlit.app import main
main()
