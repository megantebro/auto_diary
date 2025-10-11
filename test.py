import sqlite3, pathlib
db = pathlib.Path(r"C:\Users\nakam\OneDrive\デスクトップ\Auto_Diary\data\autodiary.db")
conn = sqlite3.connect(db)
for row in conn.execute("SELECT * FROM entries;"):
    print(row)
conn.close()