/* ============================================================
   password.js — El "ojito" para ver la contraseña que se escribe

   Recorre la pagina y le pone un boton de mostrar/ocultar a TODOS los
   campos de contraseña: el modal del gato (entrar, registrarse, la
   contraseña nueva de la recuperacion) y el formulario de alta de
   personal del panel.

   Se hace aqui, en un solo sitio, y no campo por campo en cada plantilla,
   por dos razones:
     - ahora mismo son cinco campos repartidos en dos archivos distintos;
     - cualquier campo de contraseña que se agregue manana lo hereda sin
       que haya que acordarse de nada.

   Tambien se ocupa de los campos que el JavaScript crea despues de que la
   pagina cargo: un MutationObserver los va atendiendo segun aparecen.
   ============================================================ */

(function () {
    "use strict";

    // Iconos en linea (no se puede usar la macro de Jinja desde aqui).
    // Mismo trazo de 1.6 y viewBox 24x24 que el resto de los iconos del
    // sitio, para que no desentone.
    const SVG_INICIO =
        '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" ' +
        'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">';

    const OJO_ABIERTO = SVG_INICIO +
        '<path d="M2 12s3.6-6.5 10-6.5S22 12 22 12s-3.6 6.5-10 6.5S2 12 2 12z"/>' +
        '<circle cx="12" cy="12" r="2.8"/></svg>';

    // Ojo tachado: el mismo dibujo con una raya encima, que es como se
    // entiende "esto esta oculto" sin tener que leer nada.
    const OJO_TACHADO = SVG_INICIO +
        '<path d="M2 12s3.6-6.5 10-6.5c1.5 0 2.9.36 4.1.9"/>' +
        '<path d="M19.6 8.6C21.2 10.2 22 12 22 12s-3.6 6.5-10 6.5c-1.2 0-2.3-.22-3.3-.58"/>' +
        '<path d="M9.9 9.9a2.8 2.8 0 0 0 3.9 3.9"/>' +
        '<path d="M3.5 3.5l17 17"/></svg>';

    const MARCA = "data-ojo-puesto";

    function esCampoDeContrasena(el) {
        return el instanceof HTMLInputElement
            && el.type === "password"
            && !el.hasAttribute(MARCA)
            // Una via de escape por si algun campo no lo quiere
            && el.dataset.sinOjo === undefined;
    }

    function ponerOjo(input) {
        input.setAttribute(MARCA, "");

        // El input se mete dentro de un contenedor relativo para poder
        // colgarle el boton encima sin descolocar el formulario.
        const caja = document.createElement("div");
        caja.className = "campo-con-ojo";
        input.parentNode.insertBefore(caja, input);
        caja.appendChild(input);

        const boton = document.createElement("button");
        boton.type = "button";          // sin esto enviaria el formulario
        boton.className = "ojo-boton";
        // Se deja alcanzable con el tabulador a proposito: quien no usa
        // raton tambien necesita poder revisar lo que escribio.
        boton.innerHTML = OJO_ABIERTO;
        boton.setAttribute("aria-label", "Mostrar la contraseña");
        boton.setAttribute("aria-pressed", "false");
        boton.title = "Mostrar la contraseña";
        caja.appendChild(boton);

        boton.addEventListener("click", function () {
            const mostrando = input.type === "text";
            input.type = mostrando ? "password" : "text";

            boton.innerHTML = mostrando ? OJO_ABIERTO : OJO_TACHADO;
            const etiqueta = mostrando ? "Mostrar la contraseña" : "Ocultar la contraseña";
            boton.setAttribute("aria-label", etiqueta);
            boton.setAttribute("aria-pressed", mostrando ? "false" : "true");
            boton.title = etiqueta;

            // Cambiar el type manda el cursor al principio en varios
            // navegadores; se devuelve al final para poder seguir
            // escribiendo donde iba.
            const fin = input.value.length;
            input.focus();
            try { input.setSelectionRange(fin, fin); } catch (e) { /* algunos no lo permiten */ }

            // El gato del modal se tapa los ojos cuando hay una contraseña
            // en foco. Si la contraseña esta a la vista, taparse no tiene
            // sentido: login.js escucha esto para destaparse.
            document.dispatchEvent(new CustomEvent("contrasena-visible", {
                detail: { visible: input.type === "text", input: input },
            }));
        });
    }

    function revisar(raiz) {
        const campos = (raiz || document).querySelectorAll('input[type="password"]');
        campos.forEach(function (input) {
            if (esCampoDeContrasena(input)) ponerOjo(input);
        });
    }

    function iniciar() {
        revisar(document);

        // Campos que aparecen despues (los crea otro script). Sin esto
        // habria que acordarse de llamar a revisar() desde cada sitio que
        // genere un formulario.
        if (!("MutationObserver" in window)) return;
        new MutationObserver(function (cambios) {
            cambios.forEach(function (cambio) {
                cambio.addedNodes.forEach(function (nodo) {
                    if (nodo.nodeType !== 1) return;
                    if (esCampoDeContrasena(nodo)) ponerOjo(nodo);
                    else revisar(nodo);
                });
            });
        }).observe(document.body, { childList: true, subtree: true });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", iniciar);
    } else {
        iniciar();
    }
})();
