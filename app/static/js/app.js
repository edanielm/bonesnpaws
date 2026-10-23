/* ============================================================
   app.js — Interactividad general del sitio Bones & Paws
   ============================================================ */

function mostrarToast(mensaje, esError = false) {
    const toast = document.getElementById("toast");
    if (!toast) return;
    toast.textContent = mensaje;
    toast.classList.toggle("error", esError);
    toast.classList.add("visible");
    clearTimeout(window._toastTimeout);
    window._toastTimeout = setTimeout(() => toast.classList.remove("visible"), 2800);
}

/* Cabecera con la que el servidor distingue una peticion de este
   JavaScript de una navegacion normal del navegador. Sin ella, entrar a
   /carrito sin sesion devolvia el JSON del error y el navegador lo
   mostraba como texto pelado en pantalla (ver decoradores.py). */
const CABECERA_AJAX = { "X-Requested-With": "XMLHttpRequest" };

async function postForm(url, datos) {
    const formData = new FormData();
    Object.entries(datos).forEach(([k, v]) => formData.append(k, v));
    const resp = await fetch(url, { method: "POST", body: formData, headers: CABECERA_AJAX });
    return resp.json();
}

/* Abre el modal de inicio de sesion desde cualquier parte del sitio. */
function pedirInicioDeSesion(mensaje) {
    mostrarToast(mensaje || "Inicia sesión para continuar.", true);
    document.querySelector("[data-abrir-login]")?.click();
}

/* ------------------------------------------------------------
   Menu de telefono

   En pantalla angosta la barra no tiene sitio para los cinco enlaces mas
   los botones de sesion, asi que se mudan a un panel desplegable. Sin
   esto, los enlaces simplemente desaparecian por debajo de 640 px y no
   habia forma de navegar el sitio desde un telefono.
   ------------------------------------------------------------ */
function initMenuMovil() {
    const boton = document.getElementById("nav-toggle");
    const panel = document.getElementById("nav-movil");
    if (!boton || !panel) return;

    function abierto() {
        return boton.getAttribute("aria-expanded") === "true";
    }

    function poner(abrir) {
        boton.setAttribute("aria-expanded", abrir ? "true" : "false");
        boton.setAttribute("aria-label", abrir ? "Cerrar el menú" : "Abrir el menú");
        panel.hidden = !abrir;
    }

    boton.addEventListener("click", () => poner(!abierto()));

    // Escape cierra, como cualquier cosa desplegable del sitio
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && abierto()) {
            poner(false);
            boton.focus();
        }
    });

    // Tocar fuera del panel lo cierra
    document.addEventListener("click", (e) => {
        if (!abierto()) return;
        if (panel.contains(e.target) || boton.contains(e.target)) return;
        poner(false);
    });

    // Al girar el telefono o agrandar la ventana, el panel deja de tener
    // sentido: los enlaces vuelven a la barra y el panel quedaria colgado.
    window.addEventListener("resize", () => {
        if (window.innerWidth > 900 && abierto()) poner(false);
    });
}

/* ------------------------------------------------------------
   Estado "ocupado" de un boton

   Mientras la peticion viaja al servidor el boton queda deshabilitado y
   con otro texto. Sin esto, un doble clic en "Confirmar compra" mandaba
   la orden dos veces y generaba dos facturas del mismo carrito.
   ------------------------------------------------------------ */
function ocupar(boton, textoOcupado) {
    if (!boton) return () => {};
    const htmlOriginal = boton.innerHTML;
    boton.disabled = true;
    boton.classList.add("cargando");
    if (textoOcupado) boton.innerHTML = textoOcupado;

    // Devuelve la funcion que lo deja como estaba
    return () => {
        boton.disabled = false;
        boton.classList.remove("cargando");
        boton.innerHTML = htmlOriginal;
    };
}

/* ------------------------------------------------------------
   Carrito: contador de la barra y actualizacion sin recargar
   ------------------------------------------------------------ */

function fijarBadgeCarrito(unidades) {
    const badge = document.getElementById("cart-badge");
    if (!badge) return;
    badge.textContent = unidades;
    badge.style.display = unidades > 0 ? "flex" : "none";
}

/**
 * Repinta los totales del carrito con lo que respondio el servidor.
 *
 * Antes cada cambio de cantidad terminaba en window.location.reload(), lo
 * que anulaba la ventaja de hacer la peticion con fetch. Ahora solo se
 * reescriben los numeros que cambiaron. Las cifras vienen ya formateadas
 * en pesos desde el servidor (filtro `pesos`), asi que el navegador no
 * tiene que reimplementar el formato colombiano.
 */
