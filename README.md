# Undercut Radar

Watches competitor product pages, remembers every price, judges whether an undercut really matters and alerts you.
**It advises only. It never changes your prices**, and the radar never suggests a price below the floor you set.

Built in the video "I Built an AI Price Radar for Amazon Sellers (Web Unlocker + Claude Code)".

```
watchlist -> fetch (Web Unlocker) -> read price (code first, AI fallback) -> history (SQLite) -> judge (rules + AI opinion) -> alert + price board
```

## Try it in 30 seconds (no key, no network)
```
python3 -m undercut_radar demo
```
Two sample competitor pages, a price drop between two runs, the alert, and `demo_board.html` with the price chart.

## Use it with your own Web Unlocker key
Needs Python 3.11 or newer. No packages to install (standard library only).
1. Get a Web Unlocker API key in your GoLogin account (free test: 1,000 requests, no card).
2. `cp .env.example .env` and put your key in it (`WEB_UNLOCKER_API_KEY=wu_...`). `.env` is git-ignored: never commit it.
3. `cp radar.toml.example radar.toml` and describe what you sell: your price, your floor, the competitor pages.
4. Check one page: `python3 -m undercut_radar check "https://www.example.com/product/123"`
5. Run the radar: `python3 -m undercut_radar run` (writes `data/radar.db` and `data/board.html`).
6. Schedule it every few hours with cron, a GitHub Action or any computer that stays on:
   `0 */6 * * * cd /path/to/undercut-radar && python3 -m undercut_radar run`

## Alerts
Always printed. Free push alerts: set `ntfy_topic` in `radar.toml` and subscribe to that topic at ntfy.sh. Linux desktop notifications use `notify-send`.

## Optional AI
Set `use_ai = true` and add `ANTHROPIC_API_KEY` to `.env`. The ordinary parser always runs first; the AI only reads pages the parser cannot,
and adds a plain-English opinion to alerts. The AI cannot override the rules (competitor total with shipping lower than yours, never below your floor).

## What the judge says
`MATCH is possible` (still above your floor), `HOLD` (they went below your floor), `RAISE` (a competitor ran out of stock), `INFO` (a competitor raised the price).

## Tests
`python3 -m unittest discover -s tests`

## Responsible use
Use public pages only (no logins), a small number of requests and your own business. Sites' terms can forbid automated access: read them.
GoLogin's terms limit Web Unlocker to your own internal business use, so run this for yourself and do not resell it as a service.
Not legal advice. For your own Amazon listings there is also an official API.

## Terms and disclaimer
Read [TERMS.md](TERMS.md). The software is provided as is, without warranty, and you use it at your own risk.

## License
MIT
