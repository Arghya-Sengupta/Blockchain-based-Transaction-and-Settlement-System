# utils.py
import hashlib
from datetime import datetime, timezone

def now_iso():
    """Return timezone-aware ISO timestamp (UTC)."""
    return datetime.now(timezone.utc).isoformat()

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()
