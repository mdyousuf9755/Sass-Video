#!/usr/bin/env python3
"""compose16 - 16:9 (1920x1080) tutorial / promo builder for the video-editor skill.

The 9:16 Reel pipeline (vedit.py + compose.py) is laid out for portrait
phones. This is its landscape sibling for YouTube / Facebook feed videos:

  * scenes are `title`, `screen` (recorded clips and stills inside a browser
    frame) and `cta`;
  * a screen scene is cut from one or more segments (clip in/out or a still),
    then fitted to the scene length (frozen last frame, or a gentle speed-up);
  * every scene carries its voice-over text (`vo`). It becomes burned-in
    Bangla subtitles and an .srt, so a draft reads well before a voice exists;
  * per-scene voice files (`vo_file`) are mixed in when present, with the
    music ducked under the voice.

  python3 compose16.py render videos/<project>/tutorial.json [--draft]

Recordings should already have the cursor and privacy masking baked in (see
reference/recording-16x9.md). Reuses HyperFrames, fonts, brand colours, SFX
and the loudness loop from vedit.py.
"""
import argparse
import datetime
import html
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compose import ICONS, chunk_text, font_faces, n, plain, rgba, rich, sub_doc, time_chunks  # noqa: E402
from vedit import ffmpeg, gsap_js, hf, load_brand, make_sfx, measure_lufs, media_duration, srt_time  # noqa: E402

W, H, FPS = 1920, 1080, 30
T = 0.4                                   # scene transition
FRAME = {"x": 200, "y": 150, "w": 1520, "bar": 44}   # browser frame; screen is 16:9 under the bar
FRAME["h"] = FRAME["w"] * 9 // 16
CAP = {"max_words": 9, "max_chars": 52}


def pfile(base, rel):
    p = Path(rel)
    return p if p.is_absolute() else base / p


# --------------------------------------------------------------- scene media

