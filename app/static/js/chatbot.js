/* ============================================================
   chatbot.js — Burbuja de chat de atencion basica
   El historial vive en sessionStorage: sigue disponible al navegar
   entre paginas dentro de la misma pestaña, y se olvida al cerrarla.
   ============================================================ */

const CHATBOT_HISTORIAL_KEY = "bandp_chatbot_historial";
const CHATBOT_MENSAJE_BIENVENIDA =
    "¡Hola! Soy Chantonieta, el asistente de Bones & Paws. Puedo ayudarte con horarios y contacto, cómo " +
    "comprar o el estado de un pedido, métodos de pago y envío, o el catálogo. ¿En qué te ayudo?";

function chatbotLeerHistorial() {
    try {
        const guardado = JSON.parse(sessionStorage.getItem(CHATBOT_HISTORIAL_KEY));
        return Array.isArray(guardado) ? guardado : [];
    } catch {
        return [];
    }
}

function chatbotGuardarHistorial(historial) {
    try {
        sessionStorage.setItem(CHATBOT_HISTORIAL_KEY, JSON.stringify(historial));
    } catch {
        // sessionStorage no disponible (modo privado, cuota llena...): el chat sigue
        // funcionando, solo no recuerda la conversacion al cambiar de pagina.
    }
}

function chatbotPintarMensaje(contenedor, rol, texto) {
    const burbuja = document.createElement("div");
    burbuja.className = `chatbot-msg ${rol}`;
    burbuja.textContent = texto;
    contenedor.appendChild(burbuja);
    contenedor.scrollTop = contenedor.scrollHeight;
}

document.addEventListener("DOMContentLoaded", () => {
    const widget = document.getElementById("chatbot-widget");
    const boton = document.getElementById("chatbot-abrir");
    const panel = document.getElementById("chatbot-panel");
    if (!widget || !boton || !panel) return;

    const cerrar = document.getElementById("chatbot-cerrar");
    const mensajesEl = document.getElementById("chatbot-mensajes");
    const form = document.getElementById("chatbot-form");
    const input = document.getElementById("chatbot-input");

    let historial = chatbotLeerHistorial();
    if (historial.length === 0) {
        historial = [{ rol: "bot", texto: CHATBOT_MENSAJE_BIENVENIDA }];
        chatbotGuardarHistorial(historial);
    }
    historial.forEach(m => chatbotPintarMensaje(mensajesEl, m.rol, m.texto));

    function chatbotDesplegar(abrir) {
        widget.classList.toggle("abierto", abrir);
        boton.setAttribute("aria-expanded", String(abrir));
        if (abrir) {
            mensajesEl.scrollTop = mensajesEl.scrollHeight;
            input.focus();
        }
    }

    boton.addEventListener("click", () => {
        chatbotDesplegar(!widget.classList.contains("abierto"));
    });

    cerrar?.addEventListener("click", () => chatbotDesplegar(false));

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && widget.classList.contains("abierto")) chatbotDesplegar(false);
    });

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const texto = input.value.trim();
        if (!texto) return;

        chatbotPintarMensaje(mensajesEl, "usuario", texto);
        historial.push({ rol: "usuario", texto });
        chatbotGuardarHistorial(historial);
        input.value = "";

        let respuesta;
        try {
            const resp = await fetch("/chatbot/mensaje", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ mensaje: texto }),
            });
            const datos = await resp.json();
            respuesta = datos.ok ? datos.respuesta : (datos.mensaje || "No pude procesar tu mensaje.");
        } catch (err) {
            respuesta = "Hubo un problema de conexión. Intenta de nuevo en un momento.";
        }

        chatbotPintarMensaje(mensajesEl, "bot", respuesta);
        historial.push({ rol: "bot", texto: respuesta });
        chatbotGuardarHistorial(historial);
    });
});
