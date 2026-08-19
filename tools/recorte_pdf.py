"""Centra los recortes que salieron del PDF (cremas, splash, duos y sets).

No son fotos sueltas sino trozos de pagina del catalogo: traen franjas de la
maqueta y restos de texto alrededor del producto, asi que el encuadre va a
mano. Las cajas estan en fracciones del recorte original (x0, y0, x1, y1).
Despues se centra en un cuadrado del color de fondo de la propia imagen.

Se pasa una sola vez sobre los recortes originales: las cajas son fracciones de
esos recortes, asi que volver a correrlo sobre el resultado lo estropea.
"""
from PIL import Image
import os, sys
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DIR = os.path.join(RAIZ, 'img')
SALIDA = sys.argv[1] if len(sys.argv) > 1 else DIR
LADO = 760
MARGEN = 0.07

CAJAS = {
  'bene-kids.webp':                                                  (0,    0,    1,    .97),
  'cremas-y-splash-cremas-charming.webp':                            (.28,  0,    .65,  1),
  'cremas-y-splash-cremas-dolce-estate.webp':                        (.60,  .06,  .95,  1),
  'cremas-y-splash-cremas-sparkling.webp':                           (.43,  0,    .98,  1),
  'cremas-y-splash-splash-charming.webp':                            (.26,  .02,  .65,  1),
  'cremas-y-splash-splash-dolce-estate.webp':                        (.53,  0,    .98,  1),
  'cremas-y-splash-splash-sparkling.webp':                           (.53,  0,    .98,  1),
  'descuentos-o-sets-especiales-duo-crema-y-splash-charming.webp':    (.38,  .06,  1,    1),
  'descuentos-o-sets-especiales-duo-crema-y-splash-dolce-estate.webp':(.42,  .26,  1,    1),
  'descuentos-o-sets-especiales-duo-crema-y-splash-sparkling.webp':   (.28,  .24,  1,    1),
  'lleva-las-3.webp':                                                (0,    0,    1,    1),
  'set-de-descubrimiento.webp':                                      (.26,  0,    1,    .30),
  'set-de-regalo.webp':                                              (0,    0,    1,    .30),
}

for nombre, (fx0, fy0, fx1, fy1) in CAJAS.items():
    ruta = os.path.join(DIR, nombre)
    im = Image.open(ruta).convert('RGB')
    w, h = im.size
    rec = im.crop((round(fx0 * w), round(fy0 * h), round(fx1 * w), round(fy1 * h)))
    chico = rec.resize((60, 60))
    bg = Counter(chico.getdata()).most_common(1)[0][0]
    lado = int(max(rec.size) * (1 + 2 * MARGEN))
    lienzo = Image.new('RGB', (lado, lado), bg)
    lienzo.paste(rec, ((lado - rec.width) // 2, (lado - rec.height) // 2))
    lienzo.resize((LADO, LADO), Image.LANCZOS).save(
        os.path.join(SALIDA, nombre), 'WEBP', quality=84, method=4)
    print('%-64s %s -> %s' % (nombre, (w, h), rec.size))
