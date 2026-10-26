"""Small shared helpers: running ffmpeg, probing files, timing maths."""
import json, os, re, subprocess, shutil

ENGINE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ENGINE, "assets")
RNNOISE = os.path.join(ASSETS, "sh.rnnn")
FPS = 30


def run(cmd, quiet=True):
    """Run a command; on failure show the tail of stderr in plain terms."""
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        tail = "\n".join(p.stderr.strip().splitlines()[-12:])
        raise RuntimeError(f"Command failed: {' '.join(cmd[:3])} ...\n{tail}")
    return p


def ffprobe(path):
    p = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", path])
    return json.loads(p.stdout)


def video_info(path):
    d = ffprobe(path)
    v = next((s for s in d["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in d["streams"] if s["codec_type"] == "audio"), None)
    if not v:
        raise RuntimeError("No video stream found. Is this a video file?")
    num, den = (v.get("avg_frame_rate") or v.get("r_frame_rate") or "30/1").split("/")
    fps = float(num) / float(den or 1) if float(den or 1) else 30.0
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = int(round(float(sd["rotation"])))
    if "rotate" in v.get("tags", {}):
        rot = int(v["tags"]["rotate"])
    w, h = int(v["width"]), int(v["height"])
    if abs(rot) in (90, 270):
        w, h = h, w
    trc = v.get("color_transfer", "") or ""
    return {
        "width": w, "height": h, "fps": round(fps, 3), "rotation": rot,
        "duration": float(d["format"].get("duration", 0) or 0),
        "codec": v.get("codec_name"), "pix_fmt": v.get("pix_fmt"),
        "hdr": trc in ("smpte2084", "arib-std-b67"), "transfer": trc,
        "has_audio": a is not None, "size_mb": round(int(d["format"].get("size", 0)) / 1e6, 1),
        "portrait": h > w,
    }


def snap(t, fps=FPS):
    return round(t * fps) / fps


def silences(path, noise="-38dB", min_d=0.4, keep=0.18):
    """Silent stretches longer than min_d, shrunk by `keep` each side so a breath stays."""
    log = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-vn", "-af",
                          f"highpass=f=80,silencedetect=noise={noise}:d={min_d}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    return [(a + keep, b - keep) for a, b in zip(st, en) if b - a > 0.5]


def subtract(iv, cuts, min_len=0.1):
    pieces = [list(iv)]
    for cs, ce in cuts:
        nxt = []
        for ps, pe in pieces:
            if ce <= ps or cs >= pe:
                nxt.append([ps, pe]); continue
            if cs > ps: nxt.append([ps, cs])
            if ce < pe: nxt.append([ce, pe])
        pieces = nxt
    return [p for p in pieces if p[1] - p[0] > min_len]


def need(binary):
    if not shutil.which(binary):
        raise RuntimeError(f"{binary} isn't installed in this workspace.")


def load_words(path):
    W = json.load(open(path))
    W = W["words"] if isinstance(W, dict) else W
    for x in W:
        x["w"] = x["w"].strip()
    return W


_FILTERS = None


def has_filter(name):
    global _FILTERS
    if _FILTERS is None:
        _FILTERS = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
    return f" {name} " in _FILTERS
