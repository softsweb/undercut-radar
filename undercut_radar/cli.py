"""python -m undercut_radar run | demo | board | check <url>"""
import argparse, sys, time
from .config import load_env, load_config
from . import fetch, extract, judge, alert, board
from .store import Store

def run_once(cfg, fetcher, store, label=""):
    n = 0
    for p in cfg.products:
        for c in p.competitors:
            res = fetcher(c.url); raw = fetch.save_raw(cfg.raw_dir, res) if res.body else ""
            data = extract.extract(res.body, cfg.use_ai, cfg.ai_model) if res.ok else None
            store.add_reading(p.name, c, res, data, raw)
            state = f"${data['price']:.2f} ({data['method']})" if data else "no usable price"
            print(f"[{label}{p.name} / {c.name}] HTTP {res.status} {res.seconds:.1f}s -> {state}")
            if data:
                two = store.last_two(p.name, c.name)
                now = two[0]; before = two[1] if len(two) > 1 else None
                ev = judge.judge(p, c, now, before)
                if ev:
                    kind, msg, verdict = ev
                    opinion = judge.ai_opinion(p, c, msg, verdict, cfg.ai_model) if cfg.use_ai else ""
                    store.add_event(p.name, c.name, kind, msg, verdict)
                    alert.send(f"UNDERCUT ALERT: {p.name}" if kind == "undercut" else f"{kind.upper()}: {p.name}", f"{msg}. {verdict} {opinion}".strip(), cfg.ntfy_topic, cfg.desktop_notify)
            n += 1; time.sleep(cfg.delay_seconds if fetcher is not fetch.local_file else 0)
    board.build(store, cfg, cfg.board_path); print("board:", cfg.board_path, store.stats())

def main(argv=None):
    ap = argparse.ArgumentParser(prog="undercut_radar"); sub = ap.add_subparsers(dest="cmd", required=True)
    for n in ("run", "demo", "board"): s = sub.add_parser(n); s.add_argument("--config", default="radar.toml")
    c = sub.add_parser("check"); c.add_argument("url")
    a = ap.parse_args(argv); load_env()
    if a.cmd == "check":
        r = fetch.web_unlocker(a.url); d = extract.extract(r.body) if r.ok else None
        print("HTTP", r.status, f"{r.seconds:.1f}s", len(r.body), "bytes ->", d or "no usable price"); return
    if a.cmd == "demo":
        print("DEMO MODE: local sample pages, no key and no network needed."); import demo_runner; demo_runner.run(None, None, run_once)
        return
    cfg = load_config(a.config); store = Store(cfg.db_path)
    if a.cmd == "board": print(board.build(store, cfg, cfg.board_path)); return
    run_once(cfg, fetch.web_unlocker, store)

if __name__ == "__main__": main()
