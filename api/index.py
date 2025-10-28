import sys
from pathlib import Path

# Ensure the repository root is on sys.path so `app` imports resolve.
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.append(str(repo_root))

from app.main import app  # noqa: E402

# Vercel will detect the module-level `app` callable and treat it as the ASGI entrypoint.
