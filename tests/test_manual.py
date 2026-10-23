"""
tests/test_manual.py

Pruebas del manual de usuario en PDF.

Lo que se comprueba aqui:

  1. Que sea alcanzable **sin sesion**. Es el punto del manual: quien no
     sabe como crear una cuenta es justamente quien mas lo necesita.
  2. Que el enlace este en el pie de TODAS las paginas publicas, no solo
     en la portada.
  3. Que los numeros que nombra (IVA, envio gratis, duracion del codigo)
     sean los que de verdad aplica la tienda. Un manual que miente es peor
     que no tener manual, y es facil que se desfase sin que nadie lo note.

No se comprueba como se ve: para eso se renderizaron las paginas y se
miraron una por una.

    pytest tests/ -v
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.config import Config
from app.extensions import db
from app.models import Cliente
from app.services import manual_service

RUTAS_PUBLICAS = ["/", "/productos", "/categorias", "/acerca", "/contacto"]


class ConfigPrueba(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
    SECRET_KEY = "clave-de-prueba"


@pytest.fixture
def app():
    aplicacion = create_app(ConfigPrueba)
    with aplicacion.app_context():
        db.create_all()
        db.session.add(Cliente(
            id_usuario="1001", nombre="Laura", apellido="Gomez",
            correo="laura@correo.com", contrasena=generate_password_hash("123456"),
            telefono="3001234567", direccion="Calle 1 Bogotá",
        ))
        db.session.commit()
        # El manual se guarda en memoria tras la primera vez; entre pruebas
        # se limpia para que cada una lo arme con SU configuracion.
        manual_service._CACHE.clear()
        yield aplicacion
    manual_service._CACHE.clear()


@pytest.fixture
def client(app):
    return app.test_client()


def texto_del_pdf(contenido):
    """
    Saca el texto del PDF sin depender de ninguna libreria nueva.

    ReportLab escribe el contenido de cada pagina comprimido con zlib y
    luego codificado en ASCII85 (es lo que hace por defecto), asi que hay
    que deshacer las dos capas en ese orden. Dentro ya queda el flujo de
    dibujo, donde el texto son las cadenas entre parentesis de los
    operadores Tj/TJ.

    Es suficiente para lo que se quiere: comprobar que el manual *dice*
    ciertas cosas. No pretende ser un extractor de PDF completo.
    """
    import base64
    import zlib

    trozos = []
    for cuerpo in re.findall(rb"stream\r?\n(.*?)endstream", contenido, re.S):
        datos = cuerpo.strip()
        try:
            datos = base64.a85decode(datos, adobe=True)
        except Exception:
            pass  # el flujo no venia en ASCII85
        try:
            datos = zlib.decompress(datos)
        except zlib.error:
            pass  # ni comprimido
        for cadena in re.findall(rb"\((?:\\.|[^\\()])*\)", datos):
            trozos.append(cadena[1:-1])

    crudo = b" ".join(trozos)
    # ReportLab escapa los parentesis y la barra dentro de las cadenas
    crudo = crudo.replace(rb"\(", b"(").replace(rb"\)", b")").replace(rb"\\", b"\\")
    # El PDF guarda las tildes en WinAnsi, que para este rango es latin-1
    return crudo.decode("latin-1", errors="replace")


# ----------------------------------------------------------------------
# Llegar al manual
# ----------------------------------------------------------------------
def test_el_manual_se_abre_sin_sesion(client):
    """
    Va sin decorador a proposito. Si alguien le pone @requiere_login, esta
    prueba lo avisa.
    """
    r = client.get("/manual")

    assert r.status_code == 200
    assert r.mimetype == "application/pdf"
    assert r.get_data()[:5] == b"%PDF-"


def test_se_abre_dentro_del_navegador_y_no_como_descarga(client):
    """
    'inline' deja hojearlo desde el telefono sin guardar un archivo; el
    boton de descargar lo pone el propio visor.
    """
    r = client.get("/manual")

    assert "inline" in r.headers["Content-Disposition"]
    assert ".pdf" in r.headers["Content-Disposition"]


@pytest.mark.parametrize("ruta", RUTAS_PUBLICAS)
def test_el_enlace_esta_en_el_pie_de_cada_pagina(client, ruta):
    """
    El pie es comun a todas las paginas, pero una plantilla que no herede
    de base.html se quedaria sin el. Mejor comprobarlo en todas.
    """
    html = client.get(ruta).get_data(as_text=True)

    assert 'href="/manual"' in html, ruta
    assert "Manual de usuario" in html, ruta


def test_el_enlace_abre_en_otra_pestana_sin_dejar_puerta_abierta(client):
    """
    target="_blank" para no perder la pagina donde iba la persona, y
    rel="noopener" porque sin el la pestaña nueva puede manipular a la que
    la abrio.
    """
    html = client.get("/").get_data(as_text=True)
    enlace = re.search(r"<a[^>]*href=\"/manual\"[^>]*>", html).group(0)

    assert 'target="_blank"' in enlace
    assert "noopener" in enlace


def test_el_enlace_esta_en_la_seccion_de_ayuda(client):
    html = client.get("/").get_data(as_text=True)
    ayuda = html.split("<h4>Ayuda</h4>", 1)[1].split("</ul>", 1)[0]

    assert 'href="/manual"' in ayuda


# ----------------------------------------------------------------------
# Que diga la verdad
# ----------------------------------------------------------------------
def test_el_manual_trae_los_datos_de_contacto_reales(client):
    texto = texto_del_pdf(client.get("/manual").get_data())

    assert "antonietawsnpaws@gmail.com" in texto
    assert "321 390 1883" in texto
    assert "bonespaws_666" in texto


def test_los_numeros_salen_de_la_configuracion_y_no_escritos_a_mano(client, app):
    """
    Esta es la prueba que justifica generar el PDF en vez de tenerlo
    guardado: si cambia el IVA o el envio gratis, el manual cambia solo.
    """
    texto = texto_del_pdf(client.get("/manual").get_data())

    assert "%d%%" % round(app.config["IVA_PORCENTAJE"] * 100) in texto
    assert "250.000" in texto  # ENVIO_GRATIS_DESDE
    assert "Bogotá" in texto or "Bogot" in texto  # una ciudad de la tabla


def test_cambiar_la_configuracion_cambia_el_manual(app):
    """
    Se fuerza un valor distinto y se comprueba que el PDF lo refleja. Si
    alguien reemplaza esto por un archivo fijo en static/, falla.
    """
    with app.app_context():
        app.config["ENVIO_GRATIS_DESDE"] = 999000
        manual_service._CACHE.clear()
        contenido, _ = manual_service.obtener(app.config, recargar=True)

    assert "999.000" in texto_del_pdf(contenido)


def test_las_reglas_del_codigo_las_lee_del_modelo(client):
    """
    La duracion y los intentos del codigo de recuperacion viven en
    codigo_recuperacion.py, que es quien los aplica. El manual no puede
    decir 15 minutos si el codigo vence a los 10.
    """
    from app.models.codigo_recuperacion import INTENTOS_MAXIMOS, VIGENCIA_MINUTOS

    texto = texto_del_pdf(client.get("/manual").get_data())

    assert "%d minutos" % VIGENCIA_MINUTOS in texto
    assert str(INTENTOS_MAXIMOS) in texto


def test_el_manual_no_usa_simbolos_que_la_fuente_no_tiene():
    """
    El manual se dibuja con Helvetica, que solo cubre WinAnsi (cp1252).

    ReportLab intenta rescatar lo que falta sacándolo de una fuente de
    símbolos, pero ese rescate **no avisa cuando sale mal**: un ☰ (U+2630)
    para el botón del menú terminó dibujado como una letra 'n' torcida, y
    eso solo se vio mirando el PDF renderizado. Esta prueba corta ese tipo
    de error antes.

    Las tildes, la ñ, las comillas angulares, el guion largo y el punto de
    viñeta sí están en WinAnsi y pasan sin problema.
    """
    ruta = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "app", "services", "manual_service.py")
    with open(ruta, encoding="utf-8") as f:
        fuente = f.read()

    fuera = sorted({c for c in fuente if ord(c) > 127 and not _cabe_en_winansi(c)})

    assert fuera == [], (
        "Estos caracteres no existen en la fuente del PDF y van a salir mal: "
        + ", ".join("%r (U+%04X)" % (c, ord(c)) for c in fuera))


def _cabe_en_winansi(caracter):
    try:
        caracter.encode("cp1252")
        return True
    except UnicodeEncodeError:
        return False


def test_el_manual_avisa_que_la_tienda_es_ficticia(client):
    """Es un proyecto academico: el manual no puede dar a entender otra cosa."""
    texto = texto_del_pdf(client.get("/manual").get_data())

    assert "ficticia" in texto
    assert "no se procesan pagos" in texto


def test_el_manual_cubre_los_temas_que_prometen_su_indice(client):
    texto = texto_del_pdf(client.get("/manual").get_data())

    for tema in ("Crear una cuenta", "Entrar a tu cuenta", "El carrito",
                 "Comprar", "Tu perfil", "Contacto"):
        assert tema in texto, tema


# ----------------------------------------------------------------------
# Que no cueste de mas
# ----------------------------------------------------------------------
def test_el_manual_se_arma_una_sola_vez(app):
    """
    Dibujar el PDF cuesta; el contenido solo cambia si cambia el codigo o
    la configuracion, asi que no tiene sentido rehacerlo en cada visita.
    """
    with app.app_context():
        manual_service._CACHE.clear()
        primero, _ = manual_service.obtener(app.config)
        assert "pdf" in manual_service._CACHE

        segundo, _ = manual_service.obtener(app.config)

    # El mismo objeto, no uno nuevo igual: prueba que no se volvio a armar
    assert primero is segundo


def test_recargar_lo_vuelve_a_armar(app):
    """Es lo que hace la ruta en modo desarrollo."""
    with app.app_context():
        manual_service._CACHE.clear()
        primero, _ = manual_service.obtener(app.config)
        segundo, _ = manual_service.obtener(app.config, recargar=True)

    assert primero is not segundo


def test_el_manual_sale_aunque_falte_el_logo(app):
    """
    Un PDF sin logo se lee perfectamente; una excepcion aqui dejaria a la
    gente sin manual.
    """
    with app.app_context():
        manual_service._CACHE.clear()
        contenido, _ = manual_service.obtener(
            app.config, logo="no/existe/logo.png", recargar=True)

    assert contenido[:5] == b"%PDF-"
    assert len(contenido) > 10_000
