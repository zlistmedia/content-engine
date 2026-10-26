"""Render vertical Shorts / Reels from a plan, entirely in the buyer's brand.

  python shorts.py <shorts-plan.json> [short-id ...]

Plan format (Claude writes this after the owner approves The Plan):
{
  "brand":  "Brand/brand-profile.json",
  "source": "work/master.mp4",
  "words":  "work/words.json",
  "out_dir": "out",
  "shorts": [
    {"id": "short-1",
     "runs": [[120, 168], [175, 190]],      # word-number ranges from transcript.txt, in play order
     "hook": ["FIRST LINE", "SECOND LINE"],   # her own words, 1 to 3 short lines
     "sticker": "SAVE POINT",                 # optional, only if the profile has stickers on
     "key": ["words", "to", "highlight"],     # phrase captions only
     "music": true,
     "crop_x": 640}                           # optional: left edge of the vertical crop, if face-finding misses
  ]
}

How it cuts: each run starts just before its first word and ends just after its last word (never
clipping it), silences longer than half a second are tightened, and every segment is read straight
from the source with its own seek, which keeps memory low on long videos.
"""
import json, os, sys, subprocess
import ce_util as U
from brand import Brand
import face as FACE
import music as MUSIC

W_OUT, H_OUT = 1080, 1920


def segments(W, runs, sil):
    used = set(i for a, b in runs for i in range(a, b + 1))
    out = []
    for a, b in runs:
        s = max(0.0, W[a]["s"] - 0.12)
        e = W[b]["e"] + 0.22
        nxt = b + 1
        if nxt < len(W) and nxt not in used:
            gap = W[nxt]["s"] - W[b]["e"]
            e = min(e, W[nxt]["s"] - 0.02) if gap > 0.05 else W[b]["e"] + 0.06
        out += U.subtract([s, e], sil)
    return out


def timeline(segs):
    def ot(t):
        acc = 0.0
        for s, e in segs:
            if t < s:
                return acc
            if t <= e:
                return acc + t - s
            acc += e - s
        return acc
    return ot, sum(e - s for s, e in segs)


def fix_word(w, fixes):
    core = w.strip(".,!?;:\"'()")
    rep = fixes.get(core.lower())
    return rep if rep else core


def caption_events(B, W, idx, ot, total, key, fixes):
    s = B.shorts.get("captions", {})
    mode = s.get("mode", "word")
    ev = []
    if mode == "word":
        for j, i in enumerate(idx):
            t0 = ot(W[i]["s"]); t1 = ot(W[idx[j + 1]]["s"]) if j + 1 < len(idx) else total
            w = fix_word(W[i]["w"], fixes)
            if t1 - t0 >= 0.05 and w:
                ev.append(("word", w, t0, t1))
    else:
        cards, cur = [], []
        for i in idx:
            cur.append(i)
            w = W[i]["w"]
            if w.endswith((".", ",", "!", "?")) or len(cur) >= 4 or sum(len(W[c]["w"]) + 1 for c in cur) >= 22:
                cards.append(cur); cur = []
        if cur:
            cards.append(cur)
        keyset = {k.lower().strip(".,!?") for k in key}
        for k, c in enumerate(cards):
            t0 = ot(W[c[0]]["s"]); t1 = ot(W[cards[k + 1][0]]["s"]) if k + 1 < len(cards) else total
            toks = []
            for j, i in enumerate(c):
                w = fix_word(W[i]["w"], fixes)
                if k == 0 and j == 0:
                    w = w[:1].upper() + w[1:]
                toks.append((w, w.lower().strip(".,!?") in keyset))
            ev.append(("phrase", toks, t0, t1))
    return ev


