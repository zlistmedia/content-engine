# Captions for each platform

Only for the platforms in `platforms.shorts`. Every word in the owner's voice: read
`voice.summary`, `voice.rules` and `voice.sample_lines` first, and match them. Check every caption
against `voice.banned_words` before showing it. Use their spelling (`business.spelling`).

## The shape (all platforms)

- **Line 1 picks up the hook**, it doesn't repeat it. It's what shows before "more", and it's
  what Instagram and TikTok search reads first, so it says the search phrase or one of the
  long-tail questions from `search-brief.json` in plain words. The hook on screen stays punchy;
  the caption is where they get found.
- **One idea, then one next step.** Their chosen next step (`offers.cta`: a free download, starter
  offer, call, website or simply "follow") is where people who don't know them yet go. Never warm-only offers. Never retired offers (`never_mention`).
- **No urgency or scarcity** unless their voice rules say otherwise.
- Write like they'd text a client, not like an ad.

## Instagram Reels

- 1 to 4 short lines, a line break between thoughts.
- Next step: "Link in bio for <their next step>" or a keyword to comment, if they run comment automations.
  If `offers.cta.type` is "follow", end with a reason to follow instead of a link.
- 3 to 5 hashtags at the end, from the brief's phrase, terms and place (for example #smallbusinessperth).
  No banned or giant generic tags.

## YouTube Shorts

- **Title:** under 70 characters, the primary phrase or a long-tail question from the brief, in
  sentence case. Searchable beats clever.
- **Description:** two lines on what it answers, then their next step with its full link (skip it if they chose "follow"), then
  "Full video: <link>" if there's a long version. Add #Shorts and two topic hashtags.
- Remind them once: links in Shorts descriptions don't click from the feed. A pinned comment helps.

## TikTok

- One or two lines, more casual than Instagram. Lead with the long-tail question from the brief:
  TikTok is a search engine for a lot of people.
- 3 to 5 hashtags. No links (they don't click). "Link in my profile" if needed.

## Facebook Reels

- Same as Instagram, minus most hashtags (one or two at most).

## Format for The Words check-in

```
SHORT 1
1a. Instagram:
<caption>

1b. YouTube title: <title>
1c. YouTube description:
<description>

1d. TikTok:
<caption>
```

So they can reply "1c: drop the second line".
