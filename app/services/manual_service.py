"""
app/services/manual_service.py

Genera el manual de usuario de la tienda en PDF.

Se arma con ReportLab, igual que la factura (ver factura_pdf_service.py),
por la misma razon: es Python puro y no necesita nada instalado aparte.

Por que se genera y no es un archivo suelto en static/
-----------------------------------------------------
El manual nombra datos que viven en la configuracion -el correo, el
telefono, el IVA, desde cuanto el envio es gratis, cuanto dura el codigo
de recuperacion-. Si fuera un PDF hecho a mano, cambiar la tarifa de envio
en config.py dejaria el manual mintiendo y nadie se enteraria. Armandolo
aqui, los numeros salen de la misma fuente que usa la tienda.

El resultado se guarda en memoria la primera vez que alguien lo pide
(_CACHE): el contenido solo cambia si cambia el codigo o la configuracion,
asi que no tiene sentido volver a dibujarlo en cada visita. En modo
desarrollo se rehace siempre, para ver los cambios al recargar.
"""
import os
from datetime import date
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, KeepTogether, NextPageTemplate, PageBreak,
    PageTemplate, Paragraph, Spacer, Table, TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

# Misma paleta del sitio y de la factura
AZUL = colors.HexColor("#4d86b8")
AZUL_SUAVE = colors.HexColor("#e2ecf6")
ROSA = colors.HexColor("#e4718f")
ROSA_SUAVE = colors.HexColor("#fbe6ec")
TEXTO = colors.HexColor("#1a2c3f")
TEXTO_TENUE = colors.HexColor("#7a8c9e")
LINEA = colors.HexColor("#d3e0ec")
AVISO_FONDO = colors.HexColor("#fdf6e3")
AVISO_BORDE = colors.HexColor("#e8d9a8")

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

ANCHO_UTIL = letter[0] - 36 * mm  # los dos margenes laterales de 18 mm

_CACHE = {}


# ----------------------------------------------------------------------
# Estilos
# ----------------------------------------------------------------------
def _estilos():
    base = getSampleStyleSheet()
    return {
        "portada_titulo": ParagraphStyle(
            "portada_titulo", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=30, textColor=AZUL, alignment=TA_CENTER, leading=34),
        "portada_sub": ParagraphStyle(
            "portada_sub", parent=base["Normal"], fontSize=13,
            textColor=TEXTO_TENUE, alignment=TA_CENTER, leading=18),
        "portada_pie": ParagraphStyle(
            "portada_pie", parent=base["Normal"], fontSize=9,
            textColor=TEXTO_TENUE, alignment=TA_CENTER, leading=14),
        # El nombre 'h_seccion' lo mira afterFlowable para armar el indice:
        # si se cambia aqui, hay que cambiarlo alla.
        "h_seccion": ParagraphStyle(
            "h_seccion", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=15, textColor=AZUL, leading=19,
            spaceBefore=16, spaceAfter=7),
        # Mismo aspecto que h_seccion pero con otro nombre, porque
        # afterFlowable arma el indice mirando el nombre del estilo: con
        # "h_seccion" el titulo "Contenido" se listaba dentro del propio
        # indice, apuntando a su misma pagina.
        "h_indice": ParagraphStyle(
            "h_indice", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=15, textColor=AZUL, leading=19, spaceAfter=10),
        "h_sub": ParagraphStyle(
            "h_sub", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=11, textColor=TEXTO, leading=15,
            spaceBefore=10, spaceAfter=4),
        "normal": ParagraphStyle(
            "normal", parent=base["Normal"], fontSize=9.5, textColor=TEXTO,
            leading=14, alignment=TA_JUSTIFY, spaceAfter=5),
        "paso": ParagraphStyle(
            "paso", parent=base["Normal"], fontSize=9.5, textColor=TEXTO,
            leading=14, leftIndent=14, bulletIndent=2, spaceAfter=4),
        "punto": ParagraphStyle(
            "punto", parent=base["Normal"], fontSize=9.5, textColor=TEXTO,
            leading=14, leftIndent=14, bulletIndent=4, spaceAfter=3),
        "aviso": ParagraphStyle(
            "aviso", parent=base["Normal"], fontSize=9, textColor=TEXTO,
            leading=13),
        "celda": ParagraphStyle(
            "celda", parent=base["Normal"], fontSize=8.8, textColor=TEXTO,
            leading=12),
        "celda_tit": ParagraphStyle(
            "celda_tit", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=8.8, textColor=colors.white, leading=12),
        "indice1": ParagraphStyle(
            "indice1", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=10, textColor=TEXTO, leading=20),
    }


