"""Price extraction. Ordinary code first (JSON-LD, meta tags, common price markup); an optional AI fallback
reads the page only when the ordinary code finds nothing. Returns a dict or None."""
import json, os, re, urllib.request

def _num(s):
    s = re.sub(r"[^\d.,]", "", str(s))
    if "," in s and "." in s: s = s.replace(",", "")
    elif "," in s: s = s.replace(",", ".") if re.search(r",\d{2}$", s) else s.replace(",", "")
    try: return float(s)
    except ValueError: return None

def _jsonld(html):
    for m in re.finditer(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', html, re.S | re.I):
        try: data = json.loads(m.group(1))
        except Exception: continue
        stack = data if isinstance(data, list) else [data]
        while stack:
            d = stack.pop()
            if isinstance(d, dict):
                if "@graph" in d: stack.extend(d["@graph"])
                offers = d.get("offers")
                if offers:
                    for o in offers if isinstance(offers, list) else [offers]:
                        price = _num(o.get("price") or o.get("lowPrice") or "")
                        if price:
                            avail = str(o.get("availability", "")).lower()
                            return {"price": price, "currency": o.get("priceCurrency", ""), "in_stock": "outofstock" not in avail and "soldout" not in avail,
                                    "seller": (o.get("seller") or {}).get("name", "") if isinstance(o.get("seller"), dict) else "", "method": "json-ld"}
    return None

def _meta(html):
    m = re.search(r'(?:property|itemprop|name)=["\'](?:product:price:amount|og:price:amount|price)["\'][^>]*content=["\']([\d.,]+)', html, re.I) \
        or re.search(r'content=["\']([\d.,]+)["\'][^>]*(?:property|itemprop)=["\'](?:product:price:amount|og:price:amount|price)', html, re.I)
    if m:
        p = _num(m.group(1))
        if p: return {"price": p, "currency": "", "in_stock": not re.search(r"out of stock|currently unavailable|sold out", html, re.I), "seller": "", "method": "meta"}
    return None

def _markup(html):
    m = re.search(r'class="a-offscreen"[^>]*>\s*\$?([\d.,]+)', html) or re.search(r'class="[^"]*(?:price|Price)[^"]*"[^>]*>\s*\$\s*([\d.,]+)', html)
    if m:
        p = _num(m.group(1))
        if p: return {"price": p, "currency": "USD", "in_stock": not re.search(r"out of stock|currently unavailable|sold out", html, re.I), "seller": "", "method": "markup"}
    return None

def ordinary(html):
    return _jsonld(html) or _meta(html) or _markup(html)

def ai_fallback(html, model="claude-haiku-5-5"):
    """Optional. Needs ANTHROPIC_API_KEY. Sends trimmed visible text and asks for strict JSON."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key: return None
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text); text = re.sub(r"\s+", " ", text)[:6000]
    body = json.dumps({"model": model, "max_tokens": 200, "messages": [{"role": "user", "content":
        'From this product page text return ONLY JSON {"price": number or null, "currency": str, "in_stock": bool, "seller": str}.\n\n' + text}]}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", body,
        {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    try:
        out = json.loads(urllib.request.urlopen(req, timeout=60).read())["content"][0]["text"]
        d = json.loads(re.search(r"\{.*\}", out, re.S).group(0))
        if d.get("price"): d["method"] = "ai"; d["price"] = float(d["price"]); return d
    except Exception:
        return None
    return None

def extract(html, use_ai=False, model="claude-haiku-5-5"):
    return ordinary(html) or (ai_fallback(html, model) if use_ai else None)
