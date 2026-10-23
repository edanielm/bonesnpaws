"""
tests/test_auth_captcha_correo.py

Pruebas del captcha y de la recuperacion de contrasena por correo.

Corren sobre SQLite en memoria, igual que test_rutas_publicas.py, y **no
mandan correo de verdad**: se reemplaza la funcion que habla con el
servidor SMTP por una que guarda el mensaje en una lista, para poder leer
el codigo que iba dentro tal como lo leeria la persona en su bandeja.

Del captcha no se puede "mirar la imagen", asi que se fija el sorteo del
codigo (fijar_codigo_captcha) para saber que salio dibujado. Lo que se
prueba igual es lo que importa: que sin el captcha correcto no se pasa,
que no sirve dos veces y que no se puede leer desde el navegador.

    pytest tests/ -v
"""
import os
import re
import smtplib
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from werkzeug.security import check_password_hash, generate_password_hash

from app import create_app
from app.config import Config
from app.extensions import db
from app.models import Cliente, CodigoRecuperacion
from app.services import captcha_service, correo_service, recuperacion_service

DOCUMENTO = "1001"
CORREO = "laura@correo.com"
CONTRASENA = "123456"

# Lo que queda "dibujado" en la imagen durante las pruebas.
CAPTCHA_FIJO = "ABCDE"


