#!/usr/bin/env python3
"""Ottimizza in WebP le immagini generate via MCP e le carica nella Media Library WordPress.

Uso:
  export WP_URL=... WP_USER=... WP_APP_PASSWORD=...
  pip install Pillow
  python optimize_and_upload.py ./assets_raw --out ./assets_webp --max-width 1920 --quality 82

Output: media_map.json → { "hero.webp": {"id": 512, "url": "https://.../hero.webp"}, ... }
Gli id/url vanno poi iniettati nel JSON Elementor come {"url": ..., "id": ...}.
"""
import argparse, base64, json, os, sys
from pathlib import Path
import urllib.request

try:
    from PIL import Image
except ImportError:
    sys.exit("Installare Pillow: pip install Pillow")

EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def optimize(src: Path, dst_dir: Path, max_width: int, quality: int) -> Path:
    img = Image.open(src)
    if img.mode in ("RGBA", "P") and src.suffix.lower() != ".png":
        img = img.convert("RGB")
    if img.width > max_width:
        img = img.resize((max_width, int(img.height * max_width / img.width)), Image.LANCZOS)
    dst = dst_dir / (src.stem + ".webp")
    img.save(dst, "WEBP", quality=quality, method=6)
    return dst


def upload(path: Path, url: str, user: str, pwd: str) -> dict:
    data = path.read_bytes()
    req = urllib.request.Request(
        url + "/wp-json/wp/v2/media",
        data=data,
        headers={
            "Content-Type": "image/webp",
            "Content-Disposition": f'attachment; filename="{path.name}"',
            "Authorization": "Basic " + base64.b64encode(f"{user}:{pwd}".encode()).decode(),
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        j = json.load(r)
    return {"id": j["id"], "url": j["source_url"]}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("src_dir")
    p.add_argument("--out", default="./assets_webp")
    p.add_argument("--max-width", type=int, default=1920)
    p.add_argument("--quality", type=int, default=82)
    p.add_argument("--skip-upload", action="store_true", help="solo ottimizzazione (Canale C)")
    args = p.parse_args()

    src_dir, out_dir = Path(args.src_dir), Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    wp_url = os.environ.get("WP_URL", "").rstrip("/")
    user, pwd = os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASSWORD", "")
    if not args.skip_upload and not (wp_url and user and pwd):
        sys.exit("Definire WP_URL, WP_USER, WP_APP_PASSWORD (o usare --skip-upload).")

    media_map = {}
    for src in sorted(src_dir.iterdir()):
        if src.suffix.lower() not in EXTS:
            continue
        webp = optimize(src, out_dir, args.max_width, args.quality)
        print(f"🖼  {src.name} → {webp.name} ({webp.stat().st_size // 1024} KB)")
        if not args.skip_upload:
            info = upload(webp, wp_url, user, pwd)
            media_map[webp.name] = info
            print(f"   ⬆  id={info['id']}  {info['url']}")

    map_file = out_dir / "media_map.json"
    map_file.write_text(json.dumps(media_map, indent=2, ensure_ascii=False))
    print(f"\n✅ Mappa media salvata in {map_file}")


if __name__ == "__main__":
    main()
