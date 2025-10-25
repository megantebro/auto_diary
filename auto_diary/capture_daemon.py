"""
AutoDiary — Screenshot capture daemon
------------------------------------
• 10分ごとなど一定間隔でスクリーンショットを保存
• 保存先: Auto_Diary/data/screenshots/YYYY-MM-DD/
• ファイル名: ss_HHMMSS_mmm.png （ミリ秒付きで重複回避）
• 複数モニタの場合は仮想全体(-1)をキャプチャ（mssの仕様）

実行例:
    uv run python -m auto_diary.capture_daemon --interval 600

オプション:
    --interval <秒>       取得間隔（デフォルト: 600=10分）
    --format png|jpg      画像形式（デフォルト: png）
    --quality 1-95        JPG保存時の画質（デフォルト: 90）
    --once                1回だけ撮影して終了（動作確認用）

依存:
    pip install mss Pillow
"""
from __future__ import annotations

import argparse
import time
from datetime import datetime
from pathlib import Path

from PIL import Image  # Pillow
import mss

from .config import SS_DIR, DATE_FMT,TARGET_MONITOR


def _timestamp_filename(ext: str) -> str:
    now = datetime.now()
    return f"ss_{now.strftime('%H%M%S')}_{int(now.microsecond/1000):03d}.{ext}"


def capture_once(output_dir: Path, fmt: str = "png", quality: int = 90) -> Path:
    """1回だけスクショを撮って指定フォルダに保存し、保存先Pathを返す。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / _timestamp_filename(fmt)

    with mss.mss() as sct:
        # mon=-1 は仮想全体（全モニタ含む）
        sct_img = sct.grab(sct.monitors[TARGET_MONITOR])
        img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
        if fmt.lower() == "jpg" or fmt.lower() == "jpeg":
            img.save(out_path, format="JPEG", quality=int(quality))
        else:
            img.save(out_path, format="PNG")

    return out_path


def run_loop(interval: int, fmt: str = "png", quality: int = 90, once: bool = False):
    print("[Capture] start", {
        "interval": interval,
        "format": fmt,
        "quality": quality,
        "root": SS_DIR,
    })
    try:
        while True:
            day_dir = SS_DIR / datetime.now().strftime(DATE_FMT)
            out = capture_once(day_dir, fmt=fmt, quality=quality)
            print(f"[Capture] saved: {out}")
            if once:
                break
            time.sleep(interval)
    except KeyboardInterrupt:
        print("[Capture] stopped by user")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--interval", type=int, default=600, help="Capture interval in seconds (default: 600)")
    p.add_argument("--format", default="png", choices=["png", "jpg", "jpeg"], help="Image format")
    p.add_argument("--quality", type=int, default=90, help="JPEG quality (1-95)")
    p.add_argument("--once", action="store_true", help="Capture only once and exit")
    args = p.parse_args()

    fmt = "jpg" if args.format.lower() in {"jpg", "jpeg"} else "png"
    quality = max(1, min(int(args.quality), 95))

    run_loop(interval=int(args.interval), fmt=fmt, quality=quality, once=bool(args.once))


if __name__ == "__main__":
    main()
