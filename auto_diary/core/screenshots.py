from pathlib import Path
from typing import List
from ..config import SS_DIR




IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}




def list_day_images(date_str: str) -> List[Path]:
    day_dir = SS_DIR / date_str
    if not day_dir.exists():
        return []
    return [p for p in sorted(day_dir.iterdir()) if p.suffix.lower() in IMAGE_EXTS]