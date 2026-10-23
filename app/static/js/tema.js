/* ============================================================
   tema.js — Interruptor de modo claro / modo oscuro
   ============================================================

   Este archivo se carga en el <head> con `defer` DESACTIVADO a
   proposito: necesita correr antes de que el navegador pinte la
   pagina para que no se vea un parpadeo blanco al entrar en modo
   oscuro (el clasico "flash of wrong theme").

   Reglas:
   - Si el visitante ya eligio un tema, se respeta y se guarda en
     localStorage bajo la clave "bandp-tema".
   - Si nunca eligio, se sigue el modo del sistema operativo y se
     actualiza solo cuando el sistema cambia.
   ============================================================ */
(function () {
    "use strict";

    var CLAVE = "bandp-tema";
    var raiz = document.documentElement;
    var consultaSistema = window.matchMedia("(prefers-color-scheme: dark)");

    function temaGuardado() {
        try {
            var v = localStorage.getItem(CLAVE);
            return v === "light" || v === "dark" ? v : null;
        } catch (e) {
            // Modo privado o cookies bloqueadas: se sigue el sistema.
            return null;
        }
    }

    function aplicar(tema) {
        raiz.setAttribute("data-theme", tema);
        var boton = document.getElementById("tema-toggle");
        if (boton) {
            var siguiente = tema === "dark" ? "claro" : "oscuro";
            boton.setAttribute("aria-label", "Cambiar a modo " + siguiente);
            boton.setAttribute("title", "Cambiar a modo " + siguiente);
            boton.setAttribute("aria-pressed", tema === "dark" ? "true" : "false");
        }
    }

    // 1. Tema inicial, antes del primer pintado
    aplicar(temaGuardado() || (consultaSistema.matches ? "dark" : "light"));

    // 2. Seguir al sistema mientras el visitante no haya elegido
    consultaSistema.addEventListener("change", function (e) {
        if (!temaGuardado()) aplicar(e.matches ? "dark" : "light");
    });

    // 3. Enganchar el boton cuando exista el DOM
    document.addEventListener("DOMContentLoaded", function () {
        var boton = document.getElementById("tema-toggle");
        if (!boton) return;
        aplicar(raiz.getAttribute("data-theme") || "light");

        boton.addEventListener("click", function () {
            var nuevo = raiz.getAttribute("data-theme") === "dark" ? "light" : "dark";
            aplicar(nuevo);
            try {
                localStorage.setItem(CLAVE, nuevo);
            } catch (e) {
                /* sin persistencia, pero el cambio igual se aplica en esta visita */
            }
        });
    });
})();
