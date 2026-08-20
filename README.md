# Catálogo Bénédiction

Web estática del catálogo de perfumes Bénédiction. HTML, CSS y JavaScript a mano.
Sin frameworks, sin build, sin dependencias y sin llamadas a internet.

## Cómo abrirlo

Doble clic en `index.html`. Funciona en `file://`, sin servidor, también desde
una memoria USB.

## Qué hay dentro

```
index.html    la página
styles.css    los estilos
app.js        el contacto, los precios y la lógica
data.js       la lista de productos, una línea por producto
img/          las fotos, en WebP
fonts/        Poppins y Archivo, autoalojadas
DESIGN.md     de dónde sale cada color y cada tipografía
tools/        los scripts que sacaron todo del PDF
```

## Cambiar el WhatsApp y los datos de contacto

Abre `app.js`. Arriba de todo está esto:

```js
const CONTACTO = {
  whatsapp: "",     // ej. "573001112233"
  telefono: "",
  correo: "",
  instagram: "",    // ej. "@bene.perfumes"
  sitio: "",
};
```

Escribe el número de WhatsApp entre las comillas, en formato internacional, sin
espacios, sin signos y sin el `+`. Para Colombia: `57` y luego el número.
Ejemplo: `whatsapp: "573001112233"`.

Mientras esté vacío, el botón "Pedir por WhatsApp" aparece desactivado. En cuanto
pongas el número, se activa solo en las 145 fichas, con el mensaje ya escrito.

Los demás campos son opcionales y aparecen en el pie de página.

## Cambiar los precios

También en `app.js`, justo debajo del contacto:

```js
const PRECIOS = {
  perfume: [["30 ml", "$45.000"], ["100 ml", "$100.000"]],
  crema:   [["Crema", "$30.000"]],
  ...
};
```

Cada línea es una lista de presentaciones. Cambia solo lo que está entre
comillas. Si un producto se vende en un tamaño nuevo, agrega un par más:

```js
perfume: [["30 ml", "$45.000"], ["50 ml", "$70.000"], ["100 ml", "$100.000"]],
```

Cambiar un precio aquí lo cambia en toda la web de una vez.

## Agregar, cambiar o quitar productos

Abre `data.js`. Cada producto es una línea:

```js
{ id: "perfumes-unisex-addiction", nombre: "Addiction", desc: "Inspirada en Lattafa Emeer", categoria: "Perfumes unisex", subcategoria: "", etiquetas: [], precio: "perfume", img: "img/perfumes-unisex-addiction.webp" },
```

- **Agregar**: copia una línea entera, pégala debajo y cambia los textos. El `id`
  tiene que ser distinto al de todas las demás.
- **Quitar**: borra la línea completa, desde la llave `{` hasta la coma final.
- **Cambiar**: edita solo lo que está entre comillas.

Qué es cada campo:

| Campo | Para qué sirve |
|---|---|
| `id` | nombre interno, único, sin espacios ni tildes |
| `nombre` | lo que se ve grande en la tarjeta |
| `desc` | la línea de abajo, la inspiración o las notas |
| `categoria` | crea un bloque en la página y un filtro |
| `subcategoria` | subtítulo dentro del bloque, puede ir vacío `""` |
| `etiquetas` | lista de palabras sueltas, por ejemplo `["femenino"]` |
| `precio` | cuál de las listas de `PRECIOS` usa este producto |
| `img` | ruta de la foto dentro de `img/` |

Para la foto: guarda el archivo dentro de `img/`, en formato WebP o JPG, cuadrado
o vertical, con el lado mayor de unos 340 píxeles, y pon su nombre en el campo
`img`.

Después de guardar, recarga la página en el navegador. No hay que compilar nada.

## Publicar en GitHub Pages

1. Sube la carpeta a un repositorio de GitHub.
2. En el repositorio, entra a **Settings**, y en el menú lateral a **Pages**.
3. En **Source** elige **Deploy from a branch**.
4. En **Branch** elige `main` y la carpeta `/ (root)`. Guarda.
5. Espera un par de minutos. La dirección aparece en esa misma pantalla, con la
   forma `https://TUUSUARIO.github.io/NOMBRE-DEL-REPO/`.

El archivo `.nojekyll` ya está incluido para que GitHub no procese la carpeta y
publique los archivos tal cual.

## Volver a generar todo desde el PDF

Solo si cambia el catálogo original. Necesita Python con `pdfplumber` y `Pillow`.

```bash
python3 tools/extract.py      # saca textos y recorta las fotos a img/
python3 tools/sheets.py       # hojas de contacto para revisar los recortes
python3 tools/build_data.py   # reescribe data.js
```

`tools/extract.py` sobrescribe `img/` y `tools/products.json`.
`tools/build_data.py` sobrescribe `data.js`, así que si editaste productos a mano,
haz una copia antes.

## Cambiar las fotos por las de los frascos originales

Las fichas muestran el frasco del perfume en el que está inspirada cada
fragancia. Esas fotos salen de una carpeta de recortes numerados (WebP con
fondo transparente):

```bash
python3 tools/fotos_nuevas.py CARPETA_DE_RECORTES
```

Dentro de `tools/fotos_nuevas.py`, el diccionario `MAPA` dice qué recorte le
toca a cada producto: a la izquierda el `id` del producto, a la derecha el
número del archivo. Para cambiar una foto, cambia el número. Para agregar una,
escribe una línea nueva. Los productos que no están en `MAPA` conservan la foto
que ya tienen: son la creación propia, las cremas, los splash, los sets, y las
fragancias cuyo frasco original no estaba entre los recortes.
