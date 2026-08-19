"""Extrae productos + fotos del catalogo PDF. Uso: python3 tools/extract.py"""
import json, os, re, unicodedata
import pdfplumber
from PIL import Image, ImageDraw, ImageChops

PDF = "benedictionpdf.pdf"
OUT_IMG = "img"
DPI = 150
K = DPI / 72.0
MAXSIDE = 340
QUALITY = 78

# paginas -> (categoria, subcategoria)
PERFUME_PAGES = {}
for n in range(6, 14):  PERFUME_PAGES[n] = ("Perfumes unisex", "")
for n in range(14, 23): PERFUME_PAGES[n] = ("Perfumes femeninos", "")
for n in range(23, 29): PERFUME_PAGES[n] = ("Perfumes masculinos", "")
PERFUME_PAGES[4] = ("Perfumes unisex", "Creación propia")
PERFUME_PAGES[5] = ("Perfumes unisex", "Creación propia")
CREMA_PAGES = {29: ("Cremas y splash", "Cremas"), 30: ("Cremas y splash", "Splash"),
               33: ("Descuentos o sets especiales", "Duo crema y splash")}

def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")

def dedupe_doubles(t):
    """Canva exporta glifos duplicados: 'CCaattaalloogg' -> 'Catalogo'."""
    if len(t) < 4 or len(t) % 2:
        return t
    if all(t[i] == t[i + 1] for i in range(0, len(t), 2)):
        return t[::2]
    return t

def lines(words, key=lambda w: True, tol=6, mid=None):
    """Agrupa palabras en lineas por 'top'. Con mid, no cruza la mitad de la pagina."""
    ws = sorted([w for w in words if key(w)],
                key=lambda w: ((0 if mid and w["x0"] < mid else 1), w["top"], w["x0"]))
    out = []
    for w in ws:
        same_side = mid is None or ((out[-1][1][0]["x0"] < mid) == (w["x0"] < mid)) if out else True
        if out and same_side and abs(w["top"] - out[-1][0]) <= tol:
            out[-1][1].append(w)
        else:
            out.append([w["top"], [w]])
    return [(t, " ".join(dedupe_doubles(x["text"]) for x in sorted(g, key=lambda x: x["x0"])),
             min(x["x0"] for x in g), max(x["x1"] for x in g), max(x["bottom"] for x in g))
            for t, g in out]

def page_bg(im):
    """Color de fondo = color mas frecuente de la pagina."""
    small = im.resize((120, 170))
    return max(set(small.getdata()), key=list(small.getdata()).count)

def local_bg(im, x0, y0, x1, y1, fallback):
    """Color justo al lado del texto: los filetes de fondo no son planos."""
    cy = int((y0 + y1) / 2)
    for x in (int(x0) - 8, int(x1) + 8, int(x0) - 16, int(x1) + 16):
        if 0 <= x < im.width and 0 <= cy < im.height:
            return im.getpixel((x, cy))
    return fallback

def masked_render(page):
    """Rasteriza a 150dpi y tapa texto y filetes con el color de fondo."""
    im = page.to_image(resolution=DPI).original.convert("RGB")
    bg = page_bg(im)
    d = ImageDraw.Draw(im)
    for w in page.extract_words():
        x0, y0 = w["x0"] * K - 4, w["top"] * K - 4
        x1, y1 = w["x1"] * K + 4, w["bottom"] * K + 4
        d.rectangle([x0, y0, x1, y1], fill=local_bg(im, x0, y0, x1, y1, bg))
    return im, bg

def product_images(page):
    """Imagenes de producto: descarta el fondo a pagina completa."""
    area = page.width * page.height
    return [im for im in page.images
            if (im["x1"] - im["x0"]) * (im["bottom"] - im["top"]) < 0.55 * area]

def trim(im, bg, tol=42):
    """Recorta al contenido real (todo lo que se aleja del fondo)."""
    diff = ImageChops.difference(im, Image.new("RGB", im.size, bg)).convert("L")
    bbox = diff.point(lambda v: 255 if v > tol else 0).getbbox()
    return bbox