def prepare_scene_video(proj, sc, out, draft):
    """Concatenate the scene's segments into one 1920x1080 clip of exactly sc['dur'] seconds."""
    base, dur = proj["_dir"], float(sc["dur"])
    ins, fl, labels = [], [], []
    for i, seg in enumerate(sc["segments"]):
        crop = seg.get("crop")
        cf = f"crop={crop[2]}:{crop[3]}:{crop[0]}:{crop[1]}," if crop else ""
        if "still" in seg:
            ins += ["-loop", "1", "-t", f"{float(seg['dur'])}", "-i", str(pfile(base, seg["still"]))]
            fl.append(f"[{i}:v]{cf}scale={W}:{H}:force_original_aspect_ratio=decrease,"
                      f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=#F4F6F6,fps={FPS},setsar=1,format=yuv420p[s{i}]")
        else:
            a, b = float(seg.get("in", 0)), seg.get("out")
            b = float(b) if b is not None else media_duration(pfile(base, seg["clip"]))
            sp = float(seg.get("speed", 1))
            ins += ["-i", str(pfile(base, seg["clip"]))]
            fl.append(f"[{i}:v]trim={a}:{b},setpts=(PTS-STARTPTS)/{sp},{cf}scale={W}:{H},fps={FPS},"
                      f"setsar=1,format=yuv420p[s{i}]")
        labels.append(f"[s{i}]")
    fl.append("".join(labels) + f"concat=n={len(labels)}:v=1:a=0[cat]")
    # fit: freeze the last frame if short; speed up (max 1.6x) and trim if long
    total = 0.0
    for seg in sc["segments"]:
        if "still" in seg:
            total += float(seg["dur"])
        else:
            b = seg.get("out")
            b = float(b) if b is not None else media_duration(pfile(base, seg["clip"]))
            total += (b - float(seg.get("in", 0))) / float(seg.get("speed", 1))
    k = min(1.6, total / dur) if total > dur else 1.0
    fl.append(f"[cat]setpts=PTS/{k:.4f},tpad=stop_mode=clone:stop_duration={dur + 1},trim=0:{dur},"
              f"setpts=PTS-STARTPTS[v]")
    ffmpeg(*ins, "-filter_complex", ";".join(fl), "-map", "[v]", "-an", "-r", str(FPS),
           "-c:v", "libx264", "-crf", "24" if draft else "15", "-preset", "veryfast" if draft else "medium",
           "-pix_fmt", "yuv420p", str(out))
    sc["_speed"], sc["_src_seconds"] = round(k, 3), round(total, 2)


# --------------------------------------------------------------- scene html

def stage(sid, i, last, dur):
    s = [f'tl.fromTo("#{sid}-stage", {{ opacity: 0, y: {0 if i == 0 else 40} }}, '
         f'{{ opacity: 1, y: 0, duration: {n(T + 0.1)}, ease: "power3.out" }}, 0);']
    if not last:
        s.append(f'tl.to("#{sid}-stage", {{ opacity: 0, y: -30, duration: {n(T * 0.7)}, ease: "power2.in" }}, '
                 f'{n(dur - T * 0.7 - 0.02)});')
    return s


def pop(sel, t):
    return (f'tl.fromTo("{sel}", {{ opacity: 0, y: 22, scale: 0.9 }}, '
            f'{{ opacity: 1, y: 0, scale: 1, duration: 0.5, ease: "back.out(1.7)" }}, {n(t)});')


def screen_html(sc, i, last, brand, sfx):
    sid, dur, C = sc["id"], float(sc["dur"]), brand["colors"]
    g, s0 = FRAME, sc["_start"]
    css = f"""#{sid}-head {{ position: absolute; left: 120px; right: 120px; top: 34px; height: 92px;
  display: flex; align-items: center; justify-content: center; }}
#{sid}-h {{ font-size: 50px; font-weight: 700; line-height: 1.15; white-space: nowrap; text-shadow: 0 4px 18px rgba(0,0,0,.35); }}
#{sid}-frame {{ position: absolute; left: {g['x']}px; top: {g['y']}px; width: {g['w']}px; height: {g['h'] + g['bar']}px;
  border-radius: 18px; overflow: hidden; background: #fff; box-shadow: 0 30px 80px rgba(0,0,0,.45); }}
#{sid}-bar {{ position: absolute; left: 0; top: 0; right: 0; height: {g['bar']}px; background: #e9eeee;
  display: flex; align-items: center; padding: 0 18px; gap: 9px; }}
#{sid}-bar i {{ display: block; width: 13px; height: 13px; border-radius: 7px; }}
#{sid}-url {{ margin-left: 16px; width: 640px; height: 28px; border-radius: 14px; background: #fff; color: #42504d;
  font-size: 17px; font-weight: 600; display: flex; align-items: center; padding: 0 16px; }}
#{sid}-screen {{ position: absolute; left: 0; top: {g['bar']}px; width: {g['w']}px; height: {g['h']}px; overflow: hidden; }}
#{sid}-cam {{ position: absolute; inset: 0; transform-origin: 50% 50%; }}
#{sid}-vid {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}"""
    script = stage(sid, i, last, dur)
    script.append(f'tl.fromTo("#{sid}-frame", {{ scale: 0.96 }}, {{ scale: 1, duration: 0.6, ease: "power3.out" }}, 0);')
    for z in sc.get("zoom", []):
        S, a = float(z.get("scale", 1.6)), float(z["t"])
        b = a + float(z.get("dur", 2.5))
        r = min(0.6, (b - a) / 2)
        lim_x, lim_y = (S - 1) * g["w"] / 2, (S - 1) * g["h"] / 2
        tx = max(-lim_x, min(lim_x, (0.5 - float(z["x"])) * g["w"] * S))
        ty = max(-lim_y, min(lim_y, (0.5 - float(z["y"])) * g["h"] * S))
        script.append(f'tl.to("#{sid}-cam", {{ scale: {n(S)}, x: {n(tx)}, y: {n(ty)}, duration: {n(r)}, ease: "power2.inOut" }}, {n(a)});')
        if not z.get("hold"):
            script.append(f'tl.to("#{sid}-cam", {{ scale: 1, x: 0, y: 0, duration: {n(r)}, ease: "power2.inOut" }}, {n(b - r)});')
    # highlight boxes (normalised to the recording) with an optional callout label
    overlays = []
    for k, hb in enumerate(sc.get("highlight", [])):
        x, y, w, h = hb["box"]
        a, d = float(hb.get("t", 0)), float(hb.get("dur", dur - float(hb.get("t", 0)) - 0.3))
        lab = (f'<div class="hl-lab" style="{"top:100%;margin-top:14px" if hb.get("below") else "bottom:100%;margin-bottom:14px"}">'
               f'{rich(hb["label"])}</div>' if hb.get("label") else "")
        overlays.append(f'<div class="hl" id="{sid}-hl{k}" style="left:{n(x * 100)}%;top:{n(y * 100)}%;'
                        f'width:{n(w * 100)}%;height:{n(h * 100)}%">{lab}</div>')
        script.append(f'tl.fromTo("#{sid}-hl{k}", {{ opacity: 0, scale: 1.12 }}, {{ opacity: 1, scale: 1, duration: 0.35, '
                      f'ease: "back.out(1.6)" }}, {n(a)});')
        script.append(f'tl.to("#{sid}-hl{k}", {{ opacity: 0, duration: 0.25 }}, {n(a + d)});')
        sfx.append(("pop", s0 + a))
    css += f"""
#{sid}-stage .hl {{ position: absolute; border: 6px solid {C['gold']}; border-radius: 16px; opacity: 0;
  box-shadow: 0 0 0 9999px rgba(7,20,22,.35), 0 0 30px {rgba(C['gold'], .6)}; }}
#{sid}-stage .hl-lab {{ position: absolute; right: 0; white-space: nowrap; padding: 8px 22px; border-radius: 14px;
  background: {C['gold']}; color: {C['bg_dark']}; font-size: 34px; font-weight: 700; box-shadow: 0 8px 22px rgba(0,0,0,.35); }}
#{sid}-stage .hl-lab .em {{ color: {C['bg_dark']}; text-decoration: underline; }}"""
    body = []
    if sc.get("headline"):
        body.append(f'<div id="{sid}-head"><h2 id="{sid}-h">{rich(sc["headline"])}</h2></div>')
        script.append(pop(f"#{sid}-h", 0.25))
        sfx.append(("pop", s0 + 0.3))
    url = html.escape(sc.get("url", brand.get("url", "")))
    body.append(f'<div id="{sid}-frame"><div id="{sid}-bar"><i style="background:#ff5f57"></i>'
                f'<i style="background:#febc2e"></i><i style="background:#28c840"></i><div id="{sid}-url">{url}</div></div>'
                f'<div id="{sid}-screen"><div id="{sid}-cam"><video id="{sid}-vid" src="../assets/clips/{sid}.mp4" '
                f'muted playsinline data-start="0" data-duration="{n(dur)}"></video>{"".join(overlays)}</div></div></div>')
    return sub_doc(sid, dur, brand, css, "\n".join(body), "\n".join(script))


def title_html(sc, i, last, brand, sfx):
    sid, dur, C = sc["id"], float(sc["dur"]), brand["colors"]
    css = f"""#{sid}-box {{ position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center;
  justify-content: center; gap: 28px; text-align: center; padding: 0 200px; }}
#{sid}-icon, #{sid}-logo {{ width: 230px; height: 230px; display: block; }}
#{sid}-icon svg {{ width: 100%; height: 100%; display: block; }}
#{sid}-h {{ font-size: 92px; font-weight: 700; line-height: 1.2; text-wrap: balance; text-shadow: 0 6px 24px rgba(0,0,0,.35); }}
#{sid}-sub {{ font-size: 46px; font-weight: 600; color: {C['text_muted']}; text-wrap: balance; }}
#{sid}-bar {{ width: 150px; height: 9px; border-radius: 5px; background: {C['gold']}; display: block; }}"""
    body, script = [f'<div id="{sid}-box">'], stage(sid, i, last, dur)
    t = 0.2
    if sc.get("icon") in ICONS:
        body.append(f'<div id="{sid}-icon">{ICONS[sc["icon"]].format(teal=C["teal"], gold=C["gold"])}</div>')
        script.append(pop(f"#{sid}-icon", t)); t += 0.35
    elif sc.get("logo"):
        body.append(f'<img id="{sid}-logo" src="../assets/logo.png" alt="">')
        script.append(pop(f"#{sid}-logo", t)); t += 0.35
    body.append(f'<h1 id="{sid}-h">{rich(sc.get("headline", ""))}</h1>')
    script.append(pop(f"#{sid}-h", t)); sfx.append(("pop", sc["_start"] + t + 0.05)); t += 0.4
    body.append(f'<i id="{sid}-bar"></i>')
    script.append(f'tl.fromTo("#{sid}-bar", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.5, ease: "power3.out" }}, {n(t)});')
    if sc.get("sub"):
        body.append(f'<div id="{sid}-sub">{rich(sc["sub"])}</div>')
        script.append(pop(f"#{sid}-sub", t + 0.3))
    body.append("</div>")
    return sub_doc(sid, dur, brand, css, "\n".join(body), "\n".join(script))


def cta_html(sc, i, last, brand, sfx):
    sid, dur, C, cta = sc["id"], float(sc["dur"]), brand["colors"], brand["cta"]
    css = f"""#{sid}-box {{ position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center;
  justify-content: center; gap: 18px; text-align: center; }}
#{sid}-box > * {{ flex-shrink: 0; }}
#{sid}-logo {{ width: 150px; height: 150px; display: block; }}
#{sid}-offer {{ font-size: 44px; font-weight: 700; padding: 8px 34px; border-radius: 40px; background: {rgba(C['gold'], .16)};
  border: 3px solid {C['gold']}; color: {C['gold_light']}; }}
#{sid}-h {{ font-size: 84px; font-weight: 700; line-height: 1.15; }}
#{sid}-btn {{ font-size: 54px; font-weight: 700; color: {C['bg_dark']}; background: {C['gold']}; padding: 16px 56px;
  border-radius: 22px; box-shadow: 0 16px 40px rgba(0,0,0,.35); }}
#{sid}-sec {{ font-size: 40px; font-weight: 600; color: {C['text_muted']}; }}
#{sid}-foot {{ margin-top: 10px; display: flex; flex-direction: column; gap: 6px; font-size: 30px; color: {C['text_muted']}; }}
#{sid}-dev {{ font-weight: 700; color: {C['text']}; }}
#{sid}-contact {{ font-size: 38px; font-weight: 700; padding: 8px 30px; border-radius: 30px; background: {rgba(C['teal'], .55)}; }}"""
    body = [f'<div id="{sid}-box">', f'<img id="{sid}-logo" src="../assets/logo.png" alt="">',
            f'<div id="{sid}-offer">{rich(cta["offer"])}</div>',
            f'<div id="{sid}-h">{rich(cta["headline"])}</div>',
            f'<div id="{sid}-btn">{html.escape(cta["url"])}</div>',
            f'<div id="{sid}-sec">{rich(cta["secondary"])}</div>',
            f'<div id="{sid}-foot"><div id="{sid}-dev">{html.escape(cta["developer"])}</div>'
            f'<div>{html.escape(brand.get("address", ""))}</div></div>',
            f'<div id="{sid}-contact">{rich(cta["contact"])}</div>', "</div>"]
    script = stage(sid, i, last, dur)
    for k, el in enumerate(("logo", "offer", "h", "btn", "sec", "foot", "contact")):
        script.append(pop(f"#{sid}-{el}", 0.2 + 0.28 * k))
    sfx.append(("pop", sc["_start"] + 0.5))
    script.append(f'tl.to("#{sid}-btn", {{ scale: 1.05, duration: 0.5, yoyo: true, repeat: 3, ease: "sine.inOut" }}, 2.6);')
    return sub_doc(sid, dur, brand, css, "\n".join(body), "\n".join(script))


# --------------------------------------------------------------- build

def build(proj, brand, hfdir, draft):
    shutil.rmtree(hfdir, ignore_errors=True)
    comp = hfdir / "compositions"
    for d in (comp, hfdir / "assets" / "fonts", hfdir / "assets" / "vendor", hfdir / "assets" / "clips"):
        d.mkdir(parents=True, exist_ok=True)
    for k in ("regular", "semibold", "bold"):
        shutil.copy2(brand["_font_" + k], hfdir / "assets" / "fonts" / brand["fonts"][k])
    shutil.copy2(gsap_js(), hfdir / "assets" / "vendor" / "gsap.min.js")
    shutil.copy2(brand["_dir"] / brand["logo"], hfdir / "assets" / "logo.png")
    C = brand["colors"]

    t, hosts, caps, cap_js, sfx, captions = 0.0, [], [], [], [], []
    scenes = proj["scenes"]
    for i, sc in enumerate(scenes):
        sc["_start"], last, sid = t, i == len(scenes) - 1, sc["id"]
        dur = float(sc["dur"])
        if i:
            sfx.append(("whoosh", max(0.0, t - 0.12)))
        if sc["type"] == "screen":
            print(f"  clip {sid} ({dur}s)")
            prepare_scene_video(proj, sc, hfdir / "assets" / "clips" / f"{sid}.mp4", draft)
            doc = screen_html(sc, i, last, brand, sfx)
        elif sc["type"] == "cta":
            doc = cta_html(sc, i, last, brand, sfx)
        else:
            doc = title_html(sc, i, last, brand, sfx)
        (comp / f"{sid}.html").write_text(doc, encoding="utf-8")
        hosts.append(f'<div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" '
                     f'data-start="{n(t)}" data-duration="{n(dur)}" data-track-index="{1 + i % 2}" '
                     f'data-width="{W}" data-height="{H}"></div>')
        # subtitles from the VO text: timed to the voice file when there is one, else spread over the scene
        if sc.get("vo"):
            vf = sc.get("vo_file")
            vo_start = t + float(sc.get("vo_offset", 0.45 if i else 0.3))
            vo_end = vo_start + (media_duration(pfile(proj["_dir"], vf)) if vf
                                 else max(1.5, dur - (0.9 if not last else 0.6)))
            # vo_overflow: the voice runs on into the next scene, so its subtitles may too
            cap_end = vo_end if sc.get("vo_overflow") else min(vo_end, t + dur - 0.3)
            timed = time_chunks(chunk_text(plain(sc["vo"]), CAP["max_words"], CAP["max_chars"]), vo_start, cap_end)
            captions += timed
            if proj.get("captions", {}).get("burn", True) and sc.get("captions", sc["type"] != "cta"):
                for a, b, text in timed:
                    k = len(caps)
                    caps.append(f'<div id="cap{k}" class="clip cap" data-start="{n(a)}" data-duration="{n(b - a)}" '
                                f'data-track-index="3"><div id="cap{k}-p" class="cap-pill">{html.escape(text)}</div></div>')
                    cap_js.append(f'tl.fromTo("#cap{k}-p", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.16, '
                                  f'ease: "power2.out" }}, {n(a)});')
        t += dur
    total = t
    draft_mark = '<div id="draft-mark">DRAFT · voice-over pending</div>' if proj.get("_no_vo") else (
        '<div id="draft-mark">DRAFT</div>' if draft else "")
    index = f"""<!doctype html>
<html lang="bn">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>{html.escape(proj.get('name', 'Video'))}</title>
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
{font_faces(brand, "")}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: {C['bg_dark']}; }}
#root {{ position: relative; width: 100%; height: 100%; overflow: hidden; font-family: "{brand['fonts']['family']}", sans-serif; }}
#bg {{ position: absolute; inset: 0; background: linear-gradient(135deg, {C['bg_dark']} 0%, {C['bg']} 55%, {C['bg_dark']} 100%); }}
#glow-a {{ position: absolute; left: -400px; top: -500px; width: 1500px; height: 1100px; border-radius: 50%;
  background: radial-gradient(closest-side, {rgba(C['teal'], .5)}, {rgba(C['teal'], 0)}); }}
#glow-b {{ position: absolute; left: 1250px; top: 600px; width: 1000px; height: 900px; border-radius: 50%;
  background: radial-gradient(closest-side, {rgba(C['gold'], .14)}, {rgba(C['gold'], 0)}); }}
#dots {{ position: absolute; inset: 0; background-image: radial-gradient(rgba(255,255,255,.05) 2px, transparent 2.5px);
  background-size: 48px 48px; }}
.cap {{ width: 100%; height: 100%; display: flex; justify-content: center; align-items: flex-end; padding: 0 260px 62px; }}
.cap-pill {{ display: block; max-width: 1400px; padding: 10px 30px; border-radius: 18px; text-align: center;
  background: rgba(7,20,22,.84); color: #fff; font-size: 40px; font-weight: 600; line-height: 1.35;
  box-shadow: 0 8px 26px rgba(0,0,0,.35); }}
#draft-mark {{ position: absolute; right: 26px; top: 20px; font-size: 22px; font-weight: 700; color: rgba(255,255,255,.5); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="{W}" data-height="{H}"
         data-duration="{n(total)}" data-fps="{FPS}">
      <div id="bg"><div id="glow-a"></div><div id="glow-b"></div><div id="dots"></div></div>
      {chr(10).join('      ' + h for h in hosts).strip()}
      {chr(10).join('      ' + c for c in caps).strip()}
      <audio id="mix" src="assets/audio/mix.wav" data-start="0" data-duration="{n(total)}" data-track-index="5" data-volume="1"></audio>
      {draft_mark}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#glow-a", {{ x: -60, y: 0 }}, {{ x: 120, y: 50, duration: {n(total)}, ease: "none" }}, 0);
      tl.fromTo("#glow-b", {{ x: 60 }}, {{ x: -100, duration: {n(total)}, ease: "none" }}, 0);
{chr(10).join('      ' + j for j in cap_js)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    (hfdir / "index.html").write_text(index, encoding="utf-8")
    (hfdir / "hyperframes.json").write_text(json.dumps({"paths": {"blocks": "compositions", "assets": "assets"},
                                                        "media": {"autoProxy": True}}, indent=2), encoding="utf-8")
    (hfdir / "meta.json").write_text(json.dumps({"id": proj["name"], "name": proj["name"]}), encoding="utf-8")
    return total, sorted(sfx, key=lambda e: e[1]), captions


def mix_audio(proj, brand, total, sfx_events, build_dir):
    A = brand["audio"]
    sfx = make_sfx(build_dir / "sfx")
    tracks = []
    # voice: per-scene files at their scene start
    vo = [(pfile(proj["_dir"], sc["vo_file"]), sc["_start"] + float(sc.get("vo_offset", 0.45 if k else 0.3)))
          for k, sc in enumerate(proj["scenes"]) if sc.get("vo_file")]
    if vo:
        raw = build_dir / "vo_raw.wav"
        ins, fl = [], []
        for i, (f, at) in enumerate(vo):
            ins += ["-i", str(f)]
            ms = int(at * 1000)
            fl.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms}[v{i}]")
        fl.append("".join(f"[v{i}]" for i in range(len(vo))) +
                  f"amix=inputs={len(vo)}:normalize=0:dropout_transition=0,apad,atrim=0:{total}[vo]")
        ffmpeg(*ins, "-filter_complex", ";".join(fl), "-map", "[vo]", "-ar", "48000", str(raw))
        tracks.append(("vo", raw, A["voice_lufs"] - float(measure_lufs(raw)["input_i"])))
    m = proj.get("music")
    if m:
        raw = build_dir / "music_raw.wav"
        ffmpeg("-stream_loop", "-1", "-i", str(pfile(proj["_dir"], m["file"])), "-af",
               f"aresample=48000,aformat=channel_layouts=stereo,atrim=0:{total},afade=t=in:d=0.5,"
               f"afade=t=out:st={max(0, total - 2.5)}:d=2.5", "-ar", "48000", str(raw))
        # with a voice the bed sits about 18 dB under it, and ducks a little more while words are spoken
        gain = float(m.get("gain_db", -18 if vo else -3))
        tracks.append(("music", raw, A["music_lufs"] - float(measure_lufs(raw)["input_i"]) + gain))
    evs = [(k, t) for k, t in sfx_events if k in sfx and 0 <= t < total]
    ins, fl, labels = [], [], []
    for name, f, g in tracks:
        ins += ["-i", str(f)]
        fl.append(f"[{len(labels)}:a]volume={g:.2f}dB[{name}]")
        labels.append(f"[{name}]")
    if vo and m:
        fl[0] = fl[0].replace("[vo]", "[vo0]") + ";[vo0]asplit=2[vo][key]"
        fl[1] = fl[1].replace("[music]", "[mu0]") + ";[mu0][key]sidechaincompress=threshold=0.04:ratio=3:attack=20:release=400[music]"
    base = len(labels)
    for j, (k, t) in enumerate(evs):
        ins += ["-i", str(sfx[k])]
        ms = int(t * 1000)
        fl.append(f"[{base + j}:a]volume={A['sfx_gain_db'].get(k, -14) - (4 if vo else 0)}dB,adelay={ms}|{ms}[x{j}]")
        labels.append(f"[x{j}]")
    mix = build_dir / "mix_pre.wav"
    fl.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:dropout_transition=0,apad,atrim=0:{total}[mx]")
    ffmpeg(*ins, "-filter_complex", ";".join(fl), "-map", "[mx]", "-ar", "48000", str(mix))
    final = build_dir / "mix.wav"
    shutil.copy2(mix, final)
    lim = 10 ** ((A["true_peak"] - 0.6) / 20)
    for _ in range(4):
        mm = measure_lufs(final)
        gain = A["target_lufs"] - float(mm["input_i"])
        if abs(gain) < 0.3 and float(mm["input_tp"]) <= A["true_peak"]:
            break
        tmp = build_dir / "mix_tmp.wav"
        ffmpeg("-i", str(final), "-af", f"volume={gain:.2f}dB,alimiter=limit={lim:.4f}:attack=3:release=60:level=false",
               "-ar", "48000", str(tmp))
        tmp.replace(final)
    return final


def cmd_render(a):
    path = Path(a.project).resolve()
    proj = json.loads(path.read_text(encoding="utf-8"))
    proj["_dir"] = path.parent
    proj["_no_vo"] = not any(sc.get("vo_file") for sc in proj["scenes"])
    brand = load_brand(proj.get("brand", "digital-studio"),
                       {"video": {"width": W, "height": H, "fps": FPS, "ratio_label": "16x9"}})
    bdir = proj["_dir"] / "build" / proj["name"]
    hfdir = bdir / "hf"
    bdir.mkdir(parents=True, exist_ok=True)
    total, sfx, captions = build(proj, brand, hfdir, a.draft)
    if a.plan_only:
        for sc in proj["scenes"]:
            print(f"  {sc['_start']:7.2f}  {sc['dur']:6.2f}  {sc['id']:16s} speed {sc.get('_speed', 1)}")
        print(f"total {total:.2f}s"); return
    print("  audio mix ...")
    audio = mix_audio(proj, brand, total, sfx, bdir)
    (hfdir / "assets" / "audio").mkdir(parents=True, exist_ok=True)
    shutil.copy2(audio, hfdir / "assets" / "audio" / "mix.wav")
    chk = hf("check", hfdir, check=False)
    if chk.returncode != 0:
        sys.stderr.write((chk.stdout + chk.stderr)[-4000:])
        if not a.force:
            sys.exit("hyperframes check failed (pass --force to render anyway)")
    print("  hyperframes render ...")
    raw = bdir / "hf_render.mp4"
    hf("render", hfdir, "--output", raw, "--fps", FPS, "--quality", "draft" if a.draft else "delivery",
       "--video-frame-format", "png", "--quiet")
    out = proj["_dir"] / "exports"
    out.mkdir(exist_ok=True)
    name = f"{proj['name']}_v{proj.get('version', 1)}_16x9_{datetime.date.today().isoformat()}"
    if proj["_no_vo"]:
        name += "_noVO"
    if a.draft:
        name += "_DRAFT"
    final = out / f"{name}.mp4"
    ffmpeg("-i", str(raw), "-i", str(audio), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-crf", "14",
           "-preset", "slow", "-tune", "stillimage", "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
           "-t", f"{total:.3f}", "-movflags", "+faststart", str(final))
    (out / f"{name}.srt").write_text("\n".join(f"{i}\n{srt_time(s)} --> {srt_time(e)}\n{t}\n"
                                                for i, (s, e, t) in enumerate(captions, 1)), encoding="utf-8")
    (out / f"{name}_timeline.json").write_text(json.dumps(
        {"total": total, "scenes": [{"id": s["id"], "start": round(s["_start"], 3), "dur": s["dur"],
                                     "speed": s.get("_speed", 1), "source_seconds": s.get("_src_seconds")}
                                    for s in proj["scenes"]]}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Done: {final} ({total:.2f}s)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("render")
    p.add_argument("project")
    p.add_argument("--draft", action="store_true")
    p.add_argument("--force", action="store_true")
    p.add_argument("--plan-only", action="store_true")
    a = ap.parse_args()
    cmd_render(a)


if __name__ == "__main__":
    main()
