# Third-party schedulers (Buffer, Later, Metricool, Planoly, Hootsuite, Hopper, SocialBee, Publer)

They all work the same way, with different button names:

1. Connect the accounts once (Instagram, Facebook, TikTok, YouTube). Each tool walks them through it.
2. Create a new post, pick the channels, upload the Short.
3. Paste the caption for each channel. Most tools let them customise per channel: use the matching
   caption file.
4. Choose the date and time from the Posting plan, then schedule.

## Bulk upload

Most of these accept a CSV for bulk scheduling. `schedule.csv` in the folder has date, time,
timezone, platform, file and caption. Every tool wants slightly different column names, so when
they say which tool, reshape the CSV to that tool's template (ask them to download the tool's sample
CSV and attach it) and give them the new file.

## When a connector exists

If Claude has a connector for their scheduler in this session, offer to schedule the posts for them,
then show the full list of posts and times and wait for a clear yes before anything goes in. Most
schedulers need the video uploaded through their own media library first, so check what the
connector can do before promising it.

## Claude in Chrome

If they use Claude in Chrome, offer: "I can open your scheduler and do this with you, you just watch
and approve." Stop before the final Schedule click on each post and ask.
