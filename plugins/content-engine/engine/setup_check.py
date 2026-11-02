"""Check (and with --install, set up) the tools the engine needs in Claude's workspace.

  python setup_check.py            -> plain-English report, installs nothing
  python setup_check.py --install  -> installs what's missing (Claude asks the owner first)

Everything runs in Claude's cloud workspace. Nothing is installed on the owner's computer.
"""
import importlib, json, shutil, subprocess, sys

PIP = {"faster_whisper": "faster-whisper", "cv2": "opencv-python-headless", "scipy": "scipy",
       "numpy": "numpy", "PIL": "pillow"}
WHAT = {
    "ffmpeg": "the video editor itself (cuts, crops, sound)",
    "faster_whisper": "speech-to-text, so every word gets a timestamp (about 75 MB, plus a 480 MB voice model on first use)",
    "cv2": "face finding, so vertical crops keep you in shot (about 60 MB)",
    "scipy": "the music bed maker (about 40 MB)",
    "numpy": "number crunching the others rely on",
    "PIL": "draws captions, hooks and stickers in your fonts",
}

HF_FIX = ("The voice model can't download, because Claude's settings are blocking huggingface.co.\n"
          "Fix (takes a minute): in Claude, open Settings, then Capabilities. Under code execution, set the\n"
          "domain allowlist to \"All domains\" (or add huggingface.co). Then start a new chat and try again.")


def model_access(model="small"):
    """'cached' if the voice model is already here, 'ok' if it can download, 'blocked' if not."""
    import glob, os, urllib.error, urllib.request
    home = os.path.expanduser("~/.cache/huggingface/hub")
    if glob.glob(os.path.join(home, f"models--Systran--faster-whisper-{model}", "snapshots", "*", "model.bin")):
        return "cached"
    try:
        req = urllib.request.Request(f"https://huggingface.co/api/models/Systran/faster-whisper-{model}",
                                     headers={"User-Agent": "content-engine"})
        urllib.request.urlopen(req, timeout=12).read(64)
        return "ok"
    except urllib.error.HTTPError as e:
        return "blocked" if e.code in (403, 407) else "ok"
    except Exception:
        return "blocked"


def status():
    s = {"ffmpeg": bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))}
    for mod in PIP:
        try:
            importlib.import_module(mod); s[mod] = True
        except Exception:
            s[mod] = False
    if s["ffmpeg"]:
        out = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
        s["ffmpeg_denoise"] = " afftdn " in out
        s["ffmpeg_zscale"] = " zscale " in out
    return s


def install(missing):
    pkgs = [PIP[m] for m in missing if m in PIP]
    if pkgs:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--break-system-packages"] + pkgs, check=True)
    if "ffmpeg" in missing:
        print("ffmpeg is missing and can't be added with pip. Try: apt-get install -y ffmpeg (if allowed here).")


if __name__ == "__main__":
    s = status()
    missing = [k for k in ["ffmpeg"] + list(PIP) if not s.get(k)]
    if "--install" in sys.argv and missing:
        install(missing)
        s = status(); missing = [k for k in ["ffmpeg"] + list(PIP) if not s.get(k)]
    print(json.dumps(s))
    if not missing:
        print("All set. Everything the engine needs is here.")
    else:
        print("Needs installing in Claude's workspace (not on your computer):")
        for m in missing:
            print(f"- {m}: {WHAT.get(m, '')}")
    if s.get("faster_whisper"):
        acc = model_access()
        print(json.dumps({"voice_model": acc}))
        if acc == "blocked":
            print(HF_FIX)
    if s.get("ffmpeg") and not s.get("ffmpeg_denoise"):
        print("Note: this ffmpeg has no voice clean-up filter. Audio will still be levelled, just not de-noised.")
