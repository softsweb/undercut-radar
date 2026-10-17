"""Loads radar.toml and the .env file (stdlib only)."""
import os, tomllib
from dataclasses import dataclass, field

def load_env(path=".env"):
    """Tiny .env reader: KEY=VALUE lines, no quotes needed. Never printed or logged."""
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

@dataclass
class Competitor:
    name: str
    url: str
    shipping: float = 0.0

@dataclass
class Product:
    name: str
    my_price: float
    floor: float                      # the radar NEVER suggests a price below this
    competitors: list = field(default_factory=list)

@dataclass
class Config:
    products: list
    db_path: str = "data/radar.db"
    raw_dir: str = "data/raw"
    board_path: str = "data/board.html"
    ntfy_topic: str = ""
    desktop_notify: bool = True
    use_ai: bool = False
    ai_model: str = "claude-haiku-5-5"
    delay_seconds: float = 3.0       # polite spacing between requests

def load_config(path="radar.toml"):
    raw = tomllib.load(open(path, "rb"))
    prods = []
    for p in raw.get("product", []):
        comps = [Competitor(c["name"], c["url"], float(c.get("shipping", 0))) for c in p.get("competitor", [])]
        prods.append(Product(p["name"], float(p["my_price"]), float(p["floor"]), comps))
    s = raw.get("settings", {})
    return Config(prods, **{k: v for k, v in s.items() if k in Config.__dataclass_fields__ and k != "products"})
