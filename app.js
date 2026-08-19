/* =====================================================================
   CONTACTO Y PRECIOS. Esto es lo unico que se toca para actualizar la web.
   ===================================================================== */

// Contacto. Pon el numero de WhatsApp en formato internacional y sin signos:
// por ejemplo "573001112233". Si se deja vacio, el boton de WhatsApp queda
// desactivado en toda la pagina.
const CONTACTO = {
  whatsapp: "",     // ej. "573001112233"
  telefono: "",
  correo: "",
  instagram: "",    // ej. "@bene.perfumes"
  sitio: "",
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

// Orden de las lineas en la portada y en la rejilla.
const ORDEN = ["Creación propia", "Perfumes unisex", "Perfumes femeninos",
  "Perfumes masculinos", "Cremas y splash", "Set de descubrimiento",
  "Béné kids - Línea infantil", "Descuentos o sets especiales"];

const $ = (s, r = document) => r.querySelector(s);
const norm = (s) => (s || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
const precioCorto = (k) => (PRECIOS[k] || [])[0]?.[1] || "";

const estado = { q: "", cats: new Set(), subs: new Set() };

const rejilla = $("#rejilla");
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
function pintaLineas(cont, valores, set) {
  cont.replaceChildren(...valores.map((v) => {
    const n = cuenta("categoria", v);
    const b = document.createElement("button");
    b.type = "button";
    b.className = "linea";
    b.dataset.tema = tema(v);
    b.setAttribute("aria-pressed", String(set.has(v)));
    b.innerHTML = `<span class="linea__n">${v}</span>` +
      `<span class="linea__c">${n} ${n === 1 ? "referencia" : "referencias"}</span>`;
    b.addEventListener("click", () => {
      set.has(v) ? set.delete(v) : set.add(v);
      render();
    });
    return b;
  }));
}

function pintaChips(cont, valores, set, clave) {
  cont.replaceChildren(...valores.map((v) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "chip";
    b.setAttribute("aria-pressed", String(set.has(v)));
    b.innerHTML = `${v}<span class="chip__n">${cuenta(clave, v)}</span>`;
    b.addEventListener("click", () => {
      set.has(v) ? set.delete(v) : set.add(v);
      render();
    });
    return b;
  }));
}

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
  pintaLineas($("#fCat"), cats, estado.cats);
  pintaChips($("#fSub"), subs, estado.subs, "subcategoria");

  $("#conteo").textContent = lista.length === 1
    ? "1 referencia en el catálogo"
    : `${lista.length} referencias en el catálogo`;
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
$("#pieContacto").textContent = [
  CONTACTO.whatsapp && `WhatsApp ${CONTACTO.whatsapp}`,
  CONTACTO.telefono, CONTACTO.correo, CONTACTO.instagram, CONTACTO.sitio,
].filter(Boolean).join(" · ") ||
  "Los datos de contacto no aparecen en el catálogo. Se cargan en app.js.";

leerURL();
$("#q").value = estado.q;
render();
