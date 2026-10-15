#!/usr/bin/env python3
"""Original, royalty-free background music, synthesised from code.

Every sound is generated here (no samples, no third-party loops), so the
output belongs to whoever runs it and can be published anywhere.

Style: bright, upbeat "tech explainer" pop: four-on-the-floor kick, claps,
hats, pumping bass, plucked chords (I-V-vi-IV), soft pad and a bell hook.

  python3 music_gen.py promo  out.wav --seconds 48
  python3 music_gen.py bed    out.wav --seconds 240     # calmer, for tutorials

Same arguments + seed -> identical file. Needs numpy; ffmpeg for loudness.
"""
import argparse
import subprocess
import sys

import numpy as np

SR = 48000


def fftconv(x, k, centred=False):
    n = len(x) + len(k) - 1
    m = 1 << (n - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(k, m), m)
    o = (len(k) - 1) // 2 if centred else 0      # centred: zero-delay for symmetric FIR kernels
    return y[o:o + len(x)]


def lowpass_kernel(fc, taps=511):
    t = np.arange(taps) - (taps - 1) / 2
    h = np.sinc(2 * fc / SR * t) * np.blackman(taps)
    return h / h.sum()


def highpass(x, fc):
    return x - fftconv(x, lowpass_kernel(fc), centred=True)


def lowpass(x, fc):
    return fftconv(x, lowpass_kernel(fc), centred=True)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def env(n, a=0.005, d=0.3):
    t = np.arange(n) / SR
    e = np.exp(-t / d)
    na = max(1, int(a * SR))
    e[:na] *= np.linspace(0, 1, na)
    return e


def osc(freq, n, shape="saw", harm=12, detune=0.0, phase=0.0):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f in (freq * (1 - detune), freq * (1 + detune)) if detune else (freq,):
        if shape == "sine":
            out += np.sin(2 * np.pi * f * t + phase)
        else:
            for k in range(1, harm + 1):
                if f * k > SR / 2.2:
                    break
                amp = 1 / k if shape == "saw" else (1 / k if k % 2 else 0)
                out += amp * np.sin(2 * np.pi * f * k * t + phase * k)
    return out / (2 if detune else 1)


class Song:
    def __init__(self, seconds, bpm, seed):
        self.bpm, self.beat = bpm, 60 / bpm
        self.n = int((seconds + 3) * SR)
        self.rng = np.random.default_rng(seed)
        self.bus = {k: np.zeros(self.n) for k in ("kick", "drums", "bass", "keys", "pad", "lead", "fx")}

    def put(self, bus, start_s, sig, gain=1.0):
        i = int(start_s * SR)
        if i >= self.n:
            return
        j = min(self.n, i + len(sig))
        self.bus[bus][i:j] += gain * sig[: j - i]

    # ---- instruments -------------------------------------------------------
    def kick(self, t, g=1.0):
        n = int(0.42 * SR)
        tt = np.arange(n) / SR
        f = 45 + 95 * np.exp(-tt / 0.035)
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.16)
        click = self.rng.standard_normal(n) * env(n, 0.0005, 0.004) * 0.25
        self.put("kick", t, s + click, g)

    def clap(self, t, g=0.5):
        n = int(0.25 * SR)
        noise = highpass(self.rng.standard_normal(n), 900)
        e = np.zeros(n)
        for off in (0, 0.011, 0.022):
            k = int(off * SR)
            e[k:] += env(n - k, 0.0005, 0.012 if off < 0.02 else 0.08)
        self.put("drums", t, noise * e, g)

    def hat(self, t, g=0.12, open_=False):
        n = int((0.18 if open_ else 0.05) * SR)
        s = highpass(self.rng.standard_normal(n), 7000) * env(n, 0.0005, 0.06 if open_ else 0.015)
        self.put("drums", t, s, g)

    def bass(self, t, note, dur, g=0.32):
        n = int(dur * SR)
        s = lowpass(osc(midi(note), n, "saw", 10), 900) * env(n, 0.004, dur * 0.9)
        s += 0.6 * osc(midi(note), n, "sine") * env(n, 0.004, dur * 0.9)
        self.put("bass", t, s, g)

    def pluck(self, t, notes, g=0.11):
        n = int(0.6 * SR)
        s = np.zeros(n)
        for nt in notes:
            s += osc(midi(nt), n, "saw", 14, detune=0.003) * env(n, 0.002, 0.12)
        self.put("keys", t, lowpass(s, 3800), g)

    def pad(self, t, notes, dur, g=0.05):
        n = int(dur * SR)
        s = np.zeros(n)
        for nt in notes:
            s += osc(midi(nt), n, "saw", 8, detune=0.006)
        a = np.minimum(1, np.arange(n) / (0.4 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.3 * SR))
        self.put("pad", t, lowpass(s, 1600) * a, g)

    def bell(self, t, note, g=0.12, dur=0.9):
        n = int(dur * SR)
        f = midi(note)
        s = (osc(f, n, "sine") + 0.35 * osc(f * 2, n, "sine") + 0.12 * osc(f * 3.01, n, "sine")) * env(n, 0.002, 0.35)
        self.put("lead", t, s, g)

    def riser(self, t, dur, g=0.035):
        n = int(dur * SR)
        s = highpass(self.rng.standard_normal(n), 2500) * (np.linspace(0, 1, n) ** 2)
        self.put("fx", t, s, g)

    def crash(self, t, g=0.06):
        n = int(1.6 * SR)
        self.put("fx", t, highpass(self.rng.standard_normal(n), 5000) * env(n, 0.001, 0.5), g)

    # ---- mix -----------------------------------------------------------------
    def mixdown(self, sidechain=0.55):
        b = self.bus
        # side-chain pump from the kick on bass/pad/keys
        k = np.abs(b["kick"])
        k = fftconv(k, np.ones(int(0.02 * SR)) / (0.02 * SR))
        duck = 1 - sidechain * np.clip(k / (k.max() + 1e-9) * 3, 0, 1)
        duck = fftconv(duck, np.ones(int(0.01 * SR)) / (0.01 * SR))
        ir_n = int(1.2 * SR)
        ir = self.rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / (0.35 * SR))
        ir = highpass(ir, 400) / np.sqrt((ir ** 2).sum())
        wet = fftconv(b["keys"] * 0.5 + b["lead"] + b["drums"] * 0.15 + b["pad"] * 0.4, ir) * 0.22
        dry = b["kick"] * 0.9 + b["drums"] + (b["bass"] + b["pad"] + b["keys"]) * duck + b["lead"] + b["fx"]
        mono = dry + wet
        # light stereo: delay the reverb/keys slightly to one side
        d = int(0.012 * SR)
        side = np.concatenate([np.zeros(d), (wet + b["keys"] * 0.3)[:-d]])
        left, right = mono + 0.25 * side, mono - 0.25 * side
        st = np.stack([left, right], 1)
        st /= np.abs(st).max() + 1e-9
        return np.tanh(st * 1.4) / np.tanh(1.4) * 0.89