function pintarTotalesCarrito(totales) {
    if (!totales) return;

    fijarBadgeCarrito(totales.unidades);

    document.querySelectorAll("[data-carrito-conteo]").forEach(el => {
        el.textContent = totales.num_items;
    });

    const subtotal = document.querySelector('[data-total="subtotal"]');
    const iva = document.querySelector('[data-total="iva"]');
    const envio = document.querySelector('[data-total="costo_envio"]');
    const total = document.querySelector('[data-total="total"]');

    if (subtotal) subtotal.textContent = totales.subtotal;
    if (iva) iva.textContent = totales.iva;
    if (total) total.textContent = totales.total;
    if (envio) {
        envio.innerHTML = totales.envio_gratis
            ? '<span class="badge exito">Gratis</span>'
            : totales.costo_envio;
    }

    // Subtotal de cada linea
    Object.entries(totales.lineas || {}).forEach(([idProducto, valor]) => {
        const celda = document.querySelector(`[data-linea-total="${idProducto}"]`);
        if (celda) celda.textContent = valor;
    });

    // Aviso de envio gratis
    const aviso = document.querySelector("[data-envio-aviso]");
    if (aviso) {
        if (totales.envio_gratis) {
            aviso.textContent = "¡Tu envío es gratis!";
        } else if (totales.num_items > 0) {
            aviso.textContent = `Te faltan ${totales.falta_para_envio_gratis} para el envío gratis.`;
        } else {
            aviso.textContent = "";
        }
    }

    // Si se quito el ultimo producto, se muestra el mensaje de carrito vacio
    // sin necesidad de recargar la pagina.
    if (totales.num_items === 0) {
        document.getElementById("carrito-layout")?.setAttribute("hidden", "");
        document.getElementById("carrito-vacio")?.removeAttribute("hidden");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    initMenuMovil();
    // Agregar al carrito desde cualquier tarjeta de producto
    document.querySelectorAll("[data-agregar-carrito]").forEach(btn => {
        btn.addEventListener("click", async (e) => {
            e.preventDefault();
            const idProducto = btn.dataset.agregarCarrito;
            const cantidadInput = document.getElementById(`cantidad-${idProducto}`);
            const cantidad = cantidadInput ? cantidadInput.value : 1;

            const restaurar = ocupar(btn, "Agregando...");
            try {
                const data = await postForm("/carrito/agregar", { id_producto: idProducto, cantidad });
                if (data.ok) {
                    mostrarToast("Producto agregado al carrito.");
                    pintarTotalesCarrito(data.totales);
                } else if (data.requiere_login) {
                    // Antes esto comparaba data.mensaje con un texto exacto, y
                    // el servidor mandaba otro: el modal nunca se abria y en su
                    // lugar salia el mensaje del servidor como error.
                    pedirInicioDeSesion(data.mensaje);
                } else {
                    mostrarToast(data.mensaje || "No se pudo agregar el producto.", true);
                }
            } catch (err) {
                mostrarToast("Error de conexión. Intenta de nuevo.", true);
            } finally {
                restaurar();
            }
        });
    });

    /* --------------------------------------------------------
       Selector de cantidad +/-
       El boton "+" respeta el stock: no deja pedir mas unidades
       de las que hay, y avisa por que se detuvo.
       -------------------------------------------------------- */
    document.querySelectorAll("[data-qty-menos]").forEach(btn => {
        btn.addEventListener("click", () => {
            const input = document.getElementById(btn.dataset.qtyMenos);
            if (input) input.value = Math.max(1, parseInt(input.value || "1", 10) - 1);
        });
    });
    document.querySelectorAll("[data-qty-mas]").forEach(btn => {
        btn.addEventListener("click", () => {
            const input = document.getElementById(btn.dataset.qtyMas);
            if (!input) return;
            const tope = parseInt(input.max || "0", 10);
            const nuevo = parseInt(input.value || "1", 10) + 1;
            if (tope && nuevo > tope) {
                mostrarToast(`Solo quedan ${tope} unidad(es) disponibles.`, true);
                input.value = tope;
                return;
            }
            input.value = nuevo;
        });
    });

    /* --------------------------------------------------------
       Carrito: cambiar cantidad (sin recargar la pagina)
       -------------------------------------------------------- */
    document.querySelectorAll("[data-cant-carrito]").forEach(input => {
        input.addEventListener("change", async () => {
            const tope = parseInt(input.dataset.stockMax || "0", 10);
            let cantidad = parseInt(input.value || "1", 10);

            if (isNaN(cantidad) || cantidad < 1) cantidad = 1;
            // El limite se avisa aqui mismo, antes de molestar al servidor
            if (tope && cantidad > tope) {
                mostrarToast(`Solo quedan ${tope} unidad(es) de «${input.dataset.nombreProducto}».`, true);
                cantidad = tope;
            }
            input.value = cantidad;

            input.disabled = true;
            try {
                const data = await postForm("/carrito/actualizar", {
                    id_producto: input.dataset.cantCarrito,
                    cantidad,
                });
                if (data.ok) {
                    pintarTotalesCarrito(data.totales);
                } else {
                    mostrarToast(data.mensaje || "No se pudo actualizar la cantidad.", true);
                }
            } catch (err) {
                mostrarToast("Error de conexión. Intenta de nuevo.", true);
            } finally {
                input.disabled = false;
            }
        });
    });

    /* --------------------------------------------------------
       Carrito: eliminar item (quita la fila, no recarga)
       -------------------------------------------------------- */
    document.querySelectorAll("[data-eliminar-carrito]").forEach(btn => {
        btn.addEventListener("click", async () => {
            const idProducto = btn.dataset.eliminarCarrito;
            const restaurar = ocupar(btn, "Quitando...");
            try {
                const data = await postForm("/carrito/eliminar", { id_producto: idProducto });
                if (data.ok) {
                    document.querySelector(`[data-fila-carrito="${idProducto}"]`)?.remove();
                    pintarTotalesCarrito(data.totales);
                    mostrarToast("Producto eliminado del carrito.");
                } else {
                    mostrarToast(data.mensaje || "No se pudo eliminar el producto.", true);
                    restaurar();
                }
            } catch (err) {
                mostrarToast("Error de conexión. Intenta de nuevo.", true);
                restaurar();
            }
        });
    });

    // Checkout: mostrar/ocultar campos segun metodo de pago
    const metodoSelect = document.getElementById("metodo_pago");
    if (metodoSelect) {
        const bloques = document.querySelectorAll("[data-metodo-bloque]");
        const actualizarBloques = () => {
            bloques.forEach(b => {
                const activo = b.dataset.metodoBloque === metodoSelect.value;
                b.style.display = activo ? "block" : "none";
                // PSE y Transferencia comparten el campo "banco": los bloques
                // ocultos se deshabilitan para que no viajen con el formulario
                // y el servidor lea el banco del metodo elegido.
                b.querySelectorAll("input, select").forEach(campo => { campo.disabled = !activo; });
            });
        };
        metodoSelect.addEventListener("change", actualizarBloques);
        actualizarBloques();
    }

    /* --------------------------------------------------------
       Checkout: enviar orden
       El boton queda deshabilitado mientras se procesa el pago: es el
       sitio donde un doble clic hace mas daño (dos facturas del mismo
       carrito). Solo se rehabilita si algo salio mal; si la compra
       funciono, la pagina ya esta navegando a la factura.
       -------------------------------------------------------- */
    const checkoutForm = document.getElementById("checkout-form");
    if (checkoutForm) {
        checkoutForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const boton = checkoutForm.querySelector('button[type="submit"]');
            const restaurar = ocupar(boton, "Procesando pago...");

            try {
                const formData = new FormData(checkoutForm);
                const resp = await fetch("/facturas/registrar", {
                    method: "POST", body: formData, headers: CABECERA_AJAX,
                });
                const data = await resp.json();
                if (data.ok) {
                    window.location.href = `/facturas/${data.numero_factura}?nueva=1`;
                } else if (data.requiere_login) {
                    // La sesion se vencio mientras llenaba el formulario
                    pedirInicioDeSesion(data.mensaje);
                    restaurar();
                } else {
                    mostrarToast(data.mensaje || "No se pudo procesar el pago.", true);
                    restaurar();
                }
            } catch (err) {
                mostrarToast("Error de conexión. Intenta de nuevo.", true);
                restaurar();
            }
        });
    }

    // Filtro de categoria en /productos (sin recargar toda la logica, solo submit)
    document.querySelectorAll("[data-filtro-categoria]").forEach(chip => {
        chip.addEventListener("click", () => {
            const url = new URL(window.location.href);
            const valor = chip.dataset.filtroCategoria;
            if (valor) url.searchParams.set("categoria", valor);
            else url.searchParams.delete("categoria");
            // Al cambiar de filtro se vuelve a la primera pagina
            url.searchParams.delete("pagina");
            window.location.href = url.toString();
        });
    });

    // Formulario de producto: previsualizar las fotos elegidas antes de enviar
    document.querySelectorAll("[data-preview-input]").forEach(input => {
        const contenedor = document.getElementById(input.dataset.previewInput);
        if (!contenedor) return;
        input.addEventListener("change", () => {
            contenedor.innerHTML = "";
            Array.from(input.files || []).forEach(archivo => {
                const item = document.createElement("div");
                item.className = "galeria-preview-item";

                const img = document.createElement("img");
                img.src = URL.createObjectURL(archivo);
                img.onload = () => URL.revokeObjectURL(img.src);
                img.alt = `Vista previa de ${archivo.name}`;
                item.appendChild(img);

                const nombre = document.createElement("span");
                nombre.className = "nombre-archivo";
                nombre.textContent = archivo.name;
                item.appendChild(nombre);

                contenedor.appendChild(item);
            });
        });
    });

    // Detalle de producto: cambiar la foto principal al hacer clic en una miniatura
    document.querySelectorAll("[data-galeria-thumb]").forEach(miniatura => {
        miniatura.addEventListener("click", () => {
            const principal = document.getElementById(miniatura.dataset.galeriaThumb);
            if (!principal) return;
            principal.src = miniatura.dataset.src;
            miniatura.parentElement.querySelectorAll(".detalle-miniatura").forEach(m => {
                m.classList.remove("activa");
                m.setAttribute("aria-pressed", "false");
            });
            miniatura.classList.add("activa");
            miniatura.setAttribute("aria-pressed", "true");
        });
    });
});
