"""Alerts: console always; ntfy (free) and desktop notification if configured."""
import subprocess, urllib.request, shutil

def send(title, message, ntfy_topic="", desktop=True):
    print(f"\n*** {title}\n    {message}\n")
    if ntfy_topic:
        try:
            req = urllib.request.Request("https://ntfy.sh/" + ntfy_topic, message.encode("utf-8"), {"Title": title.encode("ascii", "ignore").decode()})
            urllib.request.urlopen(req, timeout=15)
        except Exception as e:
            print("(ntfy failed:", e, ")")
    if desktop and shutil.which("notify-send"):
        subprocess.run(["notify-send", title, message], check=False)
