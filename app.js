/* =====================================================================
   CONTACTO Y PRECIOS. Esto es lo unico que se toca para actualizar la web.
   ===================================================================== */

// Contacto. Pon el numero de WhatsApp en formato internacional y sin signos:
// por ejemplo "573001112233". Si se deja vacio, el boton de WhatsApp queda
// desactivado en toda la pagina.
const CONTACTO = {
  whatsapp: "573178608303",     // ej. "573001112233"
  whatsapp2: "573013624187",
  telefono: "",
  correo: "",
  instagram: "",    // ej. "@bene.perfumes"
  sitio: "",
  direccion: "Cra 80 # 13a-261, CC Aquarela local A11 · junto al Éxito, Cali",
  horario: "Lunes a sábado, 10:00 a. m. – 7:00 p. m.",
};

// Precios tomados del catalogo. Cada producto apunta a una de estas listas
// por su campo "precio" en data.js.
const PRECIOS = {
  perfume: [["30 ml", "$45.000"], ["100 ml", "$100.000"]],
  crema:   [["Crema", "$30.000"]],
  splash:  [["Splash", "$30.000"]],
  duo:     [["Crema + splash", "$50.000"]],
  set5:    [["5 decants x 10 ml", "$65.000"]],
  kids:    [["Perfume 50 ml + muñeco llavero", "$65.000"]],
  regalo:  [["Perfume 30 ml + crema 120 ml + splash 140 ml", "$90.000"]],
  trio:    [["3 referencias seleccionadas", "$110.000"], ["Precio normal", "$135.000"]],
};

// Aviso legal, copiado del catalogo.
const LEGAL = "Precio disponible solo para las referencias seleccionadas. " +
  "Las marcas mencionadas en las descripciones son propiedad de sus respectivos " +
  "titulares y se citan unicamente como referencia olfativa. Bénédiction no está " +
  "afiliada a ellas.";

/* =====================================================================
   De aqui para abajo no hace falta tocar nada.
   ===================================================================== */

// Cada linea del catalogo repinta su franja con los colores de esa seccion
// en el PDF. Los nombres coinciden con los bloques [data-tema] de styles.css.
const TEMAS = {
  "Creación propia": "creacion",
  "Perfumes unisex": "unisex",
  "Perfumes femeninos": "femeninos",
  "Perfumes masculinos": "masculinos",
};
const tema = (cat) => TEMAS[cat] || "cuidado";

// Un icono de trazo por linea y por chip, dibujado con el color del texto.
// La clave es el texto exacto que se muestra; si no esta, no se pinta icono.
const ICONOS = {
  "Todos": '<path d="M4 7h16M4 12h16M4 17h16"/>',
  "Creación propia": '<path d="M12 3.5 13.9 9l5.6 1.9-5.6 1.9L12 18.3 10.1 12.8 4.5 10.9 10.1 9z"/>',
  "Perfumes unisex": '<circle cx="9" cy="12" r="5.2"/><circle cx="15" cy="12" r="5.2"/>',
  "Perfumes femeninos": '<circle cx="12" cy="9.6" r="4.6"/><path d="M12 14.2v6.3M9.2 17.7h5.6"/>',
  "Perfumes masculinos": '<circle cx="10.2" cy="13.8" r="4.6"/><path d="M13.9 10.1 19.5 4.5M15.4 4.5h4.1v4.1"/>',
  "Cremas y splash": '<path d="M12 3.4c0 0 5.8 6.4 5.8 10.1a5.8 5.8 0 0 1-11.6 0C6.2 9.8 12 3.4 12 3.4z"/>',
  "Cremas": '<path d="M8 9.5h8v10.5H8zM9.8 9.5V6.4h4.4v3.1M10.4 4h3.2"/>',
  "Splash": '<path d="M12 3.4c0 0 5.8 6.4 5.8 10.1a5.8 5.8 0 0 1-11.6 0C6.2 9.8 12 3.4 12 3.4z"/>',
  "Duo crema y splash": '<path d="M3.5 10h6v10h-6zM4.9 10V7.2h3.2V10M14.5 10h6v10h-6zM15.9 10V7.2h3.2V10"/>',
  "Set de descubrimiento": '<path d="M4.5 9h4v11h-4zM10 9h4v11h-4zM15.5 9h4v11h-4zM5.6 9V6.4h1.8V9M11.1 9V6.4h1.8V9M16.6 9V6.4h1.8V9"/>',
  "Béné kids - Línea infantil": '<path d="M3.6 19a8.4 8.4 0 0 1 16.8 0M7.1 19a4.9 4.9 0 0 1 9.8 0M10.6 19a1.4 1.4 0 0 1 2.8 0"/>',
  "Descuentos o sets especiales": '<path d="M3.6 12.6 12.6 3.6h7.8v7.8l-9 9z"/><circle cx="16.6" cy="7.4" r="1.5"/>',
};
const icono = (clave) => ICONOS[clave]
  ? `<svg class="ico" viewBox="0 0 24 24" aria-hidden="true">${ICONOS[clave]}</svg>`
  : "";