# ----------------------------------------------------------------------
# Piezas reutilizables
# ----------------------------------------------------------------------
def _pasos(s, textos):
    """Lista numerada. ReportLab la arma con bulletText, no con <ol>."""
    return [Paragraph(t, s["paso"], bulletText="%d." % (i + 1))
            for i, t in enumerate(textos)]


def _puntos(s, textos):
    return [Paragraph(t, s["punto"], bulletText="•") for t in textos]


def _aviso(s, texto, color_fondo=AVISO_FONDO, color_borde=AVISO_BORDE):
    """
    Recuadro de nota. Va dentro de una tabla de una celda porque ReportLab
    no sabe ponerle fondo ni borde a un parrafo suelto.
    """
    t = Table([[Paragraph(texto, s["aviso"])]], colWidths=[ANCHO_UTIL])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color_fondo),
        ("BOX", (0, 0), (-1, -1), 0.6, color_borde),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return [Spacer(1, 4), t, Spacer(1, 6)]


def _tabla(s, encabezados, filas, anchos=None):
    datos = [[Paragraph(c, s["celda_tit"]) for c in encabezados]]
    datos += [[Paragraph(str(c), s["celda"]) for c in fila] for fila in filas]

    t = Table(datos, colWidths=anchos or [ANCHO_UTIL / len(encabezados)] * len(encabezados),
              repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, AZUL_SUAVE]),
        ("GRID", (0, 0), (-1, -1), 0.4, LINEA),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return [Spacer(1, 4), t, Spacer(1, 8)]


def _ficha(s, filas):
    """
    Tabla de dos columnas sin encabezado, para listas de datos tipo
    "Correo: ...". Con _tabla quedaba una franja azul vacia arriba.
    """
    datos = [[Paragraph("<b>%s</b>" % k, s["celda"]), Paragraph(str(v), s["celda"])]
             for k, v in filas]
    t = Table(datos, colWidths=[ANCHO_UTIL * 0.22, ANCHO_UTIL * 0.78])
    t.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, AZUL_SUAVE]),
        ("GRID", (0, 0), (-1, -1), 0.4, LINEA),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return [Spacer(1, 4), t, Spacer(1, 8)]


def _seccion(s, titulo):
    """
    Titulo de seccion. Se marca para que el indice lo recoja solo (ver
    _PlantillaManual.afterFlowable).
    """
    return Paragraph(titulo, s["h_seccion"])


def _cargar_logo(ruta, alto_mm=22):
    """
    El logo del membrete. Si falta el archivo el manual se genera igual:
    un PDF sin logo se lee perfectamente, y una excepcion aqui dejaria a
    la gente sin manual.
    """
    if not ruta or not os.path.isfile(ruta):
        return None
    try:
        lector = ImageReader(ruta)
        ancho_px, alto_px = lector.getSize()
        alto = alto_mm * mm
        return Image(ruta, width=alto * (ancho_px / alto_px), height=alto)
    except Exception:
        return None


def _fecha_larga(f):
    return "%d de %s de %d" % (f.day, MESES[f.month - 1], f.year)


