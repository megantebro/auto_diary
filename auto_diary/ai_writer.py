from __future__ import annotations
from operator import truediv
import os, base64, traceback
from pathlib import Path
from datetime import date, datetime
from typing import List
from openai import OpenAI
from .config import SS_DIR, DATE_FMT,AI_PRONPT

from auto_diary.core.diary import upsert_entry

MODEL = "gpt-4o-mini"

def _list_images(day_dir: Path, limit: int = 8) -> List[Path]:
    exts = {".png", ".jpg", ".jpeg"}
    imgs = [p for p in day_dir.iterdir() if p.is_file() and p.suffix.lower() in exts]
    imgs.sort(key=lambda x: x.name)
    return imgs[-limit:] if limit else imgs

def _to_data_url(p: Path) -> str:
    mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
    b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{b64}"

def _build_message_content(date_str: str, images: list[Path]):
    parts = [{
        "type": "text",
        "text": (
            AI_PRONPT.format(date_str=date_str)
        ),
    }]
    for p in images:
        parts.append({
            "type": "image_url",
            "image_url": {"url": _to_data_url(p)}
        })
    print(parts)
    return parts

def write_diary_for_date(date: datetime, limit_images: int = 8) -> Path:
    day_str = date.strftime(DATE_FMT)
    day_dir = SS_DIR / day_str
    if not day_dir.exists():
        raise FileNotFoundError(f"No screenshots for {day_str}: {day_dir}")

    imgs = _list_images(day_dir, limit=limit_images)
    if not imgs:
        raise FileNotFoundError(f"No images in {day_dir}")

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("環境変数 OPENAI_API_KEY が未設定です。")

    client = OpenAI(api_key=api_key)

    try:
        print("[AI] sending request… (images:", len(imgs), ")")
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": _build_message_content(day_str, imgs)}],
            timeout=60,
        )
        print("[AI] response received")
    except Exception as e:
        print("[AI] API error:", e)
        traceback.print_exc()
        raise

    # ★ chat.completions の取り出しはこれで十分
    text = resp.choices[0].message.content
    if not text:
        raise RuntimeError("Empty response content from API")
    return text
