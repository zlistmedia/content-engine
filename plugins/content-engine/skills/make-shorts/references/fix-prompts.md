# When something looks wrong

Look before guessing. Try one fix, check it, and if it doesn't work, tell the owner plainly what
happened and what you'll try next. The owner can paste any of the quoted lines to ask for the fix.

| They say | Likely cause | Fix |
|---|---|---|
| "The colours look washed out / orange" | HDR footage that wasn't converted, or the original was converted twice | `footage.py check`: if it says HDR, re-run `prep` on the original (not the working copy). Compare a frame from the original and the Short side by side. |
| "Captions are out of sync" | A variable frame rate source, or timings taken from the original instead of the working copy | Re-transcribe `work/audio16k.wav` from the working copy and re-render. Check the source with `footage.py check` (dropped frames). |
| "A word is cut off" | The run ends inside the next word, or a silence cut clipped it | Extend the run by one word, re-render that Short only, run `verify.py`. |
| "It starts mid-word" | Run starts too late | Start the run one word earlier. |
| "I'm not in the frame" | Face-finding missed, or they moved | Check the contact sheet. Set `crop_x` for that Short in the plan (left edge of the crop, in source pixels), re-render. |
| "There are two of us on camera" | Face-finding takes the biggest face, so the crop can land on the guest or between you | Ask who the Short is about. Set `crop_x` on their side, or pick moments where the crop can stay on one person. Skip a moment that needs both. |
| "The file is too big to upload" | Over the 30 MB chat limit | `verify.py` already shrinks Shorts over 30 MB. For other files, split or use Drive. |
| "The music is too loud / I don't want music" | Profile music level | Change `look.shorts.music.level` (0.12 is soft) or set `mode` to `none`, save the profile, re-render. |
| "That's not my font" | Wrong font file, or a variable font on the wrong weight | Check `fonts` in the profile, set `variation` ("Bold"), run `look_preview.py`. |
| "The caption spelled my name wrong" | Whisper | Add it to `voice.spelling_fixes` in the profile (so it's right forever), fix `words.json`, re-render. |
| "It's taking ages" | Long render | Say where it's up to. A Short takes about 2 minutes, transcription about a third of the video's length. Converting phone HDR footage takes about as long as the video. |
| "The download link didn't work" | Drive file still Restricted | Walk them back through the share step in `getting-footage.md`. |
