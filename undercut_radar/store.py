"""SQLite price history: every reading is kept."""
import sqlite3, time, pathlib

SCHEMA = """CREATE TABLE IF NOT EXISTS readings(
 id INTEGER PRIMARY KEY, ts REAL, product TEXT, competitor TEXT, url TEXT,
 status INTEGER, usable INTEGER, price REAL, shipping REAL, in_stock INTEGER, seller TEXT, method TEXT, seconds REAL, raw TEXT);
CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, ts REAL, product TEXT, competitor TEXT, kind TEXT, message TEXT, verdict TEXT);"""

class Store:
    def __init__(self, path):
        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path); self.db.executescript(SCHEMA)
    def add_reading(self, product, comp, res, data, raw=""):
        self.db.execute("INSERT INTO readings(ts,product,competitor,url,status,usable,price,shipping,in_stock,seller,method,seconds,raw) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (time.time(), product, comp.name, comp.url, res.status, 1 if data else 0, data["price"] if data else None, comp.shipping,
             1 if (data and data.get("in_stock", True)) else 0, (data or {}).get("seller", ""), (data or {}).get("method", ""), res.seconds, raw))
        self.db.commit()
    def last_two(self, product, competitor):
        return self.db.execute("SELECT price,shipping,in_stock FROM readings WHERE product=? AND competitor=? AND usable=1 ORDER BY ts DESC LIMIT 2", (product, competitor)).fetchall()
    def history(self, product, competitor):
        return self.db.execute("SELECT ts,price+shipping FROM readings WHERE product=? AND competitor=? AND usable=1 ORDER BY ts", (product, competitor)).fetchall()
    def add_event(self, product, comp, kind, message, verdict):
        self.db.execute("INSERT INTO events(ts,product,competitor,kind,message,verdict) VALUES(?,?,?,?,?,?)", (time.time(), product, comp, kind, message, verdict)); self.db.commit()
    def stats(self):
        r = self.db.execute("SELECT COUNT(*), SUM(usable) FROM readings").fetchone()
        return {"readings": r[0], "usable": r[1] or 0}
