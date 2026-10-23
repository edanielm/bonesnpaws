"""
app/routes/decoradores.py

Controla el acceso a rutas protegidas sin bloquear la navegacion publica
del sitio (requerimiento explicito: cualquiera puede navegar sin login).

Hay tres niveles:
    requiere_login  -> hay un cliente con sesion abierta
    requiere_staff  -> hay un empleado con sesion abierta (cualquier rol)
    requiere_admin  -> hay un empleado con rol Administrador

Como el login es unico para todos, cuando falta la sesion se manda a la
portada con ?login=1, que es lo que abre el modal de inicio de sesion.
"""
from functools import wraps
from flask import session, redirect, url_for, flash, jsonify, request

from app.extensions import db
from app.models import ROL_ADMINISTRADOR, Empleado


def _es_peticion_de_javascript():
    """
    True solo si quien pide es el JavaScript del sitio, no el navegador
    navegando a una direccion.

    Antes esto se decidia por la ruta ("si empieza por /carrito o
    /facturas, es fetch"), y estaba mal: /carrito, /facturas/historial o
    /facturas/checkout tambien se abren escribiendo la direccion o
    haciendo clic en un enlace. Sin sesion, el navegador recibia el JSON
    y lo mostraba como texto pelado en pantalla:

        {"mensaje": "Debes iniciar sesion para continuar.", "ok": false}

    La cabecera X-Requested-With la pone app.js en cada fetch, asi que
    distingue las dos cosas sin adivinar por la URL.
    """
    return (
        request.is_json
        or request.headers.get("X-Requested-With") == "XMLHttpRequest"
    )


def _pedir_login(mensaje):
    """
    Respuesta comun cuando falta sesion.

    - Desde el JavaScript del sitio: JSON con requiere_login=True, para
      que app.js abra el modal de inicio de sesion.
    - Navegando: a la portada con el aviso arriba y el modal abierto.
    """
    if _es_peticion_de_javascript():
        return jsonify({"ok": False, "mensaje": mensaje, "requiere_login": True}), 401
    flash(mensaje, "warning")
    return redirect(url_for("main.index", login=1))


def _empleado_activo_de_sesion():
    """
    El Empleado de la sesion actual, solo si sigue activo. None si no hay
    sesion de personal o si a esa cuenta ya le quitaron el acceso (para
    que una desactivacion a mitad de sesion tenga efecto en el siguiente
    clic, no solo en el proximo login).
    """
    if "id_empleado" not in session:
        return None
    empleado = db.session.get(Empleado, session["id_empleado"])
    return empleado if empleado and empleado.activo else None


def requiere_login(vista):
    """Solo para clientes: carrito, checkout, historial de compras."""
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if "id_usuario" not in session:
            return _pedir_login("Debes iniciar sesión para continuar.")
        return vista(*args, **kwargs)
    return envoltura


def requiere_staff(vista):
    """
    Cualquier empleado con sesion abierta, sea administrador o vendedor.
    Es el minimo para entrar al panel.
    """
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if "id_empleado" not in session:
            return _pedir_login("Inicia sesión con una cuenta del equipo para entrar al panel.")
        if not _empleado_activo_de_sesion():
            session.clear()
            return _pedir_login("Tu cuenta ya no tiene acceso al panel. Contacta a un administrador.")
        return vista(*args, **kwargs)
    return envoltura


def requiere_admin(vista):
    """
    Solo el rol Administrador: estadisticas de ventas, gestion de personal
    y eliminacion de cuentas de clientes. Un vendedor con sesion abierta
    que intente entrar aqui se devuelve al catalogo con un aviso, no a la
    pantalla de login: su sesion es valida, lo que le falta es el permiso.
    """
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if "id_empleado" not in session:
            return _pedir_login("Inicia sesión con una cuenta del equipo para entrar al panel.")
        if not _empleado_activo_de_sesion():
            session.clear()
            return _pedir_login("Tu cuenta ya no tiene acceso al panel. Contacta a un administrador.")
        if session.get("rol") != ROL_ADMINISTRADOR:
            flash("Esta sección es solo para administradores.", "warning")
            return redirect(url_for("admin.productos"))
        return vista(*args, **kwargs)
    return envoltura