# ----------------------------------------------------------------------
# Plantilla con pie de pagina numerado e indice automatico
# ----------------------------------------------------------------------
class _PlantillaManual(BaseDocTemplate):
    """
    BaseDocTemplate (y no SimpleDocTemplate) porque hacen falta dos cosas
    que aquel no da: una portada sin pie de pagina y un indice que sepa en
    que pagina quedo cada seccion.
    """

    def __init__(self, buffer, empresa, **kw):
        self.empresa = empresa
        BaseDocTemplate.__init__(self, buffer, pagesize=letter,
                                 leftMargin=18 * mm, rightMargin=18 * mm,
                                 topMargin=18 * mm, bottomMargin=20 * mm, **kw)

        marco = Frame(self.leftMargin, self.bottomMargin,
                      self.width, self.height, id="cuerpo")
        self.addPageTemplates([
            PageTemplate(id="portada", frames=[marco]),
            PageTemplate(id="cuerpo", frames=[marco], onPage=self._pie),
        ])

    def _pie(self, canvas, doc):
        canvas.saveState()
        y = 13 * mm
        canvas.setStrokeColor(LINEA)
        canvas.setLineWidth(0.5)
        canvas.line(self.leftMargin, y + 5 * mm,
                    self.leftMargin + self.width, y + 5 * mm)

        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(TEXTO_TENUE)
        canvas.drawString(self.leftMargin, y,
                          "%s — Manual de usuario" % self.empresa["nombre"])
        canvas.drawRightString(self.leftMargin + self.width, y,
                               "Página %d" % canvas.getPageNumber())
        canvas.restoreState()

    def afterFlowable(self, flowable):
        """Cada titulo de seccion se anota en el indice con su pagina."""
        if isinstance(flowable, Paragraph) and flowable.style.name == "h_seccion":
            self.notify("TOCEntry", (0, flowable.getPlainText(), self.page))