# I-V-vi-IV in D major: D A Bm G (MIDI roots)
PROG = [(50, [62, 66, 69]), (45, [61, 64, 69]), (47, [62, 66, 71]), (43, [62, 67, 71])]
HOOK = [(0, 74), (0.75, 76), (1.5, 78), (2.5, 76), (3, 74), (4, 73), (4.75, 74), (5.5, 76), (6.5, 73),
        (8, 71), (8.75, 74), (9.5, 78), (10.5, 76), (11, 74), (12, 74), (12.75, 76), (13.5, 74), (14, 71)]


def arrange(seconds, bpm, seed, calm=False):
    s = Song(seconds, bpm, seed)
    bar = 4 * s.beat
    bars = max(4, int(seconds / bar))
    for i in range(bars):
        t0 = i * bar
        root, chord = PROG[i % 4]
        last = i == bars - 1
        intro = i < 2
        if calm:
            sect = "low" if (i // 8) % 2 == 0 else "mid"
        else:
            sect = "intro" if intro else ("A" if i < 6 else ("B" if (i - 6) % 12 < 8 else "break"))
        if last:
            s.kick(t0); s.crash(t0)
            s.bass(t0, root, bar * 1.2)
            s.pad(t0, chord, bar * 1.4, 0.06)
            s.pluck(t0, chord, 0.13)
            s.bell(t0, chord[-1] + 12, 0.10, 2.0)
            break
        s.pad(t0, chord, bar, 0.045 if not calm else 0.05)
        # plucked chords: syncopated 8ths
        for st in (0, 0.75, 1.5, 2, 2.75, 3.5):
            s.pluck(t0 + st * s.beat, chord, 0.09 if (calm or intro) else 0.11)
        if intro and not calm:
            if i == 1:
                s.riser(t0, bar)
            continue
        drums = (not calm) or sect == "mid"
        for b in range(4):
            tb = t0 + b * s.beat
            if drums and sect != "break":
                s.kick(tb, 1.0 if not calm else 0.7)
            if drums and b in (1, 3) and sect != "break":
                s.clap(tb, 0.45 if not calm else 0.3)
            s.hat(tb + s.beat / 2, 0.11 if not calm else 0.07, open_=(b == 3 and not calm))
            if not calm or sect == "mid":
                s.hat(tb, 0.05)
            # pumping 8th-note bass
            s.bass(tb, root, s.beat * 0.45, 0.30 if sect != "break" else 0.18)
            s.bass(tb + s.beat / 2, root + (12 if b == 3 else 0), s.beat * 0.4, 0.26 if sect != "break" else 0.15)
        if not calm and sect == "B":
            ph = (i - 6) % 4
            for off, nt in HOOK:
                if ph * 4 <= off < ph * 4 + 4:
                    s.bell(t0 + (off - ph * 4) * s.beat, nt, 0.11)
        if not calm and ((i - 6) % 12 == 7 or (i - 6) % 12 == 11):
            s.riser(t0 + bar / 2, bar / 2)
        if not calm and (i - 6) % 12 == 0:
            s.crash(t0)
    end = min(s.n, int((bars * bar + 2.5) * SR))
    out = s.mixdown(0.55 if not calm else 0.35)[:end]
    fade = int(0.02 * SR)
    out[:fade] *= np.linspace(0, 1, fade)[:, None]
    tail = int(1.5 * SR)
    out[-tail:] *= np.linspace(1, 0, tail)[:, None]
    return out


def write_wav(path, x):
    import wave
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("style", choices=["promo", "bed"])
    ap.add_argument("out")
    ap.add_argument("--seconds", type=float, default=48)
    ap.add_argument("--bpm", type=float, default=None)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--lufs", type=float, default=-14)
    a = ap.parse_args()
    calm = a.style == "bed"
    bpm = a.bpm or (100 if calm else 112)
    x = arrange(a.seconds, bpm, a.seed, calm)
    raw = a.out + ".raw.wav"
    write_wav(raw, x)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af",
                    f"loudnorm=I={a.lufs}:TP=-1.5:LRA=11", "-ar", str(SR), a.out], check=True)
    import os
    os.remove(raw)
    print(f"{a.style} {len(x)/SR:.1f}s @ {bpm} bpm -> {a.out}")


if __name__ == "__main__":
    sys.exit(main())