def save_crop(im, bg, box, name):
    x0, y0, x1, y1 = [int(v) for v in box]
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(im.width, x1), min(im.height, y1)
    if x1 - x0 < 20 or y1 - y0 < 20:
        return None, 0.0
    sub = im.crop((x0, y0, x1, y1))
    bb = trim(sub, bg)
    if bb:
        pad = 10
        sub = sub.crop((max(0, bb[0] - pad), max(0, bb[1] - pad),
                        min(sub.width, bb[2] + pad), min(sub.height, bb[3] + pad)))
    if min(sub.size) < 20:
        return None, 0.0
    sub.thumbnail((MAXSIDE, MAXSIDE), Image.LANCZOS)
    path = f"{OUT_IMG}/{name}.webp"
    sub.save(path, "WEBP", quality=QUALITY, method=6)
    return path, score(sub)

def score(im):
    """Fraccion de pixeles brillantes + fraccion de pixeles saturados."""
    px = list(im.convert("RGB").getdata())
    n = len(px)
    bright = sum(1 for r, g, b in px if (r + g + b) / 3 > 235)
    sat = sum(1 for r, g, b in px if max(r, g, b) - min(r, g, b) > 40)
    return round(bright / n + sat / n, 4)

def nearest_row(cy, rows):
    return min(range(len(rows)), key=lambda i: abs(cy - rows[i]))

