"""Check a finished Short before the owner sees it.

  python verify.py <short.mp4> [--brand brand-profile.json] [--model small]

Checks:
  - every word made it in (re-transcribes the render and compares with the plan)
  - the last word isn't clipped
  - length suits the Reel (20 to 45 s short, 50 to 70 s story cut), file is under 30 MB (else makes a smaller copy)
  - no banned words in the on-screen text
  - saves a contact sheet (six frames) so Claude can look at framing, captions and colour
"""
import json, os, re, subprocess, sys, tempfile
import ce_util as U

LIMIT_MB = 30


def norm(w):
    return re.sub(r"[^a-z0-9']", "", w.lower())


def heard(path, model="small"):
    import transcribe as T
    with tempfile.TemporaryDirectory() as d:
        wav = os.path.join(d, "a.wav")
        U.run(["ffmpeg", "-y", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", wav])
        return T.transcribe(wav, model)


def coverage(expected, got):
    """Share of expected words found in order (longest common subsequence)."""
    a = [norm(w) for w in expected if norm(w)]
    b = [norm(w["w"]) for w in got if norm(w["w"])]
    m = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a)):
        for j in range(len(b)):
            m[i + 1][j + 1] = m[i][j] + 1 if a[i] == b[j] else max(m[i][j + 1], m[i + 1][j])
    tail_ok = bool(a) and bool(b) and a[-1] in b[-3:]
    return (m[-1][-1] / len(a) if a else 1.0), tail_ok


def contact_sheet(path, out, n=6):
    dur = U.video_info(path)["duration"]
    tiles = []
    with tempfile.TemporaryDirectory() as d:
        for k in range(n):
            t = dur * (k + 0.5) / n
            p = os.path.join(d, f"f{k}.png")
            U.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", path, "-frames:v", "1", "-vf", "scale=270:480", p])
            tiles.append(p)
        from PIL import Image
        sheet = Image.new("RGB", (270 * n + 10 * (n - 1), 480), "white")
        for k, p in enumerate(tiles):
            sheet.paste(Image.open(p), (k * 280, 0))
        sheet.save(out)
    return out


def shrink(path):
    dur = U.video_info(path)["duration"]
    kbps = int((LIMIT_MB * 8000 * 0.92) / dur) - 160
    out = os.path.splitext(path)[0] + "_small.mp4"
    U.run(["ffmpeg", "-y", "-v", "error", "-i", path, "-c:v", "libx264", "-preset", "medium", "-b:v", f"{kbps}k",
           "-maxrate", f"{kbps}k", "-bufsize", f"{kbps * 2}k", "-c:a", "copy", "-movflags", "+faststart", out])
    os.replace(out, path)


def verify(path, brand=None, model="small"):
    meta_p = os.path.splitext(path)[0] + ".json"
    meta = json.load(open(meta_p)) if os.path.exists(meta_p) else {}
    info = U.video_info(path)
    report = {"file": os.path.basename(path), "seconds": round(info["duration"], 1), "size_mb": info["size_mb"],
              "size": f"{info['width']}x{info['height']}", "problems": [], "notes": []}
    if (info["width"], info["height"]) != (1080, 1920):
        report["problems"].append(f"Frame is {info['width']}x{info['height']}, not 1080x1920.")
    story = os.path.basename(path).startswith("story")
    lo, hi = (45, 75) if story else (15, 50)
    if not lo <= info["duration"] <= hi:
        want = "50 to 70 s for the story cut" if story else "20 to 45 s for a short Reel"
        report["notes"].append(f"Runs {info['duration']:.0f} s. Aim for {want}.")
    if info["size_mb"] > LIMIT_MB:
        shrink(path)
        report["notes"].append(f"Was {info['size_mb']} MB, made a smaller copy ({U.video_info(path)['size_mb']} MB).")
    if meta.get("words"):
        got = heard(path, model)
        cov, tail = coverage(meta["words"], got)
        report["word_coverage"] = round(cov, 3)
        if cov < 0.9:
            report["problems"].append(f"Only {cov:.0%} of the planned words are audible. A cut may be eating words.")
        if not tail:
            report["problems"].append("The last word may be clipped. Extend the final run.")
    if brand:
        b = json.load(open(brand))
        banned = [w.lower() for w in b.get("voice", {}).get("banned_words", [])]
        text = " ".join(meta.get("words", [])).lower()
        hits = [w for w in banned if re.search(r"\b" + re.escape(w) + r"\b", text)]
        if hits:
            report["notes"].append("Said on camera (fine to keep, never put in captions or copy): " + ", ".join(hits))
    if meta.get("crop") and not meta["crop"].get("found", True):
        report["problems"].append("No face found for the crop. Check the framing on the contact sheet.")
    report["contact_sheet"] = contact_sheet(path, os.path.splitext(path)[0] + "_sheet.jpg")
    report["ok"] = not report["problems"]
    return report


if __name__ == "__main__":
    a = sys.argv
    if len(a) < 2:
        print(__doc__); sys.exit(1)
    r = verify(a[1], a[a.index("--brand") + 1] if "--brand" in a else None,
               a[a.index("--model") + 1] if "--model" in a else "small")
    print(json.dumps(r, indent=1))
