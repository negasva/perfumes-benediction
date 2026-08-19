"""Hojas de contacto para revisar los recortes."""
import json, random, os
from PIL import Image, ImageDraw

def sheet(items, path, cols=8, cell=170):
    rows = (len(items) + cols - 1) // cols
    im = Image.new("RGB", (cols * cell, rows * (cell + 16)), (255, 255, 255))
    d = ImageDraw.Draw(im)
    for i, (sc, p) in enumerate(items):
        x, y = (i % cols) * cell, (i // cols) * (cell + 16)
        try:
            t = Image.open(p).convert("RGB")
        except Exception:
            continue
        t.thumbnail((cell - 8, cell - 8))
        im.paste(t, (x + 4, y + 4))
        d.rectangle([x, y, x + cell - 1, y + cell + 15], outline=(200, 200, 200))
        d.text((x + 4, y + cell + 2), f"{sc:.2f} {os.path.basename(p)[:24]}", fill=(0, 0, 0))
    im.save(path)
    print(path, len(items))

sc = [tuple(x) for x in json.load(open("tools/scores.json"))]
sc.sort()
sheet(sc[:40], "tools/sheet_peores.png")
random.seed(1)
sheet(random.sample(sc, 30), "tools/sheet_azar.png")
