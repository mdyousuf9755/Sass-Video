"""Generate a HyperFrames project (index.html + one sub-composition per scene)
from a planned edit list. All motion lives here; vedit.py handles media prep,
audio and the final mux."""
import html
import json
import re
import shutil

BREAK_AFTER = ("।", ",", "?", "!", "—", ";", ":", "|")


# ------------------------------------------------------------------ text utils

def plain(text):
    return re.sub(r"\*(.+?)\*", r"\1", text or "")


def rich(text):
    """Escape text and turn `*word*` into a gold accent span."""
    return re.sub(r"\*(.+?)\*", r'<span class="em">\1</span>', html.escape(text or ""))


def chunk_text(text, max_words, max_chars):
    chunks, cur = [], []
    for w in text.split():
        if cur and (len(cur) >= max_words or len(" ".join(cur + [w])) > max_chars):
            chunks.append(" ".join(cur))
            cur = []
        cur.append(w)
        if w.endswith(BREAK_AFTER) and len(cur) >= 2:
            chunks.append(" ".join(cur))
            cur = []
    if cur:
        chunks.append(" ".join(cur))
    return chunks


def time_chunks(chunks, start, end):
    weights = [max(4, len(c.replace(" ", ""))) for c in chunks]
    total, t, out = sum(weights), start, []
    for c, w in zip(chunks, weights):
        d = (end - start) * w / total
        out.append((round(t, 3), round(t + d, 3), c))
        t += d
    return out


def rgba(hexstr, a):
    h = hexstr.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{a})"


BN_DIGITS = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")


def bn_digits(v):
    return str(v).translate(BN_DIGITS)


def n(v):
    return f"{v:.3f}".rstrip("0").rstrip(".")


# ------------------------------------------------------------------ geometry

def device_geometry(brand, kind, src_w, src_h):
    W = brand["video"]["width"]
    L = brand["layout"]
    top, bottom = L["device_top"], L["device_bottom"]
    aspect = src_w / src_h
    if kind == "auto":
        kind = "phone" if aspect < 0.8 else brand.get("default_frame", "browser")
    if kind == "browser":
        sw = 960
        sh = int(sw / aspect) // 2 * 2
        bar = 58
        return {"kind": kind, "x": (W - sw) // 2, "y": top + 40 + bar, "w": sw, "h": sh, "bezel": 0,
                "radius": 0, "bar": bar}
    if kind == "phone":
        bez = 18
        sh = bottom - top - 2 * bez
        sw = sh * aspect
        if sw > 700:
            sw, sh = 700, 700 / aspect
        sw, sh = int(sw) // 2 * 2, int(sh) // 2 * 2
        return {"kind": kind, "x": (W - sw) // 2, "y": top + bez + ((bottom - top - 2 * bez) - sh) // 2,
                "w": sw, "h": sh, "bezel": bez, "radius": 44}
    if kind == "laptop":
        sw = 940
        sh = int(sw / aspect) // 2 * 2
        return {"kind": kind, "x": (W - sw) // 2, "y": top + 40,
                "w": sw, "h": sh, "bezel": 16, "radius": 6}
    sw = W - 2 * 60
    sh = int(sw / aspect) // 2 * 2
    if sh > bottom - top:
        sh = (bottom - top) // 2 * 2
        sw = int(sh * aspect) // 2 * 2
    return {"kind": "none", "x": (W - sw) // 2, "y": top + ((bottom - top) - sh) // 2,
            "w": sw, "h": sh, "bezel": 0, "radius": 28}


# ------------------------------------------------------------------ html bits

TEXT_SHIFT = 110  # px the device moves down when a landscape scene's text sits under the headline


def text_above_device(brand, sc):
    """Landscape frames (browser/laptop) are short, so a bottom caption would cover the UI.
    For those scenes the text line sits under the headline and the device moves down."""
    if sc.get("type") != "screen" or not sc.get("_lines") or "_info" not in sc:
        return False
    info = sc["_info"]
    return device_geometry(brand, sc.get("frame", "auto"), info["w"], info["h"])["kind"] in ("browser", "laptop")

def font_faces(brand, prefix):
    f = brand["fonts"]
    fam = f["family"]
    return "\n".join(
        f'@font-face {{ font-family: "{fam}"; src: url("{prefix}assets/fonts/{f[k]}"); font-weight: {w}; }}'
        for k, w in (("regular", 400), ("semibold", 600), ("bold", 700)))


def sub_doc(sid, dur, brand, css, body, script):
    V = brand["video"]
    fam = brand["fonts"]["family"]
    C = brand["colors"]
    return f"""<!doctype html>
<html lang="bn">
  <head><meta charset="UTF-8" /></head>
  <body>
    <template id="{sid}">
      <style>
{font_faces(brand, "../")}
#root {{ position: absolute; inset: 0; font-family: "{fam}", sans-serif; color: {C['text']}; }}
#{sid}-stage {{ position: absolute; inset: 0; }}
.em {{ color: {C['gold']}; }}
{css}
      </style>
      <div id="root" data-composition-id="{sid}" data-width="{V['width']}" data-height="{V['height']}" data-duration="{n(dur)}">
        <div id="{sid}-stage">
{body}
        </div>
      </div>
      <script>
        const tl = gsap.timeline({{ paused: true }});
{script}
        window.__timelines["{sid}"] = tl;
      </script>
    </template>
  </body>
</html>
"""


def stage_motion(sid, i, last, dur, T):
    s = []
    if i == 0:
        s.append(f'tl.fromTo("#{sid}-stage", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3, ease: "power1.out" }}, 0);')
    else:
        s.append(f'tl.fromTo("#{sid}-stage", {{ opacity: 0, y: 90 }}, '
                 f'{{ opacity: 1, y: 0, duration: {n(T + 0.1)}, ease: "power3.out" }}, {n(T * 0.3)});')
    if not last:
        s.append(f'tl.to("#{sid}-stage", {{ opacity: 0, y: -60, duration: {n(T * 0.6)}, ease: "power2.in" }}, {n(dur - T - 0.02)});')
    return s


