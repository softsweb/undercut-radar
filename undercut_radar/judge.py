"""The judge. The strict part is plain code and cannot be overridden by the AI:
 - a competitor only counts when THEIR total (price + shipping) is lower than yours,
 - the radar never suggests a price below your floor.
The optional AI only adds a plain-English opinion on top."""
import json, os, urllib.request

def landed(price, shipping): return round(price + shipping, 2)

def judge(product, comp, now, before):
    """now/before: (price, shipping, in_stock) tuples (before may be None). Returns (kind, message, verdict) or None."""
    total = landed(now[0], now[1]); me = product.my_price
    if not now[2]:
        if before and before[2]:
            return ("out_of_stock", f"{comp.name} ran out of stock", f"RAISE: you could raise {product.name} (never above your own limit).")
        return None
    if total < me:
        if before and before[2] and landed(before[0], before[1]) == total:
            return None          # same undercut as last check: already alerted, do not nag
        gap = round(me - total, 2); pct = round(gap / me * 100)
        if total < product.floor:
            return ("undercut", f"{comp.name} is ${gap:.2f} ({pct}%) below you at ${total:.2f}", f"HOLD: below your floor of ${product.floor:.2f}. Do not follow them down.")
        return ("undercut", f"{comp.name} is ${gap:.2f} ({pct}%) below you at ${total:.2f}", f"MATCH is possible: ${total:.2f} stays above your floor of ${product.floor:.2f}.")
    if before and landed(before[0], before[1]) < landed(now[0], now[1]):
        return ("raised", f"{comp.name} raised their price to ${total:.2f}", "INFO: the gap to you grew.")
    return None

def never_below_floor(product, suggested):
    return max(suggested, product.floor)

def ai_opinion(product, comp, message, verdict, model="claude-haiku-5-5"):
    """Optional plain-English opinion. Needs ANTHROPIC_API_KEY. Cannot change the verdict."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key: return ""
    body = json.dumps({"model": model, "max_tokens": 160, "messages": [{"role": "user", "content":
        f"A price radar found: {message}. Rule-based verdict: {verdict}. In two short plain sentences, say what a seller should check "
        f"(same product? bundle or used item? seller rating?). Do not suggest any price below ${product.floor:.2f}."}]}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", body,
        {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    try: return json.loads(urllib.request.urlopen(req, timeout=60).read())["content"][0]["text"].strip()
    except Exception: return ""
