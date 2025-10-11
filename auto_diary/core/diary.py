from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from .db import connect




@dataclass
class Entry:
    date: str
    body: str = ""
    ai_generated: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None




def get_entry(date_str: str) -> Optional[Entry]:
    from .db import connect
    print("[DB] get_entry() using:", connect.__module__)
    with connect() as conn:
        cur = conn.execute(
        "SELECT date, body, ai_generated, created_at, updated_at FROM entries WHERE date=?",
        (date_str,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return Entry(
        date=row[0], body=row[1] or "", ai_generated=bool(row[2]), created_at=row[3], updated_at=row[4]
        )




def upsert_entry(date_str: str, body: str, ai_generated: bool = False) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    print(f"[UPSERT] {date_str=}, {len(body)=}, {ai_generated=}") 
    with connect() as conn:
        cur = conn.execute("SELECT 1 FROM entries WHERE date=?", (date_str,))
        exists = cur.fetchone() is not None
        if exists:
            conn.execute(
            "UPDATE entries SET body=?, ai_generated=?, updated_at=? WHERE date=?",
            (body, int(ai_generated), now, date_str),
            )
        else:
            conn.execute(
            "INSERT INTO entries(date, body, ai_generated, created_at, updated_at) VALUES (?,?,?,?,?)",
            (date_str, body, int(ai_generated), now, now),
            )