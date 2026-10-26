"""Build the Ready to Post folder: one folder per post, captions as text files, a posting plan page.

  python ready_to_post.py <manifest.json>

Manifest (Claude writes it after Go Live is approved):
{
  "title": "Video 03: How to get found on Google",
  "timezone": "Australia/Perth",
  "out": "Ready to Post",                       # the parent folder; each job gets its own dated subfolder
  "name": "Google",                             # short name for the subfolder (defaults to the title)
  "scheduler": "Meta Business Suite",          # what they told us they use (or "none yet")
  "posts": [
    {"date": "2026-10-28", "time": "19:40", "label": "Short 1 - Not one client",
     "files": ["out/short-1.mp4"],
     "platforms": ["Instagram Reels", "YouTube Shorts", "TikTok"],
     "captions": {"Instagram Reels": "caption...",
                  "YouTube Shorts": {"title": "...", "description": "..."},
                  "TikTok": "caption..."},
     "notes": "Pin a comment asking ..."}
  ]
}

Makes (earlier weeks in Ready to Post are never touched; rebuilding the same job replaces only its own subfolder):
  Ready to Post/
    2026-10-28 Google/
      Posting plan.html        open on phone or laptop: every post, when, where, captions with Copy buttons
      schedule.csv             the same plan as a spreadsheet (works with bulk upload in most schedulers)
      01 Tue 28 Oct 7.40pm - Short 1/   the video + one caption file per platform
    2026-10-28 Google.zip      the job in one download. Only send it in chat if it's under 25 MB
                               (the script says). Otherwise point them to the folder, or send the
                               Posting plan and the files one at a time.
"""
import csv, datetime as dt, html, json, os, re, shutil, sys, zipfile


def slug(s):
    return re.sub(r"[\\/:*?\"<>|]+", "", s).strip()


def when(d, t):
    x = dt.datetime.strptime(f"{d} {t}", "%Y-%m-%d %H:%M")
    h = x.strftime("%I").lstrip("0")
    return x, f"{x.strftime('%a %d %b')} {h}.{x.strftime('%M%p').lower()}".replace(".00", "")


def caption_text(c):
    if isinstance(c, dict):
        return "\n\n".join(f"{k.upper()}:\n{v}" for k, v in c.items())
    return c or ""


