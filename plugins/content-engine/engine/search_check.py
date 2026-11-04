"""Check that the search phrases from the search brief made it into the copy, after the voice pass.

  python search_check.py <search-brief.json> <file.txt | manifest.json | upload-copy.txt | spec.json | shorts-plan.json>

search-brief.json (Claude writes it straight after the transcript, before any hooks):
{
  "primary":   "is a google business profile free",        # the exact phrase people type
  "variants":  ["google business profile cost", "free google listing"],
  "questions": ["how do I set up a google business profile", "how do I get more google reviews"],
  "local":     "perth",                                      # optional: their town or region
  "terms":     ["google maps", "local seo"]                 # optional: related words customers use
}

Prints every piece of copy in the file with what it carries (P = primary phrase or a variant,
Q = one of the long-tail questions, L = the local word), then the questions nothing used yet.
A phrase counts when all its main words appear in the piece, in any order, so voice edits around
the phrase still pass. Hooks and on-screen overlays are allowed to skip the phrase; titles,
descriptions, first caption lines, blog headings and pin titles should carry it.
"""
import json, re, sys
from voice_check import texts

STOP = set("a an the is are do does i my your you to of for in on and or with how what why when can it "
           "be this that should need".split())


def words(s):
    return [w for w in re.findall(r"[a-z0-9$']+", s.lower().replace("’", "'"))]


def key(phrase):
    k = [w for w in words(phrase) if w not in STOP]
    return k or words(phrase)


def carries(text, phrase):
    have = set(words(text))
    return all(w in have or w.rstrip("s") in have or (w + "s") in have for w in key(phrase))


def check(brief_path, path):
    B = json.load(open(brief_path))
    prim = [B["primary"]] + list(B.get("variants", []))
    qs = list(B.get("questions", []))
    local = (B.get("local") or "").strip()
    used = set()
    rows = []
    if path.endswith(".json"):
        pieces = texts(path)
    else:
        lines = [l.strip() for l in open(path, encoding="utf-8").read().splitlines()]
        pieces = [(f"line {i + 1}", l) for i, l in enumerate(lines) if re.search(r"[A-Za-z]{2}", l)]
    for where, t in pieces:
        flags = ""
        if any(carries(t, p) for p in prim):
            flags += "P"
        hit = [q for q in qs if carries(t, q)]
        if hit:
            flags += "Q"; used.update(hit)
        if local and local.lower() in t.lower():
            flags += "L"
        rows.append((flags or "-", where, t))
    return rows, [q for q in qs if q not in used]


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    rows, unused = check(sys.argv[1], sys.argv[2])
    n = sum(1 for f, _, _ in rows if "P" in f)
    for f, where, t in rows:
        print(f"{f:3} {where}: {t[:90]}")
    print(f"\nPrimary phrase (or a variant) in {n} of {len(rows)} pieces.")
    if unused:
        print("Long-tail questions not used yet: " + "; ".join(unused))
    if n == 0:
        print("NOTHING carries the search phrase. Put it in the title, the first line and a heading before showing the owner.")
