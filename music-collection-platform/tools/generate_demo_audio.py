# -*- coding: utf-8 -*-
"""生成随项目分发的「演示音乐」静态资源（原创合成音频 + SVG 封面）。

设计说明
--------
* 音频全部由本脚本用 Python 标准库实时合成，是原创的短片段，不包含任何
  商业录音，因此可以随源码 / 安装包自由分发，也不会出现外链失效、答辩现场
  断网无法试听的问题。
* 输出为 22050Hz / 16bit / 单声道 WAV，Chromium 原生支持，无需解码器。
* 资源写入 frontend/public/demo/，Vite 构建时会原样复制到 dist/，
  electron-builder 打包后由内置静态服务托管，开发 / 桌面 / Web 三种环境同源可达。

用法：python tools/generate_demo_audio.py
"""
import math
import os
import random
import sys
import wave
from array import array
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(ROOT, "frontend", "public", "demo", "audio")
COVER_DIR = os.path.join(ROOT, "frontend", "public", "demo", "covers")

SR = 22050                 # 采样率
TABLE_BITS = 12
TABLE_SIZE = 1 << TABLE_BITS
MASK = TABLE_SIZE - 1
TABLE = [math.sin(2.0 * math.pi * i / TABLE_SIZE) for i in range(TABLE_SIZE)]

# 每种音色的谐波结构：(倍频比, 相对音量)
TIMBRES = {
    "piano": ((1, 1.0), (2, 0.30), (3, 0.13), (4, 0.06)),
    "bell":  ((1, 1.0), (2.76, 0.42), (5.40, 0.18)),
    "pad":   ((1, 1.0), (2, 0.16), (3, 0.07)),
    "pluck": ((1, 1.0), (2, 0.45), (3, 0.22), (4, 0.10)),
    "bass":  ((1, 1.0), (2, 0.24)),
    "lead":  ((1, 1.0), (3, 0.28), (5, 0.13)),
}

NOTE_INDEX = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def freq(name):
    """音名转频率，如 C4 / F#4 / Bb3，A4 = 440Hz。"""
    pitch, octave = name[:-1], int(name[-1])
    offset = 0
    if len(pitch) > 1 and pitch[1] in "#b":
        offset = 1 if pitch[1] == "#" else -1
    midi = (octave + 1) * 12 + NOTE_INDEX[pitch[0]] + offset
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def add_tone(buf, start, dur, hz, amp, timbre="piano", decay=3.2, attack=0.008):
    """把一个带 ADSR 简化包络的加法合成音符叠加进缓冲区（定点相位累加）。"""
    first = max(0, int(start * SR))
    count = int(dur * SR)
    if count <= 0 or first >= len(buf):
        return
    count = min(count, len(buf) - first)
    step_decay = math.exp(-decay / count)
    attack_n = max(1, int(attack * SR))
    for ratio, level in TIMBRES[timbre]:
        inc = int(round(hz * ratio * TABLE_SIZE / SR * 65536))
        if inc <= 0:
            continue
        phase = 0
        env = 1.0
        gain = amp * level
        base = first
        for i in range(count):
            if i < attack_n:
                amp_now = i / attack_n
            else:
                amp_now = env
                env *= step_decay
            buf[base + i] += gain * amp_now * TABLE[(phase >> 16) & MASK]
            phase = (phase + inc) & 0xFFFFFFFF


def add_kick(buf, start, amp, rng):
    """低频底鼓：短促的下行正弦 + 少量噪声。"""
    first = int(start * SR)
    count = int(0.16 * SR)
    for i in range(count):
        idx = first + i
        if idx >= len(buf):
            break
        t = i / SR
        env = math.exp(-22 * t)
        hz = 78 - 38 * min(1.0, t / 0.12)
        buf[idx] += amp * env * math.sin(2 * math.pi * hz * t)


def add_hat(buf, start, amp, rng):
    """闭合镲：短白噪声。"""
    first = int(start * SR)
    count = int(0.05 * SR)
    for i in range(count):
        idx = first + i
        if idx >= len(buf):
            break
        buf[idx] += amp * (rng.random() * 2 - 1) * math.exp(-70 * i / SR)


