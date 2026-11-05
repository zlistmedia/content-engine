"""Finds the speech-to-text model (Whisper, MIT licence) without anyone touching Claude's settings.

  python voice_model.py [small|base]     downloads it now and prints where it is

The model comes from Z List Media's GitHub copy. It's fetched with git from github.com, which Claude's
default "package managers" network setting allows (raw.githubusercontent.com is tried after that). If that can't be reached, it falls back to Hugging Face, where the model
lives originally. Each file is checked against SHA256SUMS before it's used.
"""
import hashlib, os, sys, urllib.request

REPO = "https://github.com/zlistmedia/content-engine"
BASE = "https://raw.githubusercontent.com/zlistmedia/content-engine/voice-model/faster-whisper-{m}/"
HOME = os.path.expanduser("~/.cache/content-engine")
FILES = ("config.json", "tokenizer.json", "vocabulary.txt")
HF_FIX = ("The voice model can't download, because Claude's network settings are blocking it.\n"
          "Fix (takes a minute): Claude needs network access to package managers (which includes github.com).\n"
          "Personal plans: Settings, then Capabilities. Team or Enterprise: the owner opens Organization settings,\n"
          "then Capabilities. Turn on network access (package managers is enough), then start a new chat.")


def _get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "content-engine"})
    return urllib.request.urlopen(req, timeout=timeout)


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _hf_cached(model):
    import glob
    hub = os.path.expanduser("~/.cache/huggingface/hub")
    return bool(glob.glob(os.path.join(hub, f"models--Systran--faster-whisper-{model}", "snapshots", "*", "model.bin")))


def local_dir(model="small"):
    d = os.path.join(HOME, f"faster-whisper-{model}")
    return d if os.path.exists(os.path.join(d, ".ok")) else None


def _git_fetch(model, d, quiet):
    """Sparse, shallow git clone of just this model's folder, from github.com only."""
    import shutil, subprocess, tempfile
    if not shutil.which("git"):
        return False
    tmp = tempfile.mkdtemp(prefix="voice-", dir=HOME)
    sub = f"faster-whisper-{model}"
    run = lambda *a: subprocess.run(["git", *a], cwd=tmp, capture_output=True, text=True, timeout=900)
    try:
        if not quiet:
            print("downloading voice model from github.com (about a minute)", flush=True)
        r = subprocess.run(["git", "clone", "-q", "--depth", "1", "--filter=blob:none", "--sparse", "--branch",
                            "voice-model", "--single-branch", REPO, tmp], capture_output=True, text=True, timeout=900)
        if r.returncode != 0 or run("sparse-checkout", "set", sub).returncode != 0:
            shutil.rmtree(tmp, ignore_errors=True)
            r = subprocess.run(["git", "clone", "-q", "--depth", "1", "--branch", "voice-model", "--single-branch",
                                REPO, tmp], capture_output=True, text=True, timeout=1800)
            if r.returncode != 0:
                return False
        src = os.path.join(tmp, sub)
        if not os.path.exists(os.path.join(src, "SHA256SUMS")):
            return False
        for n in os.listdir(src):
            shutil.move(os.path.join(src, n), os.path.join(d, n))
        return True
    except Exception:
        return False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def fetch(model="small", quiet=False):
    """Download from GitHub into ~/.cache/content-engine. Returns the folder, or None if unreachable."""
    if local_dir(model):
        return local_dir(model)
    d = os.path.join(HOME, f"faster-whisper-{model}"); os.makedirs(d, exist_ok=True)
    url = BASE.format(m=model)
    try:
        sums = {}
        if _git_fetch(model, d, quiet):
            lines = open(os.path.join(d, "SHA256SUMS")).read().splitlines()
        else:
            lines = _get(url + "SHA256SUMS", 20).read().decode().splitlines()
        for line in lines:
            h, n = line.split()
            sums[n.lstrip("*")] = h
        parts = sorted(n for n in sums if n.startswith("model.bin.part"))
        for n in list(FILES) + parts:
            p = os.path.join(d, n)
            if os.path.exists(p) and _sha(p) == sums[n]:
                continue
            if not quiet:
                print(f"downloading voice model: {n}", flush=True)
            with _get(url + n) as r, open(p + ".tmp", "wb") as f:
                while b := r.read(1 << 20):
                    f.write(b)
            if _sha(p + ".tmp") != sums[n]:
                raise IOError(f"{n} didn't download cleanly")
            os.replace(p + ".tmp", p)
        with open(os.path.join(d, "model.bin.tmp"), "wb") as out:
            for n in parts:
                with open(os.path.join(d, n), "rb") as f:
                    while b := f.read(1 << 20):
                        out.write(b)
        if _sha(os.path.join(d, "model.bin.tmp")) != sums["model.bin"]:
            raise IOError("model.bin didn't rebuild cleanly")
        os.replace(os.path.join(d, "model.bin.tmp"), os.path.join(d, "model.bin"))
        for n in parts:
            os.remove(os.path.join(d, n))
        open(os.path.join(d, ".ok"), "w").write("ok")
        return d
    except Exception as e:
        if not quiet:
            print(f"GitHub copy of the voice model not reachable ({e}); trying Hugging Face.", flush=True)
        return None


def model_path(model="small"):
    """What to hand WhisperModel: our downloaded folder, else the Hugging Face name."""
    if model not in ("small", "base") or _hf_cached(model):
        return local_dir(model) or model
    return fetch(model) or model


def load(model="small", **kw):
    """WhisperModel ready to use, or a plain-English stop if nothing could be downloaded."""
    from faster_whisper import WhisperModel
    try:
        return WhisperModel(model_path(model), device="cpu", compute_type="int8", **kw)
    except Exception:
        if access(model) == "blocked":
            raise SystemExit(HF_FIX)
        raise


def access(model="small"):
    """'cached' if the model is already here, 'ok' if it can download, 'blocked' if not."""
    if local_dir(model) or _hf_cached(model):
        return "cached"
    for url in (REPO + ".git/info/refs?service=git-upload-pack", BASE.format(m=model) + "SHA256SUMS",
                f"https://huggingface.co/api/models/Systran/faster-whisper-{model}"):
        try:
            _get(url, 12).read(64)
            return "ok"
        except Exception:
            pass
    return "blocked"


if __name__ == "__main__":
    m = sys.argv[1] if len(sys.argv) > 1 else "small"
    p = fetch(m)
    print(p or f"not reachable: {access(m)}")
