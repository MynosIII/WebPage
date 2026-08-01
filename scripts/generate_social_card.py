"""Generate the deterministic 1200×630 social preview used by page metadata."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 1200, 630


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(Path("C:/Windows/Fonts") / name, size)


canvas = Image.new("RGB", (WIDTH, HEIGHT), "#121212")
draw = ImageDraw.Draw(canvas)

for y in range(HEIGHT):
    progress = y / HEIGHT
    draw.line((0, y, WIDTH, y), fill=(18, 18 + int(8 * progress), 18 + int(14 * progress)))

draw.rounded_rectangle((70, 65, 1130, 565), radius=28, fill="#191d20", outline="#00e0ff", width=3)
draw.rectangle((70, 65, 88, 565), fill="#00e0ff")
draw.text((135, 125), "MATÍAS GAGLIO", font=font("arialbd.ttf", 82), fill="#ffffff")
draw.text((140, 235), "Ecommerce · Analytics · Creative strategy", font=font("arial.ttf", 37), fill="#a9b1b7")
draw.line((140, 330, 1055, 330), fill="#344047", width=2)
draw.text((140, 380), "Data translated into decisions and visuals that convert.", font=font("arial.ttf", 32), fill="#e0e0e0")
draw.text((140, 480), "matiasgaglio.onrender.com", font=font("arialbd.ttf", 24), fill="#00e0ff")

canvas.save(ROOT / "og-card.png", optimize=True)
print("Generated og-card.png")
