from pathlib import Path
from datetime import datetime

# config.py のあるフォルダからプロジェクトルートを確定させる
ROOT_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "autodiary.db"
SS_DIR = DATA_DIR / "screenshots"
DATE_FMT = "%Y-%m-%d"

TARGET_MONITOR = -1

AI_PRONPT = """あなたは日本語で丁寧に今日のパソコンのスクリーンショットを使って日記を生成するアシスタントです。
f"対象日: {date_str}\n"
## 今日のまとめ（日本語）\n- 要約（3〜6行）\n- ハイライト（3〜6項目）\n
## Quick Summary (English)\n- 2–4 sentences\n
## タスク候補\n- 明日以降のTODOを2–4件\n"""
DATA_DIR.mkdir(parents=True, exist_ok=True)
SS_DIR.mkdir(parents=True, exist_ok=True)