def extract_perfume_page(page, pno, cat, sub, products, scores):
    W = page.width
    mid = W / 2
    words = page.extract_words(extra_attrs=["size"])
    body = [w for w in words if w["size"] < 45]
    names = lines(body, lambda w: w["size"] >= 20, mid=mid)
    descs = lines(body, lambda w: w["size"] < 20, mid=mid)
    if not names:
        return

    # agrupa lineas de nombre contiguas en un solo nombre
    cells = []
    for t, txt, x0, x1, bot in names:
        side = 0 if (x0 + x1) / 2 < mid else 1
        if cells and cells[-1]["side"] == side and t - cells[-1]["bottom"] < 14:
            cells[-1]["name"] += " " + txt
            cells[-1]["bottom"] = bot
        else:
            cells.append({"side": side, "top": t, "bottom": bot, "name": txt,
                          "x0": x0, "x1": x1})
    for c in cells:
        c["cy"] = (c["top"] + c["bottom"]) / 2

    # descripcion = lineas pequenas del mismo lado, justo debajo del nombre
    for c in cells:
        d = [txt for t, txt, x0, x1, bot in descs
             if (0 if (x0 + x1) / 2 < mid else 1) == c["side"] and 0 <= t - c["bottom"] < 90]
        c["desc"] = re.sub(r"\s+", " ", " ".join(d)).strip()

    rows = sorted({round(c["cy"] / 40) * 40 for c in cells})
    im, bg = masked_render(page)

    imgs = product_images(page)
    for im_ in imgs:
        im_["_row"] = nearest_row((im_["top"] + im_["bottom"]) / 2, rows)
        im_["_side"] = 0 if (im_["x0"] + im_["x1"]) / 2 < mid else 1

    span = (rows[-1] - rows[0]) / max(1, len(rows) - 1) if len(rows) > 1 else 220
    for c in cells:
        ri = nearest_row(c["cy"], rows)
        mine = [i for i in imgs if i["_row"] == ri and i["_side"] == c["side"]]
        if mine:
            # la union se limita a la banda de la fila y a su media columna,
            # si no entran los vecinos de arriba, abajo y al lado
            # el frasco arranca justo encima de su nombre: por arriba se corta
            # apretado, si no entra la fila anterior
            lo, hi = c["top"] - 45, c["top"] + 0.72 * span
            xlo, xhi = (0, mid + 40) if c["side"] == 0 else (mid - 40, W)
            box = (max(xlo, min(i["x0"] for i in mine)) * K,
                   max(lo, min(i["top"] for i in mine)) * K,
                   min(xhi, max(i["x1"] for i in mine)) * K,
                   min(hi, max(i["bottom"] for i in mine)) * K)
        else:
            # sin foto propia: caja mediana de la fila, desplazada a su columna
            row_imgs = [i for i in imgs if i["_row"] == ri] or imgs
            w_ = sorted((i["x1"] - i["x0"]) for i in row_imgs)[len(row_imgs) // 2]
            h_ = sorted((i["bottom"] - i["top"]) for i in row_imgs)[len(row_imgs) // 2]
            cx = mid / 2 if c["side"] == 0 else mid * 1.5
            box = ((cx - w_ / 2) * K, (c["cy"] - h_ / 2) * K, (cx + w_ / 2) * K, (c["cy"] + h_ / 2) * K)
        s = slug(f"{cat}-{c['name']}")
        path, sc = save_crop(im, bg, box, s)
        products.append({"nombre": c["name"], "desc": c["desc"], "cat": cat, "sub": sub,
                         "img": path, "pag": pno})
        if path:
            scores.append((sc, path))

def extract_hero_page(page, pno, products, scores):
    """Paginas 4 y 5: una creacion propia por pagina, titulo a pagina completa."""
    ws = page.extract_words(extra_attrs=["size"])
    big = max(w["size"] for w in ws)
    name = " ".join(dedupe_doubles(w["text"]) for w in sorted(
        [w for w in ws if w["size"] > big - 12], key=lambda w: (round(w["top"] / 10), w["x0"])))
    rest = lines([w for w in ws if w["size"] <= big - 12])
    skip = {"CREACION", "PROPIA"}
    notas = [" ".join(x for x in dedupe_doubles(txt).split()
                      if unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode().upper() not in skip)
             for _, txt, x0, _, _ in rest]
    desc = re.sub(r"\s+", " ", " ".join(notas)).strip().title()
    cat, sub = PERFUME_PAGES[pno]
    im, bg = masked_render(page)
    ims = product_images(page) or page.images
    box = (min(i["x0"] for i in ims) * K, min(i["top"] for i in ims) * K,
           max(i["x1"] for i in ims) * K, max(i["bottom"] for i in ims) * K)
    path, sc = save_crop(im, bg, box, slug(name))
    products.append({"nombre": name, "desc": desc, "cat": cat, "sub": sub, "img": path, "pag": pno})
    if path:
        scores.append((sc, path))

def extract_crema_page(page, pno, cat, sub, products, scores):
    W, mid = page.width, page.width / 2
    words = page.extract_words(extra_attrs=["size"])
    body = [w for w in words if w["size"] < 45 and w["top"] > 150]
    names = lines(body, lambda w: 24 <= w["size"] < 45)
    descs = lines(body, lambda w: w["size"] < 24)
    cells = []
    for t, txt, x0, x1, bot in names:
        if txt.startswith("$"):
            continue
        if cells and t - cells[-1]["bottom"] < 16 and abs(x0 - cells[-1]["x0"]) < 60:
            cells[-1]["name"] += " " + txt
            cells[-1]["bottom"] = bot
        else:
            cells.append({"top": t, "bottom": bot, "name": txt, "x0": x0, "x1": x1})
    im, bg = masked_render(page)
    used = set()
    for c in cells:
        d = [(txt, t) for t, txt, x0, x1, bot in descs if 0 <= t - c["bottom"] < 90]
        c["desc"] = re.sub(r"\s+", " ", " ".join(x for x, _ in d[:3])).strip()
        genero = next((x for x, _ in d if x.lower() in ("unisex", "masculino", "femenino")), "")
        c["desc"] = c["desc"].replace(genero, "").strip()
        cy = (c["top"] + c["bottom"]) / 2
        pool = [i for i in product_images(page) if id(i) not in used]
        if pool:
            i = min(pool, key=lambda i: abs((i["top"] + i["bottom"]) / 2 - cy))
            used.add(id(i))
            box = (i["x0"] * K, i["top"] * K, i["x1"] * K, i["bottom"] * K)
        else:
            box = (0, (c["top"] - 130) * K, W * K, (c["bottom"] + 190) * K)
        s = slug(f"{cat}-{sub}-{c['name']}")
        path, sc = save_crop(im, bg, box, s)
        products.append({"nombre": c["name"], "desc": c["desc"], "cat": cat, "sub": sub,
                         "genero": genero, "img": path, "pag": pno})
        if path:
            scores.append((sc, path))

def full_page_crop(page, name, products, scores, entry, ybox=None):
    im, bg = masked_render(page)
    ims = product_images(page)
    if ims:
        box = (min(i["x0"] for i in ims) * K, min(i["top"] for i in ims) * K,
               max(i["x1"] for i in ims) * K, max(i["bottom"] for i in ims) * K)
    else:
        h = page.height
        y0, y1 = ybox if ybox else (0.12, 0.92)
        box = (0, y0 * h * K, page.width * K, y1 * h * K)
    path, sc = save_crop(im, bg, box, slug(name))
    entry["img"] = path
    products.append(entry)
    if path:
        scores.append((sc, path))

def save_page_bg(pdf):
    """El fondo de pagina es un objeto imagen a pagina completa: se extrae limpio."""
    for pno in (6, 23):
        page = pdf.pages[pno - 1]
        area = page.width * page.height
        big = [i for i in page.images
               if (i["x1"] - i["x0"]) * (i["bottom"] - i["top"]) > 0.85 * area]
        if not big:
            continue
        im = page.to_image(resolution=96).original.convert("RGB")
        im.save(f"{OUT_IMG}/fondo-{'claro' if pno == 6 else 'oscuro'}.webp", "WEBP", quality=70)

def main():
    os.makedirs(OUT_IMG, exist_ok=True)
    pdf = pdfplumber.open(PDF)
    products, scores = [], []

    for pno in (4, 5):
        extract_hero_page(pdf.pages[pno - 1], pno, products, scores)
    for pno in sorted(PERFUME_PAGES):
        if pno in (4, 5):
            continue
        cat, sub = PERFUME_PAGES[pno]
        extract_perfume_page(pdf.pages[pno - 1], pno, cat, sub, products, scores)
    for pno in sorted(CREMA_PAGES):
        cat, sub = CREMA_PAGES[pno]
        extract_crema_page(pdf.pages[pno - 1], pno, cat, sub, products, scores)

    full_page_crop(pdf.pages[30], "set-de-descubrimiento", products, scores,
                   {"nombre": "Set de descubrimiento", "cat": "Set de descubrimiento", "sub": "",
                    "desc": "Experimenta con nuestro set decants x5 unidades y disfruta de una amplia "
                            "variedad de perfumes en tamaño x10ml en rollón. Elige tus 5 referencias "
                            "diferentes y escríbenos para darnos tu selección.",
                    "pag": 31}, (0.30, 0.86))
    for nm, yb in [("Béné kids - Niña", None), ("Béné kids - Niño", None), ("Béné kids - Bebé", None)]:
        pass
    full_page_crop(pdf.pages[31], "bene-kids", products, scores,
                   {"nombre": "Béné kids", "cat": "Béné kids - Línea infantil", "sub": "",
                    "desc": "Perfume x50ml + muñeco llavero. Niña, Niño y Bebé. "
                            "Pide mas diseños de muñecos.", "pag": 32}, (0.20, 0.82))
    full_page_crop(pdf.pages[33], "set-de-regalo", products, scores,
                   {"nombre": "Set de regalo", "cat": "Descuentos o sets especiales", "sub": "",
                    "desc": "Perfume x30ml, Crema x120ml, Splash x140ml. 3 Aromas diferentes.",
                    "pag": 34}, (0.12, 0.95))
    full_page_crop(pdf.pages[34], "lleva-las-3", products, scores,
                   {"nombre": "Lleva las 3", "cat": "Descuentos o sets especiales", "sub": "",
                    "desc": "Precio normal $135,000. Lleva las 3 x $110,000. "
                            "Precio disponible solo para las referencias seleccionadas.",
                    "pag": 35}, (0.25, 0.94))

    # dedupe por nombre+cat+sub
    seen, clean = set(), []
    for p in products:
        k = (slug(p["nombre"]), p["cat"], p["sub"])
        if k in seen:
            continue
        seen.add(k)
        clean.append(p)

    save_page_bg(pdf)
    json.dump(clean, open("tools/products.json", "w"), ensure_ascii=False, indent=1)
    json.dump(sorted(scores), open("tools/scores.json", "w"), indent=1)
    print("productos:", len(clean), "sin foto:", sum(1 for p in clean if not p["img"]))

if __name__ == "__main__":
    main()