def build_events(track):
    """按和弦进行生成琶音、低音、铺底与旋律音符事件。"""
    events = []
    bpm = track["bpm"]
    beat = 60.0 / bpm
    step = beat / 2            # 八分音符
    chords = track["chords"]
    loops = track.get("loops", 3)
    arp = track.get("arp", (0, 1, 2, 1))
    timbre = track.get("timbre", "piano")
    melody_timbre = track.get("melody_timbre", "pluck")
    rng = random.Random(track.get("seed", 7))
    drums = []

    for loop in range(loops):
        for ci, chord in enumerate(chords):
            t0 = (loop * len(chords) + ci) * 2 * beat
            notes = [freq(n) for n in chord]

            # 低音：根音降一个八度
            events.append((t0, 2 * beat * 0.95, notes[0] / 2, 0.32, "bass", 2.0, 0.01))

            # 铺底长音（氛围类曲目更明显）
            if track.get("pad"):
                for hz in notes[:3]:
                    events.append((t0, 2 * beat, hz / 2, 0.075, "pad", 0.5, 0.25))

            # 琶音
            for j, idx in enumerate(arp):
                t = t0 + j * step
                events.append((t, step * 1.7, notes[idx % len(notes)], 0.30, timbre, 3.4, 0.006))

            # 高八度旋律（每和弦两个音）
            if track.get("melody", True):
                lead = track.get("lead", (2, 1))
                for j, idx in enumerate(lead):
                    t = t0 + (j + 0.5) * beat
                    events.append((t, beat * 0.85, notes[idx % len(notes)] * 2,
                                   0.14, melody_timbre, 4.0, 0.01))

            if track.get("drums"):
                for b in range(2):
                    drums.append(("kick" if b == 0 else "hat", t0 + b * beat, rng))
                drums.append(("hat", t0 + beat * 1.5, rng))
    return events, drums


def render(track):
    events, drums = build_events(track)
    # 按和弦进行自然收尾，留 1.2s 让最后一个音衰减，避免每首都是同样的固定长度
    beat = 60.0 / track["bpm"]
    natural = track.get("loops", 3) * len(track["chords"]) * 2 * beat + 1.2
    duration = track.get("duration") or natural
    total = int(duration * SR)
    buf = array("d", [0.0]) * total

    for start, dur, hz, amp, timbre, decay, attack in events:
        add_tone(buf, start, dur, hz, amp, timbre, decay, attack)
    for kind, start, rng in drums:
        if kind == "kick":
            add_kick(buf, start, 0.42, rng)
        else:
            add_hat(buf, start, 0.11, rng)

    # 两段短延迟叠加，做出轻微空间感
    for delay_s, wet in ((0.19, 0.16), (0.33, 0.09)):
        delay = int(delay_s * SR)
        for i in range(delay, total):
            buf[i] += buf[i - delay] * wet

    # 首尾淡入淡出，避免爆音
    fade = int(0.35 * SR)
    for i in range(fade):
        buf[i] *= i / fade
        buf[total - 1 - i] *= i / fade

    peak = max(abs(x) for x in buf) or 1.0
    scale = 0.82 / peak
    pcm = array("h", (int(max(-1.0, min(1.0, x * scale)) * 32767) for x in buf))

    path = os.path.join(AUDIO_DIR, track["id"] + ".wav")
    with wave.open(path, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SR)
        wav.writeframes(pcm.tobytes())
    return path, len(pcm) / SR


