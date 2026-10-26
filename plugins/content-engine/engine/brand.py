"""Brand layer: reads brand-profile.json and draws every on-screen element in the buyer's look.

Nothing in the engine picks a colour or a font itself. Everything comes through here, so a
render can't drift off brand.
"""
import json, os, re
from PIL import Image, ImageDraw, ImageFont

HEX = re.compile(r"^#?([0-9a-fA-F]{6})$")


def rgba(hexstr, a=255):
    m = HEX.match(hexstr.strip())
    if not m:
        raise ValueError(f"Not a hex colour: {hexstr}")
    h = m.group(1)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def luminance(c):
    def ch(v):
        v = v / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = c[:3]
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = sorted([luminance(a), luminance(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


class Brand:
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.root = os.path.dirname(self.path)
        self.p = json.load(open(self.path, encoding="utf-8"))
        look = self.p["look"]
        self.colours = {k: rgba(v) for k, v in look["colours"].items()}
        self.fonts = look["fonts"]
        self.shorts = look.get("shorts", {})
        self.never_pairs = [tuple(x) for x in look.get("never_pairs", [])]

    # ---------- lookups ----------
    def c(self, role, a=255):
        if role in (None, "none", "transparent"):
            return (0, 0, 0, 0)
        if role.startswith("#"):
            raise ValueError(f"Use a named colour from the profile, not a raw hex ({role}). Keeps renders on brand.")
        if role not in self.colours:
            raise KeyError(f"Colour role '{role}' isn't in the profile. Roles: {', '.join(self.colours)}")
        r, g, b, _ = self.colours[role]
        return (r, g, b, a)

    def font_path(self, role):
        f = self.fonts[role]
        p = f["file"] if isinstance(f, dict) else f
        return p if os.path.isabs(p) else os.path.join(self.root, p)

    def font(self, role, size, strict=False):
        f = self.fonts[role]
        fnt = ImageFont.truetype(self.font_path(role), size)
        var = f.get("variation") if isinstance(f, dict) else None
        if var:
            ok = False
            try:
                fnt.set_variation_by_name(var); ok = True
            except Exception:
                try:
                    axes = fnt.get_variation_axes()
                    if axes and str(var).isdigit():
                        fnt.set_variation_by_axes([int(var)] + [a["default"] for a in axes[1:]]); ok = True
                except Exception:
                    pass
            if not ok and strict:
                names = []
                try:
                    names = [n.decode() if isinstance(n, bytes) else n for n in fnt.get_variation_names()]
                except Exception:
                    pass
                raise ValueError(f"weight '{var}' isn't in this font file" + (f" (it has: {', '.join(names)})" if names else " (it isn't a variable font: point to the weight's own file instead)"))
        return fnt

    # Defaults the renderers use when a field is left out. validate() checks these too.
    DEFAULTS = {
        "hook": {"text": "light", "band": "primary"},
        "captions_word": {"fill": "light", "stroke": "primary"},
        "captions_phrase": {"fill": "primary", "card": "light", "highlight": "accent", "stroke": "primary"},
        "sticker": {"text": "primary", "fill": "accent"},
    }

    def case(self, role, text):
        f = self.fonts.get(role, {})
        mode = f.get("case", "as-is") if isinstance(f, dict) else "as-is"
        return text.upper() if mode == "upper" else text.lower() if mode == "lower" else text

    def tracking(self, role):
        f = self.fonts.get(role, {})
        return f.get("tracking", 0) if isinstance(f, dict) else 0

    def check_pair(self, fg, bg):
        if (fg, bg) in self.never_pairs or (bg, fg) in self.never_pairs:
            raise ValueError(f"The style guide says never put {fg} on {bg}.")

    # ---------- text helpers ----------
    @staticmethod
    def tw(font, t, stroke=0):
        b = font.getbbox(t, stroke_width=stroke)
        return b[2] - b[0]

    def tw_tracked(self, font, t, track):
        if not track:
            return self.tw(font, t)
        return sum(self.tw(font, ch) for ch in t) + track * (len(t) - 1)

    def draw_text(self, d, xy, t, font, fill, track=0, stroke=0, stroke_fill=None):
        if not track:
            d.text(xy, t, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
            return
        x, y = xy
        for ch in t:
            d.text((x, y), ch, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
            x += self.tw(font, ch) + track

    def fit(self, role, lines, max_w, start, floor=36, track=None):
        track = self.tracking(role) if track is None else track
        size = start
        while size > floor:
            f = self.font(role, size)
            if max(self.tw_tracked(f, l, track) for l in lines) <= max_w:
                return f, size
            size -= 2
        return self.font(role, floor), floor

    # ---------- elements ----------
    def hook(self, lines, path, max_w=980):
        """Pinned hook at the top of a Short. Styles: band | plain | pill."""
        s = self.shorts.get("hook", {})
        role = s.get("font", "display")
        style = s.get("style", "band")
        lines = [self.case(role, l) for l in lines]
        txt, bg, drop = s.get("text", "light"), s.get("band", "primary"), s.get("drop")
        if style != "plain":
            self.check_pair(txt, bg)
        track = self.tracking(role)
        pad = 50 if style != "plain" else 10
        f, size = self.fit(role, lines, max_w - pad * 2, s.get("size", 92))
        lws = [self.tw_tracked(f, l, track) for l in lines]
        lh = int(size * s.get("line_height", 1.06))
        bw, bh = max(lws) + pad * 2, lh * len(lines) + (56 if style != "plain" else 20)
        dx = 8 if drop else 0
        stroke = s.get("stroke_width", 6) if style == "plain" else 0
        im = Image.new("RGBA", (bw + dx + 12 + stroke * 2, bh + dx + 12 + stroke * 2), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        if style == "band":
            d.rectangle([0, 0, bw, bh], fill=self.c(bg))
        elif style == "pill":
            d.rounded_rectangle([0, 0, bw, bh], radius=bh // 2 if len(lines) == 1 else 40, fill=self.c(bg))
        y = (28 if style != "plain" else 10) + stroke
        for l, lw in zip(lines, lws):
            x = (bw - lw) // 2 + stroke
            if drop:
                self.draw_text(d, (x + dx, y + dx), l, f, self.c(drop), track)
            self.draw_text(d, (x, y), l, f, self.c(txt), track,
                           stroke=stroke, stroke_fill=self.c(s.get("stroke", bg)) if stroke else None)
            y += lh
        im.save(path)
        return im.size

    def sticker(self, text, path, idx=0):
        s = self.shorts.get("sticker", {})
        role = s.get("font", "label")
        text = self.case(role, text)
        f = self.font(role, s.get("size", 30))
        fills = s.get("fills", [s.get("fill", "accent")])
        fill = fills[idx % len(fills)]
        fg, border = s.get("text", "primary"), s.get("border", "primary")
        self.check_pair(fg, fill)
        w = self.tw(f, text)
        pw, ph = w + 36, int(f.size * 2)
        im = Image.new("RGBA", (pw + 14, ph + 14), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        if s.get("shadow", True):
            d.rectangle([8, 8, 8 + pw, 8 + ph], fill=self.c(border))
        if s.get("shape", "rect") == "pill":
            d.rounded_rectangle([0, 0, pw, ph], radius=ph // 2, fill=self.c(fill), outline=self.c(border), width=4)
        else:
            d.rectangle([0, 0, pw, ph], fill=self.c(fill), outline=self.c(border), width=4)
        b = f.getbbox(text)
        d.text((18, (ph - (b[3] - b[1])) // 2 - b[1]), text, font=f, fill=self.c(fg))
        rot = s.get("rotate", -6) * (1 if idx % 2 == 0 else -1)
        if rot:
            im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
        im.save(path)
        return im.size

    def caption_word(self, word, path, max_w=900):
        """One word at a time. Big, outlined, hard shadow. No box."""
        s = self.shorts.get("captions", {})
        role = s.get("font", "display")
        t = self.case(role, word)
        sw = s.get("stroke_width", 7)
        size = s.get("size", 118)
        while True:
            f = self.font(role, size)
            b = f.getbbox(t, stroke_width=sw)
            w, h = b[2] - b[0], b[3] - b[1]
            if w <= max_w or size <= 56:
                break
            size -= 4
        pad, sh = 24, s.get("shadow_offset", 8)
        im = Image.new("RGBA", (w + pad * 2 + sh, h + pad * 2 + sh), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        x, y = pad - b[0], pad - b[1]
        stroke_c = self.c(s.get("stroke", "primary"))
        if sh:
            sc = self.c(s.get("shadow", s.get("stroke", "primary")))
            d.text((x + sh, y + sh), t, font=f, fill=sc, stroke_width=sw, stroke_fill=sc)
        d.text((x, y), t, font=f, fill=self.c(s.get("fill", "light")), stroke_width=sw, stroke_fill=stroke_c)
        im.save(path)
        return im.size

    def caption_phrase(self, tokens, path, max_w=900):
        """Two to four words on a card, key words highlighted. tokens = [(word, is_key)]."""
        s = self.shorts.get("captions", {})
        role = s.get("font", "body")
        f = self.font(role, s.get("size", 60))
        gap, lh = int(f.size * 0.27), int(f.size * 1.27)
        padx, pady = 34, 22
        card, fg, hl, hlfg = s.get("card", "light"), s.get("fill", "primary"), s.get("highlight", "accent"), s.get("highlight_text", s.get("fill", "primary"))
        lines, w = [[]], 0
        for t, k in tokens:
            t = self.case(role, t)
            x = self.tw(f, t) + (18 if k else 0)
            if w and w + gap + x > max_w - padx * 2:
                lines.append([]); w = 0
            lines[-1].append((t, k, x)); w += (gap if w else 0) + x
        widths = [sum(x for _, _, x in L) + gap * (len(L) - 1) for L in lines]
        bw, bh, sh = max(widths) + padx * 2, lh * len(lines) + pady * 2, 10
        im = Image.new("RGBA", (bw + sh + 8, bh + sh + 8), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        if card not in (None, "none"):
            d.rectangle([sh, sh, sh + bw, sh + bh], fill=self.c(s.get("stroke", "primary")))
            d.rectangle([0, 0, bw, bh], fill=self.c(card), outline=self.c(s.get("stroke", "primary")), width=5)
        y = pady
        for L, lw in zip(lines, widths):
            x = (bw - lw) // 2
            for t, k, x2 in L:
                if k:
                    d.rectangle([x - 4, y + 6, x + x2 - 4, y + lh - 6], fill=self.c(hl))
                    d.text((x + 5, y), t, font=f, fill=self.c(hlfg))
                else:
                    stroke = 0 if card not in (None, "none") else s.get("stroke_width", 5)
                    d.text((x, y), t, font=f, fill=self.c(fg), stroke_width=stroke, stroke_fill=self.c(s.get("stroke", "primary")))
                x += x2 + gap
            y += lh
        im.save(path)
        return im.size

    def logo(self, path, max_w=220):
        lp = self.p["look"].get("logo")
        if not lp:
            return None
        lp = lp if os.path.isabs(lp) else os.path.join(self.root, lp)
        if not os.path.exists(lp):
            return None
        im = Image.open(lp).convert("RGBA")
        if im.width > max_w:
            im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
        im.save(path)
        return im.size

    # ---------- checks ----------
    def validate(self):
        """Return a list of problems a buyer must sort before rendering. Empty list = good to go."""
        probs = []
        for role, f in self.fonts.items():
            p = self.font_path(role)
            if not os.path.exists(p):
                probs.append(f"Font for '{role}' not found: {p}")
                continue
            try:
                fnt = self.font(role, 40, strict=True)
                for ch in "AaZz09?!'":
                    if fnt.getbbox(ch)[2] <= 0:
                        probs.append(f"Font for '{role}' has no '{ch}' glyph")
            except Exception as e:
                probs.append(f"Font for '{role}' won't load: {e}")
        for sect in ("hook", "captions", "sticker"):
            for k, v in self.shorts.get(sect, {}).items():
                if isinstance(v, str) and v.startswith("#"):
                    probs.append(f"{sect}.{k} uses a raw hex ({v}). Use a colour role from the palette.")
        cap = self.shorts.get("captions", {})
        mode = cap.get("mode", "word")
        cd = dict(self.DEFAULTS["captions_word" if mode == "word" else "captions_phrase"], **cap)
        cd.setdefault("highlight_text", cd.get("fill"))
        hk = dict(self.DEFAULTS["hook"], **self.shorts.get("hook", {}))
        if mode == "word":
            checks = [(cd["fill"], cd["stroke"], "captions fill on outline")]
        else:
            checks = [(cd["highlight_text"], cd["highlight"], "highlighted caption word")]
            checks.append((cd["fill"], cd["card"], "captions text on card") if cd.get("card") not in (None, "none")
                          else (cd["fill"], cd["stroke"], "captions fill on outline"))
        if hk.get("style", "band") != "plain":
            checks.append((hk["text"], hk["band"], "hook text on band"))
        st = self.shorts.get("sticker", {})
        if st.get("enabled"):
            sd = dict(self.DEFAULTS["sticker"], **st)
            for fill in sd.get("fills", [sd["fill"]]):
                checks.append((sd["text"], fill, "sticker text"))
        for fg, bg, what in checks:
            for c in (fg, bg):
                if c and c != "none" and c not in self.colours and not str(c).startswith("#"):
                    probs.append(f"{what}: '{c}' isn't one of the palette's colours ({', '.join(self.colours)}).")
            if fg and bg and bg != "none" and fg in self.colours and bg in self.colours:
                r = contrast(self.colours[fg], self.colours[bg])
                if r < 3:
                    probs.append(f"Low contrast for {what} ({r:.1f}:1). Pick another pair from the guide.")
                if (fg, bg) in self.never_pairs or (bg, fg) in self.never_pairs:
                    probs.append(f"{what}: the guide says never pair {fg} and {bg}.")
        return probs


    def swatches(self, path):
        """One image of the palette with role, the guide's name and hex, for the owner to confirm by eye."""
        names = self.p["look"].get("colour_names", {})
        n = len(self.colours); W, H = 260 * n, 300
        im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
        try:
            f = self.font("body", 26)
        except Exception:
            f = ImageFont.load_default()
        for i, (role, c) in enumerate(self.colours.items()):
            x = i * 260
            d.rectangle([x + 10, 10, x + 250, 200], fill=c[:3], outline=(200, 200, 200))
            hexs = self.p["look"]["colours"][role].upper()
            d.text((x + 14, 212), names.get(role, role), font=f, fill=(20, 20, 20))
            d.text((x + 14, 250), hexs, font=f, fill=(90, 90, 90))
        im.save(path)
        return path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Check a brand profile and, optionally, save a swatch sheet of its colours.\n\n"
              "  python brand.py <brand-profile.json> [--swatches swatches.png]")
        sys.exit(1)
    b = Brand(sys.argv[1])
    if "--swatches" in sys.argv:
        print(b.swatches(sys.argv[sys.argv.index("--swatches") + 1]))
    pr = b.validate()
    print("Brand profile OK" if not pr else "Sort these first:\n- " + "\n- ".join(pr))
