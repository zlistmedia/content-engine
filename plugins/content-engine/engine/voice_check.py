"""Check written copy against the owner's voice rules before they see it.

  python voice_check.py <brand-profile.json> <file.txt | manifest.json | shorts-plan.json>

Flags banned words and phrases, plus rules it can check mechanically when the profile's voice rules
mention them: em dashes, exclamation marks, sentences starting with And / But / Because, and US
spellings for Australian or British English. Everything else in the voice rules is Claude's job.
"""
import json, re, sys

US_UK = {"color": "colour", "favorite": "favourite", "organize": "organise", "realize": "realise",
         "center": "centre", "behavior": "behaviour", "optimize": "optimise", "analyze": "analyse",
         "program ": "programme ", "mom": "mum", "fall ": "autumn ", "customize": "customise"}


def texts(path):
    if not path.endswith(".json"):
        return [("text", open(path, encoding="utf-8").read())]
    d = json.load(open(path, encoding="utf-8"))
    out = []
    for p in d.get("posts", []):
        for plat, c in p.get("captions", {}).items():
            if isinstance(c, dict):
                out += [(f"{p.get('label')} / {plat} {k}", v) for k, v in c.items()]
            else:
                out.append((f"{p.get('label')} / {plat}", c))
    for s in d.get("shorts", []):
        out.append((f"{s.get('id')} hook", " ".join(s.get("hook", []))))
    return out


def check(profile, path):
    v = json.load(open(profile, encoding="utf-8")).get("voice", {})
    rules = " ".join(v.get("rules", [])).lower()
    spelling = json.load(open(profile, encoding="utf-8")).get("business", {}).get("spelling", "en-AU")
    found = []
    for where, t in texts(path):
        low = t.lower()
        for w in v.get("banned_words", []):
            if re.search(r"(?<![a-z])" + re.escape(w.lower()) + r"(?![a-z])", low):
                found.append((where, f"banned: '{w}'"))
        if "em dash" in rules and ("—" in t or " -- " in t):
            found.append((where, "em dash"))
        if "exclamation" in rules and "!" in t:
            found.append((where, "exclamation mark"))
        if re.search(r"starting with and, but or because|start with and, but or because", rules):
            for m in re.finditer(r"(?:^|[.!?]\s+|\n)(And|But|Because)\b", t):
                found.append((where, f"sentence starts with '{m.group(1)}'"))
        if spelling in ("en-AU", "en-GB"):
            for us, uk in US_UK.items():
                if re.search(r"\b" + us.strip() + r"\b", low):
                    found.append((where, f"US spelling '{us.strip()}' (use '{uk.strip()}')"))
    return found


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    f = check(sys.argv[1], sys.argv[2])
    print("Voice check: clean." if not f else "Voice check found:\n" + "\n".join(f"- {w}: {p}" for w, p in f))
