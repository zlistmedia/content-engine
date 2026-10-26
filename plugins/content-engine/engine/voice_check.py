"""Check written copy against the owner's voice rules before they see it.

  python voice_check.py <brand-profile.json> <file.txt | manifest.json | shorts-plan.json | edit-plan.json | spec.json>

Reads every piece of copy in the file: captions, hooks, chapter titles, callouts, stickers, the end card,
and the headlines and bodies in Level 3 specs. Paths, ids and settings are skipped. Offers the profile
lists as warm-only or never-mention are flagged like banned words.

Flags banned words and phrases, plus rules it can check mechanically when the profile's voice rules
mention them: em dashes, exclamation marks, sentences starting with And / But / Because, and US
spellings for Australian or British English. Everything else in the voice rules is Claude's job.
"""
import json, re, sys

US_UK = {"color": "colour", "favorite": "favourite", "organize": "organise", "realize": "realise",
         "center": "centre", "behavior": "behaviour", "optimize": "optimise", "analyze": "analyse",
         "mom": "mum", "customize": "customise", "gray": "grey", "defense": "defence"}

# Keys whose values are never words the audience sees (paths, ids, settings).
SKIP = {"brand", "source", "words", "out", "out_dir", "files", "file", "id", "date", "time", "timezone",
        "url", "image", "photo", "src", "href", "runs", "overrides", "layout", "type", "ground", "font",
        "colour", "color", "key", "highlight", "platforms", "scheduler", "youtube_id", "slug", "photo_shift"}


def walk(x, where, out):
    if isinstance(x, str):
        if re.search(r"[A-Za-z]{2}", x) and not re.fullmatch(r"[^\s]*[/\\.][^\s]*", x):
            out.append((where, x))
    elif isinstance(x, list):
        strs = [i for i in x if isinstance(i, str)]
        if strs and len(strs) == len(x):
            walk(" ".join(strs), where, out)      # hook lines read as one line
        else:
            for n, i in enumerate(x):
                name = next((i[k] for k in ("label", "id", "title", "type") if isinstance(i, dict)
                             and isinstance(i.get(k), str)), str(n + 1))
                walk(i, f"{where} [{name}]", out)
    elif isinstance(x, dict):
        for k, v in x.items():
            if k in SKIP:
                continue
            walk(v, f"{where} / {k}" if where else str(k), out)


def texts(path):
    """Every piece of copy in a plain-text file, a manifest, a Shorts or edit plan, or a Level 3 spec:
    captions, hooks, chapter titles, callouts, stickers, end card, headlines, bodies, subjects."""
    if not path.endswith(".json"):
        return [("text", open(path, encoding="utf-8").read())]
    out = []
    walk(json.load(open(path, encoding="utf-8")), "", out)
    return out


def check(profile, path):
    prof = json.load(open(profile, encoding="utf-8"))
    v = prof.get("voice", {})
    rules = " ".join(v.get("rules", [])).lower()
    spelling = prof.get("business", {}).get("spelling", "en-AU")
    offers = prof.get("offers", {})
    hold_back = [(o, "warm-only offer (only for people who already know them)") for o in offers.get("warm_only", [])]
    hold_back += [(o, "retired offer, never mention") for o in offers.get("never_mention", [])]
    found = []
    for where, t in texts(path):
        low = t.lower()
        for w in v.get("banned_words", []):
            if re.search(r"(?<![a-z])" + re.escape(w.lower()) + r"(?![a-z])", low):
                found.append((where, f"banned: '{w}'"))
        for o, why in hold_back:
            name = o if isinstance(o, str) else o.get("name", "")
            if name and re.search(r"(?<![a-z])" + re.escape(name.lower()) + r"(?![a-z])", low):
                found.append((where, f"{why}: '{name}'"))
        if "em dash" in rules and ("—" in t or " -- " in t):
            found.append((where, "em dash"))
        if "exclamation" in rules and "!" in t:
            found.append((where, "exclamation mark"))
        if re.search(r"starting with and, but or because|start with and, but or because", rules):
            for m in re.finditer(r"(?:^|[.!?]\s+|\n)(And|But|Because)\b", t):
                found.append((where, f"sentence starts with '{m.group(1)}'"))
        if spelling in ("en-AU", "en-GB", "en-NZ", "en-IE"):
            for us, uk in US_UK.items():
                if re.search(r"\b" + us.strip() + r"\b", low):
                    found.append((where, f"US spelling '{us.strip()}' (use '{uk.strip()}')"))
    return found


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    f = check(sys.argv[1], sys.argv[2])
    print("Voice check: clean." if not f else "Voice check found:\n" + "\n".join(f"- {w}: {p}" for w, p in f))