TRACKS = [
    {
        "id": "night-piano", "title": "夜航", "en": "NIGHT VOYAGE",
        "bpm": 72, "chords": [["A3", "C4", "E4"], ["F3", "A3", "C4"],
                              ["C4", "E4", "G4"], ["G3", "B3", "D4"]],
        "timbre": "piano", "melody_timbre": "piano", "pad": True,
        "arp": (0, 1, 2, 1), "lead": (2, 1), "seed": 11,
        "colors": ("#161d42", "#5a4bc4", "#a99bff"), "motif": "moon",
    },
    {
        "id": "rain-bells", "title": "雨夜钟声", "en": "RAIN & BELLS",
        "bpm": 66, "chords": [["D3", "F3", "A3"], ["B2", "D3", "F3"],
                              ["G3", "B3", "D4"], ["A3", "C4", "E4"]],
        "timbre": "bell", "melody_timbre": "bell", "pad": True,
        "arp": (0, 2, 1, 2), "lead": (2, 0), "seed": 23,
        "colors": ("#10243a", "#2b6d8f", "#8fd6e8"), "motif": "rain",
    },
    {
        "id": "morning-light", "title": "晨光练习曲", "en": "MORNING LIGHT",
        "bpm": 96, "chords": [["G3", "B3", "D4"], ["C4", "E4", "G4"],
                              ["D4", "F#4", "A4"], ["E4", "G4", "B4"]],
        "timbre": "pluck", "melody_timbre": "piano", "pad": False,
        "arp": (0, 1, 2, 1), "lead": (1, 2), "seed": 31,
        "colors": ("#f7a65a", "#ffd28a", "#fff3d0"), "motif": "sun",
    },
    {
        "id": "lofi-walk", "title": "通勤 Lo-fi", "en": "LOFI WALK",
        "bpm": 84, "chords": [["F3", "A3", "C4"], ["D3", "F3", "A3"],
                              ["G3", "B3", "D4"], ["C4", "E4", "G4"]],
        "timbre": "pluck", "melody_timbre": "lead", "pad": True, "drums": True,
        "arp": (0, 2, 1, 2), "lead": (2, 0), "seed": 47,
        "colors": ("#3a2b4d", "#8b5e83", "#ffb4a2"), "motif": "wave",
    },
    {
        "id": "starlight-box", "title": "星光八音盒", "en": "STARLIGHT BOX",
        "bpm": 108, "chords": [["A3", "C#4", "E4"], ["F#3", "A3", "C#4"],
                               ["D4", "F#4", "A4"], ["E4", "G#4", "B4"]],
        "timbre": "bell", "melody_timbre": "bell", "pad": False,
        "arp": (0, 1, 2, 1), "lead": (2, 1), "seed": 59,
        "colors": ("#1a2352", "#4740a1", "#c9c2ff"), "motif": "stars",
    },
    {
        "id": "deep-focus", "title": "深度专注", "en": "DEEP FOCUS",
        "bpm": 60, "chords": [["C3", "G3", "C4"], ["A2", "E3", "A3"],
                              ["F3", "C4", "F4"], ["G3", "D4", "G4"]],
        "timbre": "pad", "melody_timbre": "bell", "pad": True,
        "arp": (0, 1, 2, 1), "lead": (2, 0), "seed": 71,
        "colors": ("#10282b", "#1f6b64", "#7fd9bd"), "motif": "rings",
    },
    {
        "id": "city-neon", "title": "城市霓虹", "en": "CITY NEON",
        "bpm": 112, "chords": [["E3", "G3", "B3"], ["C3", "E3", "G3"],
                               ["G3", "B3", "D4"], ["D3", "F#3", "A3"]],
        "timbre": "lead", "melody_timbre": "lead", "pad": False, "drums": True,
        "arp": (0, 2, 1, 2), "lead": (1, 2), "seed": 83,
        "colors": ("#20103f", "#c13584", "#ff7bc6"), "motif": "grid",
    },
    {
        "id": "waltz-memory", "title": "回忆圆舞曲", "en": "MEMORY WALTZ",
        "bpm": 92, "chords": [["C4", "E4", "G4"], ["G3", "B3", "D4"],
                              ["A3", "C4", "E4"], ["F3", "A3", "C4"]],
        "timbre": "piano", "melody_timbre": "bell", "pad": False,
        "arp": (0, 1, 2, 1), "lead": (2, 1), "seed": 97,
        "colors": ("#4a2f47", "#a86b7c", "#f4c9b8"), "motif": "rings",
    },
]

PLAYLIST_COVERS = [
    ("playlist-night", "深夜写代码", "QUIET NIGHT", ("#20205a", "#6254d6", "#b2a8ff"), "moon"),
    ("playlist-commute", "通勤路上", "ON THE WAY", ("#123a4a", "#2e9ab0", "#9fe3e8"), "wave"),
    ("playlist-weekend", "周末慢时光", "SLOW WEEKEND", ("#7a3f2c", "#df9152", "#ffe0a8"), "sun"),
    ("playlist-lab", "纯音乐实验室", "INSTRUMENTAL LAB", ("#12332f", "#2f8f7c", "#a8e6c9"), "rings"),
]


