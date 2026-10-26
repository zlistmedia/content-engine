"""The 10-second brand test that ends setup: proves fonts, colours, captions and music before any real work.

  python test_clip.py <brand-profile.json> <out.mp4> [clip.mp4]

With a clip (any 10 to 30 seconds of the owner talking, a phone selfie is fine) it transcribes the
first ten seconds and renders a real mini Short. Without one it renders the look on a plain brand
background with a sample line from the style guide, so they still see their captions and hook.
"""
import os, sys, json, tempfile
import numpy as np
import ce_util as U
from brand import Brand
import shorts as S
import music as MUSIC


def synthetic(B, work, seconds=8.0):
    line = (B.p.get("voice", {}).get("sample_lines") or ["This is how your captions will look on every Short."])[0]
    words = line.split()
    step = seconds / (len(words) + 1)
    W = [{"w": w, "s": round(0.4 + i * step, 3), "e": round(0.4 + i * step + step * 0.85, 3), "p": 1} for i, w in enumerate(words)]
    bg = B.p["look"]["colours"].get("primary", "#222222").lstrip("#")
    src = os.path.join(work, "bg.mp4")
    U.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c=0x{bg}:s=1080x1920:r=30:d={seconds + 1}",
           "-f", "lavfi", "-i", f"sine=frequency=1:sample_rate=48000:duration={seconds + 1}",
           "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", "-shortest", src])
    return src, W


def main(profile, out, clip=None):
    B = Brand(profile)
    probs = B.validate()
    if probs:
        raise SystemExit("Sort these in the brand profile first:\n- " + "\n- ".join(probs))
    work = tempfile.mkdtemp(prefix="brandtest_")
    biz = B.p.get("business", {}).get("name", "Your business")
    if clip:
        import footage as F, transcribe as T
        master, wav, _ = F.prep(clip, work)
        W = T.apply_fixes(T.transcribe(wav), B.p.get("voice", {}).get("spelling_fixes", {}))
        idx = [i for i, x in enumerate(W) if x["e"] <= 11.0] or list(range(min(len(W), 20)))
        runs = [[idx[0], idx[-1]]]
        sil = U.silences(master)
    else:
        master, W = synthetic(B, work)
        runs = [[0, len(W) - 1]]
        sil = []
    bed = None
    mus = B.shorts.get("music", {})
    if mus.get("mode", "none") == "bed":
        bed = os.path.join(work, "bed.wav")
        MUSIC.make(bed, mus.get("mood", "bright"), int(mus.get("bpm", 108)), 30)
    stick = (B.shorts.get("sticker", {}).get("words") or [None])[0]
    m = S.render_short(B, master, W, runs, ["THIS IS", biz], out, sticker=stick,
                       key=[W[runs[0][1]]["w"]], bed=bed, sil=sil)
    print(json.dumps({"test_clip": out, "seconds": m["duration"], "size_mb": m["size_mb"],
                      "face_found": m["crop"].get("found", True)}))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
