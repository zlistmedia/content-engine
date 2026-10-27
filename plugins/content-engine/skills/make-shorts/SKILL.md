---
name: make-shorts
description: Level 1 of the content engine. Turns one raw talking-to-camera video into three short captioned vertical Reels plus a 60-second story cut in the owner's brand, with captions for each platform and a Ready to Post folder. Use for "make my Shorts", "make Reels from this video", "run the engine", "edit this video", or any raw video dropped in for content.
---

# Content Engine, Level 1: Shorts

One raw video in. Three short Reels and a 60-second story out, in their brand, in their voice, ready to post. Nothing past a
check-in gets built until the owner says yes, so every change is cheap.

```
Raw video
  1. Get the video in, check it, make a clean working copy
  2. Transcribe with word timings
  3. Pick three short moments and a 60-second story, write the hooks
     ── CHECK-IN 1 · THE PLAN ──
  4. Render the four Reels, check them
     ── CHECK-IN 2 · THE CUT ──
  5. Write the captions for each platform
     ── CHECK-IN 3 · THE WORDS ──
  6. Propose dates and times
     ── CHECK-IN 4 · GO LIVE ──
  7. Build the Ready to Post folder
  8. Help them schedule (first time: set it up with them)
```

Set up a task list with these steps and check-ins so they can see progress if they step away.

## Step 0, every chat: workspace and brand

Each new chat starts with an empty workspace, so do this every time, before anything else:

1. Run `setup_check.py`. If anything's missing, ask before installing (see `brand-setup` Step 2).
2. Find their whole `Brand` folder: in their Content Engine folder (linked computer or Drive), or
   in the chat's attachments. Copy all of it into the job folder in Claude's workspace, keeping
   its subfolders: `brand-profile.json`, `fonts/` and the logo. Font paths in the profile are
   relative to it, so the profile alone won't render. No folder, but the chat is in their
   Content Engine Project? Their brand profile is in the Project's files: write it out as
   `brand-profile.json` in the job folder, exactly as it is. Fonts named in it that the engine
   bundles need no file. For any other font, ask them to attach the file, or to add it to the
   Project's files. Neither? Ask them to attach their brand profile and font files.
3. Run `brand.py <profile>` and sort anything it flags with them.

No profile means no brand: stop and run the `brand-setup` skill first (it starts with their Brand
Card). Never render with made-up
colours or fonts.

All job paths (`work/`, `out/`, the plan, the manifest) are in Claude's workspace. Only the finished
files go back to their Content Engine folder.

Read the profile's voice section before writing a single word. Every hook and caption uses their
voice rules, their spelling and their sample lines as the model, and none of their banned words.

## Talking to the owner

Short messages, one ask at a time, numbered options they can answer by number. No code, paths or
tool names (see the word list in the `brand-setup` skill). They read on their phone: put copy in
the message as plain text as well as in files. When they give notes, change exactly what they say,
in their words, and resend only what changed. Don't defend a choice.

Renders take a while. Before one starts, say how long ("about 2 minutes a Short"), then give a short
progress line as each one finishes, so it never looks stuck.

## The toolkit

Scripts are in the `engine` folder at the plugin root (`../../engine` from this file). Run each with
`python3 <engine>/<script>.py`. Each prints its usage with no arguments. If `setup_check.py` reports
anything missing, ask before installing (see Step 0).

| Script | Does |
|---|---|
| `footage.py check / prep` | Checks the video, makes `work/master.mp4` and `work/audio16k.wav` |
| `transcribe.py` | `words.json`, numbered `transcript.txt`, `retakes.txt` |
| `face.py` | Finds the face for the vertical crop (`shorts.py` calls it itself) |
| `shorts.py <plan>` | Renders the Shorts from `shorts-plan.json` |
| `verify.py <short> --brand <profile>` | Checks words, last word, length, size; makes a contact sheet |
| `voice_check.py <profile> <manifest or plan>` | Banned words and checkable voice rules in hooks and captions |
| `ready_to_post.py <manifest>` | The Ready to Post folder, posting plan page and zip |

Keep each job in its own folder: `Content Engine/Jobs/<date> <short name>/` with `work/` and
`out/` inside. Never change or move their original video.

## 1. Get the video in

See `references/getting-footage.md` for every route (Drive link, linked computer, chat upload) and
how to explain each one to a non-technical owner. Then:

- `footage.py check <video>` and tell them anything it flags in plain words.
- `footage.py prep <video> <job>/work` makes the working copy. Clean footage is used as it is (seconds).
  Phone HDR, rotated or uneven footage gets converted, which takes about as long as the video runs.

## 2. Transcribe

`transcribe.py <job>/work/audio16k.wav <job>/work --fixes <profile>` (about a third of the video's
length). `--fixes` applies their spelling fixes and switches US spelling to theirs, so captions
come out right. Read all of `transcript.txt` and `retakes.txt` before picking anything. If a name
or term is still wrong, add it to the profile's `spelling_fixes` (one word or a phrase like
"chat gbt": "ChatGPT") so it's right forever, then run `voice_check.py <profile> transcript.txt`.

## 3. Pick three moments and the story cut

Full method in `references/picking-moments.md`. In short: three Reels of 20 to 45 seconds plus one 50 to 70 second story cut (id `story`). Each short one makes a
single point that works with no other context, opens strong, ends on a full stop. Skip retakes.
Cut only at sentence boundaries.

