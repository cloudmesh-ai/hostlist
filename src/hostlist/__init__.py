import os
from .core import Hostlist

def _read_version():
    try:
        # The VERSION file is in the project root, 2 levels up from this file
        version_file = os.path.join(os.path.dirname(__file__), '..', '..', 'VERSION')
        with open(version_file, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.0.0"

__version__ = _read_version()

