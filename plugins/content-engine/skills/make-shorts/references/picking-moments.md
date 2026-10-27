# Picking the moments: three short Reels and a 60-second story

Read the whole transcript first. The filmed order is not the order it has to go in, and the best
Short is often halfway through.

## What makes a good Short

- **One point, complete on its own.** Someone who never sees the long video still gets it.
- **Opens strong.** The first line is a claim, a question, a number or a surprise, never "so" or
  "and" or a warm-up. If the strong line comes a sentence in, start there.
- **Lived experience, then the lesson.** A real moment from their business beats a tip with no story.
- **Ends on a full stop.** The last sentence lands a point, not "anyway" or a trailing "so yeah".
- **20 to 45 seconds for the short ones.** Under 20 rarely makes a full point, so extend the run to
  finish the thought rather than shipping a 10-second clip. Over 45 loses people.
- **Three different angles.** Not three versions of the same point: for example the problem, the
  shift, the first step.

## The 60-second story

After the three short ones, build one longer Reel: the story cut. It tells the whole idea of the
video in about a minute, for people who will never watch the long version.

- **50 to 70 seconds.** Built from two to four runs anywhere in the video, in the order that makes
  the best story, not the filmed order.
- **Hook, point, payoff.** Open on the sharpest question or claim, give the one idea and the reason
  for it (a real moment or number if they said one), and end on what to do or think next.
- **It can reuse a line from a short Reel**, but it must not be a short Reel stretched longer.
- In `shorts-plan.json` give it the id `story` so the checks treat it as the long one.
- Under about three minutes of talking, or only one real point in the video: skip the story cut and
  say why. Never pad it to reach a minute.

## Not enough for three

Under about three minutes of talking, or fewer than three points that stand on their own: offer two
Shorts, or one, and say why ("there's one really strong moment here, a second would repeat it").
Never pad a Short to reach a number.

## Cutting rules

- Cut only at sentence boundaries. Never start on "and", "but" or "so" unless it reads naturally.
- Skip every retake (`retakes.txt` lists lines said twice: keep the better take, usually the last).
- A run can join two non-adjacent sentences if they make one thought. Keep it to two or three runs.
- Never cut the owner's name line if it's in the moment.
- Keep their ad-libs and personality. Tidy, not sterile.

## Hooks

The hook is pinned at the top for the whole Short. It's two or three short lines from their own
words in that moment, or the question it answers, never a new claim they didn't make.

- Under 8 words a line, ideally 3 to 5.
- Their spelling and their voice. Check against `banned_words`.
- The searched question works well ("DO I NEED A WEBSITE?"), as does the sharpest line said ("NOT
  ONE CLIENT FROM A POST.").

## Word ranges

`transcript.txt` shows each sentence as `[first-last] m:ss  text`. A run is `[first, last]` word
numbers. To start mid-sentence or end early, count words within the line. The renderer adds a
breath before the first word and after the last, so don't pad the range.