# ----------------------------------------------------------------------
# El manual
# ----------------------------------------------------------------------
class ManualService:

    @staticmethod
    def generar(empresa, iva, envio_gratis_desde, envio_tarifas, envio_dias,
                vigencia_codigo_min, intentos_codigo, digitos_codigo,
                intentos_antes_de_captcha, logo=None):
        """
        Devuelve (bytes_del_pdf, nombre_de_archivo).

        Los numeros llegan por parametro y no se leen de la configuracion
        aqui dentro, por la misma razon que en FacturaPdfService: este
        servicio solo dibuja, no averigua.
        """
        s = _estilos()
        buffer = BytesIO()
        hoy = date.today()

        doc = _PlantillaManual(
            buffer, empresa,
            title="Manual de usuario — %s" % empresa["nombre"],
            author=empresa["nombre"],
            subject="Manual de usuario de la tienda en linea",
        )

        e = []

        # ---------------- Portada ----------------
        e.append(Spacer(1, 38 * mm))
        marca = _cargar_logo(logo, alto_mm=30)
        if marca is not None:
            marca.hAlign = "CENTER"
            e.append(marca)
            e.append(Spacer(1, 10 * mm))

        e.append(Paragraph("Manual de usuario", s["portada_titulo"]))
        e.append(Spacer(1, 4 * mm))
        e.append(Paragraph(empresa["nombre"], s["portada_sub"]))
        e.append(Spacer(1, 2 * mm))
        e.append(Paragraph("Tienda en línea de productos para mascotas",
                           s["portada_sub"]))
        e.append(Spacer(1, 26 * mm))
        e.append(Paragraph(
            "Cómo usar la tienda paso a paso: crear tu cuenta, encontrar lo que "
            "buscas, comprar, seguir tu pedido y recuperar tu contraseña.",
            s["portada_pie"]))
        e.append(Spacer(1, 16 * mm))
        e.append(Paragraph("Actualizado el %s" % _fecha_larga(hoy), s["portada_pie"]))

        # ---------------- Indice ----------------
        e.append(NextPageTemplate("cuerpo"))
        e.append(PageBreak())
        e.append(Paragraph("Contenido", s["h_indice"]))

        indice = TableOfContents()
        indice.levelStyles = [s["indice1"]]
        indice.dotsMinLevel = 0
        e.append(indice)
        e.append(PageBreak())

        # ---------------- 1. Antes de empezar ----------------
        e.append(_seccion(s, "1. Antes de empezar"))
        e.append(Paragraph(
            "%s es una tienda en línea de alimento, accesorios y artículos de "
            "cuidado para perros, gatos y otras mascotas. Este manual explica "
            "cómo usarla desde el navegador, en el computador o en el teléfono."
            % empresa["nombre"], s["normal"]))
        e.append(Paragraph(
            "No hace falta tener cuenta para mirar: el catálogo, las categorías, "
            "las fichas de cada producto y este mismo manual están abiertos para "
            "cualquiera. La cuenta se necesita solo para <b>comprar</b>, porque "
            "el carrito y las facturas quedan guardados a tu nombre.",
            s["normal"]))

        e.append(Paragraph("Qué necesitas", s["h_sub"]))
        e.extend(_puntos(s, [
            "Un navegador al día: Chrome, Edge, Firefox o Safari.",
            "Conexión a internet.",
            "Un correo electrónico al que tengas acceso. Es con el que entras "
            "y es a donde llega el código si olvidas tu contraseña.",
        ]))

        e.append(Paragraph("La barra de arriba", s["h_sub"]))
        e.extend(_puntos(s, [
            "<b>Bones &amp; Paws</b> (el logo): vuelve a la página de inicio.",
            "<b>Inicio, Productos, Categorías, Acerca de, Contacto</b>: las "
            "secciones de la tienda.",
            "<b>Sol / luna</b>: cambia entre modo claro y modo oscuro. La tienda "
            "recuerda cuál elegiste.",
            "<b>Carrito</b>: lo que llevas hasta ahora.",
            "<b>Iniciar sesión</b> y <b>Regístrate</b>: abren la ventana del gato.",
        ]))

        e.extend(_aviso(s,
            "<b>En el teléfono</b> los enlaces no caben en la barra, así que se "
            "guardan detrás del <b>botón de las tres rayas</b>, arriba a la "
            "derecha, al lado del carrito. Tócalo y aparecen todos, junto con "
            "los botones de entrar y registrarte."))

        # ---------------- 2. Crear una cuenta ----------------
        e.append(_seccion(s, "2. Crear una cuenta"))
        e.extend(_pasos(s, [
            "Pulsa <b>Regístrate</b> en la barra de arriba. Se abre la ventana "
            "del gato negro.",
            "Llena tus datos: nombres, apellidos, número de documento, teléfono "
            "y dirección.",
            "Escribe tu correo electrónico y la contraseña que vas a usar. "
            "Repítela en <b>Confirmar contraseña</b>.",
            "Escribe en la casilla el <b>código que aparece en la imagen</b> "
            "(el captcha).",
            "Pulsa <b>Registrarse</b>. Entras a la tienda de una vez, sin tener "
            "que iniciar sesión aparte.",
        ]))

        e.append(Paragraph("Sobre la contraseña", s["h_sub"]))
        e.extend(_puntos(s, [
            "Mínimo <b>6 caracteres</b>.",
            "El <b>ojito</b> al lado derecho de la casilla te deja ver lo que "
            "estás escribiendo, para comprobar que no te equivocaste. Vuelve a "
            "pulsarlo para ocultarla.",
            "La tienda <b>nunca guarda tu contraseña tal cual</b>: guarda una "
            "versión cifrada. Ni el personal de la tienda puede leerla.",
        ]))

        e.append(Paragraph("Sobre el código de la imagen", s["h_sub"]))
        e.append(Paragraph(
            "Ese dibujo con letras torcidas sirve para comprobar que hay una "
            "persona del otro lado y no un programa abriendo cuentas en lote. "
            "Escríbelo tal como lo ves; da igual si lo pones en mayúsculas o en "
            "minúsculas. Si no se entiende, pulsa el botón de la flecha circular "
            "que está al lado para que te dibuje otro.",
            s["normal"]))

        e.extend(_aviso(s,
            "<b>Si te dice que el documento o el correo ya están registrados</b>, "
            "es que ya tienes cuenta. Pulsa <b>Inicia Sesión</b> al final de la "
            "ventana; y si no recuerdas la contraseña, mira la sección 4."))

        # ---------------- 3. Entrar ----------------
        e.append(_seccion(s, "3. Entrar a tu cuenta"))
        e.extend(_pasos(s, [
            "Pulsa <b>Iniciar sesión</b> en la barra de arriba.",
            "Escribe tu correo y tu contraseña.",
            "Pulsa <b>Entrar</b>.",
        ]))
        e.append(Paragraph(
            "Al entrar, tu nombre aparece arriba a la derecha. Desde ahí llegas a "
            "tu perfil, y al lado está el botón para <b>Salir</b>.",
            s["normal"]))

        e.extend(_aviso(s,
            "<b>Si te equivocas %d veces seguidas</b>, la tienda empieza a "
            "pedirte también el código de la imagen. No es un castigo: es para "
            "frenar a un programa que esté probando contraseñas una por una. "
            "Cuando entras bien, el contador vuelve a cero."
            % intentos_antes_de_captcha))

        # ---------------- 4. Recuperar contrasena ----------------
        e.append(_seccion(s, "4. Si olvidaste tu contraseña"))
        e.append(Paragraph(
            "La tienda te manda un <b>código de %d dígitos</b> al correo con el "
            "que te registraste. Son dos pasos." % digitos_codigo, s["normal"]))

        e.append(Paragraph("Paso 1: pedir el código", s["h_sub"]))
        e.extend(_pasos(s, [
            "Abre <b>Iniciar sesión</b> y pulsa <b>¿Olvidaste tu contraseña?</b>",
            "Escribe tu <b>número de documento</b> y tu <b>correo</b>. Tienen que "
            "ser los dos de la misma cuenta.",
            "Escribe el código de la imagen.",
            "Pulsa <b>Enviarme el código</b>.",
        ]))
        e.append(Paragraph(
            "La pantalla te confirma a qué correo lo mandó, con la dirección "
            "tapada en parte (por ejemplo <i>an**********s@gmail.com</i>), para "
            "que nadie que esté mirando tu pantalla se entere de tu correo "
            "completo.", s["normal"]))

        e.append(Paragraph("Paso 2: cambiar la contraseña", s["h_sub"]))
        e.extend(_pasos(s, [
            "Abre tu correo y copia el código de %d dígitos. Llega en el asunto "
            "del mensaje, así que lo ves sin abrirlo." % digitos_codigo,
            "Vuelve a la tienda y escríbelo en la casilla.",
            "Escribe tu contraseña nueva dos veces. Mínimo 6 caracteres; el "
            "ojito te deja comprobar que las dos coinciden.",
            "Pulsa <b>Cambiar contraseña</b>. Ya puedes entrar con la nueva.",
        ]))

        e.extend(_aviso(s,
            "<b>El código dura %d minutos</b> y sirve <b>una sola vez</b>. "
            "Tienes %d intentos para escribirlo bien; al pasarte, hay que pedir "
            "uno nuevo. Si pides otro código, el anterior deja de servir."
            % (vigencia_codigo_min, intentos_codigo)))

        e.append(Paragraph("Si el correo no llega", s["h_sub"]))
        e.extend(_puntos(s, [
            "Revisa la carpeta de <b>correo no deseado</b> o <b>spam</b>.",
            "Comprueba que el documento y el correo sean los de tu cuenta: si no "
            "coinciden entre sí, la tienda no manda nada.",
            "Hay que esperar <b>un minuto</b> entre un envío y el siguiente.",
            "Si aún así no llega, escríbenos a %s." % empresa["correo"],
        ]))

        e.extend(_aviso(s,
            "<b>Nadie de la tienda te va a pedir ese código</b>, ni por correo, "
            "ni por teléfono, ni por redes. Si alguien te lo pide, no se lo des."))

        # ---------------- 5. Encontrar productos ----------------
        e.append(_seccion(s, "5. Encontrar lo que buscas"))
        e.extend(_puntos(s, [
            "<b>Productos</b> muestra el catálogo completo, de a una página por "
            "vez. Abajo están los números para pasar de página.",
            "<b>Categorías</b> los agrupa por tipo: alimento, accesorios, "
            "higiene y cuidado.",
            "El <b>buscador</b> encuentra por nombre, por descripción y también "
            "por el código del producto.",
            "Pulsa cualquier producto para ver su ficha: fotos, descripción, "
            "precio y cuántas unidades quedan.",
        ]))
        e.append(Paragraph(
            "Si un producto está agotado, su botón aparece desactivado. Sigue "
            "visible a propósito, para que sepas que existe y puedas volver a "
            "buscarlo más adelante.", s["normal"]))

        # ---------------- 6. El carrito ----------------
        e.append(_seccion(s, "6. El carrito"))
        e.append(Paragraph(
            "Para agregar algo al carrito hay que <b>haber entrado</b>. Si "
            "pulsas el botón sin sesión, la tienda te abre la ventana de inicio "
            "de sesión; al entrar sigues donde ibas.", s["normal"]))
        e.extend(_puntos(s, [
            "Elige la cantidad con los botones <b>-</b> y <b>+</b> y pulsa "
            "<b>Agregar al carrito</b>.",
            "El número sobre el icono del carrito te dice cuántos productos "
            "llevas.",
            "Dentro del carrito puedes cambiar cantidades o quitar lo que no "
            "quieras; los totales se recalculan solos.",
            "El carrito <b>queda guardado</b>: si cierras sesión y vuelves otro "
            "día, sigue ahí.",
        ]))
        e.extend(_aviso(s,
            "No puedes pedir más unidades de las que hay en existencia. La "
            "tienda te avisa en cuánto se detuvo y por qué."))

        # ---------------- 7. Comprar ----------------
        e.append(_seccion(s, "7. Comprar"))
        e.extend(_pasos(s, [
            "Desde el carrito, pulsa <b>Continuar la compra</b>.",
            "Revisa la dirección de entrega. Sale de la que registraste en tu "
            "perfil, así que si te mudaste, cámbiala antes en <b>Mi perfil</b>.",
            "Elige cómo pagar y llena los datos que te pida.",
            "Revisa el resumen: subtotal, IVA, envío y total.",
            "Pulsa <b>Confirmar compra</b>. Te lleva directo a tu factura.",
        ]))

        e.append(Paragraph("Formas de pago", s["h_sub"]))
        e.extend(_puntos(s, [
            "<b>Tarjeta</b> de crédito o débito.",
            "<b>PSE</b>, con tu banco.",
            "<b>Transferencia bancaria</b>.",
        ]))

        e.append(Paragraph("Cómo se calcula lo que pagas", s["h_sub"]))
        e.extend(_puntos(s, [
            "<b>Subtotal</b>: la suma de lo que llevas.",
            "<b>IVA</b>: %d%%, el que rige en Colombia." % round(iva * 100),
            "<b>Envío</b>: depende de la ciudad de tu dirección. Entre %s y %s."
            % (_pesos(min(envio_tarifas.values())), _pesos(max(envio_tarifas.values()))),
            "<b>Envío gratis</b> cuando la compra llega a %s."
            % _pesos(envio_gratis_desde),
        ]))

        ciudades = sorted(envio_tarifas.items(), key=lambda x: (x[1], x[0]))
        filas = []
        for i in range(0, len(ciudades), 2):
            par = ciudades[i:i + 2]
            fila = []
            for ciudad, valor in par:
                fila += [ciudad, _pesos(valor)]
            while len(fila) < 4:
                fila.append("")
            filas.append(fila)
        e.extend(_tabla(s, ["Ciudad", "Envío", "Ciudad", "Envío"], filas,
                        anchos=[ANCHO_UTIL * 0.3, ANCHO_UTIL * 0.2] * 2))
        e.append(Paragraph(
            "Si tu ciudad no está en la lista, se cobra la tarifa general. La "
            "entrega tarda alrededor de %d días hábiles." % envio_dias,
            s["normal"]))

        # ---------------- 8. Factura y pedido ----------------
        e.append(_seccion(s, "8. Tu factura y tu pedido"))
        e.append(Paragraph(
            "Cada compra genera una factura y una guía de envío. Las encuentras "
            "en <b>Mi perfil</b>, sección <b>Mis compras</b>.", s["normal"]))
        e.extend(_puntos(s, [
            "La factura trae el detalle de lo que compraste, el IVA, el envío y "
            "el total, también escrito en letras.",
            "Puedes <b>descargarla en PDF</b> o imprimirla.",
            "Cada pedido tiene un <b>número de guía</b> y una fecha estimada de "
            "entrega.",
        ]))

        e.append(Paragraph("En qué va tu pedido", s["h_sub"]))
        e.extend(_tabla(s, ["Estado", "Qué significa"], [
            ["Pendiente", "La compra quedó registrada y el pedido se está "
                          "preparando para salir."],
            ["En camino", "El pedido ya salió con la transportadora."],
            ["Entregado", "El pedido llegó a la dirección."],
        ], anchos=[ANCHO_UTIL * 0.25, ANCHO_UTIL * 0.75]))

        e.extend(_aviso(s,
            "<b>Tus facturas son solo tuyas.</b> Aunque alguien adivine el "
            "número de otra factura, la tienda no se la muestra."))

        # ---------------- 9. Perfil ----------------
        e.append(_seccion(s, "9. Tu perfil"))
        e.append(Paragraph(
            "Pulsa tu nombre arriba a la derecha para abrir <b>Mi perfil</b>. "
            "Ahí ves tus datos y tu historial de compras.", s["normal"]))
        e.extend(_puntos(s, [
            "Puedes cambiar tu <b>teléfono</b> y tu <b>dirección</b>. La "
            "dirección es la que se usa para calcular el envío de tu próxima "
            "compra.",
            "El <b>nombre</b>, el <b>documento</b> y el <b>correo</b> no se "
            "editan desde aquí: identifican la cuenta y aparecen en facturas ya "
            "emitidas. Si alguno quedó mal, escríbenos.",
        ]))

        # ---------------- 10. Chat ----------------
        e.append(_seccion(s, "10. El chat de ayuda"))
        e.append(Paragraph(
            "Abajo a la derecha, en todas las páginas, hay una burbuja de chat. "
            "Es <b>Chantonieta</b>, una ayuda automática que responde preguntas "
            "frecuentes sobre cómo comprar, las formas de pago, los envíos, el "
            "catálogo y los horarios. No hace falta tener cuenta para usarla.",
            s["normal"]))
        e.append(Paragraph(
            "Si tu pregunta se sale de eso, te pasa nuestros datos de contacto "
            "para que hables con una persona.", s["normal"]))

        # ---------------- 11. Problemas ----------------
        e.append(_seccion(s, "11. Si algo no sale bien"))
        e.extend(_tabla(s, ["Lo que ves", "Qué hacer"], [
            ["«Correo o contraseña incorrectos»",
             "Revisa que no haya espacios de más. Usa el ojito para ver lo que "
             "escribiste. Si no la recuerdas, mira la sección 4."],
            ["Te pide el código de la imagen al entrar",
             "Pasa después de %d intentos fallidos. Escríbelo y entra "
             "normalmente." % intentos_antes_de_captcha],
            ["«El código de la imagen no coincide»",
             "El dibujo cambia en cada intento: escribe el que estás viendo "
             "ahora, no el anterior."],
            ["«El código venció o ya se usó»",
             "Los códigos del correo duran %d minutos y sirven una vez. "
             "Pide otro." % vigencia_codigo_min],
            ["Te manda a la pantalla de entrar",
             "El carrito, las compras y el perfil necesitan sesión. Entra y "
             "vuelve a intentarlo."],
            ["No puedes agregar más unidades",
             "No quedan más en existencia. La tienda te dice cuántas hay."],
            ["La página se ve rara",
             "Recárgala. Si sigue igual, prueba con otro navegador o borra la "
             "caché."],
        ], anchos=[ANCHO_UTIL * 0.36, ANCHO_UTIL * 0.64]))

        # ---------------- 12. Equipo ----------------
        e.append(_seccion(s, "12. Para el equipo de la tienda"))
        e.append(Paragraph(
            "Las cuentas del personal no se crean desde la tienda: las abre un "
            "administrador. Entran por el <b>mismo formulario</b> que los "
            "clientes y la tienda los lleva sola a donde corresponde.",
            s["normal"]))
        e.extend(_tabla(s, ["Rol", "Qué puede hacer"], [
            ["Administrador",
             "Todo el panel: estadísticas de ventas, catálogo, fotos de "
             "producto, envíos, cuentas de clientes y cuentas del personal."],
            ["Vendedor",
             "Catálogo, fotos de producto, envíos y consulta de clientes. No "
             "ve las estadísticas ni gestiona cuentas."],
        ], anchos=[ANCHO_UTIL * 0.28, ANCHO_UTIL * 0.72]))
        e.append(Paragraph(
            "Al eliminar un producto que ya se vendió, no se borra: se oculta "
            "de la tienda. Sus facturas tienen que seguir cuadrando.",
            s["normal"]))

        # ---------------- 13. Contacto ----------------
        # KeepTogether: sin esto el titulo quedaba al final de una pagina y
        # la tabla de datos saltaba a la siguiente, casi vacia.
        e.append(KeepTogether([
            _seccion(s, "13. Contacto"),
            Paragraph(
                "Si algo no se resuelve con este manual ni con el chat, "
                "escríbenos. Respondemos en horario de atención.", s["normal"]),
        ] + _ficha(s, [
            ("Correo", empresa["correo"]),
            ("Teléfono", empresa["telefono"]),
            ("Instagram", "@%s" % empresa.get("instagram", "")),
            ("Dirección", "%s, %s" % (empresa["direccion"], empresa["ciudad"])),
            ("Horario", empresa["horario"]),
        ])))

        e.extend(_aviso(s,
            "<b>Aviso.</b> %s es una tienda ficticia creada como proyecto "
            "académico. El catálogo permite recorrer el proceso de compra "
            "completo, pero <b>no se procesan pagos ni envíos reales</b> y los "
            "comprobantes no tienen validez fiscal."
            % empresa["nombre"], ROSA_SUAVE, ROSA))

        # multiBuild y no build: el indice necesita dos pasadas, una para
        # averiguar en que pagina quedo cada seccion y otra para escribirlo.
        doc.multiBuild(e)

        return buffer.getvalue(), "Manual-de-usuario-Bones-and-Paws.pdf"