def pop(sel, t, d=0.5):
    return (f'tl.fromTo("{sel}", {{ opacity: 0, y: 26, scale: 0.86 }}, '
            f'{{ opacity: 1, y: 0, scale: 1, duration: {n(d)}, ease: "back.out(1.8)" }}, {n(t)});')


def rise(sel, t, d=0.45, dy=30):
    return (f'tl.fromTo("{sel}", {{ opacity: 0, y: {dy} }}, '
            f'{{ opacity: 1, y: 0, duration: {n(d)}, ease: "power3.out" }}, {n(t)});')


# ------------------------------------------------------------------ scenes

def screen_scene(sc, i, last, brand, T, sfx):
    sid, dur = sc["id"], sc["_dur"]
    C, L, Mo = brand["colors"], brand["layout"], brand["motion"]
    info = sc["_info"]
    g = device_geometry(brand, sc.get("frame", "auto"), info["w"], info["h"])
    if text_above_device(brand, sc):
        g["y"] += TEXT_SHIFT
    cin, speed, s0 = sc["_in"], sc["_speed"], sc["_start"]
    enter = T * 0.6 if i else 0.15

    def local(src_t):
        return max(0.0, (float(src_t) - cin) / speed)

    b = g["bezel"]
    css = [f"""#{sid}-head {{ position: absolute; left: {L['safe_side']}px; right: {L['safe_side']}px;
  top: {L['headline_y'] - 110}px; height: 220px; display: flex; align-items: center; justify-content: center; }}
#{sid}-h {{ font-size: {L['headline_size']}px; font-weight: 700; line-height: 1.22; text-align: center;
  text-wrap: balance; max-width: 940px; text-shadow: 0 6px 24px rgba(0,0,0,.35); }}
#{sid}-device {{ position: absolute; left: {g['x'] - b}px; top: {g['y'] - b}px; width: {g['w'] + 2 * b}px;
  height: {g['h'] + 2 * b + (b if g['kind'] == 'laptop' else 0)}px; border-radius: {g['radius'] + b}px;
  background: #121618; box-shadow: 0 40px 80px rgba(0,0,0,.45), inset 0 0 0 3px #3c4448; }}
#{sid}-screen {{ position: absolute; left: {g['x']}px; top: {g['y']}px; width: {g['w']}px; height: {g['h']}px;
  border-radius: {g['radius']}px; overflow: hidden; background: #000; }}
#{sid}-rig {{ position: absolute; inset: 0; transform-origin: {g['x'] + g['w'] // 2}px {g['y'] + g['h'] // 2}px; }}
#{sid}-cam {{ position: absolute; inset: 0; transform-origin: 50% 50%; }}
#{sid}-vid {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
.{sid}-hl {{ position: absolute; border: 5px solid {C['gold']}; border-radius: 16px;
  background: {rgba(C['gold'], .14)}; box-shadow: 0 0 0 8px {rgba(C['gold'], .18)}; opacity: 0; }}
.{sid}-ring {{ position: absolute; width: 0; height: 0; opacity: 0; }}
.{sid}-ring div {{ position: absolute; width: {int(g['w'] * .16)}px; height: {int(g['w'] * .16)}px;
  left: -{int(g['w'] * .08)}px; top: -{int(g['w'] * .08)}px; border-radius: 50%;
  border: 6px solid {C['gold']}; background: {rgba(C['gold'], .25)}; }}"""]
    if g["kind"] == "phone":
        css.append(f"#{sid}-notch {{ position: absolute; left: {g['x'] + g['w'] // 2 - 66}px; top: {g['y'] + 12}px; "
                   f"width: 132px; height: 32px; border-radius: 16px; background: #0b0c0d; }}")
    if g["kind"] == "laptop":
        css.append(f"#{sid}-base {{ position: absolute; left: {g['x'] - b - 70}px; top: {g['y'] + g['h'] + 2 * b}px; "
                   f"width: {g['w'] + 2 * b + 140}px; height: 26px; border-radius: 4px 4px 14px 14px; "
                   f"background: linear-gradient(#5b6266, #3a4044); }}")
    if g["kind"] == "none":
        css.append(f"#{sid}-device {{ background: {C['gold']}; box-shadow: 0 30px 70px rgba(0,0,0,.4); }}")
    if g["kind"] == "browser":
        bar = g["bar"]
        css.append(f"""#{sid}-device {{ left: {g['x']}px; top: {g['y'] - bar}px; width: {g['w']}px; height: {g['h'] + bar}px;
  border-radius: 18px; background: #e9eeed; box-shadow: 0 40px 80px rgba(0,0,0,.45); overflow: hidden; }}
#{sid}-screen {{ border-radius: 0 0 18px 18px; }}
#{sid}-bar {{ position: absolute; left: {g['x']}px; top: {g['y'] - bar}px; width: {g['w']}px; height: {bar}px;
  display: flex; align-items: center; gap: 10px; padding: 0 20px; }}
#{sid}-bar i {{ display: block; width: 14px; height: 14px; border-radius: 7px; }}
#{sid}-url {{ margin-left: 18px; flex: 1; height: 36px; border-radius: 18px; background: #ffffff; color: #42504d;
  font-size: 22px; font-weight: 600; display: flex; align-items: center; padding: 0 20px; }}""")

    overlays, script = [], stage_motion(sid, i, last, dur, T)
    for k, hb in enumerate(sc.get("highlight", [])):
        x, y, w, h = hb["box"]
        overlays.append(f'<div class="{sid}-hl" id="{sid}-hl{k}" style="left:{n(x*100)}%;top:{n(y*100)}%;'
                        f'width:{n(w*100)}%;height:{n(h*100)}%"></div>')
        t0 = local(hb.get("t", cin))
        d = float(hb.get("dur", 2.0)) / speed
        script.append(f'tl.fromTo("#{sid}-hl{k}", {{ opacity: 0, scale: 1.08 }}, {{ opacity: 1, scale: 1, duration: 0.25, ease: "power2.out" }}, {n(t0)});')
        script.append(f'tl.to("#{sid}-hl{k}", {{ opacity: 0, duration: 0.25 }}, {n(t0 + max(0.3, d - 0.25))});')
    for k, c in enumerate(sc.get("clicks", [])):
        overlays.append(f'<div class="{sid}-ring" id="{sid}-ring{k}" style="left:{n(c["x"]*100)}%;top:{n(c["y"]*100)}%">'
                        f'<div id="{sid}-ring{k}-c"></div></div>')
        t0 = local(c["t"])
        script.append(f'tl.set("#{sid}-ring{k}", {{ opacity: 1 }}, {n(t0)});')
        script.append(f'tl.to("#{sid}-ring{k}", {{ opacity: 0, duration: 0.55, ease: "power1.in" }}, {n(t0 + 0.01)});')
        script.append(f'tl.fromTo("#{sid}-ring{k}-c", {{ scale: 0.35 }}, {{ scale: 1.25, duration: 0.55, ease: "power2.out" }}, {n(t0)});')
        if t0 < dur:
            sfx.append(("click", s0 + t0))
    # guided walkthrough: a cursor glides to each button, clicks it, and a numbered
    # label names the option - one step at a time
    steps = sorted(sc.get("steps", []), key=lambda s: float(s["t"]))
    if steps:
        S = float(sc.get("follow_zoom_scale", 1.6))
        zoom = S if sc.get("follow") else 1.0
        cur_w = max(34, int(g["w"] * 0.05 / zoom ** 0.5))
        # labels live inside the zoomed camera, so shrink them by the zoom to keep their on-screen size
        fs = max(16, int(g["w"] * 0.034 * 1.2 / zoom))
        css.append(f"""#{sid}-cursor {{ position: absolute; left: 0; top: 0; width: {cur_w}px; height: {int(cur_w * 1.25)}px; opacity: 0;
  transform-origin: 0 0; filter: drop-shadow(0 4px 6px rgba(0,0,0,.35)); }}
#{sid}-cursor svg {{ display: block; width: 100%; height: 100%; }}
.{sid}-tip {{ position: absolute; opacity: 0; display: flex; align-items: center; gap: {fs // 2}px; white-space: nowrap;
  padding: {fs // 3}px {fs * 2 // 3}px {fs // 3}px {fs // 3}px; border-radius: {fs}px; background: {C['bg_dark']};
  color: #fff; font-size: {fs}px; font-weight: 700; box-shadow: 0 8px 20px rgba(0,0,0,.35); }}
.{sid}-tip b {{ display: flex; align-items: center; justify-content: center; width: {int(fs * 1.5)}px; height: {int(fs * 1.5)}px;
  border-radius: 50%; background: {C['gold']}; color: {C['bg_dark']}; font-size: {int(fs * 0.9)}px; }}""")
        overlays.append(f'<div id="{sid}-cursor"><svg viewBox="0 0 24 30"><path d="M2 2 L2 24 L8 18.5 L12.5 28 L16 26.5 '
                        f'L11.6 17.2 L19.5 17.2 Z" fill="#ffffff" stroke="#0b0c0d" stroke-width="1.8" '
                        f'stroke-linejoin="round"/></svg></div>')
        first = steps[0]
        t_first = local(first["t"])
        appear = max(0.0, t_first - 0.9)
        sx, sy = min(0.9, float(first["x"]) + 0.12), min(0.92, float(first["y"]) + 0.15)
        script.append(f'tl.fromTo("#{sid}-cursor", {{ opacity: 0, x: {n(sx * g["w"])}, y: {n(sy * g["h"])} }}, '
                      f'{{ opacity: 1, duration: 0.25 }}, {n(appear)});')
        prev_t = appear + 0.25
        for k, st in enumerate(steps):
            x, y, t = float(st["x"]), float(st["y"]), local(st["t"])
            travel = max(0.25, min(0.7, t - prev_t - 0.05))
            script.append(f'tl.to("#{sid}-cursor", {{ x: {n(x * g["w"])}, y: {n(y * g["h"])}, duration: {n(travel)}, '
                          f'ease: "power2.inOut" }}, {n(t - travel - 0.05)});')
            script.append(f'tl.to("#{sid}-cursor", {{ scale: 0.82, duration: 0.08, yoyo: true, repeat: 1 }}, {n(t)});')
            overlays.append(f'<div class="{sid}-ring" id="{sid}-sring{k}" style="left:{n(x*100)}%;top:{n(y*100)}%">'
                            f'<div id="{sid}-sring{k}-c"></div></div>')
            script.append(f'tl.set("#{sid}-sring{k}", {{ opacity: 1 }}, {n(t)});')
            script.append(f'tl.to("#{sid}-sring{k}", {{ opacity: 0, duration: 0.5, ease: "power1.in" }}, {n(t + 0.01)});')
            script.append(f'tl.fromTo("#{sid}-sring{k}-c", {{ scale: 0.35 }}, {{ scale: 1.2, duration: 0.5, ease: "power2.out" }}, {n(t)});')
            if t < dur:
                sfx.append(("click", s0 + t))
            if st.get("label"):
                # put the label on whichever side of the cursor it fits (in the zoomed view when following)
                est = (len(plain(st["label"])) * fs * 0.55 + fs * 2.6) / g["w"]
                half = 0.5 / zoom
                cx = min(max(x, half), 1 - half)          # centre of the visible window (camera is clamped)
                room_r, room_l = (cx + half) - x - 0.04, x - (cx - half) - 0.02
                go_left = est > room_r and (room_l >= est or room_l > room_r)
                horiz = f"right:{n((1 - x) * 100 + 2)}%" if go_left else f"left:{n(x * 100 + 4)}%"
                vert = f"bottom:{n((1 - y) * 100 + 3)}%" if y > 0.75 else f"top:{n(y * 100 + 5)}%"
                num = bn_digits(k + 1)
                overlays.append(f'<div class="{sid}-tip" id="{sid}-tip{k}" style="{horiz};{vert}">'
                                f'<b>{num}</b>{html.escape(st["label"])}</div>')
                t_end = local(steps[k + 1]["t"]) - 0.1 if k + 1 < len(steps) else dur - T - 0.1
                script.append(f'tl.fromTo("#{sid}-tip{k}", {{ opacity: 0, scale: 0.8 }}, '
                              f'{{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }}, {n(t + 0.08)});')
                if t_end > t + 0.5:
                    script.append(f'tl.to("#{sid}-tip{k}", {{ opacity: 0, duration: 0.15 }}, {n(t_end)});')
                sfx.append(("pop", s0 + t + 0.1))
            if sc.get("follow"):
                lim_x, lim_y = (S - 1) * g["w"] / 2, (S - 1) * g["h"] / 2
                tx = max(-lim_x, min(lim_x, (0.5 - x) * g["w"] * S))
                ty = max(-lim_y, min(lim_y, (0.5 - y) * g["h"] * S))
                script.append(f'tl.to("#{sid}-cam", {{ scale: {n(S)}, x: {n(tx)}, y: {n(ty)}, duration: {n(travel + 0.1)}, '
                              f'ease: "power2.inOut" }}, {n(t - travel - 0.1)});')
            prev_t = t
        if sc.get("follow"):
            script.append(f'tl.to("#{sid}-cam", {{ scale: 1, x: 0, y: 0, duration: 0.5, ease: "power2.inOut" }}, '
                          f'{n(max(prev_t + 0.8, dur - T - 0.6))});')
        script.append(f'tl.to("#{sid}-cursor", {{ opacity: 0, duration: 0.2 }}, {n(max(prev_t + 0.6, dur - T - 0.3))});')

    ramp = Mo["zoom_ramp_seconds"]
    for z in sc.get("zoom", []):
        S = float(z.get("scale", Mo["default_zoom"]))
        a = local(z["t"])
        bend = a + float(z.get("dur", 2.0)) / speed
        r = min(ramp, (bend - a) / 2)
        lim_x, lim_y = (S - 1) * g["w"] / 2, (S - 1) * g["h"] / 2
        tx = max(-lim_x, min(lim_x, (0.5 - float(z["x"])) * g["w"] * S))
        ty = max(-lim_y, min(lim_y, (0.5 - float(z["y"])) * g["h"] * S))
        script.append(f'tl.to("#{sid}-cam", {{ scale: {n(S)}, x: {n(tx)}, y: {n(ty)}, duration: {n(r)}, ease: "power2.inOut" }}, {n(a)});')
        script.append(f'tl.to("#{sid}-cam", {{ scale: 1, x: 0, y: 0, duration: {n(r)}, ease: "power2.inOut" }}, {n(bend - r)});')
    body = []
    if sc.get("headline"):
        body.append(f'<div id="{sid}-head"><h2 id="{sid}-h">{rich(sc["headline"])}</h2></div>')
        script.append(pop(f"#{sid}-h", enter))
        sfx.append(("pop", s0 + enter + 0.05))
    body.append(f'<div id="{sid}-rig">')
    body.append(f'<div id="{sid}-device"></div>')
    if g["kind"] == "laptop":
        body.append(f'<div id="{sid}-base"></div>')
    if g["kind"] == "browser":
        url = html.escape(sc.get("url", brand.get("url", "")))
        body.append(f'<div id="{sid}-bar"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i>'
                    f'<i style="background:#28c840"></i><div id="{sid}-url">{url}</div></div>')
    body.append(f'<div id="{sid}-screen"><div id="{sid}-cam">'
                f'<video id="{sid}-vid" src="../assets/clips/{sid}.mp4" muted playsinline '
                f'data-start="0" data-duration="{n(dur)}"></video>{"".join(overlays)}</div></div>')
    if g["kind"] == "phone":
        body.append(f'<div id="{sid}-notch"></div>')
    body.append("</div>")
    script.insert(0, f'tl.fromTo("#{sid}-rig", {{ scale: 0.94 }}, '
                     f'{{ scale: 1, duration: 0.6, ease: "power3.out" }}, 0);')
    return sub_doc(sid, dur, brand, "\n".join(css), "\n".join(body), "\n".join(script))