def motif_svg(motif, accent, rng):
    """按主题生成一点抽象装饰图形。"""
    parts = []
    if motif == "moon":
        parts.append(f'<circle cx="292" cy="104" r="52" fill="{accent}" opacity=".28"/>')
        parts.append('<circle cx="272" cy="90" r="52" fill="#ffffff" opacity=".10"/>')
    elif motif == "rain":
        for i in range(11):
            x = 40 + i * 32
            y = 60 + rng.randint(0, 90)
            parts.append(f'<line x1="{x}" y1="{y}" x2="{x - 14}" y2="{y + 46}" '
                         f'stroke="{accent}" stroke-width="2" opacity=".35"/>')
    elif motif == "sun":
        parts.append(f'<circle cx="290" cy="106" r="46" fill="{accent}" opacity=".55"/>')
        for i in range(8):
            a = i * math.pi / 4
            x1, y1 = 290 + 58 * math.cos(a), 106 + 58 * math.sin(a)
            x2, y2 = 290 + 76 * math.cos(a), 106 + 76 * math.sin(a)
            parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                         f'stroke="{accent}" stroke-width="3" opacity=".55"/>')
    elif motif == "wave":
        pts = " ".join(f"{i * 10},{190 + 26 * math.sin(i / 6)}" for i in range(41))
        parts.append(f'<polyline points="{pts}" fill="none" stroke="{accent}" '
                     'stroke-width="3" opacity=".55"/>')
    elif motif == "stars":
        for _ in range(26):
            x, y = rng.randint(20, 380), rng.randint(20, 260)
            r = rng.choice((1.5, 2, 2.8))
            parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ffffff" opacity=".65"/>')
    elif motif == "rings":
        for i in range(4):
            parts.append(f'<circle cx="300" cy="130" r="{44 + i * 30}" fill="none" '
                         f'stroke="{accent}" stroke-width="2" opacity="{0.45 - i * 0.08:.2f}"/>')
    else:  # grid
        for i in range(7):
            parts.append(f'<line x1="{i * 60}" y1="0" x2="{i * 60}" y2="400" '
                         f'stroke="{accent}" stroke-width="1" opacity=".14"/>')
            parts.append(f'<line x1="0" y1="{i * 60}" x2="400" y2="{i * 60}" '
                         f'stroke="{accent}" stroke-width="1" opacity=".14"/>')
    return "\n  ".join(parts)


def cover_svg(filename, title, en, colors, motif, badge="DEMO AUDIO"):
    c1, c2, accent = colors
    rng = random.Random(sum(ord(c) for c in title))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{c1}"/>
      <stop offset="1" stop-color="{c2}"/>
    </linearGradient>
  </defs>
  <rect width="400" height="400" fill="url(#bg)"/>
  {motif_svg(motif, accent, rng)}
  <circle cx="58" cy="326" r="18" fill="none" stroke="#ffffff" stroke-width="2" opacity=".6"/>
  <circle cx="58" cy="326" r="5" fill="#ffffff" opacity=".8"/>
  <text x="58" y="292" fill="#ffffff" font-size="30" font-weight="700"
        font-family="Microsoft YaHei, PingFang SC, sans-serif">{escape(title)}</text>
  <text x="60" y="368" fill="#ffffff" opacity=".78" font-size="13" letter-spacing="2"
        font-family="Arial, sans-serif">{escape(en)}</text>
  <text x="342" y="368" fill="#ffffff" opacity=".55" font-size="10" text-anchor="end"
        font-family="Arial, sans-serif">{escape(badge)}</text>
</svg>
'''
    with open(os.path.join(COVER_DIR, filename), "w", encoding="utf-8") as fh:
        fh.write(svg)


def main():
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(COVER_DIR, exist_ok=True)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    total_bytes = 0
    for track in TRACKS:
        path, seconds = render(track)
        size = os.path.getsize(path)
        total_bytes += size
        print(f"[audio] {os.path.basename(path):<22} {seconds:5.1f}s  {size / 1024:7.0f} KB")
        cover_svg(track["id"] + ".svg", track["title"], track["en"], track["colors"], track["motif"])

    for filename, title, en, colors, motif in PLAYLIST_COVERS:
        cover_svg(filename + ".svg", title, en, colors, motif, badge="PLAYLIST")

    print(f"[done] {len(TRACKS)} 段音频 + {len(TRACKS) + len(PLAYLIST_COVERS)} 张封面，"
          f"音频合计 {total_bytes / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    main()
