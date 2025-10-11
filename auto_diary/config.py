from pathlib import Path
from datetime import datetime

# config.py のあるフォルダからプロジェクトルートを確定させる
APP_DIR = Path(__file__).resolve().parent.parent

# Auto_Diary をルートとして固定
ROOT_DIR = APP_DIR if APP_DIR.name == "Auto_Diary" else APP_DIR.parent / "Auto_Diary"

DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "autodiary.db"
SS_DIR = DATA_DIR / "screenshots"
DATE_FMT = "%Y-%m-%d"

DATA_DIR.mkdir(parents=True, exist_ok=True)
SS_DIR.mkdir(parents=True, exist_ok=True)