Write `shorts-plan.json` (format in the `shorts.py` docstring): word ranges from `transcript.txt`,
a hook of their own words for each (two or three short lines), and a sticker word only if the
profile has stickers on. Run `voice_check.py` on the plan so no hook breaks their rules.

### Check-in 1: The Plan

One short message, laid out for a phone:

```
Here's the plan for your four Reels.

1. "<hook line>"  (0:42, starts: "<first words>...")
2. "<hook line>"  (0:31, starts: "...")
3. "<hook line>"  (0:28, starts: "...")
4. Story, 60 sec: "<hook line>"  (1:02, built from 3 moments)

Reply OK to render, or tell me what to change (by number).
```

Wait for a yes. "OK", "yes", "go" or "do it" counts. The same rule holds at every check-in: a clear
yes to that check-in, in this chat. Silence, a thumbs up to something else, or a yes to an earlier
check-in never counts.

## 4. Render and check

`shorts.py <job>/shorts-plan.json`. Then `verify.py` on each Short. Fix anything it reports before
the owner sees it:
- Words missing: a cut landed inside a word. Extend that run by one word or adjust the range.
- Last word clipped: extend the final run.
- No face found, or the wrong person: look at the contact sheet. Set `crop_x` for that Short in
  the plan (the left edge of the vertical crop, in source pixels; the docstring has an example), or
  ask them which side of the frame they sat on.

Look at every contact sheet yourself: hook readable, captions on brand and clear of the face, no
text off the edge, colours right. Render Short 1 first if it's their first run, so they can steer
the look before you render the rest.

### Check-in 2: The Cut

Send each Short (files under 30 MB go straight into the chat), plus the phone checklist from
`references/phone-checklist.md` and the notes card from `references/giving-notes.md` the first
time. Change exactly what they flag, re-render only those, resend only those.

## 5. Captions for each platform

Write per `references/platform-captions.md`, in their voice: Instagram, YouTube (title and
description), TikTok and Facebook, only for the platforms in their profile. Their free thing goes
in Instagram and YouTube. Warm-only offers never go in. Write the captions into the manifest, run
`voice_check.py`, and fix everything it finds before showing them. Then read each caption against
the rest of their voice rules yourself: the script only checks what a script can.

### Check-in 3: The Words

Captions as plain text in the message, numbered by Short and platform so they can edit by number.

## 6. Dates and times

Use their usual posting days and times if the profile has them (`platforms.cadence`). Otherwise
suggest the rhythm in `references/scheduling/README.md` and ask once: "Which days and times suit
you? Or I'll use these." Save what they say to the profile.

### Check-in 4: Go Live

One message: each Short, which platforms, which day and time. Wait for a clear yes. A yes to an
earlier check-in doesn't count for this one, and nothing gets scheduled or posted on their behalf
without it.

## 7. Ready to Post

Write the manifest (format in the `ready_to_post.py` docstring) with the approved times and
captions. Run `ready_to_post.py`. It builds this week into its own dated subfolder of Ready to Post,
so earlier weeks stay put. Deliver:
- the folder to their Content Engine folder if it's linked or on Drive
- the zip in the chat only when the script says it's under 25 MB. Otherwise send the Posting plan
  and each Short on its own (each is well under the chat limit)
- the Posting plan page: open `Posting plan.html` on any device to see every post, time and
  caption, with Copy buttons

## 8. Scheduling

Read `platforms.scheduler` in the profile first. Only if it's empty, ask where they schedule (see
`references/scheduling/README.md`) and save the answer. The first time, walk them through it one
step at a time using the matching guide. After that, point to the Posting plan and offer help with
any snags.

## Saving progress, and picking up in a new chat

Claude's workspace is wiped when a chat ends, and long jobs sometimes run past one chat. So at every
check-in, save the job's state where the next chat can find it:

- With a Content Engine folder (Drive or linked computer): copy `shorts-plan.json`, `work/words.json`,
  `work/transcript.txt`, the manifest or approved captions so far, and a `job-state.json` into
  `Content Engine/Jobs/<date> <short name>/`. `job-state.json` is one small file: the video's name and
  where it lives, which check-ins are approved, and what's next, e.g.
  `{"video": "Inbox/video-03.mp4", "approved": ["plan", "cut"], "next": "the words"}`.
- Chat only: after each approval, send one file, `Pick up <short name>.zip` (those same files), and say:
  "If this chat ends, start a new one, say pick up my Shorts, and attach this file and your video."

When a chat opens with "pick up my Shorts", "carry on" or that file: do Step 0, unpack the job into
the workspace, re-make the working copy (`footage.py prep`, fast for clean footage), and skip the
transcription because `words.json` is already there. Then tell them in one line where it's up to and
carry on from the next check-in. Never redo an approved step without asking.

## When something goes wrong

`references/fix-prompts.md` has the common problems (orange or washed-out colour, captions out of
sync, file too big, wrong person in the crop) with the cause and the fix. Look before guessing, try
one fix, and if it doesn't work, tell them plainly what happened and what you'll try next.

## Level 2 and 3

At the end of their first run, one line, once: Level 2 adds the edited YouTube video, thumbnails
and upload copy from the same footage, and Level 3 adds the blog post, email, pins, Threads and
carousel. Don't push it again in the same chat.