def build(manifest_path):
    M = json.load(open(manifest_path, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(manifest_path))
    P = lambda p: p if os.path.isabs(p) else os.path.join(base, p)
    posts = sorted(M["posts"], key=lambda p: (p["date"], p["time"]))
    parent = P(M.get("out", "Ready to Post"))
    short = slug(M.get("name") or M.get("title", "Week"))[:40].strip() or "Week"
    out = os.path.join(parent, f"{posts[0]['date'] if posts else dt.date.today().isoformat()} {short}")
    if os.path.exists(out):
        shutil.rmtree(out)          # this job's own subfolder only
    os.makedirs(out)
    rows, cards = [], []
    for n, p in enumerate(posts, 1):
        x, nice = when(p["date"], p["time"])
        folder = slug(f"{n:02d} {nice} - {p['label']}")
        fd = os.path.join(out, folder); os.makedirs(fd)
        copied = []
        for f in p.get("files", []):
            dst = os.path.join(fd, os.path.basename(f)); shutil.copy2(P(f), dst); copied.append(os.path.basename(f))
        for plat in p["platforms"]:
            c = p.get("captions", {}).get(plat, "")
            txt = caption_text(c)
            open(os.path.join(fd, slug(f"{plat} caption.txt")), "w", encoding="utf-8").write(txt + "\n")
            rows.append({"date": p["date"], "time": p["time"], "timezone": M.get("timezone", ""), "platform": plat,
                         "file": f"{folder}/{copied[0]}" if copied else "", "caption": txt})
        if p.get("notes"):
            open(os.path.join(fd, "notes.txt"), "w", encoding="utf-8").write(p["notes"] + "\n")
        cards.append((n, nice, p, folder, copied))
    with open(os.path.join(out, "schedule.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date", "time", "timezone", "platform", "file", "caption"]); w.writeheader(); w.writerows(rows)
    open(os.path.join(out, "Posting plan.html"), "w", encoding="utf-8").write(page(M, cards))
    z = out + ".zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_STORED) as zf:
        for root, _, files in os.walk(out):
            for f in files:
                full = os.path.join(root, f); zf.write(full, os.path.relpath(full, os.path.dirname(out)))
    return out, z, len(posts)


def page(M, cards):
    e = html.escape
    items = []
    for n, nice, p, folder, files in cards:
        caps = []
        for plat in p["platforms"]:
            c = p.get("captions", {}).get(plat, "")
            if isinstance(c, dict):
                for k, v in c.items():
                    caps.append(f"<div class='cap'><div class='lab'>{e(plat)} · {e(k)}</div><pre>{e(v)}</pre>"
                                f"<button onclick='cp(this)'>Copy</button></div>")
            else:
                caps.append(f"<div class='cap'><div class='lab'>{e(plat)}</div><pre>{e(c)}</pre><button onclick='cp(this)'>Copy</button></div>")
        vid = "".join(f"<video src='{e(folder)}/{e(f)}' controls playsinline preload='metadata'></video>" for f in files if f.lower().endswith(".mp4"))
        note = f"<p class='note'>{e(p['notes'])}</p>" if p.get("notes") else ""
        items.append(f"<section><div class='when'>{n:02d} · {e(nice)}</div><h2>{e(p['label'])}</h2>"
                     f"<div class='plats'>{' · '.join(e(x) for x in p['platforms'])}</div>{vid}{''.join(caps)}{note}"
                     f"<label class='done'><input type='checkbox'> Scheduled</label></section>")
    sched = M.get("scheduler") or "your scheduler"
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Posting plan</title><style>
:root{{--bg:#fafaf7;--fg:#1d1d1b;--mute:#6b6b66;--card:#fff;--line:#e4e2dc;--acc:#1d1d1b}}
@media (prefers-color-scheme:dark){{:root{{--bg:#151514;--fg:#f1f0ec;--mute:#a19f98;--card:#1e1e1c;--line:#33322f;--acc:#f1f0ec}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}}
main{{max-width:680px;margin:0 auto;padding:24px 16px 64px}} h1{{font-size:26px;margin:0 0 4px}}
.sub{{color:var(--mute);margin:0 0 24px}} section{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;margin:0 0 16px}}
.when{{font-size:13px;letter-spacing:.04em;text-transform:uppercase;color:var(--mute)}} h2{{font-size:20px;margin:4px 0}}
.plats{{color:var(--mute);font-size:14px;margin-bottom:12px}} video{{width:100%;max-width:280px;border-radius:10px;display:block;margin:8px 0 12px;background:#000}}
.cap{{border-top:1px solid var(--line);padding:10px 0}} .lab{{font-size:13px;font-weight:600;margin-bottom:4px}}
pre{{white-space:pre-wrap;font:inherit;margin:0 0 8px}} button{{font:inherit;font-size:14px;padding:6px 14px;border-radius:999px;border:1px solid var(--acc);background:transparent;color:var(--fg);cursor:pointer}}
.note{{background:var(--bg);border-radius:8px;padding:8px 10px;font-size:14px}} .done{{display:block;margin-top:8px;font-size:14px;color:var(--mute)}}
</style></head><body><main><h1>{e(M.get('title', 'Posting plan'))}</h1>
<p class="sub">Times are {e(M.get('timezone', 'local time'))}. Schedule each one in {e(sched)}, tick it off, done.</p>
{''.join(items)}</main><script>
function cp(b){{var t=b.previousElementSibling.innerText;navigator.clipboard&&navigator.clipboard.writeText(t).then(function(){{b.textContent='Copied';setTimeout(function(){{b.textContent='Copy'}},1500)}})}}
</script></body></html>"""


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    o, z, n = build(sys.argv[1])
    mb = os.path.getsize(z) / 1e6
    print(f"Ready to Post: {n} posts in {o}\nZip: {z} ({mb:.1f} MB)")
    if mb < 25:
        print("Small enough to send in chat.")
    else:
        print("Too big to send in chat. Point them to the folder (Drive or linked computer), or send the "
              "Posting plan and each file on its own (split_video.py for any video over 25 MB, if the plugin has it).")
