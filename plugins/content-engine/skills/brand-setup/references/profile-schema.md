# Brand profile: every field

`brand-profile.json` lives in `Content Engine/Brand/`. Font and logo paths are relative to that
folder. A full worked example is in `examples/sample-brand/brand-profile.json` at the plugin root.

```json
{
  "profile_version": 1,
  "business": {
    "name": "Business name exactly as written",
    "owner": "Owner's name exactly as written (accents included)",
    "website": "https://...",
    "spelling": "en-AU | en-GB | en-US",
    "what_they_do": "One plain sentence"
  },
  "voice": {
    "summary": "Two or three sentences on how they sound",
    "rules": ["Writing rules from the guide, one per line"],
    "banned_words": ["words and phrases never used in captions or copy"],
    "spelling_fixes": {"lowercase as heard": "As it must be written"},
    "sample_lines": ["Their own lines from posts or emails"]
  },
  "look": {
    "colours": {"primary": "#hex", "accent": "#hex", "secondary": "#hex", "light": "#hex"},
    "colour_names": {"primary": "the guide's own name for it"},
    "never_pairs": [["accent", "secondary"]],
    "fonts": {
      "display": {"file": "fonts/Headline.ttf", "name": "Font name", "case": "upper|lower|as-is", "tracking": 0, "variation": "Bold"},
      "body":    {"file": "fonts/Body.ttf", "name": "Font name"},
      "label":   {"file": "fonts/Label.ttf", "name": "Font name", "case": "upper"}
    },
    "logo": "logo.png or null",
    "shorts": {
      "hook":     {"style": "band|pill|plain", "font": "display", "text": "accent", "band": "primary", "drop": "secondary or omit", "size": 92, "y": 150},
      "captions": {"mode": "word|phrase", "font": "display", "size": 118, "fill": "light", "stroke": "primary",
                   "stroke_width": 7, "shadow": "primary", "shadow_offset": 8, "y": 1400,
                   "card": "light (phrase mode)", "highlight": "accent", "highlight_text": "primary"},
      "sticker":  {"enabled": false, "font": "label", "fills": ["accent"], "text": "primary", "border": "primary",
                   "rotate": -6, "words": ["SAVE THIS"]},
      "end_hold": 0.7,
      "music":    {"mode": "bed|none", "mood": "bright|calm|upbeat", "bpm": 108, "level": 0.22}
    }
  },
  "offers": {
    "free":  {"name": "...", "url": "..."},
    "entry": {"name": "...", "price": "...", "url": "..."},
    "warm_only": ["offers only mentioned to people who already know them"],
    "never_mention": ["retired offers"],
    "pitch_rules": ["Never pitch to camera"]
  },
  "platforms": {"shorts": ["Instagram Reels", "YouTube Shorts"], "scheduler": "what they use, or 'phone'",
                "cadence": "their posting days and times, e.g. 'Tue and Thu 7.40pm, Sun 8am'"},
  "review": {"reads_on": "phone", "plain_text_copy_in_reply": true}
}
```

## Notes

- Colours are always referred to by role. The scripts refuse raw hex codes in styles, so a render
  can't drift off the palette.
- Fill in every colour field in `look.shorts` (hook, captions, sticker) explicitly. Don't rely on
  defaults: what's written is what the owner approved.
- A substitute font carries `"substitute_for": "Original Name"` in its font entry, so it's never
  mistaken for the real thing later.
- `variation` picks a weight from a variable font file ("Bold", "SemiBold").
- `case: upper` sets every hook, caption or label in that font in capitals.
- `y` positions are on a 1080x1920 frame. Captions sit around 1400 to clear the face and the
  platform's buttons. Hooks sit near the top, below the platform's own top bar.
- `brand.py` checks fonts load and contain basic characters, and that text and background pairs
  have a contrast of at least 3:1. Fix anything it flags with the owner. Never swap a colour without asking.
