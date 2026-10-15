#!/usr/bin/env python3
"""vedit - build faceless SaaS explainer reels from a project.json edit list.

Rendering engine: HyperFrames (HTML + GSAP -> MP4, installed locally under
../engine). vedit.py prepares media (privacy blur, trim, speed), mixes audio,
generates the HyperFrames composition (compose.py), renders it, and muxes the
final audio.

Subcommands
  setup     install the pinned HyperFrames engine locally (engine/node_modules)
  init      create a project folder from the template
  probe     print basic info about media files
  frames    extract gridded frames from a recording (privacy boxes, zoom targets)
  tts       generate per-scene Bangla voice-over with edge-tts
  music     write a placeholder music bed (drafts only - replace before publishing)
  render    build the video (+ .srt, cover, timeline) from project.json
  preview   open the generated composition in HyperFrames Studio
  qa        technical checks + contact sheets for a rendered video

Requires: Node.js >= 22, ffmpeg/ffprobe >= 5 (libx264), Python 3.9+, Pillow.
Optional: edge-tts (pip install edge-tts) for the `tts` step.
"""
import argparse
import datetime
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover
    sys.exit("Pillow is required: pip install pillow")

SKILL = Path(__file__).resolve().parent.parent
ENGINE = SKILL / "engine"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from compose import build_project, plain  # noqa: E402
VERBOSE = False


# ---------------------------------------------------------------- utilities

def run(cmd, capture=False):
    if VERBOSE:
        print("$ " + " ".join(str(c) for c in cmd))
    p = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if p.returncode != 0:
        sys.stderr.write(p.stderr[-4000:])
        sys.exit(f"command failed: {cmd[0]} (exit {p.returncode})")
    return p.stdout + p.stderr if capture else p.stdout


def ffmpeg(*args):
    return run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args])


def probe(path):
    out = run(["ffprobe", "-v", "error", "-print_format", "json",
               "-show_format", "-show_streams", str(path)])
    return json.loads(out)


def media_duration(path):
    return float(probe(path)["format"]["duration"])


def video_info(path):
    info = probe(path)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    if v is None:
        sys.exit(f"no video stream in {path}")
    num, den = (v.get("avg_frame_rate") or "30/1").split("/")
    fps = float(num) / float(den) if float(den) else 30.0
    w, h = int(v["width"]), int(v["height"])
    rot = int((v.get("tags") or {}).get("rotate", 0))
    for sd in v.get("side_data_list", []) or []:
        rot = int(sd.get("rotation", rot))
    if abs(rot) in (90, 270):
        w, h = h, w
    return {"w": w, "h": h, "fps": fps,
            "duration": float(info["format"]["duration"]),
            "has_audio": any(s["codec_type"] == "audio" for s in info["streams"])}


def measure_lufs(path):
    out = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af",
               "loudnorm=print_format=json", "-f", "null", "-"], capture=True)
    data = json.loads(out[out.rindex("{"):out.rindex("}") + 1])
    return data


def rgb(hexstr, alpha=None):
    h = hexstr.lstrip("#")
    t = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    return t + (alpha,) if alpha is not None else t


