"""
app/routes/carrito_routes.py

Carrito del cliente. Todas las acciones (agregar, cambiar cantidad,
eliminar) responden en JSON con los totales ya recalculados, para que la
pagina se actualice sola sin recargarse entera.
"""
from flask import Blueprint, jsonify, session, request, render_template, current_app

from app.formato import pesos
from app.services.carrito_service import CarritoService
from app.routes.decoradores import requiere_login

carrito_bp = Blueprint("carrito", __name__, url_prefix="/carrito")


def _totales_para_json(id_usuario):
    """
    Los totales del carrito listos para pintar en pantalla.

    Las cifras van ya formateadas en pesos colombianos ('$ 137.910') porque
    el filtro `pesos` es el mismo que usan las plantillas y el PDF: asi el
    JavaScript no tiene que reimplementar el formato y no hay riesgo de que
    la pagina muestre los miles de otra forma tras una actualizacion.
    """
    totales = CarritoService.calcular_totales(id_usuario, current_app.config["IVA_PORCENTAJE"])
    items = totales["items"]

    return {
        "num_items": len(items),
        "unidades": sum(i.cantidad for i in items),
        "subtotal": pesos(totales["subtotal"]),
        "iva": pesos(totales["iva"]),
        "costo_envio": pesos(totales["costo_envio"]),
        "total": pesos(totales["total"]),
        "envio_gratis": totales["envio_gratis"],
        "ciudad_envio": totales["ciudad_envio"],
        "falta_para_envio_gratis": pesos(totales["falta_para_envio_gratis"]),
        "lineas": {
            str(i.id_producto): pesos(float(i.producto.precio) * i.cantidad)
            for i in items
        },
    }


@carrito_bp.route("/")
@requiere_login
def ver_carrito():
    totales = CarritoService.calcular_totales(session["id_usuario"], current_app.config["IVA_PORCENTAJE"])
    return render_template("carrito.html", **totales)


@carrito_bp.route("/agregar", methods=["POST"])
@requiere_login
def agregar():
    id_producto = request.form.get("id_producto", type=int)
    cantidad = request.form.get("cantidad", default=1, type=int)
    try:
        CarritoService.agregar_producto(session["id_usuario"], id_producto, cantidad)
    except ValueError as e:
        return jsonify({"ok": False, "mensaje": str(e)}), 400
    return jsonify({"ok": True, "totales": _totales_para_json(session["id_usuario"])})


@carrito_bp.route("/actualizar", methods=["POST"])
@requiere_login
def actualizar():
    id_producto = request.form.get("id_producto", type=int)
    cantidad = request.form.get("cantidad", type=int)
    try:
        CarritoService.actualizar_cantidad(session["id_usuario"], id_producto, cantidad)
    except ValueError as e:
        return jsonify({"ok": False, "mensaje": str(e)}), 400
    return jsonify({"ok": True, "totales": _totales_para_json(session["id_usuario"])})


@carrito_bp.route("/eliminar", methods=["POST"])
@requiere_login
def eliminar():
    id_producto = request.form.get("id_producto", type=int)
    CarritoService.eliminar_producto(session["id_usuario"], id_producto)
    return jsonify({"ok": True, "totales": _totales_para_json(session["id_usuario"])})
