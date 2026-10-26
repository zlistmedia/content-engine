"""Check a raw video and make a clean working copy.

  python footage.py check <video>             -> plain-English report (+ JSON with --json)
  python footage.py prep <video> <workdir>    -> workdir/master.mp4 (SDR, 30 fps, upright) + workdir/audio16k.wav

The working copy fixes the things that break edits later: HDR colour from phones (looks washed out
or orange), sideways rotation flags, and variable frame rates (which knock captions out of sync).
Originals are never touched.
"""
import json, os, sys
import ce_util as U


def dropped_frames(path, fps):
    p = U.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "packet=pts_time",
               "-of", "csv=p=0", "-read_intervals", "%+120", path])
    ts = sorted(float(x) for x in p.stdout.split() if x.replace(".", "", 1).isdigit())
    gaps = [b - a for a, b in zip(ts, ts[1:])]
    if not gaps or not fps:
        return 0
    return sum(1 for g in gaps if g > 1.5 / fps)


def check(path):
    i = U.video_info(path)
    notes = []
    if i["hdr"]:
        notes.append("Recorded in HDR. The working copy converts it so colours look right everywhere.")
    if i["rotation"]:
        notes.append("Has a rotation flag. The working copy stands it upright.")
    short = min(i["width"], i["height"])
    if short < 720:
        notes.append(f"Low resolution ({i['width']}x{i['height']}). It will work, but looks soft on phones. 1080p is best.")
    if not i["has_audio"]:
        notes.append("No sound track found. Shorts need your voice.")
    drops = dropped_frames(path, i["fps"])
    i["dropped_frames_first_2min"] = drops
    if drops:
        notes.append(f"{drops} dropped frames in the first two minutes. The working copy evens these out.")
    if i["duration"] < 15:
        notes.append("Shorter than 15 seconds. Fine for a test, too short for three Shorts.")
    i["notes"] = notes
    return i


def clean_enough(i, path):
    """Footage usable as-is: SDR, upright, steady frame rate, no bigger than 1080 on the short side."""
    return (not i["hdr"] and not i["rotation"] and 23.5 <= i["fps"] <= 60.5 and min(i["width"], i["height"]) <= 1080
            and i["codec"] in ("h264", "hevc", "prores", "mpeg4") and i["pix_fmt"] in ("yuv420p", "yuvj420p")
            and dropped_frames(path, i["fps"]) == 0)


def prep(path, work, force=False):
    os.makedirs(work, exist_ok=True)
    i = U.video_info(path)
    wav = os.path.join(work, "audio16k.wav")
    if not force and clean_enough(i, path):
        # nothing to fix: point at the original instead of re-encoding (saves minutes per video)
        master = os.path.join(work, "master" + (os.path.splitext(path)[1].lower() or ".mp4"))
        if os.path.lexists(master):
            os.remove(master)
        os.symlink(os.path.abspath(path), master)
        if i["has_audio"]:
            U.run(["ffmpeg", "-y", "-v", "error", "-i", master, "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", wav])
        json.dump({"source": os.path.abspath(path), "source_info": i, "master_info": i, "used_original": True},
                  open(os.path.join(work, "footage.json"), "w"), indent=1)
        return master, wav, i
    master = os.path.join(work, "master.mp4")
    vf = []
    if i["hdr"]:
        vf.append("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=reinhard:param=0.5:desat=0,"
                  "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
    vf.append("fps=30")
    if i["portrait"]:
        vf.append("scale=1080:-2:flags=lanczos" if i["width"] > 1080 else "scale=trunc(iw/2)*2:trunc(ih/2)*2")
    else:
        vf.append("scale=-2:1080:flags=lanczos" if i["height"] > 1080 else "scale=trunc(iw/2)*2:trunc(ih/2)*2")
    vf.append("format=yuv420p")
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", path, "-vf", ",".join(vf),
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-g", "30",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709"]
    cmd += ["-c:a", "aac", "-b:a", "192k", "-ar", "48000"] if i["has_audio"] else ["-an"]
    try:
        U.run(cmd + [master])
    except RuntimeError as e:
        if i["hdr"] and "zscale" in str(e):
            # this ffmpeg has no zscale: fall back to the simpler colour conversion
            vf[0] = "colorspace=all=bt709:iall=bt2020:fast=1"
            cmd[cmd.index("-vf") + 1] = ",".join(vf)
            U.run(cmd + [master])
        else:
            raise
    if i["has_audio"]:
        U.run(["ffmpeg", "-y", "-v", "error", "-i", master, "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", wav])
    out = U.video_info(master)
    json.dump({"source": os.path.abspath(path), "source_info": i, "master_info": out},
              open(os.path.join(work, "footage.json"), "w"), indent=1)
    return master, wav, out


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    if sys.argv[1] == "check":
        r = check(sys.argv[2])
        if "--json" in sys.argv:
            print(json.dumps(r, indent=1))
        else:
            print(f"{r['width']}x{r['height']}, {r['fps']} fps, {r['duration']:.0f} s, {r['size_mb']} MB, "
                  f"{'portrait' if r['portrait'] else 'landscape'}")
            print("\n".join("- " + n for n in r["notes"]) or "- Looks good. Nothing to fix.")
    elif sys.argv[1] == "prep":
        m, w, o = prep(sys.argv[2], sys.argv[3], force="--force" in sys.argv)
        print(f"Working copy ready: {m} ({o['width']}x{o['height']}, {o['duration']:.0f} s)")
