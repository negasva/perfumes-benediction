# Sistema visual, extraído del PDF

Todo lo de aquí sale de `benedictionpdf.pdf` (39 páginas, exportado desde Canva).
Nada es invención mía. Al final anoto dónde el estilo del PDF le gana a una regla
de las skills de diseño.

## 1. Paleta real

Muestreada del PDF rasterizado y de los colores de texto de los objetos de la página.

| Rol | Hex | De dónde sale |
|---|---|---|
| Fondo de página | `#EEE6D6` | fondo de las páginas 2 y 6 a 13 (portada: `#F0E4D6`) |
| Banda / filete | `#DED1C1` | la franja que va detrás de cada nombre de producto |
| Acento (único) | `#7B3F17` | color de texto dominante del PDF (`0.482 0.247 0.09`) |
| Texto principal | `#4A2A12` | versión oscurecida del mismo marrón, para contraste de lectura |
| Texto secundario | `#6B4A38` | marrón claro de los títulos (`0.553 0.38 0.318`) |
| Oliva del logo | `#392E00` | color del logotipo BÉNÉ y de los precios |

Colores que el PDF usa por sección y que **no** subí a la web, para no romper la
regla de un solo tema: rosa femenino `#FEE0DF` con banda `#EBC2C1` y texto
`#882523` (páginas 14 a 22), carbón masculino `#101010` con texto blanco
(páginas 23 a 28), gris `#EAEAE5` con banda `#DBD4CD` (páginas 29 a 39).
Siguen presentes en la web dentro de las fotos, que conservan el fondo de su
página original.

### Contraste medido (WCAG)

| Par | Ratio |
|---|---|
| texto sobre papel | 10.38:1 |
| acento sobre papel | 6.60:1 |
| texto secundario sobre papel | 6.36:1 |
| texto de botón sobre acento | 7.65:1 |
| botón desactivado | 5.26:1 |
| acento sobre filete | 5.46:1 |

Todo por encima de 4.5:1.

## 2. Tipografías

Fuentes incrustadas en el PDF, por volumen de uso:

| Fuente del PDF | Uso | Qué se usa en la web |
|---|---|---|
| Poppins Light 16pt | descripciones, cuerpo | **Poppins** (la misma, de Google Fonts, licencia OFL) |
| Neue Montreal Regular / Bold | nombres de producto y títulos | **Archivo** |
| Baskerville Display PT | precios de las páginas 31 a 34 | no se usa |
| Lora, Glacial Indifference, Times NR | apariciones sueltas | no se usan |

Poppins es literal: es la fuente del PDF y es libre, así que la web usa la misma.
Neue Montreal es comercial y en el PDF viene subconjuntada (solo trae los glifos
usados en el catálogo), así que extraerla daría una fuente rota para un buscador
donde el visitante escribe lo que quiera. Archivo es la grotesca libre más cercana
en anchura y en el corte de las terminaciones. Ambas van autoalojadas en `fonts/`
como WOFF2, sin llamadas a internet.

## 3. Tratamiento de títulos

Del PDF: peso bold, caja normal (no versalitas), interlineado muy apretado
(`Perfumes / unisex` a 75pt ocupa dos líneas pegadas), tracking ligeramente
negativo, sin sombras ni degradados. Los nombres de producto van a 27pt bold en
el mismo marrón del acento, y las descripciones a 16pt light debajo.

En la web: `line-height: 1.02` y `letter-spacing: -.02em` en h1, h2 y h3.
Las subcategorías sí van en mayúsculas con tracking abierto, copiando el
tratamiento de los rótulos pequeños del catálogo (`unisex`, `masculino`,
`femenino` en las páginas de cremas).

## 4. Textura y fondo

El fondo de cada página del PDF es un objeto imagen a página completa, con una
textura de papel muy sutil. En pantalla, a tamaño web, esa textura se pierde y
solo aporta peso, así que la web usa el color plano `#EEE6D6`. Las fotos de
producto sí conservan la textura, porque se recortaron rasterizando la página.

## 5. Marcas gráficas

- **Filete corto**: en el PDF cada nombre de producto lleva una línea horizontal
  de un par de milímetros a su izquierda o a su derecha. Es el elemento gráfico
  que más se repite en todo el catálogo. En la web es la firma: cada tarjeta
  lleva ese mismo filete antes del nombre, y los títulos de subcategoría lo
  extienden hasta el borde.
- **Banda detrás del nombre**: rectángulo relleno de `#DED1C1`, sin esquinas
  redondeadas. En la web es el fondo de la caja de foto.
- **Cero radios**: el PDF no tiene ni una esquina redondeada. La web tampoco:
  `--radio: 0` en botones, campos, chips, tarjetas y ficha.
- **Logotipo**: BÉNÉ en oliva con tracking amplio, y BÉNÉDICTION debajo mucho más
  pequeño y muy espaciado. Reconstruido con tipografía, no con imagen, porque en
  el PDF el logo es un objeto imagen y recortarlo daba un PNG con fondo crema.

## 6. Dónde el PDF le gana a las skills

Tres choques, y en los tres mandó el PDF:

1. **`design-taste-frontend` prohíbe por defecto la paleta crema con marrón
   quemado** para briefs de consumo premium, por ser el default de la IA. Pero
   crema `#EEE6D6` con marrón `#7B3F17` es literalmente la marca. Cambiarla sería
   inventar una identidad que la clienta no tiene.
2. **Las skills asumen React, Tailwind, Motion o GSAP, e imágenes de Picsum.**
   El encargo pide HTML, CSS y JS a mano, sin build ni dependencias, abriendo con
   doble clic en `file://`, y fotos reales sacadas del PDF. Manda el encargo.
3. **`ui-ux-pro-max` devolvió para "perfume beauty ecommerce" una paleta verde y
   naranja con Rubik y Nunito Sans.** Descartada entera. De esa skill me quedé
   solo con las reglas transversales: contraste 4.5:1, área táctil de 44px,
   `prefers-reduced-motion`, foco visible, sin emojis como iconos y reserva de
   alto en las imágenes.
