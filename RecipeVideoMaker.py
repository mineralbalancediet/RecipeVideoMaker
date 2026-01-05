# RecipeVideoMaker.py
# Minimal + stable (single folder, one line = one image)
# Supports 27 languages via --lang:
# ar bn zh nl en fr de el hi id it ja jv ko ms mr pl pt ru es sv ta te th tr ur vi
#
# Usage:
#   python RecipeVideoMaker.py
#   python RecipeVideoMaker.py --lang zh
#
# Folder:
#   RecipeVideoMaker.py
#   script.txt
#   1.png,2.png,3.png... (or jpg/webp)
#   ffmpeg.exe, ffprobe.exe (or in PATH)
#
# Output:
#   output.mp4 (in current folder)
# Temp files:
#   stored in system temp folder, auto-cleaned at end.

import os, re, json, time, shutil, asyncio, argparse, subprocess, tempfile
from pathlib import Path

SCRIPT_FILE = "script.txt"
OUTPUT_FILE = "output.mp4"

FPS = 30
WIDTH = 1080
HEIGHT = 1920
BACKGROUND = "black"

FFMPEG = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
FFPROBE = "ffprobe.exe" if os.name == "nt" else "ffprobe"

RATE = "+0%"
VOLUME = "+0%"
RETRIES = 2

LANGS_27 = [
    "ar","bn","zh","nl","en","fr","de","el","hi","id","it","ja","jv","ko","ms","mr",
    "pl","pt","ru","es","sv","ta","te","th","tr","ur","vi"
]

VOICE_BY_LANG = {
    "ar":"ar-EG-SalmaNeural",
    "bn":"bn-IN-TanishaaNeural",
    "zh":"zh-CN-XiaoxiaoNeural",
    "nl":"nl-NL-FennaNeural",
    "en":"en-US-JennyNeural",
    "fr":"fr-FR-DeniseNeural",
    "de":"de-DE-KatjaNeural",
    "el":"el-GR-AthinaNeural",
    "hi":"hi-IN-SwaraNeural",
    "id":"id-ID-GadisNeural",
    "it":"it-IT-ElsaNeural",
    "ja":"ja-JP-NanamiNeural",
    "jv":"jv-ID-SitiNeural",
    "ko":"ko-KR-SunHiNeural",
    "ms":"ms-MY-YasminNeural",
    "mr":"mr-IN-AarohiNeural",
    "pl":"pl-PL-AgnieszkaNeural",
    "pt":"pt-BR-FranciscaNeural",
    "ru":"ru-RU-SvetlanaNeural",
    "es":"es-ES-ElviraNeural",
    "sv":"sv-SE-SofieNeural",
    "ta":"ta-IN-PallaviNeural",
    "te":"te-IN-ShrutiNeural",
    "th":"th-TH-PremwadeeNeural",
    "tr":"tr-TR-EmelNeural",
    "ur":"ur-PK-UzmaNeural",
    "vi":"vi-VN-HoaiMyNeural",
}

LOCALE_BY_LANG = {
    "ar":["ar-EG","ar-SA","ar-AE"],
    "bn":["bn-IN","bn-BD"],
    "zh":["zh-CN","zh-TW","zh-HK"],
    "nl":["nl-NL","nl-BE"],
    "en":["en-US","en-GB","en-AU","en-CA"],
    "fr":["fr-FR","fr-CA"],
    "de":["de-DE","de-AT","de-CH"],
    "el":["el-GR"],
    "hi":["hi-IN"],
    "id":["id-ID"],
    "it":["it-IT"],
    "ja":["ja-JP"],
    "jv":["jv-ID"],
    "ko":["ko-KR"],
    "ms":["ms-MY"],
    "mr":["mr-IN"],
    "pl":["pl-PL"],
    "pt":["pt-BR","pt-PT"],
    "ru":["ru-RU"],
    "es":["es-ES","es-MX","es-US"],
    "sv":["sv-SE"],
    "ta":["ta-IN"],
    "te":["te-IN"],
    "th":["th-TH"],
    "tr":["tr-TR"],
    "ur":["ur-PK","ur-IN"],
    "vi":["vi-VN"],
}

def die(msg: str):
    print("\n[ERROR]", msg)
    raise SystemExit(1)

def run(cmd, check=True):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                       encoding="utf-8", errors="ignore")
    if check and p.returncode != 0:
        print("\n[COMMAND FAILED]\n" + " ".join(cmd))
        print("\n[STDERR]\n" + p.stderr.strip())
        die("ffmpeg/ffprobe failed")
    return p

def find_tool(name: str) -> str:
    local = Path(__file__).resolve().parent / name
    if local.exists():
        return str(local)
    path = shutil.which(name)
    if path:
        return path
    die(f"{name} not found. Put it in this folder OR add to PATH.")

def read_script(path: Path):
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            out.append(s)
    return out

def sanitize(s: str) -> str:
    s = s.replace("\ufeff", "")
    s = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", " ", s)
    s = s.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def list_images(folder: Path):
    exts = (".png", ".jpg", ".jpeg", ".webp")
    imgs = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in exts]
    def key(p: Path):
        m = re.search(r"(\d+)", p.stem)
        return int(m.group(1)) if m else 10**9
    imgs.sort(key=key)
    return imgs