def card_bottom(brand, sc):
    """Bottom inset for card scenes: stop above the caption band when captions show."""
    H, L = brand["video"]["height"], brand["layout"]
    caps = sc.get("vo") and sc.get("captions", sc.get("type") != "cta")
    return H - (L["caption_y"] - 150 if caps else L["safe_bottom"])


ICONS = {
    # USB pendrive with a red cross - "customer forgot the pendrive"
    "pendrive-x": ('<svg viewBox="0 0 120 120"><rect x="38" y="8" width="44" height="30" rx="4" fill="#cfd8dc"/>'
                   '<rect x="48" y="16" width="8" height="8" fill="#78909c"/><rect x="64" y="16" width="8" height="8" fill="#78909c"/>'
                   '<rect x="28" y="36" width="64" height="76" rx="12" fill="{teal}"/><rect x="40" y="52" width="40" height="8" rx="4" fill="{gold}"/>'
                   '<circle cx="92" cy="92" r="24" fill="#e53935"/><path d="M82 82l20 20M102 82l-20 20" stroke="#fff" stroke-width="7" stroke-linecap="round"/></svg>'),
}


def title_scene(sc, i, last, brand, T, sfx, logo):
    sid, dur, s0 = sc["id"], sc["_dur"], sc["_start"]
    C, L = brand["colors"], brand["layout"]
    enter = T * 0.6 if i else 0.15
    css = f"""#{sid}-box {{ position: absolute; left: {L['safe_side']}px; right: {L['safe_side']}px; top: {L['safe_top']}px;
  bottom: {card_bottom(brand, sc)}px; display: flex; flex-direction: column; align-items: center;
  justify-content: center; gap: 40px; text-align: center; }}
#{sid}-logo {{ width: 180px; height: 180px; display: block; }}
#{sid}-icon {{ width: 260px; height: 260px; display: block; }}
#{sid}-icon svg {{ width: 100%; height: 100%; display: block; }}
#{sid}-h {{ font-size: 96px; font-weight: 700; line-height: 1.2; text-wrap: balance; max-width: 940px;
  text-shadow: 0 8px 30px rgba(0,0,0,.35); }}
#{sid}-sub {{ font-size: 50px; font-weight: 600; line-height: 1.3; color: {C['text_muted']}; text-wrap: balance; max-width: 900px; }}
#{sid}-bar {{ width: 160px; height: 10px; border-radius: 5px; background: {C['gold']}; display: block; }}"""
    body, script = [], stage_motion(sid, i, last, dur, T)
    body.append(f'<div id="{sid}-box">')
    if sc.get("logo"):
        body.append(f'<img id="{sid}-logo" src="../assets/{logo}" alt="" />')
        script.append(pop(f"#{sid}-logo", enter))
    if sc.get("icon") in ICONS:
        svg = ICONS[sc["icon"]].replace("{teal}", C["teal"]).replace("{gold}", C["gold"])
        body.append(f'<div id="{sid}-icon">{svg}</div>')
        script.append(f'tl.fromTo("#{sid}-icon", {{ opacity: 0, scale: 0.4, rotation: -12 }}, '
                      f'{{ opacity: 1, scale: 1, rotation: 0, duration: 0.6, ease: "back.out(2)" }}, {n(enter)});')
        script.append(f'tl.to("#{sid}-icon", {{ rotation: 6, duration: 0.12, yoyo: true, repeat: 3 }}, {n(enter + 0.7)});')
    if sc.get("headline"):
        body.append(f'<h1 id="{sid}-h">{rich(sc["headline"])}</h1>')
        script.append(pop(f"#{sid}-h", enter + 0.05, 0.55))
        sfx.append(("pop", s0 + enter + 0.1))
    body.append(f'<div id="{sid}-bar"></div>')
    script.append(f'tl.fromTo("#{sid}-bar", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.5, ease: "power3.out" }}, {n(enter + 0.3)});')
    if sc.get("sub"):
        body.append(f'<p id="{sid}-sub">{rich(sc["sub"])}</p>')
        script.append(rise(f"#{sid}-sub", enter + 0.4))
    body.append("</div>")
    return sub_doc(sid, dur, brand, css, "\n".join(body), "\n".join(script))


