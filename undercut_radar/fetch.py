"""Fetchers. The default is GoLogin Web Unlocker (GET, 'apikey' header). A plain fetcher and a local-file
fetcher (demo mode) are included so you can compare and so the demo works without any key."""
import os, time, urllib.parse, urllib.request, urllib.error, pathlib, hashlib

WU_ENDPOINT = "https://parsing.webunlocker.gologin.com/v1/scrape"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

class FetchResult:
    def __init__(self, url, status, body, seconds, error=""):
        self.url, self.status, self.body, self.seconds, self.error = url, status, body, seconds, error
    @property
    def ok(self): return self.status == 200 and bool(self.body)

def _get(url, headers, timeout=120):
    t0 = time.time()
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return FetchResult(url, r.status, r.read().decode("utf-8", "replace"), time.time() - t0)
    except urllib.error.HTTPError as e:
        return FetchResult(url, e.code, e.read().decode("utf-8", "replace") if e.fp else "", time.time() - t0, str(e))
    except Exception as e:  # network errors
        return FetchResult(url, 0, "", time.time() - t0, str(e))

def web_unlocker(url, retries=3):
    """One request to Web Unlocker. Retries politely on 429/500/503 with growing waits."""
    key = os.environ.get("WEB_UNLOCKER_API_KEY", "")
    if not key:
        raise SystemExit("WEB_UNLOCKER_API_KEY is missing. Copy .env.example to .env and put your key in it.")
    q = WU_ENDPOINT + "?url=" + urllib.parse.quote(url, safe="")
    res = None
    for attempt in range(retries):
        res = _get(q, {"apikey": key})
        if res.status not in (429, 500, 503, 0):
            break
        time.sleep(2 * (attempt + 1))
    return res

def plain(url):
    """What an ordinary script would do (for comparison only)."""
    return _get(url, {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}, timeout=30)

def local_file(url, folder="demo_pages"):
    """Demo mode: 'url' is mapped to a local HTML file by the last path part."""
    name = url.rstrip("/").split("/")[-1] + ".html"
    p = pathlib.Path(folder) / name
    t0 = time.time()
    if p.exists():
        return FetchResult(url, 200, p.read_text(encoding="utf-8"), time.time() - t0)
    return FetchResult(url, 404, "", time.time() - t0, "no demo page " + str(p))

def save_raw(raw_dir, res):
    """Keep what the radar actually saw, so you can always check it."""
    pathlib.Path(raw_dir).mkdir(parents=True, exist_ok=True)
    h = hashlib.sha1(res.url.encode()).hexdigest()[:10]
    p = pathlib.Path(raw_dir) / f"{int(time.time())}_{h}_{res.status}.html"
    p.write_text(res.body or "", encoding="utf-8")
    return str(p)