def audio_dur(ffprobe: str, audio: Path) -> float:
    p = run([ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "json", str(audio)])
    return max(float(json.loads(p.stdout)["format"]["duration"]), 0.1)

async def tts_save(text: str, out_mp3: Path, voice: str):
    import edge_tts
    await edge_tts.Communicate(text=text, voice=voice, rate=RATE, volume=VOLUME).save(str(out_mp3))

async def pick_fallback(lang: str):
    try:
        import edge_tts
        voices = await edge_tts.list_voices()
    except Exception:
        return None
    for loc in LOCALE_BY_LANG.get(lang, []):
        for v in voices:
            if v.get("Locale") == loc and v.get("ShortName"):
                return v["ShortName"]
    for loc in LOCALE_BY_LANG.get(lang, []):
        for v in voices:
            if str(v.get("Locale","")).startswith(loc) and v.get("ShortName"):
                return v["ShortName"]
    return None

def img_to_mp4(ffmpeg: str, img: Path, duration: float, out_mp4: Path):
    dur = duration + 0.10
    vf = (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
        f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:{BACKGROUND},"
        f"format=yuv420p"
    )
    run([ffmpeg, "-y", "-loop", "1", "-t", f"{dur:.3f}", "-i", str(img),
         "-r", str(FPS), "-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", str(out_mp4)])

def mux(ffmpeg: str, vid: Path, aud: Path, out: Path):
    run([ffmpeg, "-y", "-i", str(vid), "-i", str(aud),
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-shortest", "-movflags", "+faststart", str(out)])

def concat(ffmpeg: str, segments, out: Path):
    lst = out.parent / "concat_list.txt"
    with lst.open("w", encoding="utf-8") as f:
        for s in segments:
            f.write(f"file '{s.as_posix()}'\n")
    run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-c", "copy", "-movflags", "+faststart", str(out)])
    try: lst.unlink()
    except: pass

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="en", choices=LANGS_27)
    args = ap.parse_args()

    base = Path(__file__).resolve().parent
    ffmpeg = find_tool(FFMPEG)
    ffprobe = find_tool(FFPROBE)

    script = base / SCRIPT_FILE
    if not script.exists():
        die("Missing script.txt")

    lines = [sanitize(x) for x in read_script(script)]
    if not lines:
        die("script.txt has no usable lines")

    images = list_images(base)
    if not images:
        die("No images found (1.png,2.png,...)")

    n = min(len(lines), len(images))
    if len(lines) != len(images):
        print(f"[WARN] Lines={len(lines)} Images={len(images)} => using first {n} pairs.\n")

    voice = VOICE_BY_LANG.get(args.lang, "en-US-JennyNeural")
    fallback = asyncio.run(pick_fallback(args.lang))
    voices = [voice] + ([fallback] if fallback and fallback != voice else [])

    failed = base / "tts_failed.txt"
    if failed.exists():
        failed.unlink()

    # temp dir: hidden from user (system temp)
    temp_dir = Path(tempfile.mkdtemp(prefix="RecipeVideoMaker_"))

    print("======================================")
    print("RecipeVideoMaker (minimal)")
    print("Lang  :", args.lang)
    print("Voice :", voice)
    if fallback and fallback != voice:
        print("Fallback:", fallback)
    print("Using :", n, "pairs")
    print("Output:", OUTPUT_FILE)
    print("======================================\n")

    t0 = time.time()
    segments = []

    try:
        for i in range(n):
            text = lines[i]
            img = images[i]

            mp3 = temp_dir / f"{i+1:03d}.mp3"
            imgmp4 = temp_dir / f"{i+1:03d}_img.mp4"
            seg = temp_dir / f"{i+1:03d}_seg.mp4"

            print(f"[{i+1:02d}/{n:02d}] TTS -> {mp3.name}")

            ok = False
            last = ""
            for v in voices:
                for attempt in range(RETRIES + 1):
                    try:
                        asyncio.run(tts_save(text, mp3, v))
                        if v != voice:
                            print(f"         [INFO] using fallback voice: {v}")
                        ok = True
                        break
                    except Exception as e:
                        last = f"{type(e).__name__}: {e}"
                        time.sleep(0.6 + attempt * 0.8)
                if ok:
                    break

            if not ok:
                with failed.open("a", encoding="utf-8") as f:
                    f.write(f"Line {i+1}: {text}\nError: {last}\n\n")
                print("         [WARN] TTS failed, logged to tts_failed.txt, skipping.\n")
                continue

            dur = audio_dur(ffprobe, mp3)
            print(f"         audio duration: {dur:.2f}s")
            print(f"         image -> video track ({img.name})")
            img_to_mp4(ffmpeg, img, dur, imgmp4)
            print("         mux audio + video")
            mux(ffmpeg, imgmp4, mp3, seg)
            segments.append(seg)
            print("")

        if not segments:
            die("All lines failed TTS. Check tts_failed.txt")

        out = base / OUTPUT_FILE
        if out.exists():
            out.unlink()

        print("[FINAL] concat segments ->", out.name)
        concat(ffmpeg, segments, out)

        print("\nDONE ✅")
        print("Created:", out)
        print(f"Time: {time.time()-t0:.1f}s")
        if failed.exists():
            print("Note: some lines failed TTS. See tts_failed.txt")

    finally:
        # clean temp folder to avoid confusing users
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    main()
