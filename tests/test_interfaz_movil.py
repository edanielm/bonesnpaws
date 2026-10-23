"""
tests/test_interfaz_movil.py

Pruebas de las tres cosas que se arreglaron pensando en el telefono y en
quien entra sin sesion:

  1. Sin sesion, navegar a una pagina protegida lleva a la portada con un
     aviso, no deja el JSON del error escrito en pantalla.
  2. Todos los campos de contraseña llevan el boton del ojito.
  3. La barra de navegacion tiene menu desplegable, para que los enlaces
     no desaparezcan sin reemplazo en pantalla angosta.

Lo visual (que nada se salga a lo ancho a 360/390 px) no se puede medir
desde aqui: eso se comprobo renderizando las paginas con Chrome headless
dentro de un iframe del ancho de un telefono. Lo que si se puede fijar
aqui es el HTML y las reglas CSS de las que depende, que es lo que
rompe sin darse cuenta al editar.

    pytest tests/ -v
"""
import io
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

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCUMENTO = "1001"
CORREO = "laura@correo.com"
CONTRASENA = "123456"


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
            id_usuario=DOCUMENTO, nombre="Laura", apellido="Gomez", correo=CORREO,
            contrasena=generate_password_hash(CONTRASENA),
            telefono="3001234567", direccion="Calle 1 Bogotá",
        ))
        db.session.commit()
        yield aplicacion


@pytest.fixture
def client(app):
    return app.test_client()


def leer(*partes):
    with io.open(os.path.join(RAIZ, *partes), encoding="utf-8") as f:
        return f.read()


# ----------------------------------------------------------------------
# 1. Sin sesion: aviso, no JSON en pantalla
# ----------------------------------------------------------------------
# Antes esto se decidia por la ruta ("si empieza por /carrito, es fetch"),
# y /carrito tambien se abre con un clic o escribiendo la direccion: el
# navegador recibia el JSON y lo mostraba como texto pelado.
RUTAS_PROTEGIDAS = [
    "/carrito/",
    "/facturas/checkout",
    "/facturas/historial",
    "/perfil/",
]

# /facturas/<numero> queda fuera a proposito: responde 403 a quien no sea
# el dueño, exista o no la factura, para no revelar cuales existen (el
# numero es un consecutivo facil de adivinar). Eso lo fija
# test_nadie_mas_puede_ver_una_factura_ajena en test_rutas_publicas.py.


@pytest.mark.parametrize("ruta", RUTAS_PROTEGIDAS)
def test_navegar_sin_sesion_redirige_en_vez_de_mostrar_json(client, ruta):
    r = client.get(ruta)

    assert r.status_code in (302, 308), r.get_data(as_text=True)[:200]
    assert "/?login=1" in r.headers["Location"]
    assert "application/json" not in r.headers.get("Content-Type", "")


@pytest.mark.parametrize("ruta", RUTAS_PROTEGIDAS)
def test_al_llegar_a_la_portada_se_ve_el_aviso(client, ruta):
    """
    El mensaje viaja en un flash y base.html lo pinta arriba del
    contenido; ?login=1 ademas abre el modal solo.
    """
    html = client.get(ruta, follow_redirects=True).get_data(as_text=True)

    assert "Debes iniciar sesión" in html or "Inicia sesión" in html
    assert 'class="alert alert-warning"' in html
    assert '{"ok": false' not in html


def test_el_javascript_del_sitio_si_recibe_json(client):
    """
    La misma ruta, pedida por fetch (con la cabecera que pone app.js),
    tiene que seguir respondiendo JSON: de eso depende que el modal se
    abra sin recargar la pagina.
    """
    r = client.post("/carrito/agregar",
                    data={"id_producto": 1, "cantidad": 1},
                    headers={"X-Requested-With": "XMLHttpRequest"})

    assert r.status_code == 401
    cuerpo = r.get_json()
    assert cuerpo["ok"] is False
    assert cuerpo["requiere_login"] is True


def test_app_js_manda_la_cabecera_y_mira_la_bandera():
    """
    Las dos puntas del contrato. Si alguien quita la cabecera, el servidor
    responderia una redireccion y resp.json() reventaria; si alguien vuelve
    a comparar el texto del mensaje, el modal dejaria de abrirse en cuanto
    se reescriba esa frase.
    """
    js = leer("app", "static", "js", "app.js")

    assert "X-Requested-With" in js
    assert "data.requiere_login" in js
    assert 'data.mensaje === "Debes iniciar sesión."' not in js


# ----------------------------------------------------------------------
# 2. El ojito en los campos de contraseña
# ----------------------------------------------------------------------
def test_el_script_del_ojito_se_carga_en_todas_las_paginas(client):
    html = client.get("/").get_data(as_text=True)

    assert "js/password.js" in html


