"""Genera data.js a partir de tools/products.json."""
import json, re, unicodedata

def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")

def precio_key(p):
    if p["nombre"] == "Set de regalo":
        return "regalo"
    if p["nombre"] == "Lleva las 3":
        return "trio"
    if p["cat"].startswith("Perfumes"):
        return "perfume"
    return {"Cremas": "crema", "Splash": "splash", "Duo crema y splash": "duo"}.get(
        p["sub"], {"Set de descubrimiento": "set5"}.get(p["cat"], "kids"))

def limpia(t):
    t = re.sub(r"^I?I?n?Inspirad", "Inspirad", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t[0].upper() + t[1:] if t else t

rows = []
for p in json.load(open("tools/products.json")):
    nombre = p["nombre"][0].upper() + p["nombre"][1:]
    rows.append({
        "id": slug(f'{p["cat"]}-{p["sub"]}-{nombre}'),
        "nombre": nombre,
        "desc": limpia(p.get("desc", "")),
        "categoria": p["cat"],
        "subcategoria": p["sub"] or (p.get("genero", "") and ""),
        "etiquetas": [x for x in [p.get("genero", "")] if x],
        "precio": precio_key(p),
        "img": p["img"] or "",
    })

def js(r):
    return ("  { id: %s, nombre: %s, desc: %s, categoria: %s, subcategoria: %s, "
            "etiquetas: %s, precio: %s, img: %s }," % tuple(
                json.dumps(r[k], ensure_ascii=False)
                for k in ("id", "nombre", "desc", "categoria", "subcategoria",
                          "etiquetas", "precio", "img")))

with open("data.js", "w", encoding="utf-8") as f:
    f.write("""// Catalogo Bénédiction. Una linea por producto.
// Para agregar un producto: copia una linea, cambia los textos y pon el nombre
// del archivo de la foto dentro de la carpeta img/.
// Los precios NO van aqui: el campo "precio" apunta a una lista que esta
// arriba de app.js (PRECIOS). Ahi se cambian los valores.

const PRODUCTOS = [
""")
    for r in rows:
        f.write(js(r) + "\n")
    f.write("];\n")
print("data.js:", len(rows), "productos")
