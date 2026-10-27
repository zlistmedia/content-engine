---
name: brand-setup
description: Set up the content engine for a new owner. Takes their one-page Brand Card (or their style guide), builds their brand profile (voice and look), checks the workspace and renders a 10-second test clip in their brand. Use for "set up my content engine", "here's my brand card", "here's my style guide", "set up my brand", or when the engine runs with no brand profile.
---

# Content Engine: brand setup

Setup turns the owner's one-page Brand Card into a brand profile that every render and every
caption reads from. The engine never picks a colour, a font or a word on its own. On brand, in voice
and in look, is the whole product.

Every owner starts from the Brand Card: one page they fill in before setup, so every profile is
built from the same fields in the same order. Setup then takes about 5 minutes and ends with a
10-second test clip in their brand. They approve the test before any real work starts.

## Talking to the owner

Most owners aren't technical. Keep every message short, one step at a time, and wait for their
reply before the next step. Never show code, file paths or tool names. Use these words:

| Say | Not |
|---|---|
| your brand profile | profile JSON, schema |
| your Content Engine folder | workdir, directory |
| the test clip | test render |
| Claude's workspace | container, sandbox, environment |
| installing the video tools | pip, ffmpeg, dependencies |

They usually read on their phone, so put any copy they need to check in the message as plain text,
as well as in any file.

## The toolkit

The engine scripts live in the `engine` folder at the root of this plugin (`../../engine` from this
file). Run them with `python3 <engine>/<script>.py`. Each script prints its own usage with no arguments.

| Script | Does |
|---|---|
| `setup_check.py` | Reports what's missing in the workspace; `--install` installs it |
| `brand.py <profile>` | Checks a profile: fonts load, colours contrast, no forbidden pairs |
| `look_preview.py` | A still of the Shorts look on their photo, with `--set` to try variations |
| `test_clip.py` | The 10-second brand test clip |

## Step 1: Their Content Engine folder

Everything for the engine lives in one place they can find again:

```
Content Engine/
  Brand/        style guide, font files, logo, brand-profile.json
  Inbox/        raw videos waiting to be made into content
  Ready to Post/
```

Work out where it lives, in this order:
1. **A folder on their computer**, if this chat is linked to it (the desktop app). Ask them to create
   or choose a folder called Content Engine and give access to it.
2. **Google Drive**, if the Drive connector is on. Make the folders there.
3. **Neither:** their home is a **Claude Project called "Content Engine"**, made in Step 7. Its files
   hold the brand profile, so every chat inside it starts with their brand. Videos go in as
   attachments, and finished content comes back as files.

## Step 2: The workspace check

Run `setup_check.py`. If anything is missing, tell them in one message what it is, that it goes in
Claude's workspace and not on their computer, and roughly how big it is (the script prints both).
Ask "OK to install these?" and wait for a yes. Then run `setup_check.py --install`.

## Step 3: Their Brand Card

The Brand Card is required. Ask for it first (where to find it: `references/brand-card.md`).

- **They attach the Brand Card zip** (or paste the text the page copies). It holds
  `Brand/brand-profile.json` in the engine's own format, `Brand/fonts/` and a one-page summary.
  Unzip it into the job folder and use the profile as it is. Then go to Step 5.
- **They haven't filled it in yet:** send them to the Brand Card page (`references/brand-card.md`).
  If they'd rather not use a web page, `references/style-guide-template.md` is the same page as a
  document to fill in and attach. Either way, wait for it. Don't build a profile from a chat
  conversation, invent a brand for them, or lift colours off their website without confirming each one.
- **They also send a full style guide:** use it to check the card (colours, fonts, rules). If the
  two disagree, ask which is right. Never pick one silently.

A card with `"file_missing": true` on a font means they typed the font name but had no file. Sort
that in Step 4. A `"_made_with"` field is just a marker and can stay.

## Step 4: Fill the gaps

Read the card for anything missing or unclear (the page flags most of it, but check), and ask about
only those, in one numbered message, five questions at most. Typical gaps: a font file, their free
thing's link, the days they post, names the captions might get wrong (their name, business, suburb,
products).

Whatever you fill in or check, these are the rules for each field (full field list in
`references/profile-schema.md`). They also cover turning the document version of the card into a
profile.

- **Colours** as hex codes. Map them to four roles: `primary` (the main dark or strong colour),
  `accent` (the highlight), `secondary` (the support colour) and `light` (the pale or neutral
  colour). If a guide gives only swatches, sample the hex from the image. Either way, show them
  `brand.py <profile> --swatches <out.png>` next to their own guide and ask "Do these match?",
  because most owners can't check a hex code by eye. Note any "never use X on Y" rule as `never_pairs`.
