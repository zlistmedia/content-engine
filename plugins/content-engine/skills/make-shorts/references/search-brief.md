# The search brief: found first, then hooky, then in their voice

Every piece the engine makes has two jobs. The hook stops the scroll. Everything underneath it
(titles, descriptions, captions, chapters, blog headings, pins, hashtags) gets the video found by
people searching for exactly what the owner talked about. The search brief is how the second job
gets done, and it comes first, before any hook is written.

## When

Straight after the transcript, before picking moments, the paper edit or any angle. Write it once
per video to `<job>/search-brief.json`. Every skill in the run reads the same file, and a new chat
reads it back instead of starting again.

## How to build it

Read the whole transcript, then the profile (`business` for what they do and where, `voice` for the
words their clients use). Work out:

1. **The primary phrase.** The exact words a stranger would type into Google or YouTube to find this
   video. Use the customer's words, not the owner's jargon: "is a google business profile free",
   not "GBP optimisation". Questions and "how to" phrases win: they match how people search.
2. **Variants (2 to 4).** Other ways people type the same need: "google business profile cost",
   "free google listing".
3. **Long-tail questions (3 to 6).** Specific questions the video actually answers, in the words
   someone would type: "how do I get more google reviews", "how much does a small business website
   cost". Pull them from what the owner says, and from questions they repeat or answer on camera.
4. **Local.** If they serve a place (`business.location`, `business.service_area`), add the town or
   region. Local searches carry it ("web designer margaret river").
5. **Terms (optional).** Related words customers use, for tags, hashtags and blog body copy.

If the owner has given you their own search data (Search Console queries, the questions clients
ask, a keyword list), use their real phrases first.

Never invent a claim to fit a phrase. The video has to answer what the phrase asks.

## The order of work

1. **Search brief** (this file).
2. **Hooks and overlays.** Punchy, short, scroll-stopping, in their words. They may use the phrase
   when it's naturally hooky ("IS A GOOGLE PROFILE ACTUALLY FREE?") but they don't have to.
3. **The searchable copy**, built from the brief: titles, descriptions, first caption lines,
   chapters, headings, pins, tags.
4. **The voice pass.** Their tone, spelling and banned words go over the top. Rework the words
   around the phrase, never the phrase itself. If the phrase holds a banned word, swap to a variant
   from the brief instead.
5. **Check.** Run `search_check.py <job>/search-brief.json <file>` on every copy file after
   `voice_check.py`. Fix any title, description, first line or heading that lost the phrase.

## Where the phrases go

| Piece | Must carry | Hook can stay free |
|---|---|---|
| YouTube title | Primary phrase first, hook after | |
| YouTube description | Primary phrase in line 1, a long-tail question or two in the body, local word if local | |
| YouTube chapters | At least two named as long-tail questions | |
| YouTube tags | Primary, variants, questions, local, terms | |
| Thumbnail words | | Yes: 2 to 4 punchy words |
| On-screen hook and callouts | | Yes |
| Shorts on YouTube: title | The question someone types, in sentence case | |
| Instagram and TikTok captions | Line 1 says the phrase or a question in plain words (both apps search captions) | The overlay hook |
| Hashtags | Topic and place tags from the brief, never giant generic ones | |
| Blog post | Title and slug with the phrase, the first two sentences answer it, H2s as long-tail questions, FAQs from the questions, a meta description with the phrase | |
| Pins | Title and description with the phrase or a variant, alt text that describes the pin with it | |
| Carousel | Cover slide asks the question; caption line 1 carries the phrase | Inside slides |
| Threads | At least two of the posts ask a long-tail question naturally | The rest |
| Email | The video and blog link; subject can be hooky | Subject line |

## In the check-ins

Show the brief at the first check-in, as three short lines they can correct:

```
Found for: "is a google business profile free"
Also: google business profile cost · free google listing
Questions it answers: how do I set up a google business profile · how do I get more google reviews
```

They know their clients' words better than anyone. Swap in theirs if they correct you.
