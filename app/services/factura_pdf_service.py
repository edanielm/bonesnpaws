"""
app/services/factura_pdf_service.py

Genera el PDF de una factura de venta.

Se usa ReportLab por portabilidad: es Python puro, se instala con pip en
Windows, macOS y Linux y no necesita librerias del sistema (a diferencia de
WeasyPrint, que en Windows exige instalar GTK aparte).

El PDF se arma en memoria y se devuelve como bytes; quien lo pida decide si
lo manda al navegador como descarga o lo guarda en disco.
"""
import os
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

from app.formato import pesos, pesos_letras, folio

# Paleta alineada con el sitio (azul y rosado pastel)
AZUL = colors.HexColor("#4d86b8")
AZUL_SUAVE = colors.HexColor("#e2ecf6")
ROSA = colors.HexColor("#e4718f")
TEXTO = colors.HexColor("#1a2c3f")
TEXTO_TENUE = colors.HexColor("#7a8c9e")
LINEA = colors.HexColor("#d3e0ec")

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def _estilos():
    base = getSampleStyleSheet()
    return {
        "empresa": ParagraphStyle("empresa", parent=base["Normal"], fontName="Helvetica-Bold",
                                  fontSize=17, textColor=AZUL, leading=20),
        "empresa_datos": ParagraphStyle("empresa_datos", parent=base["Normal"],
                                        fontSize=8.5, textColor=TEXTO_TENUE, leading=12),
        "titulo": ParagraphStyle("titulo", parent=base["Normal"], fontName="Helvetica-Bold",
                                 fontSize=13, textColor=TEXTO, alignment=TA_RIGHT, leading=16),
        "folio": ParagraphStyle("folio", parent=base["Normal"], fontName="Helvetica-Bold",
                                fontSize=15, textColor=ROSA, alignment=TA_RIGHT, leading=18),
        "meta": ParagraphStyle("meta", parent=base["Normal"], fontSize=8.5,
                               textColor=TEXTO_TENUE, alignment=TA_RIGHT, leading=12),
        "seccion": ParagraphStyle("seccion", parent=base["Normal"], fontName="Helvetica-Bold",
                                  fontSize=8, textColor=AZUL, leading=11),
        "normal": ParagraphStyle("normal", parent=base["Normal"], fontSize=9,
                                 textColor=TEXTO, leading=13),
        "celda": ParagraphStyle("celda", parent=base["Normal"], fontSize=8.5,
                                textColor=TEXTO, leading=11),
        "letras": ParagraphStyle("letras", parent=base["Normal"], fontSize=8.5,
                                 textColor=TEXTO, leading=12),
        "pie": ParagraphStyle("pie", parent=base["Normal"], fontSize=7.5,
                              textColor=TEXTO_TENUE, alignment=TA_CENTER, leading=10),
    }


def _fecha_larga(fecha):
    if not fecha:
        return "-"
    return f"{fecha.day} de {MESES[fecha.month - 1]} de {fecha.year}"