def test_el_ojito_cubre_todos_los_campos_de_contrasena():
    """
    password.js busca input[type=password] en toda la pagina, asi que basta
    con que ningun campo se declare de otra forma ni se excluya a mano.
    """
    js = leer("app", "static", "js", "password.js")

    assert 'input[type="password"]' in js
    # Los campos que aparecen despues de cargar la pagina tambien
    assert "MutationObserver" in js


@pytest.mark.parametrize("plantilla,campos", [
    (("app", "templates", "base.html"), 4),          # entrar, registro x2, recuperar x2 -> 4 visibles
    (("app", "templates", "admin", "empleado_form.html"), 1),
])
def test_las_plantillas_siguen_usando_input_type_password(plantilla, campos):
    """
    Si algun campo se cambiara a type="text" con JavaScript propio, el
    ojito no lo encontraria. Esta prueba fija que siguen siendo campos de
    contraseña de verdad.
    """
    html = leer(*plantilla)

    assert html.count('type="password"') >= campos


def test_el_ojito_tiene_estilos_en_los_dos_contextos():
    """
    El modal del gato y el panel tienen CSS distinto; el boton necesita
    reglas en los dos o en uno de ellos sale deformado (en el modal
    heredaria el ancho completo del boton rosado de enviar).
    """
    assert ".ojo-boton" in leer("app", "static", "css", "style.css")
    assert "#auth-form .ojo-boton" in leer("app", "static", "css", "login.css")


# ----------------------------------------------------------------------
# 3. Navegacion en pantalla angosta
# ----------------------------------------------------------------------
def test_la_barra_tiene_menu_desplegable(client):
    html = client.get("/").get_data(as_text=True)

    assert 'id="nav-toggle"' in html
    assert 'id="nav-movil"' in html
    assert 'aria-controls="nav-movil"' in html
    assert 'aria-expanded="false"' in html


def test_el_menu_desplegable_trae_todos_los_enlaces(client):
    """
    El panel es el unico acceso a estas paginas desde un telefono: si un
    enlace se agrega solo a la barra de escritorio, en el telefono no
    existe.
    """
    html = client.get("/").get_data(as_text=True)
    panel = html.split('id="nav-movil"', 1)[1].split("</nav>", 1)[0]

    for destino in ("/productos", "/categorias", "/acerca", "/contacto"):
        assert 'href="%s"' % destino in panel, destino


def test_el_menu_desplegable_trae_las_acciones_de_sesion(client):
    """Sin sesion: entrar y registrarse. Con sesion: perfil y salir."""
    panel = (client.get("/").get_data(as_text=True)
             .split('id="nav-movil"', 1)[1].split("</nav>", 1)[0])
    assert 'data-abrir-login="login"' in panel
    assert 'data-abrir-login="registro"' in panel

    c = client
    c.post("/auth/login", data={"email": CORREO, "password": CONTRASENA})
    panel = (c.get("/").get_data(as_text=True)
             .split('id="nav-movil"', 1)[1].split("</nav>", 1)[0])
    assert "/perfil/" in panel
    assert "/auth/logout" in panel


def test_los_enlaces_no_desaparecen_sin_reemplazo():
    """
    La regla que esconde .nav-links en pantalla angosta tiene que venir
    acompañada de la que muestra el boton de menu. Antes solo estaba la
    primera: desde un telefono no habia forma de navegar el sitio.
    """
    css = leer("app", "static", "css", "style.css")

    bloque = re.search(
        r"@media \(max-width: 900px\) \{(.*?)\n\}", css, re.S)
    assert bloque, "falta el bloque responsive de la barra"
    reglas = bloque.group(1)
    assert ".nav-links { display: none; }" in reglas
    assert ".nav-toggle { display: inline-flex; }" in reglas


def test_hay_red_de_seguridad_contra_el_desplazamiento_horizontal():
    """
    Ninguna pagina debe poder desplazarse a lo ancho en un telefono. Va en
    <html> y no en <body>: overflow-x en body rompe la barra sticky.
    """
    css = leer("app", "static", "css", "style.css")

    assert "html { overflow-x: hidden; max-width: 100%; }" in css


def test_la_pagina_declara_el_viewport(client):
    """Sin esta etiqueta el telefono dibuja la pagina a 980 px y la encoge."""
    html = client.get("/").get_data(as_text=True)

    assert 'name="viewport"' in html
    assert "width=device-width" in html


# ----------------------------------------------------------------------
# El paso del codigo no debe asomarse en el modo de entrar
# ----------------------------------------------------------------------
def test_el_enlace_de_reenviar_codigo_esta_oculto_fuera_de_su_paso():
    """
    .toggle-text pone display:block y es tambien un selector de una clase:
    sin !important ganaba por ir despues en el archivo, y "¿No te llegó?
    Pedir otro código" se veia en la pantalla de entrar.
    """
    css = leer("app", "static", "css", "login.css")

    assert ".codigo-only { display: none !important; }" in css
    assert ".codigo-mode .codigo-only { display: block !important; }" in css
