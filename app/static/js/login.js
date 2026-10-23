/* ============================================================
   login.js — Logica del modal flotante (Gato Negro Animado)
   Misma animacion e interacciones del proyecto original.

   Modos:
     login     -> correo + contrasena
     registro  -> datos del cliente + captcha
     recuperar -> documento + correo + captcha  (pide el codigo por correo)
     codigo    -> codigo del correo + contrasena nueva

   El captcha lo dibuja el servidor (/auth/captcha): aqui solo se pide la
   imagen y se manda lo que la persona escribio. La respuesta correcta
   nunca esta en el navegador, asi que no se puede leer desde la consola.
   ============================================================ */

function initLoginModal() {
    const overlay = document.getElementById("login-overlay");
    const authForm = document.getElementById("auth-form");
    const toggleFormBtn = document.getElementById("toggle-form");
    const toggleMsg = document.getElementById("toggle-msg");
    const olvidePasswordBtn = document.getElementById("olvide-password");
    const formTitle = document.getElementById("form-title");
    const submitBtn = document.getElementById("submit-btn");
    const closeBtn = document.getElementById("login-cerrar");
    const errorBox = document.getElementById("form-error");
    const recuperarDocInput = document.getElementById("recuperar-documento");
    const recuperarCodigoInput = document.getElementById("recuperar-codigo");
    const recuperarPassInput = document.getElementById("recuperar-password");
    const recuperarPassConfirmInput = document.getElementById("recuperar-password-confirm");
    const codigoAviso = document.getElementById("codigo-aviso");
    const codigoReenviarBtn = document.getElementById("codigo-reenviar");

    const captchaBloque = document.getElementById("captcha-bloque");
    const captchaImg = document.getElementById("captcha-img");
    const captchaInput = document.getElementById("captcha");
    const captchaRecargarBtn = document.getElementById("captcha-recargar");

    const eyeL = document.querySelector(".eyeball-l");
    const eyeR = document.querySelector(".eyeball-r");
    const handL = document.querySelector(".hand-l");
    const handR = document.querySelector(".hand-r");

    if (!overlay || !authForm) return;

    // modo: "login" | "registro" | "recuperar" | "codigo"
    let modo = "login";

    // El login no pide captcha de entrada; el servidor lo exige despues de
    // varios intentos fallidos y lo avisa con "captcha_requerido".
    let captchaEnLogin = false;

    /* --------------------------------------------------------
       Captcha

       Cada formulario tiene su propio "proposito" en el servidor, para que
       el captcha resuelto en uno no sirva de respuesta en otro.
       -------------------------------------------------------- */
    function propositoCaptcha() {
        if (modo === "registro") return "registro";
        if (modo === "recuperar") return "recuperar";
        return "login";
    }

    function captchaHaceFalta() {
        if (modo === "registro" || modo === "recuperar") return true;
        if (modo === "login") return captchaEnLogin;
        return false;  // el codigo del correo ya prueba la identidad
    }

    function recargarCaptcha() {
        if (!captchaImg) return;
        // El parametro suelto rompe la cache del navegador: sin el, la
        // imagen se quedaria pegada en el primer codigo.
        captchaImg.src = "/auth/captcha?para=" + propositoCaptcha()
            + "&t=" + Date.now() + "-" + Math.random().toString(36).slice(2);
        if (captchaInput) captchaInput.value = "";
    }

    function aplicarCaptcha() {
        if (!captchaBloque) return;
        const hace_falta = captchaHaceFalta();
        captchaBloque.hidden = !hace_falta;
        if (hace_falta) recargarCaptcha();
        else if (captchaInput) captchaInput.value = "";
    }

    if (captchaRecargarBtn) {
        captchaRecargarBtn.addEventListener("click", (e) => {
            e.preventDefault();
            recargarCaptcha();
            if (captchaInput) captchaInput.focus();
        });
    }

    /* --------------------------------------------------------
       Accesibilidad de la ventana

       Una ventana modal tiene que cumplir tres cosas para poder usarse sin
       raton: cerrarse con Escape, no dejar que el tabulador se escape a la
       pagina de atras (que esta tapada y no se puede ver), y devolver el
       foco al boton que la abrio al cerrarse.
       -------------------------------------------------------- */
    const FOCUSABLES = 'input, button, a[href], select, textarea, [tabindex]:not([tabindex="-1"])';
    let elementoQueAbrio = null;

    function visibles() {
        // Solo los campos del modo actual: los demas estan ocultos por CSS
        // y no deben recibir el foco al tabular.
        return Array.from(overlay.querySelectorAll(FOCUSABLES))
            .filter(el => !el.disabled && el.offsetParent !== null);
    }

    function atraparTabulador(e) {
        if (e.key !== "Tab") return;
        const campos = visibles();
        if (!campos.length) return;

        const primero = campos[0];
        const ultimo = campos[campos.length - 1];

        // Al llegar al final, el tabulador vuelve al principio (y al reves)
        if (e.shiftKey && document.activeElement === primero) {
            e.preventDefault();
            ultimo.focus();
        } else if (!e.shiftKey && document.activeElement === ultimo) {
            e.preventDefault();
            primero.focus();
        }
    }

    function alPresionarTecla(e) {
        if (e.key === "Escape") {
            e.preventDefault();
            cerrar();
        } else {
            atraparTabulador(e);
        }
    }

    function aplicarModo() {
        authForm.classList.toggle("register-mode", modo === "registro");
        authForm.classList.toggle("recuperar-mode", modo === "recuperar");
        authForm.classList.toggle("codigo-mode", modo === "codigo");

        // El texto de al lado del enlace tiene que acompañarlo: dejar
        // "¿No tienes cuenta?" junto a "Volver a Iniciar Sesión" no se
        // entiende.
        const TEXTOS = {
            registro:  ["Crear Cuenta",          "Registrarse",          "¿Ya tienes cuenta?", "Inicia Sesión"],
            recuperar: ["Recuperar Contraseña",  "Enviarme el código",   "",                   "Volver a Iniciar Sesión"],
            codigo:    ["Escribe el código",     "Cambiar contraseña",   "",                   "Volver a Iniciar Sesión"],
            login:     ["Iniciar Sesión",        "Entrar",               "¿No tienes cuenta?", "Regístrate"],
        };
        const [titulo, boton, mensaje, enlace] = TEXTOS[modo] || TEXTOS.login;
        formTitle.innerText = titulo;
        submitBtn.innerText = boton;
        toggleFormBtn.innerText = enlace;
        if (toggleMsg) toggleMsg.innerText = mensaje;

        limpiarError();
        aplicarCaptcha();
    }

    function irAModo(nuevo) {
        modo = nuevo;
        aplicarModo();
        const primerCampo = visibles().find(el => el.tagName === "INPUT");
        if (primerCampo) primerCampo.focus();
    }

    function abrir(modoInicial = "login") {
        elementoQueAbrio = document.activeElement;
        overlay.classList.add("abierto");
        overlay.setAttribute("aria-hidden", "false");
        modo = modoInicial;
        aplicarModo();

        document.addEventListener("keydown", alPresionarTecla);
        // El primer campo del formulario recibe el foco: quien navega con
        // teclado empieza escribiendo, no buscando donde esta la ventana.
        const primerCampo = visibles().find(el => el.tagName === "INPUT");
        if (primerCampo) primerCampo.focus();
    }

    function cerrar() {
        overlay.classList.remove("abierto");
        overlay.setAttribute("aria-hidden", "true");
        document.removeEventListener("keydown", alPresionarTecla);

        // El foco vuelve a donde estaba, no al principio de la pagina
        if (elementoQueAbrio && document.contains(elementoQueAbrio)) {
            elementoQueAbrio.focus();
        }
        elementoQueAbrio = null;
    }

    function limpiarError() {
        if (errorBox) { errorBox.textContent = ""; errorBox.classList.remove("visible"); }
    }

    function mostrarError(msg) {
        if (errorBox) { errorBox.textContent = msg; errorBox.classList.add("visible"); }
    }

    document.querySelectorAll("[data-abrir-login]").forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();
            abrir(btn.dataset.abrirLogin === "registro" ? "registro" : "login");
        });
    });

    if (closeBtn) closeBtn.addEventListener("click", cerrar);
    overlay.addEventListener("click", (e) => { if (e.target === overlay) cerrar(); });

    toggleFormBtn.addEventListener("click", (e) => {
        e.preventDefault();
        // Desde "recuperar" o "codigo" siempre se vuelve a "login";
        // si no, alterna login <-> registro.
        irAModo(modo === "registro" ? "login" : (modo === "login" ? "registro" : "login"));
    });

    if (olvidePasswordBtn) {
        olvidePasswordBtn.addEventListener("click", (e) => {
            e.preventDefault();
            irAModo("recuperar");
        });
    }

    // "¿No te llegó? Pedir otro código": vuelve al paso 1 con el documento
    // y el correo que ya estaban escritos, para no tipearlos de nuevo.
    if (codigoReenviarBtn) {
        codigoReenviarBtn.addEventListener("click", (e) => {
            e.preventDefault();
            irAModo("recuperar");
        });
    }

    const lookDown = () => { eyeL.style.transform = "translateY(5px)"; eyeR.style.transform = "translateY(5px)"; };
    const lookNormal = () => { eyeL.style.transform = "translateY(0)"; eyeR.style.transform = "translateY(0)"; };
    const coverEyes = () => {
        handL.style.transform = "translate(45px, -60px) scale(1.2)";
        handR.style.transform = "translate(-45px, -60px) scale(1.2)";
    };
    const uncoverEyes = () => {
        handL.style.transform = "translate(0) scale(1)";
        handR.style.transform = "translate(0) scale(1)";
    };

    authForm.querySelectorAll("input").forEach(input => {
        input.addEventListener("focus", (e) => {
            if (e.target.type === "password") { coverEyes(); lookNormal(); }
            else { uncoverEyes(); lookDown(); }
        });
    });

    // El ojito de password.js avisa cuando una contraseña queda a la vista.
    // Si se puede leer en pantalla, que el gato siga tapandose los ojos no
    // tiene sentido: se destapa y la mira, como con cualquier otro campo.
    document.addEventListener("contrasena-visible", (e) => {
        if (!authForm.contains(e.detail.input)) return;
        if (e.detail.visible) { uncoverEyes(); lookDown(); }
        else { coverEyes(); lookNormal(); }
    });

    document.addEventListener("click", (e) => {
        if (overlay.classList.contains("abierto") && !authForm.contains(e.target) && e.target !== toggleFormBtn) {
            lookNormal(); uncoverEyes();
        }
    });

    /* --------------------------------------------------------
       Envio del formulario
       -------------------------------------------------------- */
    function validarEnCliente() {
        // Lo que se puede revisar sin preguntarle al servidor se revisa
        // aqui: ahorra un viaje y, sobre todo, no gasta el captcha.
        if (captchaHaceFalta() && !captchaInput.value.trim()) {
            return "Escribe el código que aparece en la imagen.";
        }
        if (modo === "codigo") {
            if (!recuperarCodigoInput.value.trim()) {
                return "Escribe el código de 6 dígitos que te llegó al correo.";
            }
            if (recuperarPassInput.value !== recuperarPassConfirmInput.value) {
                return "Las contraseñas no coinciden.";
            }
            if (recuperarPassInput.value.length < 6) {
                return "La nueva contraseña debe tener al menos 6 caracteres.";
            }
        }
        return null;
    }

    function armarDatos() {
        const formData = new FormData(authForm);

        if (modo === "recuperar") {
            formData.set("id_usuario", recuperarDocInput.value.trim());
        } else if (modo === "codigo") {
            formData.set("id_usuario", recuperarDocInput.value.trim());
            formData.set("codigo", recuperarCodigoInput.value.trim());
            formData.set("password", recuperarPassInput.value);
            formData.delete("captcha");
        }
        return formData;
    }

    const ENDPOINTS = {
        login: "/auth/login",
        registro: "/auth/registro",
        recuperar: "/auth/recuperar/solicitar",
        codigo: "/auth/recuperar/confirmar",
    };

    const TEXTO_ESPERA = {
        login: "Un momento...",
        registro: "Creando cuenta...",
        recuperar: "Enviando el código...",
        codigo: "Cambiando la contraseña...",
    };

    authForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        limpiarError();

        const problema = validarEnCliente();
        if (problema) { mostrarError(problema); return; }

        const modoEnviado = modo;
        const formData = armarDatos();

        // El boton queda deshabilitado mientras el servidor responde, para
        // que un doble clic no mande dos registros ni dos correos.
        const textoBoton = submitBtn.innerText;
        submitBtn.disabled = true;
        submitBtn.classList.add("cargando");
        submitBtn.innerText = TEXTO_ESPERA[modoEnviado] || "Un momento...";

        const restaurarBoton = () => {
            submitBtn.disabled = false;
            submitBtn.classList.remove("cargando");
            submitBtn.innerText = textoBoton;
        };

        try {
            const resp = await fetch(ENDPOINTS[modoEnviado], { method: "POST", body: formData });
            const data = await resp.json();

            if (!data.ok) {
                mostrarError(data.mensaje || "No se pudo procesar la solicitud.");
                // El captcha es de un solo uso: si el servidor lo gasto al
                // validarlo, hay que traer una imagen nueva antes de
                // reintentar. En el login, ademas, puede aparecer por
                // primera vez justo ahora.
                if (data.captcha_requerido) {
                    if (modoEnviado === "login") captchaEnLogin = true;
                    aplicarCaptcha();
                }
                restaurarBoton();
                return;
            }

            if (modoEnviado === "recuperar") {
                // Paso 1 listo: el codigo ya salio al correo.
                if (codigoAviso) codigoAviso.textContent = data.mensaje || "";
                restaurarBoton();
                irAModo("codigo");
                return;
            }

            if (modoEnviado === "codigo") {
                // Contrasena cambiada: se vuelve al login con el formulario
                // limpio para que entre con la nueva.
                authForm.reset();
                captchaEnLogin = false;
                if (codigoAviso) codigoAviso.textContent = "";
                restaurarBoton();
                irAModo("login");
                mostrarExito(data.mensaje || "Contraseña actualizada. Ya puedes iniciar sesión.");
                return;
            }

            // Login y registro: la pagina ya esta navegando al destino, el
            // boton no se restaura a proposito.
            window.location.href = data.redirect || "/";
        } catch (err) {
            mostrarError("Error de conexión. Intenta de nuevo.");
            restaurarBoton();
        }
    });

    function mostrarExito(mensaje) {
        // mostrarToast lo define app.js; si por algun motivo no esta
        // cargado, el aviso igual se ve dentro del formulario.
        if (typeof window.mostrarToast === "function") window.mostrarToast(mensaje);
        else mostrarError(mensaje);
    }

    // Abrir automaticamente si el servidor pidio mostrar el login (ej. sesion expirada)
    if (document.body.dataset.abrirLoginAuto === "1") abrir("login");
}

document.addEventListener("DOMContentLoaded", initLoginModal);
