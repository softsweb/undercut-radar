"""Static price board: one self-contained HTML file with an SVG chart per product."""
import html, time

def build(store, cfg, out):
    parts = []
    for p in cfg.products:
        lines, allv = [], [p.my_price, p.floor]
        for c in p.competitors:
            h = store.history(p.name, c.name); lines.append((c.name, h)); allv += [v for _, v in h]
        lo, hi = min(allv) * .97, max(allv) * 1.03
        W, H = 760, 280
        ts = [t for _, h in lines for t, _ in h] or [0, 1]; t0, t1 = min(ts), max(ts) or 1
        X = lambda t: 50 + (t - t0) / ((t1 - t0) or 1) * (W - 70); Y = lambda v: H - 30 - (v - lo) / ((hi - lo) or 1) * (H - 50)
        svg = f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
        svg += f'<line x1="50" x2="{W-20}" y1="{Y(p.my_price)}" y2="{Y(p.my_price)}" stroke="#0071e3" stroke-width="3"/><text x="54" y="{Y(p.my_price)-6}" fill="#0071e3" font-size="13">you ${p.my_price:.2f}</text>'
        svg += f'<line x1="50" x2="{W-20}" y1="{Y(p.floor)}" y2="{Y(p.floor)}" stroke="#ff9f0a" stroke-dasharray="7 6" stroke-width="2"/><text x="54" y="{Y(p.floor)+16}" fill="#c77700" font-size="13">floor ${p.floor:.2f}</text>'
        cols = ["#ff3b30", "#af52de", "#1fa35c", "#555"]
        for i, (n, h) in enumerate(lines):
            if h: svg += f'<polyline fill="none" stroke="{cols[i%4]}" stroke-width="3" points="{" ".join(f"{X(t):.1f},{Y(v):.1f}" for t, v in h)}"/><text x="{W-20}" y="{Y(h[-1][1])-8}" text-anchor="end" fill="{cols[i%4]}" font-size="13">{html.escape(n)} ${h[-1][1]:.2f}</text>'
        parts.append(f'<h2>{html.escape(p.name)}</h2>{svg}</svg>')
    s = store.stats()
    page = ('<!doctype html><meta charset="utf-8"><title>Undercut Radar board</title><style>body{font:16px system-ui;background:#f5f5f7;color:#1d1d1f;max-width:820px;margin:30px auto}'
            'h1{font-size:30px}h2{margin-top:36px}svg{background:#fff;border-radius:16px;box-shadow:0 10px 30px rgba(0,0,0,.08)}</style>'
            f'<h1>Undercut Radar</h1><p>{s["usable"]} usable readings of {s["readings"]} · updated {time.strftime("%Y-%m-%d %H:%M")}</p>' + "".join(parts))
    open(out, "w", encoding="utf-8").write(page); return out
