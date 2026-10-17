"""Demo: two sample competitor pages, a price drop between two runs. Uses local files only (no key, no network)."""
import shutil, pathlib, tempfile
from undercut_radar.config import Config, Product, Competitor
from undercut_radar import fetch
from undercut_radar.store import Store

def run(cfg, store, run_once):
    tmp = pathlib.Path(tempfile.mkdtemp()); demo = pathlib.Path("demo_pages")
    cfg2 = Config([Product("Wireless Earbuds", 199.00, 180.00, [Competitor("NorthPeak Store", "https://shop.example/northpeak"),
                                                                 Competitor("BrightMart", "https://shop.example/brightmart", 5.99)])],
                  db_path=str(tmp / "demo.db"), raw_dir=str(tmp / "raw"), board_path="demo_board.html", desktop_notify=False, delay_seconds=0)
    st = Store(cfg2.db_path)
    for step, label in (("v1", "RUN 1 (normal day) "), ("v2", "RUN 2 (a competitor drops the price) ")):
        for n in ("northpeak", "brightmart"):
            shutil.copy(demo / f"{n}_{step}.html", demo / f"{n}.html")
        run_once(cfg2, fetch.local_file, st, label)
    for n in ("northpeak", "brightmart"):
        (demo / f"{n}.html").unlink(missing_ok=True)
    print("\nOpen demo_board.html in your browser to see the price history chart.")