// Los tres generos van arriba, en botones grandes. El resto queda debajo en
// botones pequenos.
const GENEROS = ["Perfumes unisex", "Perfumes femeninos", "Perfumes masculinos"];

// Orden de las lineas en la portada y en la rejilla.
const ORDEN = [...GENEROS, "Creación propia", "Cremas y splash",
  "Set de descubrimiento", "Béné kids - Línea infantil",
  "Descuentos o sets especiales"];

const $ = (s, r = document) => r.querySelector(s);
const norm = (s) => (s || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
const precioCorto = (k) => (PRECIOS[k] || [])[0]?.[1] || "";

const estado = { q: "", cats: new Set(), subs: new Set() };

const rejilla = $("#rejilla");
// Al elegir una linea la pagina baja al catalogo.
const irAlCatalogo = () => rejilla.scrollIntoView({ behavior: "smooth", block: "start" });
const vacio = $("#vacio");
const ficha = $("#ficha");
let ultimoFoco = null;

/* --- URL: los filtros viajan en el enlace para poder compartirlos ------ */
function leerURL() {
  const p = new URLSearchParams(location.search);
  estado.q = p.get("q") || "";
  estado.cats = new Set((p.get("cat") || "").split("|").filter(Boolean));
  estado.subs = new Set((p.get("sub") || "").split("|").filter(Boolean));
}
function escribirURL() {
  const p = new URLSearchParams();
  if (estado.q) p.set("q", estado.q);
  if (estado.cats.size) p.set("cat", [...estado.cats].join("|"));
  if (estado.subs.size) p.set("sub", [...estado.subs].join("|"));
  const s = p.toString();
  history.replaceState(null, "", s ? "?" + s : location.pathname);
}

/* --- Filtrado --------------------------------------------------------- */
function filtrar() {
  const q = norm(estado.q);
  return PRODUCTOS.filter((p) => {
    if (estado.cats.size && !estado.cats.has(p.categoria)) return false;
    if (estado.subs.size && !estado.subs.has(p.subcategoria)) return false;
    if (!q) return true;
    return norm(p.nombre + " " + p.desc).includes(q);
  });
}

/* --- Chips ------------------------------------------------------------ */
function cuenta(clave, valor) {
  return PRODUCTOS.filter((p) => p[clave] === valor).length;
}
// Los botones ya no llevan color propio: heredan el tema activo de la pagina,
// asi que todos se ven iguales. Al pulsar uno, la pagina entera se repinta con
// el color de esa linea. La seleccion es unica: elegir una suelta la anterior.
function pintaLineas(cont, valores, set, clase = "") {
  cont.replaceChildren(...valores.map((v) => {
    const n = cuenta("categoria", v);
    const b = document.createElement("button");
    b.type = "button";
    b.className = "linea" + (clase ? " " + clase : "");
    b.setAttribute("aria-pressed", String(set.has(v)));
    b.innerHTML = icono(v) +
      `<span class="linea__txt">` +
      `<span class="linea__n">${v}</span>` +
      `<span class="linea__c">${n} ${n === 1 ? "referencia" : "referencias"}</span>` +
      `</span>`;
    b.addEventListener("click", () => {
      const activo = set.has(v);
      set.clear();
      if (!activo) set.add(v);
      render();
      if (!activo) irAlCatalogo();
    });
    return b;
  }));
}

function chip(texto, marcado, n, alPulsar) {
  const b = document.createElement("button");
  b.type = "button";
  b.className = "chip";
  b.setAttribute("aria-pressed", String(marcado));
  b.innerHTML = icono(texto) + `<span class="chip__t">${texto}</span>` +
    (n == null ? "" : `<span class="chip__n">${n}</span>`);
  b.addEventListener("click", alPulsar);
  return b;
}

function pintaChips(cont, valores, set, clave) {
  const todos = chip("Todos", set.size === 0, PRODUCTOS.length, () => {
    set.clear();
    render();
  });
  cont.replaceChildren(todos, ...valores.map((v) =>
    chip(v, set.has(v), cuenta(clave, v), () => {
      set.has(v) ? set.delete(v) : set.add(v);
      render();
    })));
}

/* --- Menu desplegable -------------------------------------------------- */
// El panel es un <details> nativo: abre y cierra sin JS. Aqui solo se pintan
// los enlaces (uno por linea) y se aplica el filtro sin recargar.
function pintaMenu(cats) {
  const irA = (v) => {
    estado.cats.clear();
    if (v) estado.cats.add(v);
    $("#menu").open = false;
    render();
    irAlCatalogo();
  };
  const enlace = (texto, valor) => {
    const a = document.createElement("a");
    a.className = "menu__a";
    a.href = valor ? "?cat=" + encodeURIComponent(valor) : "?";
    a.setAttribute("aria-current", String(valor ? estado.cats.has(valor)
      : estado.cats.size === 0));
    a.innerHTML = icono(valor || "Todos") + `<span>${texto}</span>`;
    a.addEventListener("click", (e) => { e.preventDefault(); irA(valor); });
    return a;
  };
  $("#menuNav").replaceChildren(
    enlace("Ver todo el catálogo", null),
    ...cats.map((c) => enlace(c, c)));
}

// Clic fuera: cierra el panel.
document.addEventListener("click", (e) => {
  const m = $("#menu");
  if (m?.open && !m.contains(e.target)) m.open = false;
});

/* --- Rejilla ---------------------------------------------------------- */
function tarjeta(p) {
  const li = document.createElement("li");
  const b = document.createElement("button");
  b.type = "button";
  b.className = "tarjeta";
  b.innerHTML = `
    <span class="tarjeta__foto">
      <img src="${p.img}" alt="Producto Bénédiction ${p.nombre}"
           width="340" height="340" loading="lazy" decoding="async">
    </span>
    <span class="tarjeta__texto">
      <span class="tarjeta__n">${p.nombre}</span>
      ${p.desc ? `<span class="tarjeta__d">${p.desc}</span>` : ""}
      <span class="tarjeta__p">${precioCorto(p.precio)}</span>
    </span>`;
  b.addEventListener("click", () => abrirFicha(p, b));
  li.append(b);
  return li;
}

function render() {
  const lista = filtrar();
  const presentes = new Set(PRODUCTOS.map((p) => p.categoria));
  const cats = ORDEN.filter((c) => presentes.has(c))
    .concat([...presentes].filter((c) => !ORDEN.includes(c)));
  const subs = [...new Set(PRODUCTOS.map((p) => p.subcategoria).filter(Boolean))];
  pintaLineas($("#fGen"), cats.filter((c) => GENEROS.includes(c)),
    estado.cats, "linea--gen");
  pintaLineas($("#fCat"), cats.filter((c) => !GENEROS.includes(c)), estado.cats);
  pintaChips($("#fSub"), subs, estado.subs, "subcategoria");
  pintaMenu(cats);

  // La linea elegida repinta toda la pagina con sus colores.
  const activa = [...estado.cats][0];
  if (activa) document.body.dataset.tema = tema(activa);
  else document.body.removeAttribute("data-tema");

  $("#conteo").innerHTML = `<b>${lista.length}</b> ` +
    (lista.length === 1 ? "referencia" : "referencias");
  $("#qx").hidden = !estado.q;
  vacio.hidden = lista.length > 0;

  const frag = document.createDocumentFragment();
  for (const cat of cats) {
    const enCat = lista.filter((p) => p.categoria === cat);
    if (!enCat.length) continue;
    const sec = document.createElement("section");
    sec.className = "seccion";
    sec.dataset.tema = tema(cat);
    const caja = document.createElement("div");
    caja.className = "seccion__inner";
    caja.innerHTML = `<h2 class="seccion__t">${cat}</h2><hr class="seccion__linea">`;
    const grupos = [...new Set(enCat.map((p) => p.subcategoria))];
    for (const sub of grupos) {
      if (sub) {
        const h = document.createElement("h3");
        h.className = "sub__t";
        h.textContent = sub;
        caja.append(h);
      }
      const ul = document.createElement("ul");
      ul.className = "tarjetas";
      ul.append(...enCat.filter((p) => p.subcategoria === sub).map(tarjeta));
      caja.append(ul);
    }
    sec.append(caja);
    frag.append(sec);
  }
  rejilla.replaceChildren(frag);
  escribirURL();
}

/* --- Ficha ------------------------------------------------------------ */
function abrirFicha(p, origen) {
  ultimoFoco = origen;
  ficha.dataset.tema = tema(p.categoria);
  $("#fichaImg").src = p.img;
  $("#fichaImg").alt = `Producto Bénédiction ${p.nombre}`;
  $("#fichaRuta").textContent = [p.categoria, p.subcategoria].filter(Boolean).join(" · ");
  $("#fichaNombre").textContent = p.nombre;
  $("#fichaDesc").textContent = p.desc;
  $("#fichaDesc").hidden = !p.desc;
  $("#fichaEtiquetas").replaceChildren(...p.etiquetas.map((t) => {
    const li = document.createElement("li");
    li.textContent = t;
    return li;
  }));
  $("#fichaPrecios").replaceChildren(...(PRECIOS[p.precio] || []).map(([n, v]) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<th scope="row">${n}</th><td>${v}</td>`;
    return tr;
  }));

  const wa = $("#fichaWa");
  const nota = $("#fichaWaNota");
  if (CONTACTO.whatsapp) {
    const msg = `Hola, quiero pedir ${p.nombre} (${p.categoria}) del catálogo Bénédiction.`;
    wa.href = `https://wa.me/${CONTACTO.whatsapp}?text=${encodeURIComponent(msg)}`;
    wa.removeAttribute("aria-disabled");
    wa.removeAttribute("tabindex");
    nota.hidden = true;
  } else {
    wa.href = "#";
    wa.setAttribute("aria-disabled", "true");
    wa.setAttribute("tabindex", "-1");
    nota.hidden = false;
    nota.textContent = "El catálogo no trae número de contacto. Agrega el WhatsApp en app.js para activar el botón.";
  }
  ficha.showModal();
  $(".ficha__x").focus();
}

ficha.addEventListener("click", (e) => {
  // clic fuera del contenido: el backdrop es el propio <dialog>
  if (e.target === ficha) ficha.close();
  if (e.target.closest("[data-cerrar]")) ficha.close();
  if (e.target.closest('[aria-disabled="true"]')) e.preventDefault();
});
ficha.addEventListener("close", () => ultimoFoco?.focus());

/* --- Arranque --------------------------------------------------------- */
$("#q").addEventListener("input", (e) => { estado.q = e.target.value; render(); });
$("#qx").addEventListener("click", () => {
  estado.q = "";
  $("#q").value = "";
  render();
  $("#q").focus();
});
$("#limpiar").addEventListener("click", limpiar);
vacio.querySelector("[data-limpiar]").addEventListener("click", limpiar);

function limpiar() {
  estado.q = "";
  estado.cats.clear();
  estado.subs.clear();
  $("#q").value = "";
  render();
  $("#q").focus();
}

$("#portadaPrecio").textContent =
  `Perfume 30 ml ${PRECIOS.perfume[0][1]} · 100 ml ${PRECIOS.perfume[1][1]}`;
$("#pieLegal").textContent = LEGAL;
$("#pieDir").textContent = CONTACTO.direccion;
$("#pieHorario").textContent = CONTACTO.horario;

// Un enlace wa.me por numero; se muestra en formato local para leerlo facil.
const local = (n) => n.replace(/^57/, "").replace(/(\d{3})(\d{3})(\d{4})/, "$1 $2 $3");
$("#pieContacto").replaceChildren(...[CONTACTO.whatsapp, CONTACTO.whatsapp2]
  .filter(Boolean).map((n) => {
    const a = document.createElement("a");
    a.className = "pie__wa";
    a.href = `https://wa.me/${n}`;
    a.rel = "noopener";
    a.target = "_blank";
    a.textContent = `WhatsApp ${local(n)}`;
    return a;
  }));

leerURL();
$("#q").value = estado.q;
render();
