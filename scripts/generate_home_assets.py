"""Generate responsive WebP assets used by the homepage.

Run from the repository root:
    python scripts/generate_home_assets.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "home"
ASSETS = {
    "growth": ROOT / "1783099763384.jpg",
    "profitability": ROOT / "Caso2.jpeg",
    "content": ROOT / "Revolution" / "New Style Images" / "61HEg-LnYyL._AC_SL1400_.jpg",
    "voc": ROOT / "creatives" / "voc-bath-mat" / "01-suction-system.jpg",
    "creative": ROOT / "EBC1.jpg",
}
TARGET_WIDTHS = (640, 1200)


def generate() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for slug, source in ASSETS.items():
        with Image.open(source) as original:
            image = ImageOps.exif_transpose(original).convert("RGB")
            for target_width in TARGET_WIDTHS:
                width = min(target_width, image.width)
                height = round(image.height * width / image.width)
                resized = image if width == image.width else image.resize((width, height), Image.Resampling.LANCZOS)
                destination = OUTPUT / f"{slug}-{width}.webp"
                resized.save(destination, "WEBP", quality=82, method=6, optimize=True)
                print(f"Generated {destination.relative_to(ROOT)} ({width}x{height})")


if __name__ == "__main__":
    generate()