def render_short(B, src, W, runs, hook, out, sticker=None, key=(), crop=None, bed=None, sil=(), workdir=None,
                 sticker_idx=0):
    workdir = workdir or os.path.splitext(out)[0] + "_parts"
    os.makedirs(workdir, exist_ok=True)
    segs = segments(W, runs, sil)
    if not segs:
        raise RuntimeError("Nothing left to render after trimming. Check the word ranges.")
    idx = [i for a, b in runs for i in range(a, b + 1)]
    ot, total = timeline(segs)
    hold = float(B.shorts.get("end_hold", 0.7))
    total_h = total + hold
    info = U.video_info(src)
    if crop is None:
        crop = FACE.locate(src, segs[0][0], segs[-1][1], samples=8)
    if crop.get("portrait"):
        vchain = f"scale={W_OUT}:{H_OUT}:force_original_aspect_ratio=increase:flags=lanczos,crop={W_OUT}:{H_OUT},setsar=1"
    else:
        vchain = f"crop={crop['crop_w']}:{info['height']}:{crop['crop_x']}:0,scale={W_OUT}:{H_OUT}:flags=lanczos,setsar=1"
    n = len(segs)
    parts = []
    for j, (a, b) in enumerate(segs):
        d = b - a
        parts.append(f"[{j}:v]setpts=PTS-STARTPTS[v{j}];[{j}:a]asetpts=PTS-STARTPTS,afade=t=in:d=0.025,"
                     f"afade=t=out:st={max(0, d - 0.04):.3f}:d=0.04[a{j}];")
    if os.path.exists(U.RNNOISE) and U.has_filter("arnndn"):
        rn = f"arnndn=m='{U.RNNOISE}':mix=0.85,"
    else:
        rn = "afftdn=nf=-25:tn=1,"  # ffmpeg's built-in noise reduction, gentle
    fc = ("".join(parts) + "".join(f"[v{j}][a{j}]" for j in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac];"
          f"[vc]tpad=stop_mode=clone:stop_duration={hold},{vchain}[v];"
          f"[ac]aresample=48000,highpass=f=70,{rn}loudnorm=I=-14:TP=-1.5,aresample=48000,apad=pad_dur={hold}")
    inputs = sum([["-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", src] for a, b in segs], [])
    if bed:
        level = float(B.shorts.get("music", {}).get("level", 0.22))
        fc += (f",asplit=2[voice][sc];[{n}:a]aresample=48000,atrim=0:{total_h:.2f},asetpts=PTS-STARTPTS,"
               f"afade=t=out:st={max(0, total_h - 2):.2f}:d=2,volume={level}[b0];"
               f"[b0][sc]sidechaincompress=threshold=0.06:ratio=2.5:attack=40:release=600[bed];"
               f"[voice][bed]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]")
        inputs += ["-i", bed]
    else:
        fc += ",alimiter=limit=0.95[a]"
    base = os.path.join(workdir, "base.mp4")
    U.run(["ffmpeg", "-y", "-v", "error"] + inputs + ["-filter_complex", fc, "-map", "[v]", "-map", "[a]",
           "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-r", "30", "-c:a", "aac", "-b:a", "160k", base])

    # pass 2: brand layer, composited in RGB so colours land exactly, then back to bt709
    fixes = {k.lower(): v for k, v in B.p.get("voice", {}).get("spelling_fixes", {}).items()}
    ins = ["-i", base]; f2 = ["[0:v]format=rgb24[o0];"]; cur = "o0"; k = 1

    def add(png, x, y, t0=None, t1=None):
        nonlocal cur, k
        ins.extend(["-i", png])
        en = f":enable='between(t,{t0:.2f},{t1:.2f})'" if t0 is not None else ""
        f2.append(f"[{cur}][{k}:v]overlay=x={x}:y={y}:format=rgb{en}[o{k}];")
        cur = f"o{k}"; k += 1

    hy = int(B.shorts.get("hook", {}).get("y", 150))
    hh = 0
    if hook:
        hw, hh = B.hook(hook, os.path.join(workdir, "hook.png"))
        add(os.path.join(workdir, "hook.png"), (W_OUT - hw) // 2, hy)
    st = B.shorts.get("sticker", {})
    if sticker and st.get("enabled"):
        sw, sh = B.sticker(sticker, os.path.join(workdir, "sticker.png"), sticker_idx)
        add(os.path.join(workdir, "sticker.png"), W_OUT - sw - 56, hy + hh + 30, 0.3, total_h)
    cy = int(B.shorts.get("captions", {}).get("y", 1400))
    for j, (kind, payload, t0, t1) in enumerate(caption_events(B, W, idx, ot, total_h, key, fixes)):
        p = os.path.join(workdir, f"c{j:03d}.png")
        cw, ch = B.caption_word(payload, p) if kind == "word" else B.caption_phrase(payload, p)
        add(p, (W_OUT - cw) // 2, cy - ch // 2, t0, t1 - 0.01)
    f2.append(f"[{cur}]scale=out_color_matrix=bt709:out_range=tv,format=yuv420p[vout]")
    script = os.path.join(workdir, "overlay.txt")
    open(script, "w").write("".join(f2))
    U.run(["ffmpeg", "-y", "-v", "error", "-filter_complex_threads", "1", "-threads", "2"] + ins +
          ["-filter_complex_script", script, "-map", "[vout]", "-map", "0:a", "-c:a", "copy",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
           "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-maxrate", "6M", "-bufsize", "12M",
           "-r", "30", "-movflags", "+faststart", out])
    meta = {"out": out, "segments": segs, "duration": round(total_h, 2), "words": [W[i]["w"] for i in idx],
            "crop": crop, "size_mb": round(os.path.getsize(out) / 1e6, 1)}
    json.dump(meta, open(os.path.splitext(out)[0] + ".json", "w"), indent=1)
    return meta


def main(plan_path, only=None):
    plan = json.load(open(plan_path))
    base = os.path.dirname(os.path.abspath(plan_path))
    P = lambda p: p if os.path.isabs(p) else os.path.join(base, p)
    B = Brand(P(plan["brand"]))
    probs = B.validate()
    if probs:
        raise SystemExit("The brand profile needs sorting first:\n- " + "\n- ".join(probs))
    src, W = P(plan["source"]), U.load_words(P(plan["words"]))
    out_dir = P(plan.get("out_dir", "out")); os.makedirs(out_dir, exist_ok=True)
    sil = U.silences(src)
    bed = None
    mus = B.shorts.get("music", {})
    if mus.get("mode", "none") == "bed":
        bed = os.path.join(out_dir, f"bed_{mus.get('mood', 'bright')}_{mus.get('bpm', 108)}.wav")
        if not os.path.exists(bed):
            MUSIC.make(bed, mus.get("mood", "bright"), int(mus.get("bpm", 108)), 70)
    stickers = B.shorts.get("sticker", {}).get("words", [])
    for n, s in enumerate(plan["shorts"]):
        if only and s["id"] not in only:
            continue
        out = os.path.join(out_dir, f"{s['id']}.mp4")
        sticker = s.get("sticker") or (stickers[n % len(stickers)] if stickers else None)
        crop = None
        if s.get("crop_x") is not None:
            info = U.video_info(src); cw = int(round(info["height"] * 9 / 16 / 2) * 2)
            cx = int(min(max(int(s["crop_x"]), 0), info["width"] - cw)); cx -= cx % 2
            crop = {"crop_x": cx, "crop_w": cw, "found": True, "portrait": info["portrait"], "manual": True}
        m = render_short(B, src, W, s["runs"], s.get("hook"), out, sticker=sticker, key=s.get("key", []),
                         crop=crop, bed=bed if s.get("music", True) else None, sil=sil, sticker_idx=n)
        flag = "" if m["crop"].get("found", True) else "  (no face found: centred crop, check framing)"
        print(f"{s['id']}: {m['duration']} s, {m['size_mb']} MB{flag}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    main(sys.argv[1], sys.argv[2:] or None)
