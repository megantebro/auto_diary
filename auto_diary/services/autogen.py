from pathlib import Path
from typing import List




def generate_from_images(date_str: str, images: List[Path]) -> str:
    if not images:
        return ""
    first = images[0].name
    last = images[-1].name
    lines = [
    f"{date_str} の活動メモ",
    f"・画像枚数: {len(images)}",
    f"・最初のスクショ: {first}",
    f"・最後のスクショ: {last}",
    "・気づき: 今日はPC作業が中心。詳細はサムネイルを参照。",
    ]
    return "\n".join(lines)