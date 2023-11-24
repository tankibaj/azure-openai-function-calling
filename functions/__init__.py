import sys
from pathlib import Path

# Adds the parent directory to sys.path to access the 'core' package
sys.path.append(str(Path(__file__).resolve().parent.parent))
