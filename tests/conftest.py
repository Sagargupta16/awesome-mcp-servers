"""Make the gate scripts importable.

`scripts/` is a directory of standalone entry points rather than an installed
package, so pytest cannot import them until the directory is on `sys.path`.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
