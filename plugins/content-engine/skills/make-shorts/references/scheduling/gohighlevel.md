# GoHighLevel (and white-label versions such as Tekmatix)

GoHighLevel's Social Planner schedules to Instagram, Facebook, TikTok, YouTube, LinkedIn,
Pinterest and Google Business Profile from one place.

## By hand

1. Marketing > Social Planner. Connect accounts under Settings the first time.
2. Media Storage: create a folder (for example "Shorts") and upload the files from the Ready to Post folder.
3. Social Planner > New Post. Pick the accounts.
4. Add media from Media Storage. For video, wait until it shows as processed.
5. Paste the caption. For YouTube, fill the title field too and choose Short.
6. Schedule: pick the date and time, then Schedule.

## With the HighLevel connector (if Claude has it in this session)

Uploading media through the API isn't possible, so the owner uploads the files to Media Storage
first (steps 2). Then Claude can create the scheduled posts:

- Find the media URLs in that folder and check each file's size matches the local file (catches a stale upload).
- Videos must show as encoded before posting.
- Create one post per platform with the caption and time from the manifest.
- Show the full list and wait for a yes before creating them. Then list the scheduled posts back to confirm.

Every write call needs the account's user ID and an idempotency key. Times are in UTC: convert from
their time zone.
