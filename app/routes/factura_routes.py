import os
from io import BytesIO

from flask import (
    Blueprint, abort, jsonify, session, request, render_template,
    current_app, send_file,
)

from app.extensions import db
from app.services.factura_service import FacturaService
from app.services.carrito_service import CarritoService
from app.services.factura_pdf_service import FacturaPdfService
from app.services.factura_word_service import FacturaWordService
from app.services.excel_service import ExcelService
from app.routes.decoradores import requiere_login

factura_bp = Blueprint("factura", __name__, url_prefix="/facturas")


@factura_bp.route("/checkout")
@requiere_login
def checkout():
    from app.models import Cliente  # local: evita un import circular al arrancar

    totales = CarritoService.calcular_totales(session["id_usuario"], current_app.config["IVA_PORCENTAJE"])
    cliente = db.session.get(Cliente, session["id_usuario"])
    return render_template(
        "facturas/crear.html",
        # A donde se despacha el pedido: es de donde sale la tarifa de envio,
        # asi que se muestra antes de pagar y no solo despues, en la factura.
        session_direccion=cliente.direccion if cliente else None,
        **totales,
    )


@factura_bp.route("/registrar", methods=["POST"])
@requiere_login
def registrar():
    metodo_pago = request.form.get("metodo_pago", "Tarjeta")
    datos_pago = {
        "banco": request.form.get("banco"),
        "numero_cuenta": request.form.get("numero_cuenta"),
        "titular": request.form.get("titular"),
        "numero_tarjeta": request.form.get("numero_tarjeta"),
        "franquicia": request.form.get("franquicia"),
        "fecha_vencimiento": request.form.get("fecha_vencimiento") or None,
    }
    try:
        factura = FacturaService.registrar_venta(
            session["id_usuario"], current_app.config["IVA_PORCENTAJE"], metodo_pago, datos_pago
        )
    except ValueError as e:
        return jsonify({"ok": False, "mensaje": str(e)}), 400

    return jsonify({"ok": True, "numero_factura": factura.numero_factura})


@factura_bp.route("/historial")
@requiere_login
def historial():
    # Cada factura trae su envio (relacion Factura.envio), asi que "Mis
    # compras" puede mostrar en que va el pedido y no solo cuanto costo.
    facturas = FacturaService.historial_cliente(session["id_usuario"])
    return render_template("facturas/listar.html", facturas=facturas)


def _factura_autorizada(numero_factura):
    """
    Devuelve (factura, cliente) si quien pide puede verla.

    Puede verla el cliente dueno de la factura y tambien cualquier empleado
    con sesion abierta -administrador o vendedor-, que necesita consultarlas
    desde el panel para atender al cliente. Cualquier otro caso corta con
    403: una factura lleva datos personales y el numero es un consecutivo
    facil de adivinar.
    """
    from app.models import Factura, Cliente

    factura = db.get_or_404(Factura, numero_factura)
    es_dueno = factura.id_usuario == session.get("id_usuario")
    es_del_equipo = "id_empleado" in session
    if not (es_dueno or es_del_equipo):
        abort(403)

    return factura, db.get_or_404(Cliente, factura.id_usuario)


@factura_bp.route("/<int:numero_factura>")
def detalle(numero_factura):
    factura, cliente = _factura_autorizada(numero_factura)
    return render_template("facturas/detalle.html", factura=factura, cliente=cliente)


MIME_PDF = "application/pdf"
MIME_WORD = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
MIME_EXCEL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _descargar_factura(numero_factura, generador, tipo_mime):
    """
    Genera la factura con `generador` (PDF o Word), se la manda por correo
    al cliente y la entrega como descarga.

    La copia por correo sale solo cuando quien descarga es el propio
    cliente: si un empleado la baja desde el panel para consultarla, el
    cliente no tiene por que recibir un correo que no pidio.
    """
    factura, cliente = _factura_autorizada(numero_factura)
    cfg = current_app.config

    contenido, nombre_archivo = generador(
        factura=factura,
        cliente=cliente,
        empresa=cfg["EMPRESA"],
        prefijo=cfg["FACTURA_PREFIJO"],
        nota=cfg["FACTURA_NOTA"],
        logo=os.path.join(current_app.static_folder, "img", "logo.png"),
    )

    if factura.id_usuario == session.get("id_usuario") and "id_empleado" not in session:
        _enviar_copia_al_cliente(factura, cliente, contenido, nombre_archivo, tipo_mime)

    return send_file(
        BytesIO(contenido),
        mimetype=tipo_mime,
        as_attachment=True,
        download_name=nombre_archivo,
    )


def _enviar_copia_al_cliente(factura, cliente, contenido, nombre_archivo, tipo_mime):
    """
    Manda la factura al correo registrado del cliente. Si el correo falla
    la descarga sigue igual: el cliente ya tiene su factura en la mano y un
    error de SMTP no debe quitarsela.
    """
    from app.formato import folio, pesos
    from app.services import correo_service

    cfg = current_app.config
    numero = folio(factura.numero_factura, cfg["FACTURA_PREFIJO"])
    texto = (
        f"Hola {cliente.nombre},\n\n"
        f"Te enviamos una copia de tu factura {numero} del "
        f"{factura.fecha:%d/%m/%Y} por {pesos(factura.total)}.\n"
        f"La encuentras adjunta a este correo.\n\n"
        f"¡Gracias por comprar en {cfg['EMPRESA']['nombre']}!\n"
        f"{cfg['EMPRESA']['web']}"
    )
    try:
        correo_service.enviar(
            cliente.correo,
            f"Tu factura {numero} — {cfg['EMPRESA']['nombre']}",
            texto,
            adjuntos=[(contenido, nombre_archivo, tipo_mime)],
        )
    except correo_service.CorreoNoEnviado as e:
        current_app.logger.warning("Factura %s descargada pero no enviada por correo: %s", numero, e)


@factura_bp.route("/<int:numero_factura>/pdf")
def descargar_pdf(numero_factura):
    """Descarga la factura como PDF (y se la manda al correo del cliente)."""
    return _descargar_factura(numero_factura, FacturaPdfService.generar, MIME_PDF)


@factura_bp.route("/<int:numero_factura>/word")
def descargar_word(numero_factura):
    """Descarga la factura como Word (y se la manda al correo del cliente)."""
    return _descargar_factura(numero_factura, FacturaWordService.generar, MIME_WORD)


@factura_bp.route("/historial/excel")
@requiere_login
def historial_excel():
    """Las compras del cliente con sesion abierta, en Excel."""
    contenido, nombre_archivo = ExcelService.compras_cliente(session["id_usuario"])
    return send_file(
        BytesIO(contenido),
        mimetype=MIME_EXCEL,
        as_attachment=True,
        download_name=nombre_archivo,
    )
