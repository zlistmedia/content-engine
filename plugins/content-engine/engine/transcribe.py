"""Transcribe with word timings and lay out the transcript for picking moments.

  python transcribe.py <audio16k.wav> <workdir> [--model small] [--fixes brand-profile.json]
  (--fixes applies the profile's spelling fixes and converts US spelling to the profile's own)

Writes:
  words.json        every word with start/end seconds (index = word number)
  transcript.txt    numbered sentences: [first-last] m:ss  text   (used to pick Shorts)
  retakes.txt       lines said twice (likely retakes to skip)
"""
import json, os, re, sys, wave
from collections import defaultdict
import numpy as np


def transcribe(wav, model="small", threads=2):
    from faster_whisper import WhisperModel
    w = wave.open(wav)
    a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    m = WhisperModel(model, device="cpu", compute_type="int8", cpu_threads=threads)
    segs, info = m.transcribe(a, language="en", word_timestamps=True, vad_filter=False, beam_size=5)
    words = []
    for s in segs:
        for x in s.words:
            st, en = x.start, x.end
            # Whisper hides a long pause inside the next word: pull its start in.
            if en - st > 0.6:
                st = en - 0.38
            words.append({"w": x.word.strip(), "s": round(st, 3), "e": round(en, 3), "p": round(x.probability, 3)})
    return words


def join_split_tokens(words):
    """Whisper sometimes splits 'Z-List' into 'Z' + '-List' or '2.5' into '2' + '.5'. Join them back."""
    out = []
    for x in words:
        if out and (x["w"].startswith("-") or re_num_tail.match(x["w"]) and out[-1]["w"][-1:].isdigit()):
            out[-1]["w"] += x["w"]; out[-1]["e"] = x["e"]
        else:
            out.append(dict(x))
    return out


re_num_tail = re.compile(r"^[.,]\d")


def apply_fixes(words, fixes):
    """Spelling fixes from the brand profile. Keys can be one word ('zoe') or a phrase ('chat gbt')."""
    words = join_split_tokens(words)
    norm = lambda w: re.sub(r"[^a-z0-9'-]", "", w.lower())
    singles = {k.lower(): v for k, v in (fixes or {}).items() if " " not in k.strip()}
    phrases = [(k.lower().split(), v) for k, v in (fixes or {}).items() if " " in k.strip()]
    compact = lambda w: re.sub(r"[^a-z0-9]", "", w.lower())
    for parts, rep in sorted(phrases, key=lambda p: -len(p[0])):
        target = compact("".join(parts))
        if not target:
            continue
        i = 0
        while i < len(words):
            # grow a window from word i until its letters match the phrase (however Whisper split or hyphenated it)
            acc, j = "", i
            while j < len(words) and len(acc) < len(target):
                acc += compact(words[j]["w"]); j += 1
            if acc == target and words[i]["w"]:
                tail = re.sub(r"^.*?([.,!?;:]*)$", r"\1", words[j - 1]["w"])
                words[i]["w"] = rep + tail; words[i]["e"] = words[j - 1]["e"]
                for k in range(i + 1, j):
                    words[k]["w"] = ""
                i = j
            else:
                i += 1
    words = [x for x in words if x["w"]]
    for x in words:
        core = x["w"].strip(".,!?;:\"'")
        rep = singles.get(core.lower())
        if rep:
            x["w"] = x["w"].replace(core, rep)
    return words


US_TO_UK = [(r"^(colo)r(s|ed|ing|ful)?$", r"\1ur\2"), (r"^(favo)r(ite|ites|s)?$", r"\1ur\2"),
            (r"^(behavio|neighbo|labo|hono|humo|flavo)r(s)?$", r"\1ur\2"),
            (r"^(organi|reali|recogni|optimi|customi|priori|summari|speciali|apologi|minimi|maximi|categori|emphasi|utili|personali|monetis)z(e|es|ed|ing|ation|ations)$", r"\1s\2"),
            (r"^(analy|paraly)z(e|es|ed|ing)$", r"\1s\2"), (r"^(cent|theat|met|fib)er(s)?$", r"\1re\2"),
            (r"^mom(s)?$", r"mum\1"), (r"^travel(ed|er|ers|ing)$", r"travell\1"), (r"^catalog(s)?$", r"catalogue\1"),
            (r"^program(s)?$", r"programme\1"), (r"^gray$", r"grey"), (r"^defense$", r"defence"), (r"^license$", r"licence")]


def to_uk(words, spelling):
    """Whisper writes US spelling. Captions get burned in, so match the owner's spelling."""
    if spelling not in ("en-AU", "en-GB", "en-NZ", "en-IE"):
        return words
    for x in words:
        m = re.match(r"^([^A-Za-z]*)([A-Za-z]+)([^A-Za-z]*)$", x["w"])
        if not m:
            continue
        pre, core, post = m.groups()
        low = core.lower()
        for pat, rep in US_TO_UK:
            if pat.startswith("^program") and spelling == "en-AU":
                continue  # Australians write "program"
            new = re.sub(pat, rep, low)
            if new != low:
                new = new.capitalize() if core[0].isupper() else new
                x["w"] = pre + new + post
                break
    return words


def sentences(words):
    out, cur = [], []
    for i, x in enumerate(words):
        cur.append(i)
        if x["w"].endswith((".", "?", "!")) or len(cur) >= 40:
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out


def retakes(words, n=5):
    norm = [re.sub(r"[^a-z0-9']", "", x["w"].lower()) for x in words]
    seen = defaultdict(list)
    for i in range(len(norm) - n + 1):
        g = tuple(norm[i:i + n])
        if all(g):
            seen[g].append(i)
    hits = []
    for g, idx in seen.items():
        if len(idx) > 1 and idx[-1] - idx[0] < 400:
            hits.append((idx, " ".join(g)))
    hits.sort()
    # merge overlapping n-gram hits into one note per repeated stretch
    merged = []
    for idx, g in hits:
        if merged and abs(idx[0] - merged[-1][0][0]) <= n:
            continue
        merged.append((idx, g))
    return merged


def mmss(t):
    return f"{int(t // 60)}:{int(t % 60):02d}"


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    wav, work = sys.argv[1], sys.argv[2]
    model = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else "small"
    fixes, spelling = {}, "en-AU"
    if "--fixes" in sys.argv:
        prof = json.load(open(sys.argv[sys.argv.index("--fixes") + 1]))
        fixes = prof["voice"].get("spelling_fixes", {}); spelling = prof.get("business", {}).get("spelling", "en-AU")
    W = apply_fixes(to_uk(transcribe(wav, model), spelling), fixes)
    os.makedirs(work, exist_ok=True)
    json.dump({"words": W}, open(os.path.join(work, "words.json"), "w"))
    with open(os.path.join(work, "transcript.txt"), "w") as f:
        for s in sentences(W):
            f.write(f"[{s[0]}-{s[-1]}] {mmss(W[s[0]]['s'])}  {' '.join(W[i]['w'] for i in s)}\n")
    with open(os.path.join(work, "retakes.txt"), "w") as f:
        for idx, g in retakes(W):
            f.write(f"said {len(idx)}x at words {', '.join(map(str, idx))} ({', '.join(mmss(W[i]['s']) for i in idx)}): \"{g}...\"\n")
    unsure = [x for x in W if x["p"] < 0.5]
    print(f"{len(W)} words, {len(sentences(W))} sentences. {len(unsure)} words Whisper wasn't sure of.")
