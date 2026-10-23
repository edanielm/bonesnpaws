"""
app/routes/perfil_routes.py

Perfil unico del sitio. Hay una sola direccion, /perfil, y lo que muestra
depende de quien tenga la sesion abierta:

    cliente  -> sus datos de contacto y el resumen de sus compras
    empleado -> sus datos, su rol, que le permite ese rol y los accesos
                directos a las secciones del panel que si puede abrir

Es la contraparte del login unico: si todos entran por el mismo formulario,
todos tienen que poder ver "su" perfil en la misma direccion, sin que el
cliente tenga que saber que existe /admin ni el vendedor tenga que buscar
su ficha en otra parte.
"""
from flask import (
    Blueprint, session, render_template, request, jsonify, redirect, url_for, flash,
)

from app.extensions import db
from app.models import Cliente, Empleado
from app.services.admin_service import AdminService

perfil_bp = Blueprint("perfil", __name__, url_prefix="/perfil")


@perfil_bp.route("/")
def ver():
    # El empleado se comprueba primero: si alguien tuviera las dos sesiones,
    # manda la del equipo, que es la mas especifica.
    if "id_empleado" in session:
        empleado = db.get_or_404(Empleado, session["id_empleado"])
        return render_template(
            "perfil/empleado.html",
            empleado=empleado,
            resumen=AdminService.resumen_empleado(empleado.id_empleado),
        )

    if "id_usuario" in session:
        cliente = db.get_or_404(Cliente, session["id_usuario"])
        return render_template(
            "perfil/cliente.html",
            cliente=cliente,
            resumen=AdminService.detalle_cliente(cliente.id_usuario),
        )

    flash("Inicia sesión para ver tu perfil.", "warning")
    return redirect(url_for("main.index", login=1))


@perfil_bp.route("/actualizar", methods=["POST"])
def actualizar():
    """
    Guarda los datos que cada quien puede cambiar de si mismo.

    Nombre, documento y correo no se editan aqui: identifican la cuenta y
    estan enlazados al historial de facturas. El rol tampoco, por razones
    obvias -nadie se asciende solo-; eso lo cambia un administrador.
    """
    if "id_empleado" in session:
        empleado = db.get_or_404(Empleado, session["id_empleado"])
        empleado.telefono = request.form.get("telefono", empleado.telefono)
        db.session.commit()
        return jsonify({"ok": True})

    if "id_usuario" in session:
        cliente = db.get_or_404(Cliente, session["id_usuario"])
        cliente.telefono = request.form.get("telefono", cliente.telefono)
        cliente.direccion = request.form.get("direccion", cliente.direccion)
        db.session.commit()
        return jsonify({"ok": True})

    # requiere_login=True es lo que mira app.js para abrir el modal. Antes
    # comparaba el texto del mensaje, que es fragil: bastaba cambiarle una
    # palabra aqui para que el modal dejara de abrirse.
    return jsonify({
        "ok": False,
        "mensaje": "Debes iniciar sesión para continuar.",
        "requiere_login": True,
    }), 401
