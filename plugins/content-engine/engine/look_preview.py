"""Still preview of the Shorts look, so the owner can pick between options before any video renders.

  python look_preview.py <brand-profile.json> <out.png> [photo.jpg] [--set captions.mode=phrase hook.style=pill ...]

Draws a 9:16 frame (their photo, or a plain brand background) with the hook, a sticker and one
caption, scaled to 540x960 for a phone. Use --set to try a variation without changing the profile.
"""
import json, os, sys, tempfile
from PIL import Image
from brand import Brand


def apply_sets(B, sets):
    for s in sets:
        k, v = s.split("=", 1)
        sect, key = k.split(".", 1)
        v = json.loads(v) if v[:1] in "[{0123456789-" or v in ("true", "false") else v
        B.shorts.setdefault(sect, {})[key] = v


def render(profile, out, photo=None, sets=()):
    B = Brand(profile); apply_sets(B, sets)
    W, H = 1080, 1920
    if photo:
        im = Image.open(photo).convert("RGB")
        r = max(W / im.width, H / im.height)
        im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
        x, y = (im.width - W) // 2, (im.height - H) // 2
        im = im.crop((x, y, x + W, y + H)).convert("RGBA")
    else:
        im = Image.new("RGBA", (W, H), B.c(B.p["look"].get("preview_background", "secondary")))
    d = tempfile.mkdtemp()
    biz = B.p.get("business", {}).get("name", "Your business")
    hw, hh = B.hook(["THIS IS YOUR", "HOOK LINE"], os.path.join(d, "h.png"))
    im.alpha_composite(Image.open(os.path.join(d, "h.png")), ((W - hw) // 2, int(B.shorts.get("hook", {}).get("y", 150))))
    st = B.shorts.get("sticker", {})
    if st.get("enabled"):
        word = (st.get("words") or ["SAVE THIS"])[0]
        sw, sh = B.sticker(word, os.path.join(d, "s.png"))
        im.alpha_composite(Image.open(os.path.join(d, "s.png")), (W - sw - 56, 150 + hh + 30))
    cap = B.shorts.get("captions", {})
    cy = int(cap.get("y", 1400))
    if cap.get("mode", "word") == "word":
        line = (B.p.get("voice", {}).get("sample_lines") or [biz])[0]
        word = max((w.strip(".,!?;:'\"") for w in line.split()), key=len)
        cw, ch = B.caption_word(word, os.path.join(d, "c.png"))
    else:
        words = (B.p.get("voice", {}).get("sample_lines") or ["Captions look like this"])[0].split()[:4]
        cw, ch = B.caption_phrase([(w, i == len(words) - 1) for i, w in enumerate(words)], os.path.join(d, "c.png"))
    im.alpha_composite(Image.open(os.path.join(d, "c.png")), ((W - cw) // 2, cy - ch // 2))
    im.convert("RGB").resize((540, 960), Image.LANCZOS).save(out, quality=90)
    return out


if __name__ == "__main__":
    a = sys.argv
    if len(a) < 3:
        print(__doc__); sys.exit(1)
    sets = a[a.index("--set") + 1:] if "--set" in a else []
    photo = a[3] if len(a) > 3 and a[3] != "--set" else None
    print(render(a[1], a[2], photo, sets))