def logo_scene(sc, i, last, brand, T, sfx, logo):
    sid, dur, s0 = sc["id"], sc["_dur"], sc["_start"]
    C, L = brand["colors"], brand["layout"]
    enter = T * 0.6 if i else 0.15
    css = f"""#{sid}-box {{ position: absolute; left: {L['safe_side']}px; right: {L['safe_side']}px; top: {L['safe_top']}px;
  bottom: {card_bottom(brand, sc)}px; display: flex; flex-direction: column; align-items: center;
  justify-content: center; text-align: center; }}
#{sid}-halo {{ width: 360px; height: 360px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  background: radial-gradient(closest-side, {rgba(C['teal_light'], .45)}, {rgba(C['teal_light'], 0)}); }}
#{sid}-logo {{ width: 250px; height: 250px; display: block; }}
#{sid}-name {{ margin-top: 20px; font-size: 96px; font-weight: 700; color: {C['gold']}; line-height: 1.1; }}
#{sid}-by {{ margin-top: 10px; font-size: 40px; font-weight: 600; color: {C['text_muted']}; }}
#{sid}-tag {{ margin-top: 36px; font-size: 54px; font-weight: 600; text-wrap: balance; max-width: 900px; }}"""
    tagline = sc.get("sub", brand.get("tagline", ""))
    body = [f'<div id="{sid}-box"><div id="{sid}-halo"><img id="{sid}-logo" src="../assets/{logo}" alt="" /></div>',
            f'<div id="{sid}-name">{html.escape(brand["name"])}</div>']
    script = stage_motion(sid, i, last, dur, T)
    script.append(f'tl.fromTo("#{sid}-logo", {{ opacity: 0, scale: 0.5, rotation: -8 }}, '
                  f'{{ opacity: 1, scale: 1, rotation: 0, duration: 0.7, ease: "back.out(1.6)" }}, {n(enter)});')
    script.append(f'tl.fromTo("#{sid}-halo", {{ scale: 0.6, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.9, ease: "power2.out" }}, {n(enter)});')
    script.append(rise(f"#{sid}-name", enter + 0.3))
    sfx.append(("pop", s0 + enter + 0.1))
    if brand.get("byline"):
        body.append(f'<div id="{sid}-by">{html.escape(brand["byline"])}</div>')
        script.append(rise(f"#{sid}-by", enter + 0.5, dy=16))
    if tagline:
        body.append(f'<div id="{sid}-tag">{rich(tagline)}</div>')
        script.append(rise(f"#{sid}-tag", enter + 0.7))
    body.append("</div>")
    return sub_doc(sid, dur, brand, css, "\n".join(body), "\n".join(script))