class ConfigPrueba(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
    # DEBUG en False a proposito: con DEBUG el servicio de correo vuelca el
    # mensaje en la consola en vez de enviarlo, y aqui se quiere ejercitar
    # el camino de envio real (interceptado).
    DEBUG = False
    SECRET_KEY = "clave-de-prueba"
    MAIL_USUARIO = "tienda@bonesandpaws.co"
    MAIL_CONTRASENA = "contrasena-de-aplicacion-falsa"
    MAIL_REMITENTE = "tienda@bonesandpaws.co"


@pytest.fixture
def app():
    aplicacion = create_app(ConfigPrueba)
    with aplicacion.app_context():
        db.create_all()
        db.session.add(Cliente(
            id_usuario=DOCUMENTO, nombre="Laura", apellido="Gomez", correo=CORREO,
            contrasena=generate_password_hash(CONTRASENA),
            telefono="3001234567", direccion="Calle 1 Bogotá",
        ))
        db.session.commit()
        yield aplicacion


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def buzon(monkeypatch):
    """
    Intercepta el envio: devuelve la lista de mensajes que *habrian* salido.
    Se parchea _entregar (la que abre la conexion SMTP) y no enviar(), para
    que el armado del mensaje -asunto, remitente, HTML- si se ejercite.
    """
    mensajes = []
    monkeypatch.setattr(correo_service, "_entregar", mensajes.append)
    return mensajes


@pytest.fixture
def fijar_codigo_captcha(monkeypatch):
    """
    Hace predecible el codigo del captcha, que es el equivalente de "la
    persona mira la imagen y lee lo que dice".
    """
    import random

    choice_real = random.choice
    posicion = {"i": 0}

    def choice_predecible(secuencia):
        if secuencia is captcha_service.ALFABETO:
            caracter = CAPTCHA_FIJO[posicion["i"] % len(CAPTCHA_FIJO)]
            posicion["i"] += 1
            return caracter
        return choice_real(secuencia)

    monkeypatch.setattr(random, "choice", choice_predecible)

    def pedir(c, proposito):
        """Pide la imagen (eso genera el codigo) y devuelve lo que dibujo."""
        posicion["i"] = 0
        assert c.get("/auth/captcha?para=" + proposito).status_code == 200
        return CAPTCHA_FIJO

    return pedir


def _datos_registro(**extra):
    datos = {
        "id_usuario": "2002", "names": "Nuevo", "lastnames": "Cliente",
        "email": "nuevo@correo.com", "password": "abcdef",
        "phone": "3002223344", "address": "Calle 9 Bogotá",
    }
    datos.update(extra)
    return datos


# ----------------------------------------------------------------------
# La imagen del captcha
# ----------------------------------------------------------------------
def test_la_imagen_del_captcha_es_un_svg_que_no_se_cachea(client):
    r = client.get("/auth/captcha?para=registro")

    assert r.status_code == 200
    assert r.mimetype == "image/svg+xml"
    # Sin esto el navegador reutilizaria la primera imagen para siempre
    assert "no-store" in r.headers["Cache-Control"]


def test_el_codigo_no_aparece_escrito_en_el_svg(client):
    """
    Esta es la prueba que justifica la fuente de lineas de _GLIFOS.

    Con <text> el codigo quedaria escrito tal cual en el XML de la imagen,
    y leerlo seria una sola expresion regular sobre la respuesta de
    /auth/captcha. Dibujado con <path> no hay ningun caracter en el SVG:
    solo coordenadas.
    """
    svg = client.get("/auth/captcha?para=registro").get_data(as_text=True)

    assert "<text" not in svg
    # Ningun nodo con contenido textual: '>X<' seria un caracter suelto
    assert re.search(r">[A-Z0-9]<", svg) is None
    # Un <path> por polilinea de cada caracter, mas el ruido de fondo
    assert svg.count("<path") >= captcha_service.LONGITUD


def test_cada_caracter_sale_dibujado_distinto(client):
    """
    Los trazos llevan giro, inclinacion y un temblor por vertice. Sin eso,
    las coordenadas de una 'A' serian siempre las mismas y bastaria
    compararlas contra _GLIFOS -que esta en el codigo del proyecto- para
    resolver el captcha sin mirar la imagen.
    """
    with client.application.test_request_context():
        primero = captcha_service._trazar_caracter("A", 20, 25)
        segundo = captcha_service._trazar_caracter("A", 20, 25)

    assert primero != segundo


def test_todos_los_caracteres_del_alfabeto_tienen_glifo():
    """
    Si el alfabeto y la fuente se desincronizan, generar_svg explota con un
    KeyError en mitad de una peticion.
    """
    sin_glifo = [c for c in captcha_service.ALFABETO if c not in captcha_service._GLIFOS]

    assert sin_glifo == []


def test_el_alfabeto_no_tiene_caracteres_que_se_confundan(client):
    """0/O y 1/I/L se leen mal: un captcha que falla a un humano no sirve."""
    assert not set("01OIL") & set(captcha_service.ALFABETO)


def test_la_respuesta_del_captcha_no_viaja_al_navegador(client):
    """
    Lo unico que sale del servidor es la imagen; en la sesion queda el
    hash. Si el codigo en claro viajara, se podria leer desde la consola
    del navegador y el captcha no serviria de nada.
    """
    svg = client.get("/auth/captcha?para=registro").get_data(as_text=True)

    with client.session_transaction() as sesion:
        guardado = sesion["captcha"]["registro"]

    assert sorted(guardado) == ["expira", "hash"]
    assert guardado["hash"] not in svg


def test_cada_peticion_genera_un_codigo_distinto(client):
    client.get("/auth/captcha?para=registro")
    with client.session_transaction() as sesion:
        primero = sesion["captcha"]["registro"]["hash"]

    client.get("/auth/captcha?para=registro")
    with client.session_transaction() as sesion:
        segundo = sesion["captcha"]["registro"]["hash"]

    assert primero != segundo


# ----------------------------------------------------------------------
# Captcha en el registro
# ----------------------------------------------------------------------
def test_el_registro_sin_captcha_no_crea_la_cuenta(client, app):
    r = client.post("/auth/registro", data=_datos_registro(captcha=""))

    assert r.status_code == 400
    assert r.get_json()["captcha_requerido"] is True
    assert db.session.get(Cliente, "2002") is None


def test_el_registro_con_el_captcha_equivocado_no_crea_la_cuenta(
        client, app, fijar_codigo_captcha):
    fijar_codigo_captcha(client, "registro")

    r = client.post("/auth/registro", data=_datos_registro(captcha="ZZZZZ"))

    assert r.status_code == 400
    assert db.session.get(Cliente, "2002") is None


def test_el_registro_con_el_captcha_correcto_crea_la_cuenta(
        client, app, fijar_codigo_captcha):
    codigo = fijar_codigo_captcha(client, "registro")

    r = client.post("/auth/registro", data=_datos_registro(captcha=codigo))

    assert r.status_code == 200
    assert r.get_json()["ok"] is True
    assert db.session.get(Cliente, "2002") is not None


def test_el_captcha_no_distingue_mayusculas(client, app, fijar_codigo_captcha):
    """Escribir 'abcde' en vez de 'ABCDE' tiene que pasar igual."""
    codigo = fijar_codigo_captcha(client, "registro")

    r = client.post("/auth/registro", data=_datos_registro(captcha=codigo.lower()))

    assert r.status_code == 200


def test_el_mismo_captcha_no_sirve_dos_veces(client, app, fijar_codigo_captcha):
    codigo = fijar_codigo_captcha(client, "registro")
    client.post("/auth/registro", data=_datos_registro(captcha=codigo))

    # Segundo registro reusando el captcha ya gastado
    r = client.post("/auth/registro", data=_datos_registro(id_usuario="3003",
                                                           email="otro@correo.com",
                                                           captcha=codigo))

    assert r.status_code == 400
    assert db.session.get(Cliente, "3003") is None


def test_el_captcha_de_un_formulario_no_sirve_en_otro(client, app, fijar_codigo_captcha):
    """
    Resolver el captcha del login no debe habilitar el del registro: cada
    formulario tiene su propio proposito en la sesion.
    """
    codigo = fijar_codigo_captcha(client, "login")

    r = client.post("/auth/registro", data=_datos_registro(captcha=codigo))

    assert r.status_code == 400


# ----------------------------------------------------------------------
# Captcha en el login: aparece recien tras varios fallos
# ----------------------------------------------------------------------
def test_el_login_normal_no_pide_captcha(client):
    r = client.post("/auth/login", data={"email": CORREO, "password": CONTRASENA})

    assert r.status_code == 200
    assert r.get_json()["ok"] is True


@pytest.mark.parametrize("fallos", [1, 2])
def test_los_primeros_fallos_no_piden_captcha(client, fallos):
    for _ in range(fallos):
        r = client.post("/auth/login", data={"email": CORREO, "password": "mala"})

    assert r.status_code == 401
    assert r.get_json()["captcha_requerido"] is False


def test_tras_tres_fallos_el_login_pide_captcha(client):
    for _ in range(3):
        r = client.post("/auth/login", data={"email": CORREO, "password": "mala"})
    assert r.get_json()["captcha_requerido"] is True

    # Ahora ni con la contrasena correcta se entra sin resolver la imagen
    r = client.post("/auth/login", data={"email": CORREO, "password": CONTRASENA})
    assert r.status_code == 400
    assert r.get_json()["captcha_requerido"] is True


def test_con_captcha_resuelto_se_entra_despues_de_los_fallos(client, fijar_codigo_captcha):
    for _ in range(3):
        client.post("/auth/login", data={"email": CORREO, "password": "mala"})

    codigo = fijar_codigo_captcha(client, "login")
    r = client.post("/auth/login", data={"email": CORREO, "password": CONTRASENA,
                                         "captcha": codigo})

    assert r.status_code == 200
    assert r.get_json()["ok"] is True


def test_entrar_bien_borra_el_contador_de_fallos(client, fijar_codigo_captcha):
    for _ in range(3):
        client.post("/auth/login", data={"email": CORREO, "password": "mala"})
    codigo = fijar_codigo_captcha(client, "login")
    client.post("/auth/login", data={"email": CORREO, "password": CONTRASENA,
                                     "captcha": codigo})

    with client.session_transaction() as sesion:
        assert "intentos_login" not in sesion


# ----------------------------------------------------------------------
# Recuperar contrasena: paso 1, pedir el codigo
# ----------------------------------------------------------------------
def _solicitar(client, pedir_captcha, documento=DOCUMENTO, correo=CORREO):
    codigo_imagen = pedir_captcha(client, "recuperar")
    return client.post("/auth/recuperar/solicitar",
                       data={"id_usuario": documento, "email": correo,
                             "captcha": codigo_imagen})


def _codigo_del_correo(mensaje):
    """Saca los 6 digitos del asunto, que es donde los ve la persona."""
    return re.search(r"\b(\d{6})\b", mensaje["Subject"]).group(1)


def test_pedir_el_codigo_manda_un_correo_al_cliente(client, buzon, fijar_codigo_captcha):
    r = _solicitar(client, fijar_codigo_captcha)

    assert r.status_code == 200
    assert r.get_json()["paso"] == "codigo"
    assert len(buzon) == 1
    assert buzon[0]["To"] == CORREO
    assert ConfigPrueba.MAIL_REMITENTE in buzon[0]["From"]
    # Texto plano + HTML: hay lectores de correo que no muestran HTML
    assert buzon[0].is_multipart()


def test_el_aviso_en_pantalla_no_repite_el_correo_completo(client, buzon, fijar_codigo_captcha):
    """
    La pantalla confirma a donde fue el codigo con el correo enmascarado,
    para no mostrar la direccion entera a quien este mirando de reojo.
    """
    mensaje = _solicitar(client, fijar_codigo_captcha).get_json()["mensaje"]

    assert CORREO not in mensaje
    assert recuperacion_service.enmascarar_correo(CORREO) in mensaje


def test_el_codigo_se_guarda_hasheado(client, app, buzon, fijar_codigo_captcha):
    _solicitar(client, fijar_codigo_captcha)
    codigo = _codigo_del_correo(buzon[0])

    fila = CodigoRecuperacion.query.one()

    assert codigo not in fila.codigo_hash
    assert check_password_hash(fila.codigo_hash, codigo)


def test_sin_captcha_no_se_manda_ningun_correo(client, buzon):
    r = client.post("/auth/recuperar/solicitar",
                    data={"id_usuario": DOCUMENTO, "email": CORREO, "captcha": ""})

    assert r.status_code == 400
    assert buzon == []


def test_un_documento_y_un_correo_que_no_son_de_la_misma_cuenta_no_mandan_correo(
        client, buzon, fijar_codigo_captcha):
    r = _solicitar(client, fijar_codigo_captcha, documento="9999")

    assert r.status_code == 400
    assert buzon == []


def test_no_se_puede_pedir_otro_codigo_de_inmediato(client, buzon, fijar_codigo_captcha):
    """Si no, el boton se vuelve una maquina de spam contra ese correo."""
    _solicitar(client, fijar_codigo_captcha)

    r = _solicitar(client, fijar_codigo_captcha)

    assert r.status_code == 400
    assert "espera" in r.get_json()["mensaje"].lower()
    assert len(buzon) == 1


def test_si_el_correo_no_sale_no_queda_un_codigo_huerfano(
        client, app, monkeypatch, fijar_codigo_captcha):
    def rechazar(_mensaje):
        raise smtplib.SMTPAuthenticationError(535, b"credenciales incorrectas")

    monkeypatch.setattr(correo_service, "_entregar", rechazar)

    r = _solicitar(client, fijar_codigo_captcha)

    assert r.status_code == 503
    # El mensaje que ve la persona no delata el error de SMTP
    assert "535" not in r.get_json()["mensaje"]
    assert CodigoRecuperacion.query.count() == 0


# ----------------------------------------------------------------------
# Sin cuenta de correo configurada
# ----------------------------------------------------------------------
# Son los dos modos de MAIL_A_CONSOLA. Importa que sean excluyentes: si el
# codigo se imprimiera en la consola *y* ademas la peticion fallara, en
# pantalla quedaria un codigo que el servicio acaba de invalidar.
class ConfigSinCorreo(ConfigPrueba):
    MAIL_USUARIO = ""
    MAIL_CONTRASENA = ""


class ConfigSinCorreoConsola(ConfigSinCorreo):
    MAIL_A_CONSOLA = True


class ConfigSinCorreoEstricta(ConfigSinCorreo):
    MAIL_A_CONSOLA = False


def _app_con(config):
    aplicacion = create_app(config)
    with aplicacion.app_context():
        db.create_all()
        db.session.add(Cliente(
            id_usuario=DOCUMENTO, nombre="Laura", apellido="Gomez", correo=CORREO,
            contrasena=generate_password_hash(CONTRASENA),
            telefono="3001234567", direccion="Calle 1 Bogotá",
        ))
        db.session.commit()
        yield aplicacion


@pytest.fixture
def app_consola():
    yield from _app_con(ConfigSinCorreoConsola)


@pytest.fixture
def app_estricta():
    yield from _app_con(ConfigSinCorreoEstricta)


def test_sin_cuenta_y_con_consola_el_flujo_sigue_y_el_codigo_queda_usable(
        app_consola, fijar_codigo_captcha, caplog):
    """
    Modo demo: el correo se imprime en la consola y la recuperacion
    continua, asi que el codigo impreso tiene que servir de verdad.
    """
    import logging

    c = app_consola.test_client()
    with caplog.at_level(logging.WARNING):
        r = _solicitar(c, fijar_codigo_captcha)

    assert r.status_code == 200
    assert "CORREO SIN ENVIAR" in caplog.text
    codigo = re.search(r"Asunto: .*?(\d{6})", caplog.text).group(1)

    # El codigo que quedo en la consola es el que abre la cuenta
    assert _confirmar(c, codigo).status_code == 200
    assert check_password_hash(db.session.get(Cliente, DOCUMENTO).contrasena,
                               "clave-nueva-456")


def test_sin_cuenta_y_sin_consola_se_avisa_y_no_queda_codigo(
        app_estricta, fijar_codigo_captcha, caplog):
    """Modo producción: no se finge el envío ni se filtra el código."""
    import logging

    c = app_estricta.test_client()
    with caplog.at_level(logging.WARNING):
        r = _solicitar(c, fijar_codigo_captcha)

    assert r.status_code == 503
    assert "CORREO SIN ENVIAR" not in caplog.text
    assert CodigoRecuperacion.query.count() == 0


# ----------------------------------------------------------------------
# Recuperar contrasena: paso 2, usar el codigo
# ----------------------------------------------------------------------
def _confirmar(client, codigo, contrasena="clave-nueva-456"):
    return client.post("/auth/recuperar/confirmar",
                       data={"id_usuario": DOCUMENTO, "email": CORREO,
                             "codigo": codigo, "password": contrasena})


def test_el_codigo_correcto_cambia_la_contrasena(client, app, buzon, fijar_codigo_captcha):
    _solicitar(client, fijar_codigo_captcha)
    codigo = _codigo_del_correo(buzon[0])

    r = _confirmar(client, codigo)

    assert r.status_code == 200
    cliente = db.session.get(Cliente, DOCUMENTO)
    assert check_password_hash(cliente.contrasena, "clave-nueva-456")
    assert not check_password_hash(cliente.contrasena, CONTRASENA)


def test_un_codigo_equivocado_no_cambia_nada_y_descuenta_intentos(
        client, app, buzon, fijar_codigo_captcha):
    _solicitar(client, fijar_codigo_captcha)

    r = _confirmar(client, "000000")

    assert r.status_code == 400
    assert check_password_hash(db.session.get(Cliente, DOCUMENTO).contrasena, CONTRASENA)
    assert CodigoRecuperacion.query.one().intentos == 1


def test_el_codigo_se_quema_tras_cinco_intentos(client, app, buzon, fijar_codigo_captcha):
    _solicitar(client, fijar_codigo_captcha)
    codigo = _codigo_del_correo(buzon[0])

    for _ in range(5):
        _confirmar(client, "000000")

    # El codigo bueno ya no sirve: hay que pedir otro
    r = _confirmar(client, codigo)
    assert r.status_code == 400
    assert "nuevo" in r.get_json()["mensaje"].lower()
    assert check_password_hash(db.session.get(Cliente, DOCUMENTO).contrasena, CONTRASENA)


def test_el_codigo_no_se_puede_usar_dos_veces(client, app, buzon, fijar_codigo_captcha):
    _solicitar(client, fijar_codigo_captcha)
    codigo = _codigo_del_correo(buzon[0])
    _confirmar(client, codigo)

    r = _confirmar(client, codigo, contrasena="otra-clave-789")

    assert r.status_code == 400
    assert check_password_hash(db.session.get(Cliente, DOCUMENTO).contrasena, "clave-nueva-456")


def test_un_codigo_vencido_no_sirve(client, app, buzon, fijar_codigo_captcha):
    from datetime import datetime, timedelta

    _solicitar(client, fijar_codigo_captcha)
    codigo = _codigo_del_correo(buzon[0])

    fila = CodigoRecuperacion.query.one()
    fila.expira_en = datetime.now() - timedelta(minutes=1)
    db.session.commit()

    r = _confirmar(client, codigo)

    assert r.status_code == 400
    assert check_password_hash(db.session.get(Cliente, DOCUMENTO).contrasena, CONTRASENA)


def test_pedir_un_codigo_nuevo_anula_el_anterior(client, app, buzon, fijar_codigo_captcha):
    from datetime import datetime, timedelta

    _solicitar(client, fijar_codigo_captcha)
    viejo = _codigo_del_correo(buzon[0])

    # Se finge que paso la espera entre envios
    fila = CodigoRecuperacion.query.one()
    fila.creado_en = datetime.now() - timedelta(minutes=5)
    db.session.commit()

    _solicitar(client, fijar_codigo_captcha)
    nuevo = _codigo_del_correo(buzon[1])
    assert viejo != nuevo

    assert _confirmar(client, viejo).status_code == 400
    assert _confirmar(client, nuevo).status_code == 200


def test_la_contrasena_nueva_tiene_un_minimo(client, app, buzon, fijar_codigo_captcha):
    _solicitar(client, fijar_codigo_captcha)
    codigo = _codigo_del_correo(buzon[0])

    r = _confirmar(client, codigo, contrasena="123")

    assert r.status_code == 400
    assert check_password_hash(db.session.get(Cliente, DOCUMENTO).contrasena, CONTRASENA)


def test_con_la_contrasena_nueva_se_entra_y_con_la_vieja_no(
        client, app, buzon, fijar_codigo_captcha):
    _solicitar(client, fijar_codigo_captcha)
    _confirmar(client, _codigo_del_correo(buzon[0]))

    otro = client.application.test_client()
    assert otro.post("/auth/login", data={"email": CORREO,
                                          "password": CONTRASENA}).status_code == 401
    assert otro.post("/auth/login", data={"email": CORREO,
                                          "password": "clave-nueva-456"}).status_code == 200


# ----------------------------------------------------------------------
# Lo que ve la persona
# ----------------------------------------------------------------------
def test_el_modal_trae_el_captcha_y_el_paso_del_codigo(client):
    html = client.get("/").get_data(as_text=True)

    for marca in ('id="captcha-bloque"', 'id="captcha-img"', 'id="captcha-recargar"',
                  'id="recuperar-codigo"', 'id="codigo-reenviar"', 'class="codigo-only"'):
        assert marca in html, marca


def test_acerca_de_trae_los_enlaces_de_gmail_e_instagram(client):
    html = client.get("/acerca").get_data(as_text=True)

    assert "mailto:antonietawsnpaws@gmail.com" in html
    assert "https://www.instagram.com/bonespaws_666/" in html
    # Un enlace a otra pestaña sin noopener deja que la pagina abierta
    # manipule a la que la abrio
    assert 'rel="noopener noreferrer"' in html
