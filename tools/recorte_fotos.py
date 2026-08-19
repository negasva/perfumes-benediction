"""Recorta el aire transparente de cada foto y la deja centrada en un lienzo
cuadrado. Las fotos vienen con el producto pegado a la derecha y mucho vacio a
la izquierda, asi que en la tarjeta se veian pequenas y descuadradas.

El lado del cuadrado se calcula sobre el lado mayor del recorte. Como todas las
fotos traen el frasco a la misma altura (~1200 px), todos los productos quedan
a la misma escala en la rejilla.
"""
from PIL import Image
import os, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DIR = os.path.join(RAIZ, 'img')
LADO = 760          # lado final en px
MARGEN = 0.06       # aire alrededor del producto, sobre el lado mayor

tocadas = antes = despues = 0
for nombre in sorted(os.listdir(DIR)):
    ruta = os.path.join(DIR, nombre)
    im = Image.open(ruta)
    if im.mode != 'RGBA':        # los recortes del PDF son opacos: no se tocan
        continue
    caja = im.getchannel('A').getbbox()
    if not caja:
        continue
    rec = im.crop(caja)
    lado = int(max(rec.size) * (1 + 2 * MARGEN))
    lienzo = Image.new('RGBA', (lado, lado), (0, 0, 0, 0))
    lienzo.paste(rec, ((lado - rec.width) // 2, (lado - rec.height) // 2))
    lienzo = lienzo.resize((LADO, LADO), Image.LANCZOS)
    antes += os.path.getsize(ruta)
    lienzo.save(ruta, 'WEBP', quality=82, method=6)
    despues += os.path.getsize(ruta)
    tocadas += 1

print(f'fotos recortadas: {tocadas}')
print(f'peso: {antes//1024} KB -> {despues//1024} KB')
