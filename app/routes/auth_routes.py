"""
app/routes/auth_routes.py

Entrada y salida de la aplicacion. Hay un solo formulario de login para
todo el mundo (el modal del gato, en base.html) y una sola ruta que lo
atiende: /auth/login. Sea cliente, administrador o vendedor, todos mandan
correo y contrasena al mismo sitio; lo que cambia es donde aterrizan.

Captcha
-------
El mismo modal atiende tres formularios, y cada uno trata el captcha
distinto segun lo que le pueda pasar si lo automatizan:

  - /auth/registro            captcha siempre (evita cuentas en lote)
  - /auth/recuperar/solicitar captcha siempre (cada envio manda un correo
                              de verdad a un cliente de verdad)
  - /auth/login               captcha solo despues de
                              INTENTOS_ANTES_DE_CAPTCHA fallos seguidos, para
                              no estorbarle a quien escribe bien su clave

Recuperacion de contrasena
--------------------------
Son dos rutas porque son dos pasos: /auth/recuperar/solicitar manda el
codigo al correo y /auth/recuperar/confirmar lo valida y cambia la
contrasena. La logica vive en recuperacion_service.
"""
from flask import Blueprint, Response, request, jsonify, session, redirect, url_for

from app.services import captcha_service, correo_service, recuperacion_service
from app.services.auth_service import AuthService, TIPO_CLIENTE

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Fallos de login seguidos que se perdonan antes de empezar a pedir
# captcha. Tres es suficiente para un dedo torpe y muy poco para un
# programa que prueba contrasenas.
INTENTOS_ANTES_DE_CAPTCHA = 3
CLAVE_INTENTOS = "intentos_login"


def _abrir_sesion(tipo, usuario):
    """
    Guarda en la sesion los datos de quien acaba de entrar y devuelve la
    URL donde debe aterrizar segun su rol.

    Las claves de sesion se mantienen separadas a proposito:
      - cliente : id_usuario / nombre   -> lo que usan carrito y facturas
      - empleado: id_empleado / nombre_admin / rol -> lo que usa el panel

    Asi una cosa no se confunde con la otra, y el resto del proyecto sigue
    leyendo las mismas claves de siempre.
    """
    session.clear()
    session["tipo_usuario"] = tipo

    if tipo == TIPO_CLIENTE:
        session["id_usuario"] = usuario.id_usuario
        session["nombre"] = usuario.nombre
        return url_for("main.index")

    session["id_empleado"] = usuario.id_empleado
    session["nombre_admin"] = usuario.nombre
    session["rol"] = usuario.nombre_rol

    # El vendedor no tiene acceso a las estadisticas, asi que entra
    # directo a la seccion que si le corresponde.
    if usuario.es_administrador:
        return url_for("admin.dashboard")
    return url_for("admin.productos")


def _error(mensaje, codigo=400, **extra):
    """Respuesta de error con el mismo formato que espera login.js."""
    cuerpo = {"ok": False, "mensaje": mensaje}
    cuerpo.update(extra)
    return jsonify(cuerpo), codigo


# ----------------------------------------------------------------------
# Captcha
# ----------------------------------------------------------------------
@auth_bp.route("/captcha")
def captcha():
    """
    Imagen del captcha. Cada peticion genera un codigo nuevo, asi que la
    respuesta no se puede cachear ni compartir entre pestanas.
    """
    svg = captcha_service.generar_svg(request.args.get("para", "registro"))
    respuesta = Response(svg, mimetype="image/svg+xml")
    respuesta.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    respuesta.headers["Pragma"] = "no-cache"
    return respuesta


# ----------------------------------------------------------------------
# Login
# ----------------------------------------------------------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    correo = request.form.get("email", "").strip()
    contrasena = request.form.get("password", "")

    # El captcha aparece recien cuando el patron de fallos deja de parecer
    # humano. Antes de eso, entrar sigue siendo escribir correo y clave.
    fallos = session.get(CLAVE_INTENTOS, 0)
    if fallos >= INTENTOS_ANTES_DE_CAPTCHA:
        if not captcha_service.validar("login", request.form.get("captcha", "")):
            return _error(
                "El código de la imagen no coincide. Intenta con el nuevo.",
                captcha_requerido=True,
            )

    tipo, usuario = AuthService.login(correo, contrasena)
    if not usuario:
        fallos += 1
        session[CLAVE_INTENTOS] = fallos
        return _error(
            "Correo o contraseña incorrectos.",
            codigo=401,
            captcha_requerido=fallos >= INTENTOS_ANTES_DE_CAPTCHA,
        )

    # _abrir_sesion limpia la sesion entera, asi que el contador de fallos
    # y los captcha pendientes se van con ella.
    return jsonify({"ok": True, "redirect": _abrir_sesion(tipo, usuario)})


