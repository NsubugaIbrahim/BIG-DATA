import sqlite3

conn = sqlite3.connect("patents.db")
cursor = conn.cursor()

with open("schema.sql", "w") as f:
    for row in cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';"):
        if row[0]:
            f.write(row[0] + ";\n\n")

print("schema.sql generated!")