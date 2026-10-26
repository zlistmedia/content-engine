# Content Engine · Level 1: Shorts

One video of you talking to camera goes in. Three Shorts come out, captioned in your fonts, your
colours and your words, with a caption written for each platform and a folder that tells you what
to post where and when.

Made by Zoë Condon, Z List Media.

## What you need

- A paid Claude plan that can run code and create files (the editing happens in Claude's own
  workspace, so nothing gets installed on your computer)
- Your **Brand Card**: one page you fill in online in about 10 minutes, with your colours, fonts,
  caption look and voice. It shows you a live preview of your Shorts as you go, then saves as one
  file for Claude. Have your colour codes and font files (.ttf or .otf) handy.
- A video of you talking to camera: 5 to 10 minutes, face roughly in the middle, one speaker.
- Google Drive (or the Claude desktop app linked to your computer) to get big videos to Claude.

## Getting started

1. Add the plugin to Claude.
2. Fill in your Brand Card and save it. Start a new chat, say **"set up my content engine"** and
   attach it.
   (No Google Drive or linked computer? Attach your brand profile and font files at the start of
   each new chat, as Claude starts fresh each time.)
   Claude checks your card, asks about anything missing, shows your look on a photo of you, then
   makes a 10-second test clip in your brand. About 5 minutes, once.
3. Film. Put the video in your Content Engine > Inbox folder in Google Drive.
4. Say **"make my Shorts"**. Claude checks in with you four times along the way:
   - **The Plan:** the three moments and hooks
   - **The Cut:** the three Shorts to watch on your phone
   - **The Words:** the captions for each platform
   - **Go Live:** what's going where and when
5. Post from your Ready to Post folder. The first time, Claude walks you through scheduling in
   whatever you use (the Instagram app, Meta Business Suite, YouTube Studio, TikTok, Buffer, Later,
   GoHighLevel and more).

## Good to know

- **Nothing goes off brand.** Every colour, font and word on screen comes from your Brand Card.
  Anything it doesn't cover (a stand-in font, say) you see and approve before it's used.
- **Your originals are never touched.** Claude works on a copy.
- **Each Short takes about 2 minutes to make.** Claude tells you where it's up to.
- **You approve every step.** Nothing is posted or scheduled without your yes.
- **The music is made in code**, so there are no licensing worries. You can turn it off.

## What's inside

| Part | What it does |
|---|---|
| `skills/brand-setup` | Turns your Brand Card into your brand profile, ends with the test clip |
| `skills/make-shorts` | The Shorts workflow, the four check-ins, captions, Ready to Post, scheduling help |
| `engine/` | The editing toolkit Claude runs: footage check, transcription, face-aware vertical crop, Shorts render, checks, Ready to Post folder |
| `examples/sample-brand` | A made-up brand profile showing every setting |

## Credits and licences

- Speech-to-text: faster-whisper (MIT), Whisper model by OpenAI (MIT)
- Face finding: YuNet model from OpenCV Zoo (MIT); Haar cascade from OpenCV (Intel licence, BSD-style)
- Voice clean-up: ffmpeg's built-in noise reduction
- Example fonts in `examples/sample-brand/fonts`: DM Serif Display and Inter, both SIL Open Font
  Licence (licence files included)

Level 2 (YouTube: the edited long video, thumbnails and upload copy) and Level 3 (the full week:
blog, email, pins, Threads and carousel) build on the same brand profile.
