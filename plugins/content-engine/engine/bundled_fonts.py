"""Free Google Fonts that ship with the engine (SIL Open Font Licence, see fonts/licences).

When a brand profile names a font but its file isn't there, the engine uses the bundled copy,
so most owners never have to download a font. Latin characters only, which covers English captions.
"""
import os, re

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
WEIGHTS = ["Thin", "ExtraLight", "Light", "Regular", "Medium", "SemiBold", "Bold", "ExtraBold", "Black"]
ROLE_WEIGHT = {"display": "Bold", "body": "Regular", "label": "SemiBold", "accent": "Bold"}


def _key(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def _index():
    fams = {}
    for fn in os.listdir(HERE) if os.path.isdir(HERE) else []:
        if not fn.endswith(".ttf"):
            continue
        base = fn[:-4]
        if base.endswith("-Variable"):  # variable font: one file holds every weight
            fams.setdefault(_key(base[: -len("-Variable")]), {})["variable"] = fn
        else:
            fam, _, w = base.rpartition("-")
            fams.setdefault(_key(fam), {})[w] = fn
    return fams


def _split(name):
    """'Poppins Bold' -> ('poppins', 'Bold'); 'Inter' -> ('inter', None)."""
    k = _key(name)
    for w in sorted(WEIGHTS, key=len, reverse=True):
        if k.endswith(w.lower()) and len(k) > len(w):
            return k[: -len(w)], w
    return k, None


def families():
    return sorted(_index())


def resolve(name, role="body", weight=None):
    """Return (absolute path, variation name or None) for a bundled font, or None if we don't have it."""
    fam, w_in_name = _split(name)
    w = weight or w_in_name or ROLE_WEIGHT.get(role, "Regular")
    entry = _index().get(fam)
    if not entry:
        return None
    if "variable" in entry:
        return os.path.join(HERE, entry["variable"]), w
    if w in entry:
        return os.path.join(HERE, entry[w]), None
    # nearest weight we have
    order = sorted(entry, key=lambda x: abs(WEIGHTS.index(x) - WEIGHTS.index(w)) if x in WEIGHTS else 99)
    return os.path.join(HERE, entry[order[0]]), None


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Bundled fonts:\n  " + "\n  ".join(families()) + "\n\n  python bundled_fonts.py \"Poppins\" [display|body|label]")
        sys.exit(0)
    print(resolve(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "body"))