def srt_time(t):
    ms = int(round(max(0.0, t) * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def deep_merge(a, b):
    out = dict(a)
    for k, v in b.items():
        out[k] = deep_merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


# ------------------------------------------------------------- brand/project

def load_brand(ref, overrides=None):
    p = Path(ref)
    if not p.suffix:
        p = SKILL / "brands" / ref / "brand.json"
    brand = json.loads(p.read_text(encoding="utf-8"))
    brand = deep_merge(brand, overrides or {})
    brand["_dir"] = p.parent
    fdir = (p.parent / brand["fonts"]["dir"]).resolve()
    brand["_fontdir"] = fdir
    for k in ("regular", "semibold", "bold"):
        brand["_font_" + k] = fdir / brand["fonts"][k]
    return brand


def load_project(path):
    path = Path(path).resolve()
    proj = json.loads(path.read_text(encoding="utf-8"))
    proj["_file"] = path
    proj["_dir"] = path.parent
    ref = proj.get("brand", "digital-studio")
    if Path(ref).suffix:
        ref = str(pfile(proj, ref))
    return proj, load_brand(ref, proj.get("brand_overrides"))


def pfile(proj, rel):
    p = Path(rel)
    return p if p.is_absolute() else (proj["_dir"] / p)


def font(brand, weight, size):
    return ImageFont.truetype(str(brand["_font_" + weight]), size,
                              layout_engine=ImageFont.Layout.RAQM)


# ------------------------------------------------------------------ graphics

def supersampled(size, draw_fn, scale=2):
    w, h = size
    big = Image.new("RGBA", (w * scale, h * scale), (0, 0, 0, 0))
    draw_fn(big, ImageDraw.Draw(big), scale)
    return big.resize((w, h), Image.LANCZOS)


def logo_png(brand, proj, size, out):
    """Brand logo fitted into a size x size transparent square (placeholder if missing)."""
    c = brand["colors"]
    cands = [proj.get("logo"), brand.get("logo")]
    src = None
    for cand in cands:
        if not cand:
            continue
        for base in (proj["_dir"], brand["_dir"]):
            p = Path(base) / cand
            if p.exists():
                src = p
                break
        if src:
            break
    if src:
        im = Image.open(src).convert("RGBA")
        im.thumbnail((size, size), Image.LANCZOS)
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        canvas.paste(im, ((size - im.width) // 2, (size - im.height) // 2), im)
        canvas.save(out)
        return True
    initials = "".join(w[0] for w in brand["name"].split()[:2]).upper()

    def draw(im, d, s):
        S = size * s
        d.rounded_rectangle((0, 0, S - 1, S - 1), int(S * 0.24), fill=rgb(c["teal"], 255))
        d.rounded_rectangle((S * 0.06, S * 0.06, S * 0.94, S * 0.94), int(S * 0.2),
                            outline=rgb(c["gold"], 255), width=int(S * 0.03))
        f = font(brand, "bold", int(S * 0.42))
        bb = d.textbbox((0, 0), initials, font=f)
        d.text(((S - (bb[2] - bb[0])) / 2 - bb[0], (S - (bb[3] - bb[1])) / 2 - bb[1]),
               initials, font=f, fill=rgb(c["gold"], 255))
    supersampled((size, size), draw).save(out)
    return False


# --------------------------------------------------------------------- audio

SFX = {
    "click": ("aevalsrc=exprs='0.7*sin(2*PI*2600*t)*exp(-t*95)+0.35*(random(0)*2-1)*exp(-t*260)'"
              ":s=48000:d=0.09,highpass=f=900"),
    "pop": ("aevalsrc=exprs='0.85*sin(2*PI*(420+1100*exp(-t*32))*t)*exp(-t*22)':s=48000:d=0.2"),
    "whoosh": ("anoisesrc=c=pink:r=48000:d=0.55:a=0.9,"
               "volume='pow(sin(PI*t/0.55),3)':eval=frame,highpass=f=350,lowpass=f=5200"),
}


def make_sfx(dirpath):
    dirpath.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, src in SFX.items():
        p = dirpath / f"{name}.wav"
        if not p.exists():
            ffmpeg("-f", "lavfi", "-i", src, "-ac", "2", "-ar", "48000", str(p))
        paths[name] = p
    return paths


def make_placeholder_music(out, seconds=60, bpm=112):
    b = 60.0 / bpm
    root = (f"if(lt(mod(t,{16*b}),{4*b}),220,if(lt(mod(t,{16*b}),{8*b}),174.61,"
            f"if(lt(mod(t,{16*b}),{12*b}),261.63,196)))")
    pluck = f"(0.55+0.45*exp(-mod(t,{b/2})*6))"
    pad = (f"0.07*{pluck}*(sin(2*PI*{root}*t)+0.8*sin(2*PI*{root}*1.26*t)"
           f"+0.7*sin(2*PI*{root}*1.5*t)+0.3*sin(2*PI*{root}*2*t))")
    kick = f"0.5*sin(2*PI*(50+90*exp(-mod(t,{b})*30))*mod(t,{b}))*exp(-mod(t,{b})*9)"
    hat = f"0.05*(random(0)*2-1)*exp(-mod(t+{b/2},{b})*70)"
    expr = f"{pad}+{kick}+{hat}"
    ffmpeg("-f", "lavfi", "-i", f"aevalsrc=exprs='{expr}|{expr}':s=48000:d={seconds}",
           "-af", "lowpass=f=9000,afade=t=in:d=0.5", str(out))


# ------------------------------------------------------------ scene planning

def scene_vo_file(proj, sc):
    if sc.get("vo_file"):
        p = pfile(proj, sc["vo_file"])
        return p if p.exists() else None
    tts = proj["_dir"] / "build" / "tts" / f"{sc['id']}.mp3"
    return tts if sc.get("vo") and tts.exists() and tts.stat().st_size > 0 else None


def vo_mode(proj, brand):
    return proj.get("voiceover", {}).get("mode", brand["voice"].get("default_mode", "scenes"))


def scene_lines(sc):
    """On-screen supporting text for a scene (no-voice-over videos)."""
    t = sc.get("text")
    if not t:
        return []
    return [t] if isinstance(t, str) else list(t)


def music_source(proj, build):
    m = proj.get("music") or {}
    if not m.get("file"):
        return None
    if m["file"] == "placeholder":
        src = build / "placeholder_music.wav"
        if not src.exists():
            build.mkdir(parents=True, exist_ok=True)
            make_placeholder_music(src, seconds=90)
        return src
    return pfile(proj, m["file"])


def detect_beats(proj, build):
    """Tempo + first-beat phase of the music, via `hyperframes beats` (cached).
    Returns (beat_seconds, phase_seconds) or None."""
    m = proj.get("music") or {}
    bpm = m.get("bpm", "auto")
    if not bpm or bpm == "off":
        return None
    if m.get("file") == "placeholder":
        return 60.0 / 112, 0.0
    if bpm != "auto":
        return 60.0 / float(bpm), float(m.get("first_beat", 0))
    src = music_source(proj, build)
    if not src or not src.exists():
        return None
    key = hashlib.sha1(f"{src.resolve()}|{src.stat().st_size}|{src.stat().st_mtime}".encode()).hexdigest()[:12]
    cache = build / "beats.json"
    if cache.exists():
        c = json.loads(cache.read_text())
        if c.get("key") == key:
            return c["beat"], c["phase"]
    probe_dir = build / "beats_probe"
    shutil.rmtree(probe_dir, ignore_errors=True)
    (probe_dir / "assets").mkdir(parents=True)
    dst = probe_dir / "assets" / ("music" + src.suffix)
    shutil.copy2(src, dst)
    d = min(120.0, media_duration(dst))
    (probe_dir / "index.html").write_text(
        '<!doctype html><html><head><meta charset="UTF-8"></head><body>'
        f'<div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="{d:.2f}">'
        f'<audio id="music" src="assets/{dst.name}" data-start="0" data-duration="{d:.2f}"></audio></div></body></html>')
    r = hf("beats", probe_dir, "--json", check=False)
    try:
        out = json.loads(r.stdout[r.stdout.index("{"):r.stdout.rindex("}") + 1])
        data = json.loads((probe_dir / out["file"]).read_text())
        beat = 60.0 / float(out["bpm"])
        phase = float(data["beats"][0]["time"]) % beat
    except (ValueError, KeyError, IndexError, OSError):
        print("NOTE: beat detection failed - cuts are not snapped to the music (set music.bpm to fix).")
        return None
    cache.write_text(json.dumps({"key": key, "beat": beat, "phase": phase, "bpm": out["bpm"]}))
    print(f"  music tempo: {out['bpm']} BPM (cuts snap to the beat)")
    return beat, phase


def plan(proj, brand, build=None):
    """Resolve durations, speeds and absolute timeline for every scene."""
    T, Vo, Cp = brand["motion"]["transition_seconds"], brand["voice"], brand["captions"]
    mode = vo_mode(proj, brand)
    scenes = proj["scenes"]
    planned = []
    for i, sc in enumerate(scenes):
        sc = dict(sc)
        sc.setdefault("id", f"s{i+1}")
        last = i == len(scenes) - 1
        overlap = 0 if last else T
        vo_dur, vo_src = 0.0, None
        if mode == "scenes":
            f = scene_vo_file(proj, sc)
            if f:
                vo_dur, vo_src = media_duration(f), f
            elif sc.get("vo"):
                vo_dur = len(sc["vo"].replace(" ", "")) / Vo["chars_per_second_estimate"]
                vo_src = "estimate"
        # on-screen text: each line held long enough to read
        lines, off = [], 0.0
        if mode == "none":
            for line in scene_lines(sc):
                d = max(Cp.get("min_line_seconds", 1.4),
                        len(plain(line).replace(" ", "")) / Cp.get("reading_cps", 11))
                lines.append((round(off, 3), round(d, 3), line))
                off += d
        sc["_lines"] = lines
        body = vo_dur if vo_dur else off
        need = (Vo["lead_in_seconds"] + body + Vo["tail_seconds"] + overlap) if body else 0
        if sc.get("type") == "screen":
            clip = pfile(proj, sc.get("clip", ""))
            if not sc.get("clip") or not clip.exists():
                sys.exit(f"scene {sc['id']}: recording not found: {clip}")
            info = video_info(clip)
            sc["_info"] = info
            cin = float(sc.get("in", 0))
            cout = float(sc.get("out", info["duration"]))
            speed = float(sc.get("speed", 1.0))
            natural = (cout - cin) / speed
            if sc.get("steps"):
                # every click needs time to land and its label time to be read
                last_step = max(float(st["t"]) for st in sc["steps"])
                need = max(need, (last_step - cin) / speed + 1.6 + overlap)
            if sc.get("duration"):
                dur = float(sc["duration"])
            elif mode == "none":
                # no narration: the demo sets the pace, capped so a scene never drags
                # (a guided walkthrough may run longer - its clicks set the length)
                cap = brand["motion"].get("max_screen_seconds", 8.0) + overlap
                if sc.get("steps"):
                    cap = max(cap, need)
                dur = max(need, min(natural + overlap, cap), 2.0)
            else:
                dur = max(need, 2.0) if need else natural
            if natural > dur + 0.05 and sc.get("auto_speed", True) and not sc.get("duration"):
                speed = min(2.5, (cout - cin) / dur)
            sc.update(_in=cin, _out=cout, _speed=speed)
        else:
            if sc.get("type") == "list":
                # every item needs time to land and be read
                items = sc.get("items", [])
                need = max(need, 0.9 + len(items) * float(sc.get("item_gap", 0.55)) + 1.6 + overlap)
            dur = float(sc["duration"]) if sc.get("duration") else max(need, 2.5)
        sc["_dur"] = dur
        sc["_vo_dur"], sc["_vo_src"] = vo_dur, vo_src
        planned.append(sc)

    beats = detect_beats(proj, build) if build is not None and mode == "none" else None
    if beats:
        b = beats[0]
        for i, sc in enumerate(planned):
            if sc.get("duration"):
                continue
            last = i == len(planned) - 1
            span = sc["_dur"] - (0 if last else T)
            span = max(1, math.ceil(span / b - 0.15)) * b
            sc["_dur"] = span + (0 if last else T)
            if sc.get("type") == "screen" and sc.get("auto_speed", True):
                natural = (sc["_out"] - sc["_in"]) / sc["_speed"]
                if natural > sc["_dur"] + 0.05:
                    sc["_speed"] = min(2.5, (sc["_out"] - sc["_in"]) / sc["_dur"])
    proj["_beats"] = beats
    t = 0.0
    for i, sc in enumerate(planned):
        sc["_dur"] = round(sc["_dur"], 3)
        sc["_start"] = round(t, 3)
        t += sc["_dur"] - (T if i < len(planned) - 1 else 0)
    total = round(t, 3)
    if mode == "single":
        # one continuous recording: captions follow scene windows
        for sc in planned:
            sc["_vo_src"] = "single"
    return planned, total


# ------------------------------------------------------------ scene renders

def norm_box(b, w, h, pad=0):
    """Normalised [x, y, w, h] -> pixel box. Size is clamped to the frame; position
    is not (a box may sit partly or fully off-frame while content scrolls)."""
    x, y, bw, bh = b
    BW = max(2, min(w, int(bw * w) + 2 * pad) // 2 * 2)
    BH = max(2, min(h, int(bh * h) + 2 * pad) // 2 * 2)
    return int(x * w) - pad, int(y * h) - pad, BW, BH


def lerp_expr(a, b, t0, t1):
    if t1 <= t0 or a == b:
        return f"{a}"
    return f"({a}+({b}-{a})*clip((t-{t0})/{t1-t0},0,1))"


def prepare_clip(proj, brand, sc, out, draft):
    """Bake privacy blur into the recording, then trim / speed / freeze-extend it to
    exactly the scene length. Blur boxes use normalised source coords and source seconds."""
    fps = brand["video"]["fps"]
    info = sc["_info"]
    sw, sh = info["w"] // 2 * 2, info["h"] // 2 * 2
    dur, cin, cout, speed = sc["_dur"], sc["_in"], sc["_out"], sc["_speed"]
    fl = [f"[0:v]fps={fps},scale={sw}:{sh},setsar=1,format=yuv420p[s0]"]
    cur, k = "s0", 0
    style = brand["privacy"].get("style", "blur")
    for b in sc.get("blur", []):
        X, Y, BW, BH = norm_box(b["box"], sw, sh, pad=6)
        t0 = float(b.get("t", 0))
        t1 = float(b["until"]) if b.get("until") is not None else 1e9
        en = f"between(t,{t0},{t1})"
        if b.get("to"):
            X1, Y1, _, _ = norm_box([b["to"][0], b["to"][1], b["box"][2], b["box"][3]], sw, sh, pad=6)
            ts, te = float(b.get("move_from", t0)), float(b.get("move_until", t1))
            xe, ye = lerp_expr(X, X1, ts, te), lerp_expr(Y, Y1, ts, te)
        else:
            xe, ye = str(X), str(Y)
        k += 1
        if style == "solid" or b.get("style") == "solid":
            col = brand["colors"]["bg_dark"].lstrip("#")
            fl.append(f"[{cur}]drawbox=x='{xe}':y='{ye}':w={BW}:h={BH}:color=0x{col}@1:t=fill:enable='{en}'[s{k}]")
        else:
            r = max(2, min(30, min(BW, BH) // 2 - 1))
            fl.append(f"[{cur}]split[m{k}][c{k}];"
                      f"[c{k}]crop=w={BW}:h={BH}:x='clip({xe},0,iw-{BW})':y='clip({ye},0,ih-{BH})',boxblur=lr={r}:lp=3:cr={max(1, r // 2 - 1)}:cp=3[b{k}];"
                      f"[m{k}][b{k}]overlay=x='{xe}':y='{ye}':enable='{en}'[s{k}]")
        cur = f"s{k}"
    fl.append(f"[{cur}]trim=start={cin}:end={cout},setpts=(PTS-STARTPTS)/{speed},fps={fps},"
              f"tpad=stop_mode=clone:stop_duration={dur + 1},trim=duration={dur},format=yuv420p[out]")
    ffmpeg("-i", str(pfile(proj, sc["clip"])), "-filter_complex", ";".join(fl), "-map", "[out]", "-an",
           "-c:v", "libx264", "-preset", "veryfast" if draft else "medium", "-crf", "20" if draft else "14",
           "-pix_fmt", "yuv420p", "-r", str(fps), str(out))


# ------------------------------------------------------------------ engine

def engine_env():
    env = dict(os.environ, HYPERFRAMES_NO_TELEMETRY="1", DO_NOT_TRACK="1")
    if "HYPERFRAMES_BROWSER_PATH" not in env:
        for cand in ("/opt/pw-browsers/chromium",):
            if Path(cand).exists():
                env["HYPERFRAMES_BROWSER_PATH"] = cand
    return env


def hf_bin():
    b = ENGINE / "node_modules" / ".bin" / "hyperframes"
    if not b.exists():
        sys.exit("HyperFrames engine not installed. Run: python3 scripts/vedit.py setup")
    return b


def gsap_js():
    p = ENGINE / "node_modules" / "gsap" / "dist" / "gsap.min.js"
    if not p.exists():
        sys.exit("gsap missing from the engine. Run: python3 scripts/vedit.py setup")
    return p


def hf(*args, cwd=None, check=True):
    cmd = [str(hf_bin()), *[str(x) for x in args]]
    if VERBOSE:
        print("$ " + " ".join(cmd))
    p = subprocess.run(cmd, cwd=cwd, env=engine_env(), capture_output=True, text=True)
    if check and p.returncode != 0:
        sys.stderr.write((p.stdout + p.stderr)[-6000:])
        sys.exit(f"hyperframes {args[0]} failed (exit {p.returncode})")
    return p


# --------------------------------------------------------------------- mixing

def build_audio(proj, brand, planned, total, sfx_events, build):
    A, Vo = brand["audio"], brand["voice"]
    sfx = make_sfx(build / "sfx")
    vo_cfg = proj.get("voiceover", {})
    tracks = {}

    # voice
    clips = []
    if vo_cfg.get("mode") == "single" and vo_cfg.get("file"):
        clips.append((pfile(proj, vo_cfg["file"]), float(vo_cfg.get("offset", 0.3))))
    else:
        for sc in planned:
            if isinstance(sc["_vo_src"], Path):
                clips.append((sc["_vo_src"], sc["_start"] + Vo["lead_in_seconds"]))
    if clips:
        raw = build / "vo_raw.wav"
        ins, fl = [], []
        for i, (f, t) in enumerate(clips):
            ins += ["-i", str(f)]
            ms = int(t * 1000)
            fl.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms}[v{i}]")
        fl.append("".join(f"[v{i}]" for i in range(len(clips))) +
                  f"amix=inputs={len(clips)}:normalize=0:dropout_transition=0,apad,atrim=0:{total}[vo]")
        ffmpeg(*ins, "-filter_complex", ";".join(fl), "-map", "[vo]", "-ar", "48000", str(raw))
        g = A["voice_lufs"] - float(measure_lufs(raw)["input_i"])
        tracks["vo"] = (raw, g)

    # music
    mcfg = proj.get("music")
    src = music_source(proj, build)
    if src:
        raw = build / "music_raw.wav"
        ss = float(mcfg.get("start", 0))
        if proj.get("_beats"):
            ss += proj["_beats"][1]  # start on a beat so cuts land on it
        ffmpeg("-stream_loop", "-1", "-ss", f"{ss}", "-i", str(src), "-af",
               f"aresample=48000,aformat=channel_layouts=stereo,atrim=0:{total},"
               f"afade=t=in:d=0.3,afade=t=out:st={max(0, total - 1.8)}:d=1.8",
               "-ar", "48000", str(raw))
        default_gain = A["music_gain_db"] if "vo" in tracks else A.get("music_gain_db_no_vo", 0)
        g = A["music_lufs"] - float(measure_lufs(raw)["input_i"]) + float(mcfg.get("gain_db", default_gain))
        tracks["music"] = (raw, g)

    # sfx
    sfx_track = None
    evs = [(n, t) for n, t in sfx_events if n in sfx and 0 <= t < total]
    if evs and proj.get("sound_design", True):
        sfx_track = build / "sfx_track.wav"
        ins, fl = [], []
        for i, (n, t) in enumerate(evs):
            ins += ["-i", str(sfx[n])]
            ms = int(t * 1000)
            db = A["sfx_gain_db"].get(n, -14)
            fl.append(f"[{i}:a]volume={db}dB,adelay={ms}|{ms}[x{i}]")
        fl.append("".join(f"[x{i}]" for i in range(len(evs))) +
                  f"amix=inputs={len(evs)}:normalize=0:dropout_transition=0,apad,atrim=0:{total}[sx]")
        ffmpeg(*ins, "-filter_complex", ";".join(fl), "-map", "[sx]", "-ar", "48000", str(sfx_track))

    mix = build / "mix_pre.wav"
    ins, fl, labels = [], [], []
    idx = 0
    if "vo" in tracks:
        ins += ["-i", str(tracks["vo"][0])]
        fl.append(f"[{idx}:a]volume={tracks['vo'][1]:.2f}dB,asplit=2[vo][key]")
        labels.append("[vo]")
        idx += 1
    if "music" in tracks:
        ins += ["-i", str(tracks["music"][0])]
        fl.append(f"[{idx}:a]volume={tracks['music'][1]:.2f}dB[mu]")
        if "vo" in tracks:
            fl.append(f"[mu][key]sidechaincompress=threshold={A['duck_threshold']}:ratio={A['duck_ratio']}"
                      f":attack=15:release=350:makeup=1[duck]")
            labels.append("[duck]")
        else:
            labels.append("[mu]")
        idx += 1
    elif "vo" in tracks:
        fl.append("[key]anullsink")
    if sfx_track:
        ins += ["-i", str(sfx_track)]
        labels.append(f"[{idx}:a]")
        idx += 1
    if not labels:
        ffmpeg("-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{total}", str(mix))
        return mix
    fl.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:dropout_transition=0,"
              f"atrim=0:{total}[mx]")
    ffmpeg(*ins, "-filter_complex", ";".join(fl), "-map", "[mx]", "-ar", "48000", str(mix))

    # loudness: gain to target behind a peak limiter, re-measured until within 0.3 LU
    final = build / "mix.wav"
    shutil.copy2(mix, final)
    lim = 10 ** ((A["true_peak"] - 0.6) / 20)
    for _ in range(4):
        m = measure_lufs(final)
        gain = A["target_lufs"] - float(m["input_i"])
        if abs(gain) < 0.3 and float(m["input_tp"]) <= A["true_peak"]:
            break
        tmp = build / "mix_tmp.wav"
        ffmpeg("-i", str(final), "-af", f"volume={gain:.2f}dB,alimiter=limit={lim:.4f}:attack=3:release=60:level=false",
               "-ar", "48000", str(tmp))
        tmp.replace(final)
    return final


# ------------------------------------------------------------------ commands

def cmd_render(a):
    proj, brand = load_project(a.project)
    V = brand["video"]
    build = proj["_dir"] / "build"
    hfdir = build / "hf"
    outdir = proj["_dir"] / "out"
    for d in (build, hfdir / "assets" / "clips", hfdir / "assets" / "audio", outdir):
        d.mkdir(parents=True, exist_ok=True)
    planned, total = plan(proj, brand, build)

    print(f"Timeline ({len(planned)} scenes, {total:.1f}s, target {V['target_seconds']}s):")
    for sc in planned:
        src = sc["_vo_src"]
        vo = "" if not sc.get("vo") or vo_mode(proj, brand) == "none" else (
            " vo=est" if src == "estimate" else " vo=file" if isinstance(src, Path) else " vo=single")
        if sc["_lines"]:
            vo = f" text={len(sc['_lines'])} line(s)"
        extra = f" speed={sc['_speed']:.2f}" if sc.get("type") == "screen" else ""
        print(f"  {sc['_start']:6.2f}s  {sc['_dur']:5.2f}s  {sc.get('type', 'title'):6s} {sc['id']}{vo}{extra}")
    if total > V["max_seconds"]:
        print(f"WARNING: {total:.1f}s exceeds the {V['max_seconds']}s platform limit")
    elif abs(total - V["target_seconds"]) > 3:
        print(f"WARNING: {total:.1f}s is off the {V['target_seconds']}s target - adjust scene lengths, clip in/out or on-screen text")
    if any(sc["_vo_src"] == "estimate" for sc in planned):
        print("NOTE: some scenes have no voice file - durations are estimated (draft timing).")
    if a.plan_only:
        return

    for sc in planned:
        if sc.get("type") == "screen":
            print(f"  preparing clip {sc['id']} (privacy blur, trim, speed) ...")
            prepare_clip(proj, brand, sc, hfdir / "assets" / "clips" / f"{sc['id']}.mp4", a.draft)
    logo_png(brand, proj, 512, hfdir / "assets" / "logo.png")
    sfx_events, captions = build_project(proj, brand, planned, total, hfdir, "logo.png", gsap_js(), a.draft)
    print("  mixing audio ...")
    audio = build_audio(proj, brand, planned, total, sfx_events, build)
    shutil.copy2(audio, hfdir / "assets" / "audio" / "mix.wav")

    print("  hyperframes check ...")
    chk = hf("check", hfdir, check=False)
    tail = [l for l in (chk.stdout + chk.stderr).strip().splitlines() if l.strip()][-12:]
    print("    " + "\n    ".join(tail))
    if chk.returncode != 0 and not a.force:
        sys.exit("hyperframes check reported blocking findings (see above). Fix them or pass --force.")

    date = datetime.date.today().isoformat()
    name = f"{proj.get('name', 'Project')}_v{proj.get('version', 1)}_{V['ratio_label']}_{date}"
    if a.draft:
        name += "_DRAFT"
    raw = build / "hf_render.mp4"
    print("  hyperframes render ...")
    r = hf("render", hfdir, "--output", raw, "--fps", V["fps"], "--quality", "draft" if a.draft else "delivery",
           "--video-frame-format", "png", "--quiet")
    for line in (r.stdout + r.stderr).splitlines():
        if "beginframe" in line or "screenshot" in line:
            print("    " + line.strip())
            break
    final = outdir / f"{name}.mp4"
    vinfo = probe(raw)["streams"]
    vs = next(s for s in vinfo if s["codec_type"] == "video")
    vcodec = ["-c:v", "copy"] if vs["codec_name"] == "h264" and vs.get("pix_fmt") == "yuv420p" else \
        ["-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p"]
    ffmpeg("-i", str(raw), "-i", str(audio), "-map", "0:v:0", "-map", "1:a:0", *vcodec,
           "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-t", f"{total:.3f}", "-movflags", "+faststart", str(final))

    srt = outdir / f"{name}.srt"
    srt.write_text("\n".join(f"{i}\n{srt_time(s)} --> {srt_time(e)}\n{t}\n"
                             for i, (s, e, t) in enumerate(captions, 1)), encoding="utf-8")
    cover = outdir / f"{name}_cover.jpg"
    ffmpeg("-ss", f"{float(proj.get('cover_at', min(1.5, total / 2)))}", "-i", str(final),
           "-frames:v", "1", "-q:v", "2", str(cover))
    timeline = [{"id": s["id"], "type": s.get("type", "title"), "start": s["_start"], "duration": s["_dur"],
                 "vo_seconds": round(s["_vo_dur"], 2), "vo_source": str(s["_vo_src"]) if s["_vo_src"] else None,
                 "speed": round(s.get("_speed", 1), 2)} for s in planned]
    (outdir / f"{name}_timeline.json").write_text(
        json.dumps({"total": total, "scenes": timeline, "sfx": sfx_events}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(f"\nDone: {final}\n      {srt}\n      {cover}\n      composition: {hfdir}")


def cmd_setup(a):
    if not shutil.which("npm"):
        sys.exit("npm not found - install Node.js 22+ first")
    p = subprocess.run(["npm", "ci" if (ENGINE / "package-lock.json").exists() else "install",
                        "--no-audit", "--no-fund"], cwd=ENGINE, env=engine_env())
    if p.returncode:
        sys.exit("npm install failed")
    env = engine_env()
    if "HYPERFRAMES_BROWSER_PATH" not in env:
        print("Fetching the pinned Chrome build for rendering ...")
        hf("browser", "ensure")
    r = hf("doctor", "--json", check=False)
    try:
        checks = json.loads(r.stdout)["checks"]
        for c in checks:
            if c.get("name") in ("Version", "Node.js", "FFmpeg", "FFprobe", "Chrome"):
                print(f"  [{'ok' if c.get('ok') else 'FAIL'}] {c['name']}: {c.get('detail', '')}")
    except (ValueError, KeyError):
        print(r.stdout[-2000:])


def cmd_preview(a):
    proj, _ = load_project(a.project)
    hfdir = proj["_dir"] / "build" / "hf"
    if not (hfdir / "index.html").exists():
        sys.exit("render the project once first (python3 scripts/vedit.py render project.json --draft)")
    subprocess.run([str(hf_bin()), "preview", str(hfdir)], env=engine_env())


def cmd_tts(a):
    proj, brand = load_project(a.project)
    Vo = brand["voice"]
    try:
        import edge_tts
    except ImportError:
        sys.exit("edge-tts not installed: pip install edge-tts  (or record the voice-over and set vo_file)")
    import asyncio
    outdir = proj["_dir"] / "build" / "tts"
    outdir.mkdir(parents=True, exist_ok=True)
    voice = a.voice or Vo["tts_voice"]
    rate = a.rate or Vo["tts_rate"]

    async def one(sc):
        text = plain(sc["vo"])
        key = hashlib.sha1(f"{voice}|{rate}|{Vo['tts_pitch']}|{text}".encode()).hexdigest()[:12]
        out = outdir / f"{sc['id']}.mp3"
        stamp = outdir / f"{sc['id']}.key"
        if out.exists() and out.stat().st_size and stamp.exists() and stamp.read_text() == key and not a.force:
            return f"{sc['id']}: cached"
        kw = {"rate": rate, "pitch": Vo["tts_pitch"]}
        if a.proxy:
            kw["proxy"] = a.proxy
        await edge_tts.Communicate(text, voice, **kw).save(str(out))
        stamp.write_text(key)
        return f"{sc['id']}: {media_duration(out):.2f}s"

    for sc in proj["scenes"]:
        if sc.get("vo") and not sc.get("vo_file"):
            try:
                print(asyncio.run(one(sc)))
            except Exception as e:  # network / service errors
                sys.exit(f"TTS failed for {sc.get('id')}: {e}\n"
                         "Check internet access, or record the voice-over and set vo_file per scene.")


def cmd_frames(a):
    clip = Path(a.clip)
    out = Path(a.out or (clip.parent / f"{clip.stem}_frames"))
    out.mkdir(parents=True, exist_ok=True)
    info = video_info(clip)
    tmp = out / "_raw"
    tmp.mkdir(exist_ok=True)
    for f in tmp.glob("*.png"):
        f.unlink()
    width = a.width
    ffmpeg("-i", str(clip), "-vf", f"fps=1/{a.every},scale={width}:-2", str(tmp / "f_%05d.png"))
    frames = sorted(tmp.glob("f_*.png"))
    fnt = ImageFont.truetype(str(SKILL / "assets/fonts/HindSiliguri-Bold.ttf"), 18)
    tiles = []
    for i, f in enumerate(frames):
        t = i * a.every
        im = Image.open(f).convert("RGB")
        d = ImageDraw.Draw(im, "RGBA")
        w, h = im.size
        for k in range(1, 10):
            x, y = int(w * k / 10), int(h * k / 10)
            d.line((x, 0, x, h), fill=(255, 0, 80, 110), width=1)
            d.line((0, y, w, y), fill=(255, 0, 80, 110), width=1)
            d.text((x + 2, 2), f".{k}", font=fnt, fill=(255, 0, 80, 255))
            d.text((2, y + 1), f".{k}", font=fnt, fill=(255, 0, 80, 255))
        d.rectangle((w - 110, h - 34, w, h), fill=(0, 0, 0, 170))
        d.text((w - 104, h - 32), f"t={t:.1f}s", font=fnt, fill=(255, 255, 255, 255))
        p = out / f"t{t:07.2f}.png"
        im.save(p)
        tiles.append(im)
    shutil.rmtree(tmp)
    cols = a.cols
    for s in range(0, len(tiles), a.per_sheet):
        group = tiles[s:s + a.per_sheet]
        tw = 300
        th = int(tw * group[0].height / group[0].width)
        rows = math.ceil(len(group) / cols)
        sheet = Image.new("RGB", (cols * tw, rows * th), (20, 20, 20))
        for j, im in enumerate(group):
            sheet.paste(im.resize((tw, th), Image.LANCZOS), ((j % cols) * tw, (j // cols) * th))
        sheet.save(out / f"sheet_{s // a.per_sheet + 1:02d}.jpg", quality=88)
    print(f"{len(tiles)} frames ({info['w']}x{info['h']}, {info['duration']:.1f}s) -> {out}")
    print("Grid lines are at 0.1 steps of width/height; use them for normalised [x, y, w, h] boxes.")


def cmd_qa(a):
    video = Path(a.video)
    brand = load_brand(a.brand)
    V, A = brand["video"], brand["audio"]
    info = probe(video)
    vs = next(s for s in info["streams"] if s["codec_type"] == "video")
    au = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    dur = float(info["format"]["duration"])
    num, den = vs["avg_frame_rate"].split("/")
    fps = float(num) / float(den)
    checks = []

    def check(name, ok, detail, warn=False):
        checks.append({"check": name, "status": "PASS" if ok else ("WARN" if warn else "FAIL"), "detail": detail})

    check("resolution", (vs["width"], vs["height"]) == (V["width"], V["height"]), f"{vs['width']}x{vs['height']}")
    check("video codec", vs["codec_name"] == "h264" and vs.get("pix_fmt") == "yuv420p",
          f"{vs['codec_name']} {vs.get('pix_fmt')}")
    check("frame rate", abs(fps - V["fps"]) < 0.1, f"{fps:.2f} fps")
    check("duration limit", dur <= V["max_seconds"], f"{dur:.2f}s (max {V['max_seconds']}s)")
    check("duration target", abs(dur - V["target_seconds"]) <= 3, f"{dur:.2f}s (target {V['target_seconds']}s)", warn=True)
    if au:
        check("audio codec", au["codec_name"] == "aac" and int(au["sample_rate"]) == 48000,
              f"{au['codec_name']} {au['sample_rate']} Hz {int(au.get('bit_rate', 0)) // 1000} kbps")
        m = measure_lufs(video)
        li, tp = float(m["input_i"]), float(m["input_tp"])
        check("loudness", abs(li - A["target_lufs"]) <= 1.0, f"{li:.1f} LUFS (target {A['target_lufs']})")
        check("true peak", tp <= A["true_peak"] + 0.5, f"{tp:.1f} dBTP")
    else:
        check("audio", False, "no audio stream")
    out = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-vf",
               "blackdetect=d=0.1:pix_th=0.06", "-an", "-f", "null", "-"], capture=True)
    blacks = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", out)
    check("black frames", not blacks, ", ".join(f"{s}-{e}s" for s, e in blacks) or "none")
    if au:
        out = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-af",
                   "silencedetect=n=-45dB:d=1.5", "-vn", "-f", "null", "-"], capture=True)
        sil = re.findall(r"silence_start: ([\d.]+)", out)
        check("long silences", not sil, ", ".join(f"{float(s):.1f}s" for s in sil) or "none", warn=True)

    qdir = Path(a.out or (video.parent / f"{video.stem}_qa"))
    qdir.mkdir(parents=True, exist_ok=True)
    tmp = qdir / "_f"
    tmp.mkdir(exist_ok=True)
    for f in tmp.glob("*.png"):
        f.unlink()
    ffmpeg("-i", str(video), "-vf", f"fps=1/{a.every},scale=270:480", str(tmp / "q_%04d.png"))
    frames = sorted(tmp.glob("q_*.png"))
    L = brand["layout"]
    cols = 6
    rows = math.ceil(len(frames) / cols)
    sheet = Image.new("RGB", (cols * 270, rows * 500), (16, 16, 16))
    fnt = ImageFont.truetype(str(brand["_font_bold"]), 16)
    sx = 270 / V["width"]
    for i, f in enumerate(frames):
        im = Image.open(f).convert("RGB")
        d = ImageDraw.Draw(im, "RGBA")
        if a.guides:
            d.rectangle((L["safe_side"] * sx, L["safe_top"] * sx, 270 - L["safe_side"] * sx,
                         L["safe_bottom"] * sx), outline=(255, 60, 60, 200), width=1)
        x, y = (i % cols) * 270, (i // cols) * 500
        sheet.paste(im, (x, y))
        ImageDraw.Draw(sheet).text((x + 6, y + 481), f"{i * a.every:.1f}s", font=fnt, fill=(230, 230, 230))
    sheet_path = qdir / "contact_sheet.jpg"
    sheet.save(sheet_path, quality=88)
    shutil.rmtree(tmp)
    (qdir / "report.json").write_text(json.dumps(checks, indent=2), encoding="utf-8")
    w = max(len(c["check"]) for c in checks)
    for c in checks:
        print(f"  [{c['status']}] {c['check']:<{w}}  {c['detail']}")
    print(f"\nContact sheet: {sheet_path}  (red box = text safe zone)")
    if any(c["status"] == "FAIL" for c in checks):
        sys.exit(1)


def cmd_probe(a):
    for f in a.files:
        info = probe(f)
        d = float(info["format"]["duration"])
        parts = [f"{f}: {d:.2f}s"]
        for s in info["streams"]:
            if s["codec_type"] == "video":
                vi = video_info(f)
                parts.append(f"video {s['codec_name']} {vi['w']}x{vi['h']} {vi['fps']:.2f}fps")
            elif s["codec_type"] == "audio":
                parts.append(f"audio {s['codec_name']} {s.get('sample_rate')}Hz ch={s.get('channels')}")
        print("  ".join(parts))


def cmd_music(a):
    out = Path(a.out)
    make_placeholder_music(out, seconds=a.seconds)
    print(f"placeholder music -> {out} (not for publishing)")


def cmd_init(a):
    d = Path(a.dir)
    if (d / "project.json").exists() and not a.force:
        sys.exit(f"{d / 'project.json'} already exists (use --force to overwrite)")
    for sub in ("recordings", "audio", "out"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    tpl = json.loads((SKILL / "templates" / "project.example.json").read_text(encoding="utf-8"))
    tpl["brand"] = a.brand
    if a.name:
        tpl["name"] = a.name
    (d / "project.json").write_text(json.dumps(tpl, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"project created in {d}: put screen recordings in recordings/, music in audio/")


def main():
    global VERBOSE
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-v", "--verbose", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("setup"); p.set_defaults(fn=cmd_setup)

    p = sub.add_parser("preview"); p.add_argument("project"); p.set_defaults(fn=cmd_preview)

    p = sub.add_parser("init"); p.add_argument("dir"); p.add_argument("--brand", default="digital-studio")
    p.add_argument("--name"); p.add_argument("--force", action="store_true"); p.set_defaults(fn=cmd_init)

    p = sub.add_parser("probe"); p.add_argument("files", nargs="+"); p.set_defaults(fn=cmd_probe)

    p = sub.add_parser("frames"); p.add_argument("clip"); p.add_argument("--every", type=float, default=0.5)
    p.add_argument("--out"); p.add_argument("--width", type=int, default=720)
    p.add_argument("--cols", type=int, default=6); p.add_argument("--per-sheet", type=int, default=24)
    p.set_defaults(fn=cmd_frames)

    p = sub.add_parser("tts"); p.add_argument("project"); p.add_argument("--voice"); p.add_argument("--rate")
    p.add_argument("--proxy"); p.add_argument("--force", action="store_true"); p.set_defaults(fn=cmd_tts)

    p = sub.add_parser("music"); p.add_argument("out"); p.add_argument("--seconds", type=int, default=60)
    p.set_defaults(fn=cmd_music)

    p = sub.add_parser("render"); p.add_argument("project"); p.add_argument("--draft", action="store_true")
    p.add_argument("--plan-only", action="store_true")
    p.add_argument("--force", action="store_true", help="render even if hyperframes check fails")
    p.set_defaults(fn=cmd_render)

    p = sub.add_parser("qa"); p.add_argument("video"); p.add_argument("--brand", default="digital-studio")
    p.add_argument("--every", type=float, default=1.5); p.add_argument("--out")
    p.add_argument("--no-guides", dest="guides", action="store_false"); p.set_defaults(fn=cmd_qa)

    a = ap.parse_args()
    VERBOSE = a.verbose
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found on PATH")
    a.fn(a)


if __name__ == "__main__":
    main()