class FacturaPdfService:

    @staticmethod
    def generar(factura, cliente, empresa, prefijo="BP", nota="", logo=None):
        """
        Devuelve (bytes_del_pdf, nombre_de_archivo).

        `factura` debe traer cargados sus `detalles`; `cliente` es el dueno
        de la factura. Ambos llegan ya resueltos para que este servicio no
        consulte la base de datos: solo dibuja.

        `logo` es la ruta al archivo de imagen del membrete. Si no existe o
        no se puede leer, el PDF se genera igual sin el: una factura sin
        logo sigue siendo valida, una excepcion aqui dejaria al cliente sin
        su comprobante.
        """
        s = _estilos()
        buffer = BytesIO()
        numero = folio(factura.numero_factura, prefijo)

        doc = SimpleDocTemplate(
            buffer, pagesize=letter,
            leftMargin=18 * mm, rightMargin=18 * mm,
            topMargin=16 * mm, bottomMargin=16 * mm,
            title=f"Factura {numero} - {empresa['nombre']}",
            author=empresa["nombre"],
            subject="Factura de venta",
        )

        elementos = []

        # ---------- Encabezado: vendedor a la izquierda, factura a la derecha ----------
        datos_empresa = (
            f"NIT {empresa['nit']}<br/>"
            f"{empresa['direccion']}<br/>"
            f"{empresa['ciudad']}<br/>"
            f"Tel. {empresa['telefono']} &nbsp;·&nbsp; {empresa['correo']}"
        )
        emisor = [Paragraph(empresa["nombre"], s["empresa"]),
                  Spacer(1, 3), Paragraph(datos_empresa, s["empresa_datos"])]

        # El logo va en su propia columna, a la izquierda del nombre
        marca = _cargar_logo(logo)
        bloque_emisor = (
            Table([[marca, emisor]], colWidths=[19 * mm, None],
                  style=TableStyle([
                      ("VALIGN", (0, 0), (-1, -1), "TOP"),
                      ("LEFTPADDING", (0, 0), (-1, -1), 0),
                      ("RIGHTPADDING", (0, 0), (0, 0), 5),
                      ("TOPPADDING", (0, 0), (-1, -1), 0),
                      ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                  ]))
            if marca is not None else emisor
        )

        encabezado = Table(
            [[
                bloque_emisor,
                [Paragraph("FACTURA DE VENTA", s["titulo"]),
                 Paragraph(numero, s["folio"]),
                 Spacer(1, 3),
                 Paragraph(f"Fecha de expedición<br/>{_fecha_larga(factura.fecha)}", s["meta"])],
            ]],
            colWidths=[None, 62 * mm],
        )
        encabezado.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))
        elementos += [encabezado, Spacer(1, 6 * mm)]
        elementos.append(Table([[""]], colWidths=[doc.width], rowHeights=[1.6],
                               style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), AZUL)])))
        elementos.append(Spacer(1, 5 * mm))

        # ---------- Datos del cliente ----------
        cliente_izq = (
            f"<b>{cliente.nombre} {cliente.apellido}</b><br/>"
            f"Documento: {cliente.id_usuario}<br/>"
            f"{cliente.correo}"
        )
        cliente_der = (
            f"Teléfono: {cliente.telefono or '-'}<br/>"
            f"Dirección: {cliente.direccion or '-'}<br/>"
            f"Forma de pago: <b>{factura.metodo_pago}</b>"
        )
        bloque_cliente = Table(
            [[Paragraph("FACTURAR A", s["seccion"]), ""],
             [Paragraph(cliente_izq, s["normal"]), Paragraph(cliente_der, s["normal"])]],
            colWidths=[doc.width * 0.52, doc.width * 0.48],
        )
        bloque_cliente.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, 0), (-1, -1), AZUL_SUAVE),
            ("TOPPADDING", (0, 0), (-1, 0), 6),
            ("BOTTOMPADDING", (0, -1), (-1, -1), 7),
            ("LEFTPADDING", (0, 0), (-1, -1), 9),
            ("RIGHTPADDING", (0, 0), (-1, -1), 9),
            ("SPAN", (0, 0), (1, 0)),
        ]))
        elementos += [bloque_cliente, Spacer(1, 6 * mm)]

        # ---------- Detalle de productos ----------
        filas = [["#", "Descripción", "Cant.", "Valor unitario", "Valor total"]]
        for i, d in enumerate(factura.detalles, start=1):
            nombre = d.producto.nombre if d.producto else "Producto retirado del catálogo"
            filas.append([
                str(i),
                Paragraph(nombre, s["celda"]),
                str(d.cantidad),
                pesos(d.precio_unitario),
                pesos(d.subtotal_producto),
            ])

        tabla = Table(filas, colWidths=[10 * mm, None, 16 * mm, 30 * mm, 30 * mm], repeatRows=1)
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), AZUL),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("TEXTCOLOR", (0, 1), (-1, -1), TEXTO),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("ALIGN", (2, 0), (2, -1), "CENTER"),
            ("ALIGN", (3, 0), (-1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LINEBELOW", (0, 1), (-1, -1), 0.5, LINEA),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafd")]),
        ]))
        elementos += [tabla, Spacer(1, 5 * mm)]

        # ---------- Monto en letras + totales ----------
        totales = Table(
            [["Subtotal", pesos(factura.subtotal)],
             ["IVA (19%)", pesos(factura.iva)],
             ["Envío", pesos(factura.costo_envio)],
             ["TOTAL A PAGAR", pesos(factura.total)]],
            colWidths=[32 * mm, 30 * mm],
        )
        totales.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("TEXTCOLOR", (0, 0), (-1, -2), TEXTO_TENUE),
            ("LINEABOVE", (0, -1), (-1, -1), 0.8, LINEA),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, -1), (-1, -1), 11),
            ("TEXTCOLOR", (0, -1), (-1, -1), ROSA),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, -1), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))

        letras = Paragraph(
            f'<font color="#7a8c9e">Son:</font> {pesos_letras(factura.total)}', s["letras"]
        )
        cierre = Table([[letras, totales]], colWidths=[None, 64 * mm])
        cierre.setStyle(TableStyle([
            ("VALIGN", (0, 0), (0, 0), "TOP"),
            ("VALIGN", (1, 0), (1, 0), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))
        elementos += [cierre, Spacer(1, 10 * mm)]

        # ---------- Pie ----------
        elementos.append(Table([[""]], colWidths=[doc.width], rowHeights=[0.8],
                               style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), LINEA)])))
        elementos.append(Spacer(1, 3 * mm))
        elementos.append(Paragraph(
            f"Gracias por comprar en {empresa['nombre']} &nbsp;·&nbsp; {empresa['web']}", s["pie"]))
        if nota:
            elementos += [Spacer(1, 2 * mm), Paragraph(nota, s["pie"])]

        doc.build(elementos, onFirstPage=_numerar_pagina, onLaterPages=_numerar_pagina)

        return buffer.getvalue(), f"factura-{numero}.pdf"


def _cargar_logo(ruta, lado=16 * mm):
    """
    Devuelve el logo como Image de ReportLab, escalado a un cuadrado y
    conservando su proporcion. Si el archivo no existe o no se puede leer,
    devuelve None y el encabezado se arma sin el.
    """
    if not ruta or not os.path.isfile(ruta):
        return None
    try:
        ancho, alto = ImageReader(ruta).getSize()
        escala = min(lado / ancho, lado / alto)
        return Image(ruta, width=ancho * escala, height=alto * escala)
    except Exception:
        return None


def _numerar_pagina(canvas, doc):
    """Numero de pagina al pie, para facturas de mas de una hoja."""
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(TEXTO_TENUE)
    canvas.drawRightString(doc.pagesize[0] - 18 * mm, 10 * mm, f"Página {canvas.getPageNumber()}")
    canvas.restoreState()