# ----------------------------------------------------------------------
# Registro
# ----------------------------------------------------------------------
@auth_bp.route("/registro", methods=["POST"])
def registro():
    """
    El registro publico crea siempre clientes. Las cuentas de personal
    (administrador y vendedor) no se abren desde la tienda: las siembra la
    base de datos o las crea un administrador.
    """
    if not captcha_service.validar("registro", request.form.get("captcha", "")):
        return _error(
            "El código de la imagen no coincide. Te generamos uno nuevo.",
            captcha_requerido=True,
        )

    try:
        cliente = AuthService.registrar_cliente(
            id_usuario=request.form.get("id_usuario", "").strip(),
            nombre=request.form.get("names", "").strip(),
            apellido=request.form.get("lastnames", "").strip(),
            correo=request.form.get("email", "").strip(),
            contrasena=request.form.get("password", ""),
            telefono=request.form.get("phone", "").strip(),
            direccion=request.form.get("address", "").strip(),
        )
    except ValueError as e:
        # El captcha ya se consumio al validarlo: se avisa al navegador
        # para que pida una imagen nueva antes de reintentar.
        return _error(str(e), captcha_requerido=True)

    return jsonify({"ok": True, "redirect": _abrir_sesion(TIPO_CLIENTE, cliente)})


# ----------------------------------------------------------------------
# Recuperar contrasena (dos pasos)
# ----------------------------------------------------------------------
@auth_bp.route("/recuperar/solicitar", methods=["POST"])
def recuperar_solicitar():
    """
    Paso 1: documento + correo + captcha -> se manda el codigo al correo.
    """
    if not captcha_service.validar("recuperar", request.form.get("captcha", "")):
        return _error(
            "El código de la imagen no coincide. Te generamos uno nuevo.",
            captcha_requerido=True,
        )

    documento = request.form.get("id_usuario", "").strip()
    correo = request.form.get("email", "").strip()

    try:
        destino = recuperacion_service.solicitar_codigo(documento, correo)
    except ValueError as e:
        return _error(str(e), captcha_requerido=True)
    except correo_service.CorreoNoEnviado as e:
        return _error(str(e), codigo=503, captcha_requerido=True)

    return jsonify({
        "ok": True,
        "paso": "codigo",
        "mensaje": "Te enviamos un código de 6 dígitos a " + destino
                   + ". Revísalo y escríbelo aquí (vence en 15 minutos).",
    })


@auth_bp.route("/recuperar/confirmar", methods=["POST"])
def recuperar_confirmar():
    """
    Paso 2: codigo + contrasena nueva -> se cambia la contrasena.

    Aqui no se pide captcha: el codigo que llego al correo ya prueba que
    del otro lado hay alguien con acceso a esa cuenta, y los reintentos
    los limita el propio codigo (5 y queda quemado).
    """
    try:
        recuperacion_service.restablecer(
            documento=request.form.get("id_usuario", "").strip(),
            correo=request.form.get("email", "").strip(),
            codigo=request.form.get("codigo", ""),
            nueva_contrasena=request.form.get("password", ""),
        )
    except ValueError as e:
        return _error(str(e))

    # Quien acaba de probar que es el dueno de la cuenta no deberia quedar
    # bloqueado por los fallos de login que lo trajeron hasta aqui.
    session.pop(CLAVE_INTENTOS, None)

    return jsonify({
        "ok": True,
        "mensaje": "Contraseña actualizada. Ya puedes iniciar sesión.",
    })


@auth_bp.route("/logout")
def logout():
    """Salida unica: cierra la sesion sea del tipo que sea."""
    session.clear()
    return redirect(url_for("main.index"))