def _pesos(valor):
    """
    '$ 14.000'. No se usa app.formato.pesos porque aquel devuelve el texto
    con el simbolo pensado para HTML; aqui basta esto y evita el import.
    """
    return "$ {:,.0f}".format(valor).replace(",", ".")


def obtener(config, logo=None, recargar=False):
    """
    El manual listo para servir, con los numeros de la configuracion.

    Se guarda en memoria tras la primera vez. `recargar=True` lo rehace;
    es lo que hace la ruta en modo desarrollo, para ver los cambios al
    recargar la pagina en vez de tener que reiniciar el servidor.
    """
    # Las dos reglas del codigo de recuperacion viven con el modelo, que es
    # quien las aplica. Se leen de ahi para que el manual no pueda decir
    # "15 minutos" mientras el codigo vence a los 10.
    from app.models.codigo_recuperacion import INTENTOS_MAXIMOS, VIGENCIA_MINUTOS
    from app.routes.auth_routes import INTENTOS_ANTES_DE_CAPTCHA
    from app.services.recuperacion_service import LONGITUD_CODIGO

    if recargar or "pdf" not in _CACHE:
        _CACHE["pdf"] = ManualService.generar(
            empresa=config["EMPRESA"],
            iva=config["IVA_PORCENTAJE"],
            envio_gratis_desde=config["ENVIO_GRATIS_DESDE"],
            envio_tarifas=config["ENVIO_TARIFAS"],
            envio_dias=config["ENVIO_DIAS_ESTIMADOS"],
            vigencia_codigo_min=VIGENCIA_MINUTOS,
            intentos_codigo=INTENTOS_MAXIMOS,
            digitos_codigo=LONGITUD_CODIGO,
            intentos_antes_de_captcha=INTENTOS_ANTES_DE_CAPTCHA,
            logo=logo,
        )
    return _CACHE["pdf"]