- **Fonts:** names and roles (headline, body, label or accent). Fonts get drawn into the video, so
  the engine needs the actual font. **First check the engine's own copies:** run
  `bundled_fonts.py` for the list. Popular free Google Fonts ship with the engine (Poppins, Inter,
  Montserrat, Lato, Open Sans, DM Sans, Raleway, Playfair Display and more), so if theirs is on the
  list, they don't need a file at all: `brand.py` picks it up from the name and says so. Only ask for
  files (.ttf or .otf) for fonts that aren't on the list. If they only know the name:
  - Check Google Fonts first: many Canva fonts are Google Fonts and free to download. Send the link
    to that font's page and tell them to tap "Get font", then "Download all".
  - Bought fonts (Fontshare, Creative Market, a designer): the files are in their download or
    receipt email.
  - Adobe Fonts and Canva's own fonts (like Canva Sans) can't be downloaded as files. Offer the
    closest free match, say plainly that it's a substitute, record it in the profile as
    `"substitute_for": "<original name>"`, and show it in the look preview so they agree to it
    knowing what it is.
- **Logo:** a PNG with a clear background, if they have one. Shorts don't use it. It's kept for
  Levels 2 and 3 (thumbnails and graphics).
- **Voice:** tone, words they use, words they never use, spelling (Australian, US, UK), names and
  brand terms to spell exactly, anything they never say. Their own sample lines from posts or
  emails are gold: ask for three if the guide has none.
- **Rules:** minimum sizes, logo placement, colours that must never touch.

## Step 5: Check the look, by picture

The card already holds their caption style, hook style and music, chosen against a live preview.
Write any changes into the profile, keeping every colour field in `look.shorts` explicit. Run
`brand.py` and sort anything it flags with them, including a font weight that isn't in the file.

Ask for a photo of themselves (a selfie is fine) and render `look_preview.py` with it, so they see
the look drawn by the engine itself in their real font files. If they want to compare, show two
looks side by side using `--set`. For example:
- A: one big word at a time in the headline font, outlined in `primary` (bold, high energy)
- B: two to four words on a `light` card with the key word on `accent` (calm, easy to read)

Vary the hook between band, pill and plain to suit the guide. Ask "A or B? Or tell me what to
change." Apply exactly what they say. Check the preview shows the font weights you set (a bold
headline should look bold). A sticker only goes on if their guide has a playful label style.
Music: bright, calm, upbeat or none, asked in one line.

## Step 6: The test clip

Ask for 10 to 30 seconds of them talking to camera (a phone selfie is fine), then run
`test_clip.py <profile> <out.mp4> <their clip>`. With no clip, it renders on a plain brand
background so they still see the look. Send the clip with three questions:
1. Do the colours and fonts look like your brand?
2. Can you read every caption easily on your phone?
3. Anything to change?

Apply their changes to the profile and re-render. Repeat until they say it's right.

## Step 7: Save and hand over

Save `brand-profile.json` (and any font files and logo) to `Content Engine/Brand/` if they have that
folder. Then set them up so they never repeat this, in this order, one step per message:

1. **Their files.** Send three files:
   - `brand-profile.json`: the profile itself.
   - `My brand.md`: a one-page summary in plain words (who they are, colours with names and hex
     codes, fonts, caption and hook style, voice rules, banned words, offers, posting days). This is
     for them to read, and it also lets Claude read their brand in any chat.
   - Any font files they gave you that aren't bundled (say which, or say none are needed).
2. **Their Project instructions.** Send this as plain text in the message, filled in, ready to copy:

   > This Project is my Content Engine. Every chat here makes content for {{business name}} using
   > the Content Engine plugin. My brand profile and brand summary are in this Project's files. At
   > the start of each chat, rebuild brand-profile.json from the Project file exactly as it is, and
   > never pick a colour, font or word that isn't in it. {{Spelling, e.g. Australian English}}.

3. **Make the Project.** Walk them through it, waiting for a reply after each step:
   - "On claude.ai, open **Projects** in the left menu, then **New project**. Call it Content Engine."
   - "In the Project, find **Instructions**, paste in the text above, and save."
   - "Under **Files**, add `brand-profile.json` and `My brand.md`" (and their font files, if any).
   - "Open a new chat inside the Project and say hi, so we know it's working."
   If they're in the desktop app with a linked Content Engine folder, the Project is optional: say so
   and skip it if they'd rather not.
4. **What's next**, in two lines:

> Your brand's set. Film 5 to 10 minutes talking to camera about one question your clients ask,
> then open a chat in your Content Engine Project, attach it, and say "make my Shorts".

## When they change something later

"Make the captions bigger", "we've changed our yellow", "never say hustle": update the profile,
re-run `brand.py`, show a fresh `look_preview.py` still, and save. Their edits are the profile.