def list_scene(sc, i, last, brand, T, sfx, logo):
    """Headline + feature items that pop in one by one, each with a gold tick."""
    sid, dur, s0 = sc["id"], sc["_dur"], sc["_start"]
    C, L = brand["colors"], brand["layout"]
    enter = T * 0.6 if i else 0.15
    items = sc.get("items", [])
    gap = float(sc.get("item_gap", 0.55))
    css = f"""#{sid}-box {{ position: absolute; left: {L['safe_side']}px; right: {L['safe_side']}px; top: {L['safe_top']}px;
  bottom: {brand['video']['height'] - L['safe_bottom']}px; display: flex; flex-direction: column; align-items: center;
  justify-content: center; gap: 30px; }}
#{sid}-h {{ font-size: 80px; font-weight: 700; line-height: 1.2; text-align: center; text-wrap: balance; max-width: 940px;
  margin-bottom: 18px; text-shadow: 0 8px 30px rgba(0,0,0,.35); }}
.{sid}-item {{ width: 900px; display: flex; align-items: center; gap: 26px; padding: 22px 30px; border-radius: 28px;
  background: {rgba(C['teal'], .32)}; border: 2px solid {rgba(C['teal_light'], .35)}; }}
.{sid}-tick {{ flex: none; width: 64px; height: 64px; border-radius: 50%; background: {C['gold']}; display: flex;
  align-items: center; justify-content: center; }}
.{sid}-tick svg {{ width: 36px; height: 36px; display: block; }}
.{sid}-label {{ font-size: 50px; font-weight: 700; line-height: 1.25; }}"""
    tick = ('<svg viewBox="0 0 24 24"><path d="M5 12.5l4.2 4.2L19 7" fill="none" '
            f'stroke="{C["bg_dark"]}" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    body = [f'<div id="{sid}-box">']
    script = stage_motion(sid, i, last, dur, T)
    if sc.get("headline"):
        body.append(f'<h2 id="{sid}-h">{rich(sc["headline"])}</h2>')
        script.append(pop(f"#{sid}-h", enter))
        sfx.append(("pop", s0 + enter + 0.05))
    for k, it in enumerate(items):
        t = enter + 0.5 + k * gap
        body.append(f'<div class="{sid}-item" id="{sid}-it{k}"><div class="{sid}-tick" id="{sid}-tk{k}">{tick}</div>'
                    f'<div class="{sid}-label">{rich(it)}</div></div>')
        script.append(f'tl.fromTo("#{sid}-it{k}", {{ opacity: 0, x: -60 }}, {{ opacity: 1, x: 0, duration: 0.4, ease: "power3.out" }}, {n(t)});')
        script.append(f'tl.fromTo("#{sid}-tk{k}", {{ scale: 0 }}, {{ scale: 1, duration: 0.35, ease: "back.out(2.4)" }}, {n(t + 0.12)});')
        sfx.append(("pop", s0 + t + 0.12))
    body.append("</div>")
    return sub_doc(sid, dur, brand, css, "\n".join(body), "\n".join(script))


def cta_scene(sc, i, last, brand, T, sfx, logo):
    sid, dur, s0 = sc["id"], sc["_dur"], sc["_start"]
    C, L = brand["colors"], brand["layout"]
    cta = dict(brand.get("cta", {}), **sc.get("cta", {}))
    enter = T * 0.6 if i else 0.15
    css = f"""#{sid}-box {{ position: absolute; left: {L['safe_side']}px; right: {L['safe_side']}px; top: {L['safe_top']}px;
  bottom: {card_bottom(brand, sc)}px; display: flex; flex-direction: column; align-items: center;
  justify-content: center; text-align: center; gap: 16px; }}
#{sid}-logo {{ width: 120px; height: 120px; display: block; }}
#{sid}-name {{ font-size: 54px; font-weight: 700; color: {C['gold']}; margin-top: -14px; }}
#{sid}-btnwrap {{ position: relative; width: 920px; height: 136px; display: block; }}
#{sid}-btn {{ position: absolute; inset: 0; border-radius: 68px; background: linear-gradient(180deg, {C['gold_light']}, {C['gold']});
  color: {C['bg_dark']}; font-size: 66px; font-weight: 700; display: flex; align-items: center; justify-content: center;
  box-shadow: 0 18px 40px rgba(0,0,0,.35); }}
#{sid}-tap {{ position: absolute; right: 90px; top: 68px; width: 0; height: 0; }}
#{sid}-tapc {{ position: absolute; width: 120px; height: 120px; left: -60px; top: -60px; border-radius: 50%;
  border: 6px solid #ffffff; background: rgba(255,255,255,.25); opacity: 0; }}
#{sid}-url {{ padding: 18px 46px; border-radius: 60px; border: 4px solid {C['teal_light']}; font-size: 46px;
  font-weight: 600; background: {rgba(C['bg_dark'], .55)}; display: block; }}
#{sid}-sec {{ font-size: 58px; font-weight: 700; }}
#{sid}-offer {{ padding: 12px 40px; border-radius: 50px; border: 3px solid {C['gold']}; background: {rgba(C['gold'], .14)};
  font-size: 54px; font-weight: 700; display: block; }}
#{sid}-box > * {{ flex-shrink: 0; }}
#{sid}-foot {{ display: flex; flex-direction: column; align-items: center; gap: 6px; margin-top: -8px; }}
#{sid}-dev {{ font-size: 34px; font-weight: 700; color: {C['gold_light']}; }}
#{sid}-addr {{ font-size: 30px; font-weight: 600; color: {C['text_muted']}; }}
#{sid}-contact {{ padding: 14px 40px; border-radius: 50px; background: {C['teal']}; border: 3px solid {C['teal_light']};
  font-size: 50px; font-weight: 700; display: block; box-shadow: 0 12px 30px rgba(0,0,0,.3); }}"""
    body = [f'<div id="{sid}-box">', f'<img id="{sid}-logo" src="../assets/{logo}" alt="" />',
            f'<div id="{sid}-name">{html.escape(brand["name"])}</div>',
            (f'<div id="{sid}-offer">{rich(cta["offer"])}</div>' if cta.get("offer") else ""),
            f'<div id="{sid}-btnwrap"><div id="{sid}-btn">{rich(cta["headline"])}</div>'
            f'<div id="{sid}-tap"><div id="{sid}-tapc"></div></div></div>',
            f'<div id="{sid}-url">{html.escape(cta["url"])}</div>']
    script = stage_motion(sid, i, last, dur, T)
    script += [pop(f"#{sid}-logo", enter), rise(f"#{sid}-name", enter + 0.2, dy=16)]
    if cta.get("offer"):
        script.append(pop(f"#{sid}-offer", enter + 0.3))
        sfx.append(("pop", s0 + enter + 0.35))
        enter += 0.4
    t1, t2, t3 = enter + 0.45, enter + 1.0, enter + 1.5
    script.append(pop(f"#{sid}-btn", t1, 0.55))
    script.append(pop(f"#{sid}-url", t2))
    sfx += [("pop", s0 + t1 + 0.05), ("pop", s0 + t2 + 0.05)]
    if cta.get("secondary"):
        body.append(f'<div id="{sid}-sec">{rich(cta["secondary"])}</div>')
        script.append(pop(f"#{sid}-sec", t3))
        sfx.append(("pop", s0 + t3 + 0.05))
    addr = cta.get("address", brand.get("address")) if sc.get("address", True) else None
    if cta.get("developer") or addr:
        foot = []
        if cta.get("developer"):
            foot.append(f'<div id="{sid}-dev">{html.escape(cta["developer"])}</div>')
        if addr:
            foot.append(f'<div id="{sid}-addr">{html.escape(addr)}</div>')
        body.append(f'<div id="{sid}-foot">{"".join(foot)}</div>')
        script.append(rise(f"#{sid}-foot", t3 + 0.3, dy=12))
    if cta.get("contact"):
        # the very last thing on screen: the contact number
        body.append(f'<div id="{sid}-contact">{rich(cta["contact"])}</div>')
        tc = max(t3 + 1.0, dur - 2.4)
        script.append(pop(f"#{sid}-contact", tc))
        sfx.append(("pop", s0 + tc + 0.05))
    # a finite "tap" on the button, then a gentle pulse
    tap = t3 + 0.5
    if tap + 0.6 < dur:
        script.append(f'tl.set("#{sid}-tapc", {{ opacity: 1 }}, {n(tap)});')
        script.append(f'tl.fromTo("#{sid}-tapc", {{ scale: 0.4 }}, {{ scale: 1.4, duration: 0.6, ease: "power2.out" }}, {n(tap)});')
        script.append(f'tl.to("#{sid}-tapc", {{ opacity: 0, duration: 0.45, ease: "power1.in" }}, {n(tap + 0.15)});')
        script.append(f'tl.to("#{sid}-btn", {{ scale: 0.95, duration: 0.1, yoyo: true, repeat: 1 }}, {n(tap)});')
        sfx.append(("click", s0 + tap))
        pulses = int((dur - tap - 0.9) // 1.2)
        if pulses > 0:
            script.append(f'tl.to("#{sid}-btn", {{ scale: 1.04, duration: 0.6, ease: "sine.inOut", yoyo: true, '
                          f'repeat: {pulses * 2 - 1} }}, {n(tap + 0.4)});')
    body.append("</div>")
    return sub_doc(sid, dur, brand, css, "\n".join(body), "\n".join(script))


# ------------------------------------------------------------------ project

def build_project(proj, brand, planned, total, hfdir, logo_file, gsap_js, draft=False):
    """Write the HyperFrames project. Returns (sfx_events, caption_chunks)."""
    V, L, C, Mo, Vo = brand["video"], brand["layout"], brand["colors"], brand["motion"], brand["voice"]
    W, H = V["width"], V["height"]
    T = Mo["transition_seconds"]
    fam = brand["fonts"]["family"]
    comp = hfdir / "compositions"
    comp.mkdir(parents=True, exist_ok=True)
    for sub in ("fonts", "vendor"):
        (hfdir / "assets" / sub).mkdir(parents=True, exist_ok=True)
    for k in ("regular", "semibold", "bold"):
        shutil.copy2(brand["_font_" + k], hfdir / "assets" / "fonts" / brand["fonts"][k])
    shutil.copy2(gsap_js, hfdir / "assets" / "vendor" / "gsap.min.js")

    sfx, captions, hosts, caps, cap_js = [], [], [], [], []
    for i, sc in enumerate(planned):
        sid, last = sc["id"], i == len(planned) - 1
        kind = sc.get("type", "title")
        if i:
            sfx.append(("whoosh", max(0.0, sc["_start"] - 0.1)))
        if kind == "screen":
            doc = screen_scene(sc, i, last, brand, T, sfx)
        elif kind == "logo":
            doc = logo_scene(sc, i, last, brand, T, sfx, logo_file)
        elif kind == "cta":
            doc = cta_scene(sc, i, last, brand, T, sfx, logo_file)
        elif kind == "list":
            doc = list_scene(sc, i, last, brand, T, sfx, logo_file)
        else:
            doc = title_scene(sc, i, last, brand, T, sfx, logo_file)
        (comp / f"{sid}.html").write_text(doc, encoding="utf-8")
        hosts.append(f'<div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" '
                     f'data-start="{n(sc["_start"])}" data-duration="{n(sc["_dur"])}" data-track-index="{1 + i % 2}" '
                     f'data-width="{W}" data-height="{H}"></div>')

        if sc.get("_lines"):
            base = sc["_start"] + Vo["lead_in_seconds"] + (T * 0.3 if i else 0)
            timed = [(round(base + o, 3), round(base + o + d, 3), plain(t)) for o, d, t in sc["_lines"]]
            scene_end = sc["_start"] + sc["_dur"] - (T * 0.5 if not last else 0.05)
            # the last line stays up until the scene ends, so the demo is never caption-less
            timed[-1] = (timed[-1][0], round(max(timed[-1][1], scene_end), 3), timed[-1][2])
            captions += timed
            if sc.get("captions", True) and proj.get("captions", {}).get("burn", True):
                for a, b, text in timed:
                    b = min(b, scene_end)
                    if b - a < 0.15:
                        continue
                    k = len(caps)
                    pad = (f' style="padding-bottom:{H - (L["device_top"] + TEXT_SHIFT + 20)}px"'
                           if text_above_device(brand, sc) else "")
                    caps.append(f'<div id="cap{k}" class="clip cap" data-start="{n(a)}" data-duration="{n(b - a)}" '
                                f'data-track-index="3"{pad}><div id="cap{k}-p" class="cap-pill">{html.escape(text)}</div></div>')
                    cap_js.append(f'tl.fromTo("#cap{k}-p", {{ opacity: 0, y: 18, scale: 0.94 }}, '
                                  f'{{ opacity: 1, y: 0, scale: 1, duration: 0.22, ease: "back.out(1.6)" }}, {n(a)});')
        elif sc.get("vo") and proj.get("voiceover", {}).get("mode", brand["voice"].get("default_mode", "scenes")) != "none":
            vs = sc["_start"] + Vo["lead_in_seconds"]
            ve = vs + sc["_vo_dur"]
            if proj.get("voiceover", {}).get("mode") == "single":
                vs, ve = sc["_start"] + 0.1, sc["_start"] + sc["_dur"] - T
            timed = time_chunks(chunk_text(plain(sc["vo"]), brand["captions"]["max_words"],
                                           brand["captions"]["max_chars"]), vs, max(vs + 0.5, ve))
            captions += timed
            scene_end = sc["_start"] + sc["_dur"] - (T * 0.5 if not last else 0.05)
            if sc.get("captions", kind != "cta") and proj.get("captions", {}).get("burn", True):
                for a, b, text in timed:
                    b = min(b, scene_end)
                    if b - a < 0.15:
                        continue
                    k = len(caps)
                    caps.append(f'<div id="cap{k}" class="clip cap" data-start="{n(a)}" data-duration="{n(b - a)}" '
                                f'data-track-index="3"><div id="cap{k}-p" class="cap-pill">{html.escape(text)}</div></div>')
                    cap_js.append(f'tl.fromTo("#cap{k}-p", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.14, ease: "power2.out" }}, {n(a)});')
    for e in proj.get("sfx", []):
        sfx.append((e["type"], float(e["t"])))

    draft_mark = ('<div id="draft-mark">DRAFT</div>' if draft else "")
    index = f"""<!doctype html>
<html lang="bn">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>{html.escape(proj.get('name', 'Reel'))}</title>
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
{font_faces(brand, "")}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: {C['bg_dark']}; }}
#root {{ position: relative; width: 100%; height: 100%; overflow: hidden; font-family: "{fam}", sans-serif; }}
#bg {{ position: absolute; inset: 0; background: linear-gradient(180deg, {C['bg_dark']} 0%, {C['bg']} 50%, {C['bg_dark']} 100%); }}
#glow-a {{ position: absolute; left: -260px; top: -620px; width: 1600px; height: 1300px; border-radius: 50%;
  background: radial-gradient(closest-side, {rgba(C['teal'], .55)}, {rgba(C['teal'], 0)}); }}
#glow-b {{ position: absolute; left: 560px; top: 1380px; width: 900px; height: 900px; border-radius: 50%;
  background: radial-gradient(closest-side, {rgba(C['gold'], .16)}, {rgba(C['gold'], 0)}); }}
#dots {{ position: absolute; inset: 0; background-image: radial-gradient(rgba(255,255,255,.05) 2px, transparent 2.5px);
  background-size: 54px 54px; }}
.cap {{ width: 100%; height: 100%; display: flex; justify-content: center; align-items: flex-end;
  padding: 0 {L['safe_side'] + 30}px {H - L['caption_y']}px; }}
.cap-pill {{ display: block; max-width: 900px; padding: 14px 34px; border-radius: 26px; text-align: center;
  background: {rgba(C['caption_box'], .82)}; color: {C['text']}; font-size: {L['caption_size']}px; font-weight: 700;
  line-height: 1.3; text-wrap: balance; box-shadow: 0 10px 30px rgba(0,0,0,.3); }}
#draft-mark {{ position: absolute; right: 30px; top: 30px; font-size: 34px; font-weight: 700; color: rgba(255,255,255,.45); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="{W}" data-height="{H}"
         data-duration="{n(total)}" data-fps="{V['fps']}">
      <div id="bg"><div id="glow-a"></div><div id="glow-b"></div><div id="dots"></div></div>
      {chr(10).join('      ' + h for h in hosts).strip()}
      {chr(10).join('      ' + c for c in caps).strip()}
      <audio id="mix" src="assets/audio/mix.wav" data-start="0" data-duration="{n(total)}" data-track-index="5" data-volume="1"></audio>
      {draft_mark}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#glow-a", {{ x: -80, y: 0 }}, {{ x: 90, y: 60, duration: {n(total)}, ease: "none" }}, 0);
      tl.fromTo("#glow-b", {{ x: 60 }}, {{ x: -80, duration: {n(total)}, ease: "none" }}, 0);
{chr(10).join('      ' + j for j in cap_js)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    (hfdir / "index.html").write_text(index, encoding="utf-8")
    (hfdir / "hyperframes.json").write_text(json.dumps({
        "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
        "media": {"autoProxy": True}}, indent=2), encoding="utf-8")
    (hfdir / "meta.json").write_text(json.dumps({"id": proj.get("name", "reel"), "name": proj.get("name", "reel")}),
                                     encoding="utf-8")
    return sorted(sfx, key=lambda e: e[1]), captions
