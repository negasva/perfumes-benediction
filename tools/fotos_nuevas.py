"""Cambia las fotos del catalogo por los recortes de los frascos originales.

Cada producto de Benediction esta inspirado en un perfume de marca. Este script
reemplaza la foto de la ficha por el recorte del frasco original, que viene con
el fondo ya recortado (PNG/WebP con transparencia).

MAPA relaciona el id del producto con el numero del recorte. Los productos que
no aparecen aqui se quedan con su foto actual: o son creacion propia, o son
cremas, splash y sets, o no habia un recorte del frasco original.

Uso: python3 tools/fotos_nuevas.py CARPETA_DE_RECORTES

El encuadre es el mismo de tools/recorte_fotos.py: se recorta el aire
transparente, se centra en un cuadrado y se guarda a 760 px.
"""
from PIL import Image
import os, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(RAIZ, 'img')
LADO = 760
MARGEN = 0.06

MAPA = {
    "perfumes-unisex-addiction": "66",
    "perfumes-unisex-cheval": "204",
    "perfumes-unisex-cosmos": "20",
    "perfumes-unisex-cazzi": "251",
    "perfumes-unisex-cioccolate": "317",
    "perfumes-unisex-crimson-elixir": "306",
    "perfumes-unisex-dukhan": "41",
    "perfumes-unisex-femme": "288",
    "perfumes-unisex-galax": "252",
    "perfumes-unisex-etoile": "215",
    "perfumes-unisex-fruto-silvestre": "299",
    "perfumes-unisex-gold-dust": "441",
    "perfumes-unisex-khaneli": "265",
    "perfumes-unisex-heaven": "274",
    "perfumes-unisex-kafic": "213",
    "perfumes-unisex-khora": "235",
    "perfumes-unisex-king": "234",
    "perfumes-unisex-legacy": "242",
    "perfumes-unisex-litmus": "371",
    "perfumes-unisex-kirkja": "250",
    "perfumes-unisex-legado": "413",
    "perfumes-unisex-luxo": "298",
    "perfumes-unisex-lychee": "51",
    "perfumes-unisex-nubit": "301",
    "perfumes-unisex-magnus": "229",
    "perfumes-unisex-origen": "440",
    "perfumes-unisex-orion": "254",
    "perfumes-unisex-purple": "50",
    "perfumes-unisex-rush": "310",
    "perfumes-unisex-passion": "237",
    "perfumes-unisex-sadje": "65",
    "perfumes-unisex-sparkling": "78",
    "perfumes-unisex-summer-intense": "323",
    "perfumes-unisex-white-star": "223",
    "perfumes-unisex-star": "231",
    "perfumes-unisex-yuzu": "06",
    "perfumes-unisex-costiera-solar": "71",
    "perfumes-unisex-costiera": "344",
    "perfumes-femeninos-afrodita": "60",
    "perfumes-femeninos-beautiful-girl": "174",
    "perfumes-femeninos-bouquete": "175",
    "perfumes-femeninos-candied-lemond": "165",
    "perfumes-femeninos-dania": "46",
    "perfumes-femeninos-coqueiro": "188",
    "perfumes-femeninos-dania-doux": "47",
    "perfumes-femeninos-diva": "385",
    "perfumes-femeninos-dolce-estate": "192",
    "perfumes-femeninos-eden": "266",
    "perfumes-femeninos-dolce-caramella": "366",
    "perfumes-femeninos-dolce-orchidea": "191",
    "perfumes-femeninos-exclusif": "150",
    "perfumes-femeninos-exquisite": "302",
    "perfumes-femeninos-fresh-spring": "160",
    "perfumes-femeninos-incanto": "446",
    "perfumes-femeninos-floral-bomb": "390",
    "perfumes-femeninos-goddes": "170",
    "perfumes-femeninos-lovely-red": "374",
    "perfumes-femeninos-le-fruit": "42",
    "perfumes-femeninos-magnetia": "155",
    "perfumes-femeninos-neige-vainilla": "49",
    "perfumes-femeninos-passaro": "389",
    "perfumes-femeninos-oud-rose": "363",
    "perfumes-femeninos-pilvi": "187",
    "perfumes-femeninos-pink-kiss": "224",
    "perfumes-femeninos-precious": "162",
    "perfumes-femeninos-rose": "199",
    "perfumes-femeninos-plenitud": "161",
    "perfumes-femeninos-santorini": "166",
    "perfumes-femeninos-sexy-girl": "153",
    "perfumes-femeninos-sophistique": "182",
    "perfumes-femeninos-suklaa": "152",
    "perfumes-femeninos-soberana": "179",
    "perfumes-femeninos-summer-lady": "167",
    "perfumes-femeninos-sunny-sky": "43",
    "perfumes-femeninos-tuki": "63",
    "perfumes-femeninos-sweet-pistacho": "361",
    "perfumes-masculinos-alpha": "394",
    "perfumes-masculinos-aquila": "194",
    "perfumes-masculinos-boise": "332",
    "perfumes-masculinos-aqua-fresh": "87",
    "perfumes-masculinos-beast": "258",
    "perfumes-masculinos-cavalo": "196",
    "perfumes-masculinos-charming": "103",
    "perfumes-masculinos-citrus-king": "312",
    "perfumes-masculinos-elisium": "131",
    "perfumes-masculinos-choklad": "96",
    "perfumes-masculinos-eclipse": "271",
    "perfumes-masculinos-elixir": "81",
    "perfumes-masculinos-khalil": "195",
    "perfumes-masculinos-fresh-vibration": "364",
    "perfumes-masculinos-heros": "126",
    "perfumes-masculinos-signore": "272",
    "perfumes-masculinos-skote": "108",
    "perfumes-masculinos-rasha": "40",
    "perfumes-masculinos-sillage": "257",
    "perfumes-masculinos-the-secret": "228",
    "perfumes-masculinos-uomo": "142",
    "perfumes-masculinos-verz": "119",
    "perfumes-masculinos-uomo-intense": "141",
    "perfumes-masculinos-verz-plus": "117",
    "perfumes-masculinos-you-intense": "90",
}


def encuadra(im):
    caja = im.getchannel('A').getbbox()
    rec = im.crop(caja) if caja else im
    lado = int(max(rec.size) * (1 + 2 * MARGEN))
    lienzo = Image.new('RGBA', (lado, lado), (0, 0, 0, 0))
    lienzo.paste(rec, ((lado - rec.width) // 2, (lado - rec.height) // 2))
    return lienzo.resize((LADO, LADO), Image.LANCZOS)


def main():
    if len(sys.argv) < 2:
        sys.exit('uso: python3 tools/fotos_nuevas.py CARPETA_DE_RECORTES')
    origen = sys.argv[1]
    hechas = faltan = 0
    for pid, numero in sorted(MAPA.items()):
        entrada = os.path.join(origen, numero + '.webp')
        if not os.path.exists(entrada):
            print('falta el recorte', entrada)
            faltan += 1
            continue
        im = Image.open(entrada).convert('RGBA')
        encuadra(im).save(os.path.join(DIR, pid + '.webp'), 'WEBP',
                          quality=82, method=6)
        hechas += 1
    print('fotos cambiadas: %d   sin recorte: %d' % (hechas, faltan))


if __name__ == '__main__':
    main()
