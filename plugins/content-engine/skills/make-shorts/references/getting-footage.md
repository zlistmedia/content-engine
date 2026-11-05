# Getting the video to Claude

Raw phone videos are big. Phones film in 4K by default, so even 3 to 5 minutes is 0.6 to 1.5 GB.
Claude takes up to 500 MB per file attached to a chat, and only 30 MB per file in a Project's Files.
This is the step non-technical owners find hardest: go slowly, one step per message, tell them
exactly what to tap, and never ask them to film again.

Pick the route in this order.

## Route 1: a folder on their computer (recommended)

For anyone using the Claude desktop app. No uploading and no size limit.

1. "Put the video in your Content Engine > Inbox folder on your computer." (If it's on their phone:
   AirDrop, or plug the phone in, or upload it to Google Drive or iCloud on the phone and download
   it on the computer.)
2. If this chat can't see the folder yet: "In the Claude desktop app, add your Content Engine folder
   to this chat with the folder button." Wait for it.
3. Read the video straight from the folder. If the folder is mounted in the workspace, use the file
   where it is. If it has to be copied across and is over about 400 MB, make a 1080p copy on their
   computer first when a shell there has ffmpeg
   (`ffmpeg -i in.mov -vf scale=-2:1080 -c:v libx264 -crf 20 -preset veryfast -c:a aac -b:a 160k inbox_1080.mp4`,
   or `scale=1080:-2` for vertical), then copy that. Otherwise go to Route 2's "smaller copy" steps.

## Route 2: attach it to the chat

Fine up to 500 MB per file: about 4 minutes of 1080p, but rarely a 4K video.

- It goes into a **new chat** (inside their Content Engine Project if they have one) with the
  paperclip, never into the Project's Files section, which takes only 30 MB.
- **Too big to attach?** Don't ask them to film again. Ask them to save a smaller copy at 1080p:
  - Mac: open it in QuickTime Player, File > Export As > 1080p.
  - Windows: open it in Clipchamp (built in), Export > 1080p.
  - Phone only: a free video compressor app, set to 1080p.
  Nothing is lost: the engine makes everything at 1080p anyway.
- Still too big after that (a long recording): send just the audio (Voice Memos or any audio export)
  plus a photo of them, and the engine works from those.

## Route 3: a Google Drive link (only if their Claude can reach Google's download address)

Claude's default network settings don't include Google's download address, so don't lead with this.
Use it when they offer a Drive link, or they've told you their Claude allows all domains.

1. "Share the video file itself (not the folder): Share, then General access, Anyone with the link.
   Copy the link and paste it here. You can switch it back once I have it."
2. Take the file ID from the link (`/d/<ID>/`), then
   `curl -L -o raw.mp4 "https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t"`.
   Check the size matches what Drive shows. A small HTML page back means the link isn't public yet.
3. If it fails with a network error or a 403, don't send them into settings. Say: "Claude can't
   download from Drive on your settings. Easiest is to download it to your computer and use your
   Content Engine folder instead," and switch to Route 1 (or Route 2).
4. Once you have it: "Got it. You can set it back to Restricted now."

## Filming tips to give them once (first run only, or if they ask how to film)

- **Camera at 1080p, 30 fps.** iPhone: Settings > Camera > Record Video > 1080p HD at 30 fps.
  Android: the camera app's video settings, FHD or 1080p at 30. Files stay small enough to attach,
  and nothing is lost.
- HDR off if the phone has the option (iPhone: Settings > Camera > Formats > Most Compatible, and
  turn off HDR Video). The engine fixes HDR anyway, it just saves time.
- Phone at eye level, landscape for YouTube or vertical if it's only for Shorts, face roughly in
  the middle third of the frame.
- Light in front of them (a window), not behind.
- A clip-on mic or AirPods beats the phone's own mic.
- Start with the question their clients ask, then answer it like they're talking to one person.
  Ad-libs and personality are good. Retakes are fine: the engine finds and skips them.
- 5 to 10 minutes is plenty for three strong Shorts.
