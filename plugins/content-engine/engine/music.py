"""Make a royalty-free music bed in code, so there are no licensing questions.

  python music.py <out.wav> [--mood bright|calm|upbeat] [--bpm 108] [--seconds 60]

bright: major keys, light beat, soft arpeggio (warm, never ominous)
calm:   slow open chords, no claps, gentle pulse
upbeat: brighter drums, busier arpeggio
"""
import sys
import numpy as np
import scipy.io.wavfile as wf

SR = 48000
MOODS = {
    "bright": {"prog": [[60, 64, 67, 72], [55, 62, 67, 71], [57, 60, 64, 69], [53, 60, 65, 69]], "bass": [36, 43, 45, 41],
               "kick": 0.5, "clap": 0.12, "hat": 0.05, "arp_from": 2, "arp": 0.05, "chord": 0.09},
    "calm":   {"prog": [[53, 57, 60, 64], [52, 55, 60, 67], [50, 53, 57, 60], [46, 53, 57, 62]], "bass": [41, 40, 38, 34],
               "kick": 0.22, "clap": 0.0, "hat": 0.018, "arp_from": 1, "arp": 0.035, "chord": 0.1},
    "upbeat": {"prog": [[62, 66, 69, 74], [57, 64, 69, 73], [59, 62, 66, 71], [55, 62, 67, 71]], "bass": [38, 45, 47, 43],
               "kick": 0.6, "clap": 0.16, "hat": 0.07, "arp_from": 1, "arp": 0.06, "chord": 0.08},
}


def make(out, mood="bright", bpm=108, seconds=60, seed=3):
    M = MOODS.get(mood, MOODS["bright"])
    beat = 60 / bpm
    bars = int(np.ceil(seconds / (4 * beat))) + 1
    n_total = int(SR * bars * 4 * beat)
    L = np.zeros(n_total); R = np.zeros(n_total)
    rng = np.random.default_rng(seed)

    def hz(m): return 440 * 2 ** ((m - 69) / 12)

    def note(f, start, length, amp, kind="ep", pan=0.0):
        n = int(length * SR); t = np.arange(n) / SR
        if kind == "ep":
            s = np.sin(2*np.pi*f*t) + 0.35*np.sin(2*np.pi*2*f*t)*np.exp(-t*6) + 0.12*np.sin(2*np.pi*3*f*t)*np.exp(-t*9)
            env = np.exp(-t*2.2) * (1 - np.exp(-t*200))
        elif kind == "pluck":
            s = np.sin(2*np.pi*f*t) + 0.5*np.sin(2*np.pi*2*f*t) + 0.2*np.sin(2*np.pi*4*f*t)
            env = np.exp(-t*9) * (1 - np.exp(-t*400))
        else:
            s = np.sin(2*np.pi*f*t) + 0.25*np.sin(2*np.pi*2*f*t)
            env = np.minimum(1, t*80) * np.exp(-t*1.6)
        x = s * env * amp; i = int(start*SR); j = min(n_total, i+n); x = x[:j-i]
        L[i:j] += x*(1-pan)*0.707; R[i:j] += x*(1+pan)*0.707

    def drum(start, kind, amp):
        if amp <= 0: return
        if kind == "kick":
            n = int(0.35*SR); t = np.arange(n)/SR; f = 55+70*np.exp(-t*30); s = np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*9)
        elif kind == "clap":
            n = int(0.18*SR); t = np.arange(n)/SR; s = rng.standard_normal(n)*np.exp(-t*28); s = np.convolve(s, np.ones(6)/6, "same")
        else:
            n = int(0.05*SR); t = np.arange(n)/SR; s = np.diff(np.r_[0, rng.standard_normal(n)])*np.exp(-t*90)
        i = int(start*SR); j = min(n_total, i+n); x = s[:j-i]*amp; L[i:j] += x; R[i:j] += x

    for b in range(bars):
        ch = M["prog"][b % 4]; t0 = b*4*beat
        for k, m in enumerate(ch): note(hz(m), t0, 4*beat, M["chord"], "ep", pan=(k-1.5)*0.2)
        note(hz(M["bass"][b % 4]), t0, 2*beat, 0.22, "bass"); note(hz(M["bass"][b % 4]), t0+2.5*beat, 1.5*beat, 0.16, "bass")
        if b >= M["arp_from"]:
            arp = [ch[0]+12, ch[2]+12, ch[1]+12, ch[3]+12]
            for s8 in range(8): note(hz(arp[s8 % 4]), t0+s8*beat/2, beat/2, M["arp"], "pluck", pan=0.4 if s8 % 2 else -0.4)
        if b >= 1:
            for q in range(4):
                if q in (0, 2): drum(t0+q*beat, "kick", M["kick"])
                if q in (1, 3): drum(t0+q*beat, "clap", M["clap"])
            for s8 in range(8): drum(t0+s8*beat/2+(0.012 if s8 % 2 else 0), "hat", M["hat"] if s8 % 2 else M["hat"]*0.6)
    mix = np.stack([L, R], 1); mix = np.tanh(mix*1.2); mix /= np.abs(mix).max()/0.8
    fade = int(1.5*SR); mix[:fade] *= np.linspace(0, 1, fade)[:, None]
    mix = mix[:int(seconds*SR)]
    wf.write(out, SR, (mix*32767).astype(np.int16))
    return out


if __name__ == "__main__":
    a = sys.argv
    if len(a) < 2:
        print(__doc__); sys.exit(1)
    g = lambda k, d: type(d)(a[a.index(k)+1]) if k in a else d
    make(a[1], g("--mood", "bright"), g("--bpm", 108), g("--seconds", 60))
    print("Music bed written:", a[1])
