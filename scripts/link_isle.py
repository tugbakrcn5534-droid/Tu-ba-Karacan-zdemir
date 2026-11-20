#!/usr/bin/env python3
"""Bir video linkini (Instagram, TikTok, YouTube...) Claude'un okuyabileceği hale getirir.

Çıktı: linkler/<klasör>/
  README.md     -> açıklama metni (caption), hesap, süre, konuşma dökümü
  kareler.jpg   -> videodan alınmış karelerin tek görselde özeti
  kare_XX.jpg   -> tek tek kareler
  bilgi.json    -> ham bilgiler
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
CIKTI_KOK = KOK / "linkler"
MAKS_KARE = 12


def calistir(komut, **kw):
    print("+", " ".join(map(str, komut)), flush=True)
    return subprocess.run(komut, check=True, **kw)


def klasor_adi(bilgi, url):
    tarih = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    kimlik = bilgi.get("id") or re.sub(r"\W+", "-", url)[-20:]
    site = (bilgi.get("extractor_key") or "link").lower()
    return f"{tarih}_{site}_{kimlik}"


def indir(url, gecici):
    gecici.mkdir(parents=True, exist_ok=True)
    komut = [
        "yt-dlp", "--no-playlist", "--write-info-json",
        "-f", "mp4/bestvideo*+bestaudio/best",
        "--merge-output-format", "mp4",
        "-o", str(gecici / "video.%(ext)s"),
    ]
    cerez = os.environ.get("COOKIES_FILE")
    if cerez and Path(cerez).is_file() and Path(cerez).stat().st_size > 0:
        komut += ["--cookies", cerez]
    calistir(komut + [url])
    video = next(gecici.glob("video.*[!json]"))
    bilgi = json.loads(next(gecici.glob("*.info.json")).read_text())
    return video, bilgi


def kareler(video, hedef, sure):
    sure = max(float(sure or 0), 1.0)
    adet = min(MAKS_KARE, max(4, int(sure // 3)))
    for i in range(adet):
        t = sure * (i + 0.5) / adet
        calistir(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{t:.2f}", "-i", str(video),
                  "-frames:v", "1", "-vf", "scale=540:-2", str(hedef / f"kare_{i+1:02d}.jpg")])
    sutun = 4
    satir = (adet + sutun - 1) // sutun
    calistir(["ffmpeg", "-loglevel", "error", "-y", "-framerate", "1",
              "-i", str(hedef / "kare_%02d.jpg"),
              "-vf", f"scale=360:-2,tile={sutun}x{satir}:padding=6:color=white",
              "-frames:v", "1", str(hedef / "kareler.jpg")])
    return adet


def dokum(video):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return "_(faster-whisper kurulu değil, döküm atlandı)_", None
    model = WhisperModel(os.environ.get("WHISPER_MODEL", "small"), device="cpu", compute_type="int8")
    parcalar, info = model.transcribe(str(video), vad_filter=True)
    satirlar = [f"[{p.start:05.1f}s] {p.text.strip()}" for p in parcalar]
    return ("\n".join(satirlar) or "_(konuşma bulunamadı)_"), info.language


def main():
    if len(sys.argv) < 2:
        sys.exit("Kullanım: link_isle.py <url>")
    url = sys.argv[1].strip()
    gecici = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "link_isle"
    video, bilgi = indir(url, gecici)

    hedef = CIKTI_KOK / klasor_adi(bilgi, url)
    hedef.mkdir(parents=True, exist_ok=True)
    sure = bilgi.get("duration")
    kare_sayisi = kareler(video, hedef, sure)
    metin, dil = dokum(video)

    ozet = {k: bilgi.get(k) for k in (
        "id", "title", "description", "uploader", "uploader_id", "channel", "duration",
        "upload_date", "like_count", "comment_count", "view_count", "webpage_url", "tags")}
    ozet["kaynak_link"] = url
    ozet["dil"] = dil
    (hedef / "bilgi.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=2))

    readme = f"""# {bilgi.get('title') or 'Video'}

- **Link:** {url}
- **Hesap:** {bilgi.get('uploader') or bilgi.get('channel') or '-'} ({bilgi.get('uploader_id') or '-'})
- **Süre:** {sure or '-'} sn · **Dil:** {dil or '-'}
- **Beğeni / yorum / izlenme:** {bilgi.get('like_count')} / {bilgi.get('comment_count')} / {bilgi.get('view_count')}

## Açıklama metni

{bilgi.get('description') or '_(yok)_'}

## Konuşma dökümü

```
{metin}
```

## Kareler ({kare_sayisi} adet)

![kareler](kareler.jpg)
"""
    (hedef / "README.md").write_text(readme)
    print(f"TAMAM: {hedef.relative_to(KOK)}")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"klasor={hedef.relative_to(KOK)}\n")


if __name__ == "__main__":
    main()
