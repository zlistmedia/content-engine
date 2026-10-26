# Getting the video to Claude

Raw videos are big (0.5 to 3 GB). A chat upload tops out far below that, so most owners need one of
the routes below. This is the step non-technical owners find hardest: go slowly, one step per
message, and tell them exactly what to tap.

## Route 1: Google Drive link (works for everyone)

What to tell them:

1. "Put the video in your Content Engine > Inbox folder in Google Drive." (On a phone: open the
   Drive app, tap +, Upload, choose the video. Big files take a while on mobile data: wifi is best.)
2. "Tap the three dots next to the video, then Share, then General access, and change Restricted to
   Anyone with the link. Tap Copy link and paste it here. This lets me download it. Only someone
   with the exact link can open it, and you'll switch it back in a minute."
3. Once you've downloaded it: "Got it. You can set it back to Restricted now."

How to download it in the workspace: take the file ID from the link (`/d/<ID>/`), then
`curl -L -o raw.mp4 "https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t"`.
Check the size matches what Drive shows. If the download comes back as a small HTML page, the
link isn't public yet: ask them to check step 2.

If the Drive connector is on, find the file there first to get its ID and exact size.

## Route 2: their computer (desktop app, chat linked to the computer)

Ask for access to the folder with the video (usually Videos or Downloads, or their Content Engine
Inbox), then copy just that file into the workspace. Files over a few hundred MB may need Route 1.

## Route 3: straight into the chat

Fine for short clips under about 30 MB (a 20-second phone clip). Not for full videos.

## Filming tips to give them once (first run only, if they ask how to film)

- Phone at eye level, landscape for YouTube or vertical if it's only for Shorts, face roughly in
  the middle third of the frame.
- Light in front of them (a window), not behind.
- A clip-on mic or AirPods beats the phone's own mic.
- Start with the question their clients ask, then answer it like they're talking to one person.
  Ad-libs and personality are good. Retakes are fine: the engine finds and skips them.
- 5 to 10 minutes is plenty for three strong Shorts.
- HDR off if the phone has the option (iPhone: Settings > Camera > Formats > Most Compatible, and
  turn off HDR Video). The engine fixes HDR anyway, it just saves time.
