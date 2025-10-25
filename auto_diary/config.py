from pathlib import Path
from datetime import datetime

# config.py のあるフォルダからプロジェクトルートを確定させる
ROOT_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "autodiary.db"
SS_DIR = DATA_DIR / "screenshots"
DATE_FMT = "%Y-%m-%d"

DATA_DIR.mkdir(parents=True, exist_ok=True)
SS_DIR.mkdir(parents=True, exist_ok=True)
