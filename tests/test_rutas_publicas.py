"""
tests/test_rutas_publicas.py

Pruebas de la aplicacion: que arranque, que todas las rutas respondan y
que las reglas de negocio del panel admin se cumplan.

Corren sobre una base SQLite en memoria creada desde los modelos, con
datos de prueba sembrados aqui mismo. Eso las hace ejecutables en
cualquier equipo, sin MySQL encendido y sin tocar la base 'bandp' real.

    pytest tests/ -v

Nota: SQLite no tiene los triggers ni los procedimientos de objetos.sql
(eso es exclusivo de MySQL), asi que aqui se prueba la capa Flask —
rutas, servicios y plantillas—, no el "escudo logico" de la base de datos.
"""
import io
import os
import sys
import tempfile
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from werkzeug.datastructures import FileStorage

from app.config import Config

# Carpeta aparte para los archivos que suban las pruebas de fotos de
# producto: si se usara UPLOAD_FOLDER tal cual (app/static/uploads), las
# pruebas escribirian archivos reales dentro del proyecto.
_UPLOAD_FOLDER_PRUEBA = tempfile.mkdtemp(prefix="bandp_test_uploads_")


class ConfigPrueba(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
    SECRET_KEY = "clave-de-prueba"
    UPLOAD_FOLDER = _UPLOAD_FOLDER_PRUEBA


from app import create_app
from app.extensions import db
from app.models import (
    Categoria, Proveedor, Producto, Cliente, Rol, Empleado, Factura, Detalle,
    Carrito, CarritoProducto, Transportadora, Envio, ROL_ADMINISTRADOR, ROL_VENDEDOR,
)


def _sembrar():
    """Datos minimos para ejercitar catalogo, ventas, cuentas y roles."""
    db.create_all()

    for i, nombre in enumerate(["Perros", "Gatos", "Otros"], start=1):
        db.session.add(Categoria(id_categoria=i, nombre=nombre))

    db.session.add(Proveedor(id_proveedor=1, nombre="Distribuidora Patitas",
                             direccion="Cra 1 #2-3", telefono="3001112233",
                             correo="ventas@patitas.co", asesor="Ana"))

    for pid, codigo, nom, precio, stock, cat in [
        (1, "PER-0001", "Alimento premium perro 3kg", 89000, 20, 1),
        (2, "GAT-0001", "Arena aglomerante gato 5kg", 42000, 4, 2),
        (3, "PER-0002", "Collar reflectivo", 25000, 0, 1),
    ]:
        db.session.add(Producto(id_producto=pid, codigo=codigo, nombre=nom,
                                descripcion="Producto de prueba", precio=precio,
                                stock=stock, id_categoria=cat, id_proveedor=1))

    db.session.add(Rol(id_rol=1, nombre=ROL_ADMINISTRADOR,
                       descripcion="Acceso total al panel."))
    db.session.add(Rol(id_rol=2, nombre=ROL_VENDEDOR,
                       descripcion="Catálogo y consulta de clientes."))

    db.session.add(Empleado(id_empleado=999, nombre="Admin", apellido="Sistema",
                            correo="admin", contrasena="admin123",
                            telefono="3000000000", id_rol=1))
    db.session.add(Empleado(id_empleado=998, nombre="Vendedor", apellido="Demo",
                            correo="vendedor", contrasena="vendedor123",
                            telefono="3009999999", id_rol=2))

    # La direccion lleva ciudad a proposito: de ahi sale la tarifa de envio
    db.session.add(Cliente(id_usuario="1001", nombre="Laura", apellido="Gomez",
                           correo="laura@correo.com", contrasena="123456",
                           telefono="3001234567", direccion="Calle 1 Bogotá"))
    db.session.add(Cliente(id_usuario="1003", nombre="Sin", apellido="Compras",
                           correo="sincompras@correo.com", contrasena="123456",
                           telefono="3007654321", direccion="Calle 3 Pasto"))

    # Transportadoras: sin ellas no se puede generar la guia de un envio
    db.session.add(Transportadora(id_transportadora=1, nombre="Servientrega", telefono="6015551234"))
    db.session.add(Transportadora(id_transportadora=2, nombre="Coordinadora", telefono="6044445678"))

    # El cliente sin compras tiene carrito: debe borrarse junto con su cuenta
    db.session.add(Carrito(id_carrito=1, id_usuario="1003"))
    db.session.add(CarritoProducto(id_carrito=1, id_producto=1, cantidad=2))

    hoy = date.today()
    for num, dias, metodo, sub in [(1, 0, "Tarjeta", 89000), (2, 40, "PSE", 42000)]:
        iva = round(sub * 0.19)
        db.session.add(Factura(numero_factura=num, fecha=hoy - timedelta(days=dias),
                               subtotal=sub, iva=iva, costo_envio=8000,
                               total=sub + iva + 8000, id_usuario="1001",
                               id_empleado=999, metodo_pago=metodo))
        db.session.add(Detalle(id_detalle=num, numero_factura=num, id_producto=num,
                               cantidad=num, precio_unitario=sub,
                               subtotal_producto=sub * num))

    db.session.commit()


@pytest.fixture
def app():
    aplicacion = create_app(ConfigPrueba)
    with aplicacion.app_context():
        _sembrar()
        yield aplicacion


@pytest.fixture
def client(app):
    return app.test_client()


def _entrar(app, correo, contrasena):
    """
    Inicia sesion por el formulario unico del sitio. Es el mismo endpoint
    para cliente, administrador y vendedor: precisamente eso es lo que se
    quiere comprobar.
    """
    c = app.test_client()
    respuesta = c.post("/auth/login", data={"email": correo, "password": contrasena})
    assert respuesta.status_code == 200, respuesta.get_data(as_text=True)
    return c, respuesta.get_json()


@pytest.fixture
def admin(app):
    """Cliente HTTP autenticado con el rol Administrador."""
    c, _ = _entrar(app, "admin", "admin123")
    return c


@pytest.fixture
def vendedor(app):
    """Cliente HTTP autenticado con el rol Vendedor."""
    c, _ = _entrar(app, "vendedor", "vendedor123")
    return c


@pytest.fixture
def comprador(app):
    """Cliente HTTP con la sesion del cliente 1001, dueno de las facturas."""
    c = app.test_client()
    with c.session_transaction() as s:
        s["id_usuario"] = "1001"
        s["nombre"] = "Laura"
    return c


# ----------------------------------------------------------------------
# Rutas publicas
# ----------------------------------------------------------------------

@pytest.mark.parametrize("ruta", [
    "/",
    "/productos",
    "/productos?q=alimento",
    "/productos?categoria=1",
    "/productos/1",
    "/productos/3",          # producto agotado
    "/categorias",
    "/acerca",
    "/contacto",
])
def test_rutas_publicas_responden(client, ruta):
    assert client.get(ruta).status_code == 200


def test_el_login_del_panel_lleva_al_formulario_unico(client):
    """
    Ya no hay una pantalla de login aparte para el panel. La direccion
    vieja se conserva y manda a la portada con el modal abierto.
    """
    respuesta = client.get("/admin/login", follow_redirects=False)
    assert respuesta.status_code == 302
    assert "login=1" in respuesta.headers["Location"]


def test_carrito_sin_sesion_no_deja_entrar(client):
    assert client.get("/carrito/", follow_redirects=False).status_code in (302, 401)


# ----------------------------------------------------------------------
# Interfaz: iconos, tema y respaldo de imagenes
# ----------------------------------------------------------------------

def test_la_portada_trae_el_interruptor_de_tema(client):
    html = client.get("/").get_data(as_text=True)
    assert 'id="tema-toggle"' in html
    assert "js/tema.js" in html


def test_los_iconos_son_svg_y_no_emojis(client):
    html = client.get("/").get_data(as_text=True)
    assert html.count('class="ico ') >= 3
    assert "🐾" not in html and "🛒" not in html


def test_las_imagenes_tienen_respaldo_local(client):
    """Sin internet o sin la carpeta uploads/, no debe verse un icono roto."""
    html = client.get("/productos").get_data(as_text=True)
    assert "/static/img/sin-imagen.svg" in html
    assert "placehold.co" not in html


# ----------------------------------------------------------------------
# Panel de administracion
# ----------------------------------------------------------------------

@pytest.mark.parametrize("ruta", ["/admin/", "/admin/usuarios", "/admin/productos"])
def test_panel_admin_exige_sesion(client, ruta):
    assert client.get(ruta, follow_redirects=False).status_code == 302


@pytest.mark.parametrize("ruta", [
    "/admin/",
    "/admin/usuarios",
    "/admin/usuarios?q=laura",
    "/admin/usuarios/1001",
    "/admin/usuarios/1003",
    "/admin/productos",
    "/admin/productos/crear",
    "/admin/productos/1/editar",
])
def test_panel_admin_con_sesion(admin, ruta):
    assert admin.get(ruta).status_code == 200


def test_el_dashboard_muestra_las_estadisticas(admin):
    html = admin.get("/admin/").get_data(as_text=True)
    for seccion in ["Ventas totales", "chart-barras", "Facturas recientes"]:
        assert seccion in html


# ----------------------------------------------------------------------
# Login unico: cliente, administrador y vendedor por el mismo formulario
# ----------------------------------------------------------------------

@pytest.mark.parametrize("correo, contrasena, destino", [
    ("laura@correo.com", "123456", "/"),                 # cliente -> tienda
    ("admin", "admin123", "/admin/"),                    # admin   -> estadisticas
    ("vendedor", "vendedor123", "/admin/productos"),     # vendedor-> catalogo
])
def test_todos_entran_por_el_mismo_formulario(app, correo, contrasena, destino):
    """
    Un solo endpoint (/auth/login) atiende a los tres tipos de cuenta.
    Lo que cambia segun el rol es donde aterriza cada quien.
    """
    _, datos = _entrar(app, correo, contrasena)
    assert datos["ok"] is True
    assert datos["redirect"] == destino


def test_una_contrasena_mala_no_deja_entrar_a_nadie(client):
    respuesta = client.post("/auth/login", data={"email": "admin", "password": "noesesta"})
    assert respuesta.status_code == 401
    assert respuesta.get_json()["ok"] is False


def test_la_salida_es_unica_para_todos(admin):
    admin.get("/auth/logout", follow_redirects=False)
    # Sin sesion, el panel vuelve a mandar al login
    assert admin.get("/admin/productos", follow_redirects=False).status_code == 302


# ----------------------------------------------------------------------
# Permisos por rol
# ----------------------------------------------------------------------

@pytest.mark.parametrize("ruta", [
    "/admin/usuarios",
    "/admin/usuarios/1001",
    "/admin/productos",
    "/admin/productos/crear",
    "/admin/productos/1/editar",
])
def test_el_vendedor_gestiona_catalogo_y_consulta_clientes(vendedor, ruta):
    assert vendedor.get(ruta).status_code == 200


def test_el_vendedor_no_entra_a_las_estadisticas(vendedor):
    """Su sesion es valida; lo que le falta es el permiso, no el login."""
    respuesta = vendedor.get("/admin/", follow_redirects=False)
    assert respuesta.status_code == 302
    assert "/admin/productos" in respuesta.headers["Location"]


def test_el_vendedor_no_puede_borrar_cuentas(vendedor, app):
    vendedor.post("/admin/usuarios/1003/eliminar", follow_redirects=False)
    assert db.session.get(Cliente, "1003") is not None


def test_el_menu_del_vendedor_no_ofrece_estadisticas(vendedor, admin):
    del_vendedor = vendedor.get("/admin/productos").get_data(as_text=True)
    del_admin = admin.get("/admin/productos").get_data(as_text=True)
    assert "Estadísticas" not in del_vendedor
    assert "Estadísticas" in del_admin


# ----------------------------------------------------------------------
# Perfil segun el usuario que inicio sesion
# ----------------------------------------------------------------------

def test_el_perfil_sin_sesion_manda_al_login(client):
    respuesta = client.get("/perfil/", follow_redirects=False)
    assert respuesta.status_code == 302
    assert "login=1" in respuesta.headers["Location"]


def test_el_perfil_de_un_cliente_muestra_sus_compras(comprador):
    html = comprador.get("/perfil/").get_data(as_text=True)
    assert "Laura" in html
    assert "Compras realizadas" in html
    assert "Mi rol" not in html          # eso es del personal


@pytest.mark.parametrize("correo, contrasena, rol", [
    ("admin", "admin123", "Administrador"),
    ("vendedor", "vendedor123", "Vendedor"),
])
def test_el_perfil_del_personal_muestra_su_rol(app, correo, contrasena, rol):
    sesion, _ = _entrar(app, correo, contrasena)
    html = sesion.get("/perfil/").get_data(as_text=True)
    assert "Mi rol" in html
    assert rol in html
    assert "Ventas atendidas" in html


def test_cada_quien_edita_solo_lo_suyo(comprador, admin):
    """El cliente cambia telefono y direccion; el empleado solo su telefono."""
    assert comprador.post("/perfil/actualizar",
                          data={"telefono": "3110000000", "direccion": "Calle 9"}).status_code == 200
    assert db.session.get(Cliente, "1001").telefono == "3110000000"

    assert admin.post("/perfil/actualizar", data={"telefono": "3115555555"}).status_code == 200
    assert db.session.get(Empleado, 999).telefono == "3115555555"


# ----------------------------------------------------------------------
# Reglas de negocio del borrado de cuentas
# ----------------------------------------------------------------------

def test_no_se_puede_borrar_un_cliente_con_compras(admin, app):
    """Sus facturas son historico contable; la llave foranea lo prohibe."""
    respuesta = admin.post("/admin/usuarios/1001/eliminar", follow_redirects=False)
    assert respuesta.status_code == 302
    assert "/admin/usuarios/1001" in respuesta.headers["Location"]
    assert db.session.get(Cliente, "1001") is not None


def test_se_borra_un_cliente_sin_compras_junto_con_su_carrito(admin, app):
    admin.post("/admin/usuarios/1003/eliminar", follow_redirects=False)
    assert db.session.get(Cliente, "1003") is None
    assert Carrito.query.filter_by(id_usuario="1003").count() == 0


# ----------------------------------------------------------------------
# Codigo unico de producto (reemplaza al autoincremental)
# ----------------------------------------------------------------------

def _producto_nuevo(codigo, nombre="Juguete de prueba"):
    from app.services.producto_service import ProductoService

    return ProductoService.crear(codigo=codigo, nombre=nombre, descripcion="",
                                 precio=15000, stock=5, id_categoria=1, id_proveedor=1)


def test_no_se_pueden_crear_dos_productos_con_el_mismo_codigo(app):
    """Es la razon de ser del codigo: que el catalogo no se duplique."""
    from app.services.producto_service import ProductoService

    _producto_nuevo("PER-0500", "Pelota")
    with pytest.raises(ValueError, match="PER-0500"):
        _producto_nuevo("PER-0500", "Pelota otra vez")

    assert Producto.query.filter_by(codigo="PER-0500").count() == 1
    assert ProductoService.obtener_por_codigo("PER-0500").nombre == "Pelota"


def test_el_codigo_se_normaliza_antes_de_comparar(app):
    """'per-0501 ' y 'PER-0501' son el mismo producto, no dos."""
    _producto_nuevo("PER-0501", "Correa")
    with pytest.raises(ValueError):
        _producto_nuevo("  per-0501  ", "Correa repetida")


def test_un_producto_sin_codigo_no_se_guarda(app):
    with pytest.raises(ValueError, match="código único"):
        _producto_nuevo("   ", "Sin codigo")


def test_editar_un_producto_no_choca_con_su_propio_codigo(app):
    """Guardar sin cambiar el codigo no puede leerse como duplicado."""
    from app.services.producto_service import ProductoService

    ProductoService.actualizar(1, codigo="PER-0001", nombre="Alimento premium perro 3kg")
    assert db.session.get(Producto, 1).codigo == "PER-0001"


def test_el_codigo_sugerido_sigue_la_serie_de_la_categoria(app):
    from app.services.producto_service import ProductoService

    # Sembrados: PER-0001 y PER-0002 en Perros, GAT-0001 en Gatos
    assert ProductoService.sugerir_codigo(1) == "PER-0003"
    assert ProductoService.sugerir_codigo(2) == "GAT-0002"
    assert ProductoService.sugerir_codigo(3) == "OTR-0001"


def test_el_catalogo_se_puede_buscar_por_codigo(client):
    html = client.get("/productos?q=GAT-0001").get_data(as_text=True)
    assert "Arena aglomerante gato 5kg" in html


def test_el_panel_muestra_el_codigo_de_cada_producto(admin):
    html = admin.get("/admin/productos").get_data(as_text=True)
    assert "PER-0001" in html and "GAT-0001" in html


# ----------------------------------------------------------------------
# Estadisticas calculadas por AdminService
# ----------------------------------------------------------------------

def test_el_resumen_de_ventas_cuadra(app):
    from app.services.admin_service import AdminService

    resumen = AdminService.resumen_ventas()
    esperado = sum(s + round(s * 0.19) + 8000 for s in (89000, 42000))

    assert round(resumen["total_ventas"]) == esperado
    assert resumen["num_facturas"] == 2
    assert round(resumen["ticket_promedio"]) == round(esperado / 2)
    assert resumen["productos_agotados"] == 1     # el collar
    assert resumen["productos_stock_bajo"] == 1   # la arena, 4 unidades


def test_la_serie_mensual_no_deja_huecos(app):
    """Los meses sin ventas deben venir en cero, no faltar."""
    from app.services.admin_service import AdminService

    serie = AdminService.ventas_por_mes(6)
    assert len(serie) == 6
    assert all("total" in punto and "pct" in punto for punto in serie)


# ----------------------------------------------------------------------
# Formato de cifras
# ----------------------------------------------------------------------

@pytest.mark.parametrize("numero, letras", [
    (0, "CERO"),
    (100, "CIEN"),
    (1000, "MIL"),                    # no 'UN MIL'
    (21000, "VEINTIUN MIL"),          # apocope antes de MIL
    (21000000, "VEINTIUN MILLONES"),  # apocope antes de MILLONES
    (1000000, "UN MILLON"),
    (137910, "CIENTO TREINTA Y SIETE MIL NOVECIENTOS DIEZ"),
])
def test_monto_en_letras(numero, letras):
    from app.formato import numero_a_letras
    assert numero_a_letras(numero) == letras


def test_formato_de_pesos_colombianos():
    """Separador de miles con punto y sin centavos."""
    from app.formato import pesos, folio
    assert pesos(137910) == "$ 137.910"
    assert pesos(1234567.0) == "$ 1.234.567"
    assert pesos(None) == "$ 0"
    assert folio(42, "BP") == "BP-000042"


# ----------------------------------------------------------------------
# Factura: documento en pantalla, PDF y control de acceso
# ----------------------------------------------------------------------

def test_la_factura_muestra_el_documento_completo(comprador):
    html = comprador.get("/facturas/1").get_data(as_text=True)

    # Identificacion del documento y del vendedor
    assert "BP-000001" in html
    assert "Factura de venta" in html
    assert "901.234.567-8" in html          # NIT de la tienda
    # Datos del comprador
    assert "Laura Gomez" in html
    assert "laura@correo.com" in html
    # Cifras en formato colombiano y el monto en letras
    assert "$ " in html
    assert "PESOS M/CTE" in html
    # Acciones
    assert "Descargar PDF" in html
    assert "window.print()" in html


def test_la_factura_se_descarga_como_pdf(comprador):
    r = comprador.get("/facturas/1/pdf")

    assert r.status_code == 200
    assert r.mimetype == "application/pdf"
    assert "attachment" in r.headers["Content-Disposition"]
    assert "factura-BP-000001.pdf" in r.headers["Content-Disposition"]

    datos = r.get_data()
    assert datos.startswith(b"%PDF-")        # cabecera valida
    assert datos.rstrip().endswith(b"%%EOF")  # no quedo truncado
    assert len(datos) > 1500                  # tiene contenido, no es una hoja vacia


def test_la_factura_se_descarga_como_word(comprador):
    from docx import Document

    r = comprador.get("/facturas/1/word")

    assert r.status_code == 200
    assert r.mimetype == (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert "factura-BP-000001.docx" in r.headers["Content-Disposition"]

    # Que Word lo pueda abrir y que lleve lo esencial de la factura
    doc = Document(io.BytesIO(r.get_data()))
    texto = "\n".join(p.text for p in doc.paragraphs)
    for tabla in doc.tables:
        for fila in tabla.rows:
            for celda in fila.cells:
                texto += "\n" + celda.text
                for anidada in celda.tables:
                    texto += "\n" + "\n".join(c.text for f in anidada.rows for c in f.cells)
    assert "BP-000001" in texto
    assert "Laura Gomez" in texto
    assert "Alimento premium perro 3kg" in texto
    assert "TOTAL A PAGAR" in texto
    assert "PESOS M/CTE" in texto


@pytest.fixture
def buzon(app, monkeypatch):
    """Correo configurado, pero sin conexion SMTP: devuelve lo que habria salido."""
    from app.services import correo_service

    app.config.update(MAIL_USUARIO="tienda@correo.com", MAIL_CONTRASENA="clave")
    mensajes = []
    monkeypatch.setattr(correo_service, "_entregar", mensajes.append)
    return mensajes


@pytest.mark.parametrize("formato, adjunto", [
    ("pdf", "factura-BP-000001.pdf"),
    ("word", "factura-BP-000001.docx"),
])
def test_al_descargar_la_factura_le_llega_al_cliente_por_correo(comprador, buzon, formato, adjunto):
    assert comprador.get(f"/facturas/1/{formato}").status_code == 200

    assert len(buzon) == 1
    mensaje = buzon[0]
    assert mensaje["To"] == "laura@correo.com"
    assert "BP-000001" in mensaje["Subject"]
    assert [a.get_filename() for a in mensaje.iter_attachments()] == [adjunto]


def test_si_la_descarga_el_equipo_no_se_le_manda_correo_al_cliente(admin, buzon):
    assert admin.get("/facturas/1/pdf").status_code == 200
    assert buzon == []


def test_si_el_correo_falla_la_factura_se_descarga_igual(comprador, app, monkeypatch):
    from app.services import correo_service

    def rechazar(_mensaje):
        raise OSError("sin conexion")

    app.config.update(MAIL_USUARIO="tienda@correo.com", MAIL_CONTRASENA="clave")
    monkeypatch.setattr(correo_service, "_entregar", rechazar)

    r = comprador.get("/facturas/1/pdf")
    assert r.status_code == 200
    assert r.get_data().startswith(b"%PDF-")


def test_el_cliente_descarga_sus_compras_en_excel(comprador):
    from openpyxl import load_workbook

    r = comprador.get("/facturas/historial/excel")

    assert r.status_code == 200
    assert r.mimetype == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    libro = load_workbook(io.BytesIO(r.get_data()))
    assert libro.sheetnames == ["Mis compras", "Productos comprados"]

    compras = list(libro["Mis compras"].iter_rows(min_row=2, values_only=True))
    assert sorted(f[0] for f in compras) == ["BP-000001", "BP-000002"]
    # Los montos van como numeros, para que se puedan sumar en Excel
    assert sum(f[7] for f in compras) == pytest.approx(
        (89000 + round(89000 * 0.19) + 8000) + (42000 + round(42000 * 0.19) + 8000)
    )

    productos = [f[3] for f in libro["Productos comprados"].iter_rows(min_row=2, values_only=True)]
    assert sorted(productos) == ["Alimento premium perro 3kg", "Arena aglomerante gato 5kg"]


def test_el_excel_de_compras_solo_trae_las_del_cliente(app):
    from openpyxl import load_workbook

    otro = app.test_client()
    with otro.session_transaction() as s:
        s["id_usuario"] = "1003"      # cliente sin compras
    r = otro.get("/facturas/historial/excel")

    assert r.status_code == 200
    libro = load_workbook(io.BytesIO(r.get_data()))
    assert libro["Mis compras"].max_row == 1   # solo el encabezado


def test_el_excel_de_compras_pide_sesion(client):
    assert client.get("/facturas/historial/excel").status_code in (302, 401)


def test_el_administrador_descarga_el_reporte_de_ventas(admin):
    from openpyxl import load_workbook

    r = admin.get("/admin/reporte-ventas.xlsx")

    assert r.status_code == 200
    libro = load_workbook(io.BytesIO(r.get_data()))
    assert libro.sheetnames == ["Resumen", "Facturas", "Detalle de ventas", "Productos", "Clientes"]

    facturas = list(libro["Facturas"].iter_rows(min_row=2, values_only=True))
    assert len(facturas) == 2
    assert {f[3] for f in facturas} == {"Laura Gomez"}

    clientes = {f[0]: f for f in libro["Clientes"].iter_rows(min_row=2, values_only=True)}
    assert clientes["1001"][5] == 2     # compras
    assert clientes["1003"][5] == 0

    productos = {f[0]: f for f in libro["Productos"].iter_rows(min_row=2, values_only=True)}
    assert productos["PER-0001"][6] == 1   # unidades vendidas
    assert productos["GAT-0001"][6] == 2


def test_el_vendedor_no_descarga_el_reporte_de_ventas(vendedor):
    r = vendedor.get("/admin/reporte-ventas.xlsx")
    assert r.status_code in (302, 403)


@pytest.mark.parametrize("ruta", ["/facturas/1", "/facturas/1/pdf", "/facturas/1/word"])
def test_nadie_mas_puede_ver_una_factura_ajena(app, ruta):
    """El numero de factura es un consecutivo: sin este control, se adivina."""
    otro = app.test_client()
    with otro.session_transaction() as s:
        s["id_usuario"] = "1003"      # cliente distinto al dueno
    assert otro.get(ruta).status_code == 403

    anonimo = app.test_client()
    assert anonimo.get(ruta).status_code == 403


@pytest.mark.parametrize("ruta", ["/facturas/1", "/facturas/1/pdf"])
def test_el_administrador_si_puede_ver_cualquier_factura(admin, ruta):
    assert admin.get(ruta).status_code == 200


# ----------------------------------------------------------------------
# Fotos de producto (imagen_producto)
# ----------------------------------------------------------------------

def _archivo(nombre="foto.png", contenido=b"contenido-de-prueba", tipo="image/png"):
    """FileStorage de prueba: al servicio le basta con extension y tamano, no valida que sea una imagen real."""
    return FileStorage(stream=io.BytesIO(contenido), filename=nombre, content_type=tipo)


def test_un_producto_sin_fotos_usa_el_placeholder(app):
    producto = db.session.get(Producto, 1)
    assert producto.imagenes == []
    assert producto.imagen_url == "/static/img/sin-imagen.svg"


def test_subir_una_imagen_por_el_panel_la_deja_como_principal(admin, app):
    from app.models import ImagenProducto

    resp = admin.post(
        "/admin/productos/2/editar",
        data={"imagenes": [_archivo()]},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 302

    imagenes = ImagenProducto.query.filter_by(id_producto=2).all()
    assert len(imagenes) == 1
    assert imagenes[0].es_principal is True


def test_una_extension_no_permitida_se_rechaza_sin_romper_el_producto(admin, app):
    from app.models import ImagenProducto

    resp = admin.post(
        "/admin/productos/2/editar",
        data={"imagenes": [_archivo("archivo.exe")]},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert "problema con las imágenes" in resp.get_data(as_text=True)
    assert ImagenProducto.query.filter_by(id_producto=2).count() == 0
    # El producto en si no quedo afectado por el error de la imagen
    assert db.session.get(Producto, 2).nombre == "Arena aglomerante gato 5kg"


def test_un_archivo_demasiado_grande_se_rechaza(admin, app):
    from app.models import ImagenProducto

    contenido_grande = b"0" * (app.config["MAX_IMAGE_SIZE"] + 1)
    resp = admin.post(
        "/admin/productos/2/editar",
        data={"imagenes": [_archivo("grande.png", contenido_grande)]},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert "problema con las imágenes" in resp.get_data(as_text=True)
    assert ImagenProducto.query.filter_by(id_producto=2).count() == 0


def test_marcar_otra_imagen_como_principal_desmarca_las_demas(app):
    from app.models import ImagenProducto
    from app.services.imagen_service import ImagenService

    primera = ImagenService.agregar(1, archivo=_archivo("a.png"))
    segunda = ImagenService.agregar(1, archivo=_archivo("b.png"))
    assert primera.es_principal is True
    assert segunda.es_principal is False

    ImagenService.marcar_principal(segunda.id_imagen)

    assert db.session.get(ImagenProducto, primera.id_imagen).es_principal is False
    assert db.session.get(ImagenProducto, segunda.id_imagen).es_principal is True


def test_reemplazar_una_imagen_conserva_si_era_principal(app):
    from app.services.imagen_service import ImagenService

    original = ImagenService.agregar(1, archivo=_archivo("original.png"))
    id_imagen = original.id_imagen
    ruta_original = original.ruta_imagen
    assert original.es_principal is True

    # SQLAlchemy devuelve el mismo objeto (identity map): hay que guardar la
    # ruta antes de reemplazar, no comparar contra el objeto despues.
    actualizada = ImagenService.reemplazar(id_imagen, archivo=_archivo("nueva.png"))

    assert actualizada.id_imagen == id_imagen
    assert actualizada.es_principal is True
    assert actualizada.ruta_imagen != ruta_original


def test_eliminar_la_imagen_principal_promueve_a_la_siguiente(app):
    from app.models import ImagenProducto
    from app.services.imagen_service import ImagenService

    primera = ImagenService.agregar(1, archivo=_archivo("a.png"))
    segunda = ImagenService.agregar(1, archivo=_archivo("b.png"))

    ImagenService.eliminar(primera.id_imagen)

    restantes = ImagenProducto.query.filter_by(id_producto=1).all()
    assert len(restantes) == 1
    assert restantes[0].id_imagen == segunda.id_imagen
    assert restantes[0].es_principal is True


def test_eliminar_una_imagen_borra_tambien_el_archivo_fisico(app):
    from app.services.imagen_service import ImagenService

    imagen = ImagenService.agregar(1, archivo=_archivo("borrar.png"))
    ruta_absoluta = os.path.join(app.config["UPLOAD_FOLDER"], imagen.ruta_imagen[len("/static/uploads/"):])
    assert os.path.exists(ruta_absoluta)

    ImagenService.eliminar(imagen.id_imagen)

    assert not os.path.exists(ruta_absoluta)


# ----------------------------------------------------------------------
# Chat de atencion basica
# ----------------------------------------------------------------------

@pytest.mark.parametrize("mensaje, intencion_esperada", [
    ("¿Cuál es el horario de atención?", "horarios_contacto"),
    ("¿Cómo hago para comprar?", "compra_pedido"),
    ("¿Qué métodos de pago aceptan?", "pagos_envios"),
    ("¿Qué categorías de productos tienen?", "productos_categorias"),
    ("Hola, buenas tardes", "saludo"),
])
def test_el_chatbot_reconoce_cada_caso_cubierto(client, mensaje, intencion_esperada):
    resp = client.post("/chatbot/mensaje", json={"mensaje": mensaje})
    assert resp.status_code == 200

    datos = resp.get_json()
    assert datos["ok"] is True
    assert datos["intencion"] == intencion_esperada
    assert len(datos["respuesta"]) > 0


def test_el_chatbot_responde_por_defecto_si_no_entiende(client):
    resp = client.post("/chatbot/mensaje", json={"mensaje": "asdkjfh qwerty zxcvb"})
    datos = resp.get_json()

    assert resp.status_code == 200
    assert datos["ok"] is True
    assert datos["intencion"] is None
    assert "@" in datos["respuesta"]  # ofrece un correo de contacto humano


def test_el_chatbot_rechaza_un_mensaje_vacio(client):
    resp = client.post("/chatbot/mensaje", json={"mensaje": "   "})
    assert resp.status_code == 400
    assert resp.get_json()["ok"] is False


# ----------------------------------------------------------------------
# Seccion "Nosotros"
# ----------------------------------------------------------------------

def test_la_seccion_nosotros_muestra_datos_reales_de_contacto(client):
    html = client.get("/acerca").get_data(as_text=True)
    assert "antonietawsnpaws@gmail.com" in html
    assert "+57 321 390 1883" in html
    assert "901.234.567-8" not in html  # el NIT es de la factura, no de esta pagina
    assert "arquitectura MVC" not in html  # contenido tecnico de relleno, ya no debe aparecer


def test_contacto_y_nosotros_muestran_los_mismos_datos(client):
    """
    Los dos los saca de Config.EMPRESA. Antes estaban escritos a mano en
    cada plantilla y cambiar el telefono obligaba a acordarse de los dos
    sitios; esta prueba es la que avisa si vuelven a separarse.
    """
    acerca = client.get("/acerca").get_data(as_text=True)
    contacto = client.get("/contacto").get_data(as_text=True)

    for dato in ("antonietawsnpaws@gmail.com", "+57 321 390 1883", "bonespaws_666"):
        assert dato in acerca, dato
        assert dato in contacto, dato


def test_no_quedan_datos_de_contacto_de_relleno(client):
    """Los de muestra del esqueleto del proyecto ya no deben aparecer."""
    for ruta in ("/acerca", "/contacto"):
        html = client.get(ruta).get_data(as_text=True)
        assert "hola@bonesandpaws.co" not in html, ruta
        assert "300 000 0000" not in html, ruta


# ----------------------------------------------------------------------
# Gestion de personal (crear empleados, quitarles el acceso)
# ----------------------------------------------------------------------

def test_solo_el_administrador_entra_a_personal(vendedor, admin):
    assert vendedor.get("/admin/empleados", follow_redirects=False).status_code == 302
    assert admin.get("/admin/empleados").status_code == 200


def test_el_administrador_crea_un_empleado_nuevo(admin, app):
    from app.models import Empleado

    resp = admin.post(
        "/admin/empleados/crear",
        data={
            "nombre": "Marta", "apellido": "Suárez", "correo": "marta.suarez@bandp.com",
            "contrasena": "clave123", "telefono": "3001112233", "id_rol": "2",
        },
        follow_redirects=False,
    )
    assert resp.status_code == 302

    nuevo = Empleado.query.filter_by(correo="marta.suarez@bandp.com").first()
    assert nuevo is not None
    assert nuevo.nombre_rol == "Vendedor"
    assert nuevo.activo is True
    # La contrasena nunca se guarda en texto plano para cuentas nuevas
    assert nuevo.contrasena != "clave123"

    # Y ya puede iniciar sesion con lo que se le asigno
    c, datos = _entrar(app, "marta.suarez@bandp.com", "clave123")
    assert datos["ok"] is True


def test_no_se_puede_crear_dos_empleados_con_el_mismo_correo(admin):
    resp = admin.post(
        "/admin/empleados/crear",
        data={
            "nombre": "Otro", "apellido": "Admin", "correo": "vendedor",  # ya existe (fixture)
            "contrasena": "clave123", "telefono": "", "id_rol": "1",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert "Ya existe una cuenta de personal" in resp.get_data(as_text=True)


def test_desactivar_un_empleado_le_bloquea_el_login(admin, app):
    resp = admin.post("/admin/empleados/998/desactivar", follow_redirects=False)
    assert resp.status_code == 302

    assert db.session.get(Empleado, 998).activo is False

    respuesta = app.test_client().post(
        "/auth/login", data={"email": "vendedor", "password": "vendedor123"}
    )
    assert respuesta.status_code == 401
    assert respuesta.get_json()["ok"] is False


def test_desactivar_a_un_empleado_le_cierra_la_sesion_que_ya_tenia_abierta(admin, vendedor):
    """No solo bloquea logins nuevos: si ya estaba adentro, pierde el acceso en su siguiente clic."""
    assert vendedor.get("/admin/productos").status_code == 200

    admin.post("/admin/empleados/998/desactivar", follow_redirects=False)

    assert vendedor.get("/admin/productos", follow_redirects=False).status_code == 302


def test_un_administrador_no_puede_desactivar_su_propia_cuenta(admin):
    resp = admin.post("/admin/empleados/999/desactivar", follow_redirects=True)
    assert resp.status_code == 200
    assert "No puedes desactivar tu propia cuenta" in resp.get_data(as_text=True)
    assert db.session.get(Empleado, 999).activo is True


def test_reactivar_le_devuelve_el_acceso(admin, app):
    admin.post("/admin/empleados/998/desactivar")
    admin.post("/admin/empleados/998/reactivar")

    assert db.session.get(Empleado, 998).activo is True
    _, datos = _entrar(app, "vendedor", "vendedor123")
    assert datos["ok"] is True


def test_cambiar_el_rol_de_un_empleado_le_cambia_los_permisos(admin, app):
    """Bajar a alguien de Administrador a Vendedor es 'quitarle permisos' sin desactivarlo."""
    resp = admin.post(
        "/admin/empleados/998/editar",
        data={"nombre": "Vendedor", "apellido": "Demostración", "correo": "vendedor", "telefono": "", "id_rol": "1"},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert db.session.get(Empleado, 998).nombre_rol == "Administrador"


# ======================================================================
# SPRINT 4 — mejoras
# ======================================================================

# ----------------------------------------------------------------------
# Los id los asigna la base de datos, no la aplicacion
#   Antes se calculaban con MAX(id)+1, que se rompe si dos personas
#   guardan a la vez: las dos leen el mismo maximo.
# ----------------------------------------------------------------------

def test_un_producto_nuevo_recibe_su_id_de_la_base_de_datos(app):
    from app.services.producto_service import ProductoService

    producto = ProductoService.crear(codigo="PER-0900", nombre="Cama grande", descripcion="",
                                     precio=120000, stock=3, id_categoria=1, id_proveedor=1)
    # Sembrados hay 3 productos (id 1, 2 y 3): el nuevo continua la serie
    assert producto.id_producto is not None
    assert producto.id_producto > 3


def test_dos_productos_seguidos_no_comparten_id(app):
    """Es justo lo que fallaba con MAX(id_producto)+1 bajo concurrencia."""
    from app.services.producto_service import ProductoService

    uno = ProductoService.crear(codigo="PER-0901", nombre="Correa", descripcion="",
                                precio=25000, stock=5, id_categoria=1, id_proveedor=1)
    dos = ProductoService.crear(codigo="PER-0902", nombre="Bozal", descripcion="",
                                precio=30000, stock=5, id_categoria=1, id_proveedor=1)
    assert uno.id_producto != dos.id_producto


def test_una_venta_toma_su_numero_de_factura_de_la_base(comprador, app):
    from app.services.carrito_service import CarritoService
    from app.services.factura_service import FacturaService

    CarritoService.agregar_producto("1001", 1, 1)
    factura = FacturaService.registrar_venta("1001", 0.19, "Tarjeta", {})

    # Ya hay dos facturas sembradas (1 y 2): la nueva no puede repetir numero
    assert factura.numero_factura > 2
    assert Factura.query.filter_by(numero_factura=factura.numero_factura).count() == 1


# ----------------------------------------------------------------------
# Costo de envio segun la ciudad
#   Antes era un valor fijo de $12.000 para todo el pais.
# ----------------------------------------------------------------------

def test_el_envio_cuesta_segun_la_ciudad_de_la_direccion(app):
    from app.services.envio_service import EnvioService

    # Bogota es la tarifa mas barata; Pasto, la mas cara del catalogo
    assert EnvioService.calcular_costo("Calle 1 Bogotá", 50000) == 8000
    assert EnvioService.calcular_costo("Calle 3 Pasto", 50000) == 16000


def test_una_direccion_sin_ciudad_conocida_usa_la_tarifa_por_defecto(app):
    from app.services.envio_service import EnvioService

    assert EnvioService.ciudad_de("Vereda El Roble, finca sin numero") is None
    assert EnvioService.calcular_costo("Vereda El Roble", 50000) == app.config["ENVIO_TARIFA_DEFECTO"]


def test_la_ciudad_se_detecta_sin_depender_de_las_tildes(app):
    from app.services.envio_service import EnvioService

    assert EnvioService.ciudad_de("Carrera 30 MEDELLIN") == "Medellín"
    assert EnvioService.ciudad_de("carrera 30 medellín") == "Medellín"


def test_una_compra_grande_no_paga_envio(app):
    from app.services.envio_service import EnvioService

    minimo = app.config["ENVIO_GRATIS_DESDE"]
    assert EnvioService.calcular_costo("Calle 3 Pasto", minimo) == 0
    assert EnvioService.calcular_costo("Calle 3 Pasto", minimo - 1) > 0


def test_el_carrito_muestra_el_envio_calculado_y_no_uno_fijo(comprador, app):
    from app.services.carrito_service import CarritoService

    CarritoService.agregar_producto("1001", 1, 1)
    totales = CarritoService.calcular_totales("1001", 0.19)

    assert totales["ciudad_envio"] == "Bogotá"      # de la direccion del cliente
    assert totales["costo_envio"] == 8000
    assert totales["total"] == round(totales["subtotal"] + totales["iva"] + 8000, 2)


# ----------------------------------------------------------------------
# Envios: cada venta genera su guia
# ----------------------------------------------------------------------

def test_al_comprar_se_genera_el_envio_con_su_guia(comprador, app):
    from app.services.carrito_service import CarritoService
    from app.services.factura_service import FacturaService

    CarritoService.agregar_producto("1001", 1, 2)
    factura = FacturaService.registrar_venta("1001", 0.19, "Tarjeta", {})

    envio = Envio.query.filter_by(numero_factura=factura.numero_factura).first()
    assert envio is not None
    assert envio.estado == "Pendiente"
    assert envio.numero_guia.startswith("BP-")
    # La entrega estimada nunca puede ser anterior al despacho
    assert envio.fecha_entrega_estimada > envio.fecha_envio


def test_el_cliente_ve_el_estado_de_su_pedido_en_mis_compras(comprador, app):
    from app.services.carrito_service import CarritoService
    from app.services.factura_service import FacturaService

    CarritoService.agregar_producto("1001", 1, 1)
    FacturaService.registrar_venta("1001", 0.19, "Tarjeta", {})

    html = comprador.get("/facturas/historial").get_data(as_text=True)
    assert "Envío" in html
    assert "Pendiente" in html


def test_la_factura_muestra_el_seguimiento_del_pedido(comprador, app):
    """El bloque de seguimiento va fuera del documento: la factura no cambia."""
    from app.services.carrito_service import CarritoService
    from app.services.factura_service import FacturaService

    CarritoService.agregar_producto("1001", 1, 1)
    factura = FacturaService.registrar_venta("1001", 0.19, "Tarjeta", {})

    html = comprador.get(f"/facturas/{factura.numero_factura}").get_data(as_text=True)
    assert "Seguimiento de tu pedido" in html
    assert "Servientrega" in html or "Coordinadora" in html
    assert "seguimiento-pasos" in html


def test_una_factura_sin_envio_no_muestra_seguimiento(comprador):
    """Las facturas viejas del historico no tienen guia y no deben romperse."""
    html = comprador.get("/facturas/1").get_data(as_text=True)
    assert "Seguimiento de tu pedido" not in html
    assert "BP-000001" in html          # la factura si se ve completa


def test_el_pdf_de_la_factura_sigue_funcionando_con_envio(comprador, app):
    """El seguimiento es solo de la pagina web; el PDF no debe alterarse."""
    from app.services.carrito_service import CarritoService
    from app.services.factura_service import FacturaService

    CarritoService.agregar_producto("1001", 1, 1)
    factura = FacturaService.registrar_venta("1001", 0.19, "Tarjeta", {})

    r = comprador.get(f"/facturas/{factura.numero_factura}/pdf")
    assert r.status_code == 200
    assert r.get_data().startswith(b"%PDF-")


def test_el_equipo_puede_mover_un_envio_de_estado(admin, app):
    from app.services.carrito_service import CarritoService
    from app.services.factura_service import FacturaService

    CarritoService.agregar_producto("1001", 1, 1)
    factura = FacturaService.registrar_venta("1001", 0.19, "Tarjeta", {})
    envio = Envio.query.filter_by(numero_factura=factura.numero_factura).first()

    # La tabla del panel lista la guia antes de tocarla
    html = admin.get("/admin/envios").get_data(as_text=True)
    assert envio.numero_guia in html
    assert "Pendiente" in html

    admin.post(f"/admin/envios/{envio.id_envio}/estado", data={"estado": "Entregado"})

    actualizado = db.session.get(Envio, envio.id_envio)
    assert actualizado.estado == "Entregado"
    # Al marcarlo entregado se sella la fecha real
    assert actualizado.fecha_entrega_real == date.today()

    # Y el filtro por estado deja ver solo los entregados
    entregados = admin.get("/admin/envios?estado=Entregado").get_data(as_text=True)
    assert envio.numero_guia in entregados
    assert envio.numero_guia not in admin.get("/admin/envios?estado=Pendiente").get_data(as_text=True)


def test_devolver_un_envio_a_en_camino_borra_la_fecha_de_entrega(app):
    from app.services.envio_service import EnvioService

    db.session.add(Envio(id_envio=1, numero_factura=1, id_transportadora=1,
                         numero_guia="BP-000001-001", fecha_envio=date.today(),
                         fecha_entrega_estimada=date.today() + timedelta(days=3),
                         estado="Pendiente"))
    db.session.commit()

    EnvioService.actualizar_estado(1, "Entregado")
    assert db.session.get(Envio, 1).fecha_entrega_real is not None

    EnvioService.actualizar_estado(1, "En camino")
    assert db.session.get(Envio, 1).fecha_entrega_real is None


def test_un_estado_de_envio_inventado_se_rechaza(app):
    from app.services.envio_service import EnvioService

    db.session.add(Envio(id_envio=2, numero_factura=2, id_transportadora=1,
                         numero_guia="BP-000002-001", fecha_envio=date.today(),
                         estado="Pendiente"))
    db.session.commit()

    with pytest.raises(ValueError):
        EnvioService.actualizar_estado(2, "Perdido en el camino")


def test_el_panel_de_envios_exige_sesion_del_equipo(client, vendedor):
    assert client.get("/admin/envios", follow_redirects=False).status_code == 302
    assert vendedor.get("/admin/envios").status_code == 200


# ----------------------------------------------------------------------
# Paginacion
#   Antes cada listado traia todas las filas en cada visita.
# ----------------------------------------------------------------------

def _sembrar_muchos_productos(cantidad):
    from app.services.producto_service import ProductoService

    for i in range(cantidad):
        ProductoService.crear(codigo=f"OTR-{i:04d}", nombre=f"Juguete de prueba {i:02d}",
                              descripcion="Producto para probar la paginación",
                              precio=15000, stock=10, id_categoria=3, id_proveedor=1)


def test_el_catalogo_se_sirve_de_a_una_pagina(client, app):
    _sembrar_muchos_productos(20)
    por_pagina = app.config["PRODUCTOS_POR_PAGINA"]

    from app.services.producto_service import ProductoService
    primera = ProductoService.listar_paginado(pagina=1)

    assert len(primera.items) == por_pagina
    assert primera.total == 23          # 20 nuevos + 3 sembrados
    assert primera.pages > 1
    assert primera.has_next is True


def test_la_barra_de_paginacion_aparece_cuando_hay_mas_de_una_pagina(client, app):
    _sembrar_muchos_productos(20)

    html = client.get("/productos").get_data(as_text=True)
    assert 'class="paginacion"' in html
    assert "pagina=2" in html


def test_la_segunda_pagina_trae_productos_distintos(client, app):
    _sembrar_muchos_productos(20)

    from app.services.producto_service import ProductoService
    ids_p1 = {p.id_producto for p in ProductoService.listar_paginado(pagina=1).items}
    ids_p2 = {p.id_producto for p in ProductoService.listar_paginado(pagina=2).items}

    assert ids_p1 and ids_p2
    assert not (ids_p1 & ids_p2)


def test_con_pocos_productos_no_se_pinta_la_barra(client):
    """Solo hay 3 productos sembrados: una pagina y sin barra."""
    html = client.get("/productos").get_data(as_text=True)
    assert 'class="paginacion"' not in html


def test_las_cuentas_de_clientes_tambien_se_paginan(admin, app):
    from app.services.admin_service import AdminService

    for i in range(20):
        db.session.add(Cliente(id_usuario=f"200{i:04d}", nombre=f"Cliente{i}", apellido="Prueba",
                               correo=f"cliente{i}@correo.com", contrasena="123456",
                               telefono="3000000000", direccion="Calle 1 Bogotá"))
    db.session.commit()

    filas, paginacion = AdminService.listar_clientes_paginado(pagina=1)
    assert len(filas) == app.config["USUARIOS_POR_PAGINA"]
    assert paginacion.total == 22       # 20 nuevos + 2 sembrados
    assert admin.get("/admin/usuarios?pagina=2").status_code == 200


def test_la_busqueda_se_conserva_al_cambiar_de_pagina(client, app):
    _sembrar_muchos_productos(20)

    html = client.get("/productos?q=Juguete").get_data(as_text=True)
    # Los enlaces de la barra tienen que llevar la busqueda puesta
    assert "q=Juguete" in html


# ----------------------------------------------------------------------
# Migracion de contrasenas en texto plano
# ----------------------------------------------------------------------

def test_entrar_con_una_contrasena_en_texto_plano_la_deja_cifrada(app):
    """Los datos semilla traen la contrasena a la vista; al entrar se migra."""
    laura = db.session.get(Cliente, "1001")
    assert laura.contrasena == "123456"          # texto plano, como venia

    _entrar(app, "laura@correo.com", "123456")

    guardada = db.session.get(Cliente, "1001").contrasena
    assert guardada != "123456"
    assert guardada.startswith(("pbkdf2:", "scrypt:", "argon2:"))


def test_tras_migrarse_la_contrasena_sigue_sirviendo(app):
    """La persona no tiene que cambiar nada: entra igual que siempre."""
    _entrar(app, "laura@correo.com", "123456")      # primera vez: migra
    _, datos = _entrar(app, "laura@correo.com", "123456")   # segunda: ya hasheada
    assert datos["ok"] is True


def test_una_contrasena_mala_no_migra_nada(app):
    respuesta = app.test_client().post(
        "/auth/login", data={"email": "laura@correo.com", "password": "noesesta"}
    )
    assert respuesta.status_code == 401
    assert db.session.get(Cliente, "1001").contrasena == "123456"


def test_el_script_de_migracion_cifra_todas_las_cuentas(app):
    """Equivale a `python database/migrar_contrasenas.py --aplicar`."""
    from werkzeug.security import generate_password_hash
    from app.services.auth_service import esta_hasheada

    pendientes = [c for c in Cliente.query.all() if not esta_hasheada(c.contrasena)]
    assert pendientes, "los datos semilla deben empezar en texto plano"

    for cliente in pendientes:
        cliente.contrasena = generate_password_hash(cliente.contrasena)
    db.session.commit()

    assert all(esta_hasheada(c.contrasena) for c in Cliente.query.all())
    # Y las credenciales de siempre siguen funcionando
    _, datos = _entrar(app, "laura@correo.com", "123456")
    assert datos["ok"] is True


# ----------------------------------------------------------------------
# Carrito: control de stock y respuesta con totales (sin recargar)
# ----------------------------------------------------------------------

def test_el_carrito_responde_con_los_totales_recalculados(comprador):
    """Es lo que permite actualizar la pagina sin recargarla entera."""
    respuesta = comprador.post("/carrito/agregar", data={"id_producto": 1, "cantidad": 2})
    datos = respuesta.get_json()

    assert datos["ok"] is True
    totales = datos["totales"]
    assert totales["num_items"] == 1
    assert totales["unidades"] == 2
    assert totales["subtotal"].startswith("$")     # ya formateado en pesos
    assert "1" in totales["lineas"]                 # subtotal de esa linea


def test_no_se_puede_pedir_mas_stock_del_que_hay(comprador):
    """La arena tiene 4 unidades sembradas."""
    respuesta = comprador.post("/carrito/agregar", data={"id_producto": 2, "cantidad": 9})
    assert respuesta.status_code == 400
    assert respuesta.get_json()["ok"] is False


def test_lo_que_ya_esta_en_el_carrito_cuenta_para_el_stock(comprador):
    """Agregar 3 + 3 de algo de lo que solo quedan 4 no puede pasar."""
    assert comprador.post("/carrito/agregar", data={"id_producto": 2, "cantidad": 3}).status_code == 200

    respuesta = comprador.post("/carrito/agregar", data={"id_producto": 2, "cantidad": 3})
    assert respuesta.status_code == 400
    assert "carrito" in respuesta.get_json()["mensaje"]


def test_subir_la_cantidad_por_encima_del_stock_se_rechaza(comprador):
    comprador.post("/carrito/agregar", data={"id_producto": 2, "cantidad": 1})

    respuesta = comprador.post("/carrito/actualizar", data={"id_producto": 2, "cantidad": 99})
    assert respuesta.status_code == 400
    assert respuesta.get_json()["ok"] is False


def test_vaciar_el_carrito_deja_los_totales_en_cero(comprador):
    comprador.post("/carrito/agregar", data={"id_producto": 1, "cantidad": 1})
    respuesta = comprador.post("/carrito/eliminar", data={"id_producto": 1})

    totales = respuesta.get_json()["totales"]
    assert totales["num_items"] == 0
    assert totales["costo_envio"] == "$ 0"


def test_el_carrito_marca_el_tope_de_stock_en_cada_campo(comprador):
    """El navegador necesita saber el maximo para avisar antes de enviar."""
    comprador.post("/carrito/agregar", data={"id_producto": 2, "cantidad": 1})

    html = comprador.get("/carrito/").get_data(as_text=True)
    assert 'data-stock-max="4"' in html


# ----------------------------------------------------------------------
# Checkout
#   La pagina de pago no tenia ninguna prueba y estaba rota: la linea
#   `precio * cantidad | pesos` aplicaba el filtro a la cantidad (en Jinja
#   el filtro va antes que la multiplicacion), asi que cargarla con el
#   carrito lleno reventaba con un TypeError.
# ----------------------------------------------------------------------

def test_el_checkout_carga_con_el_carrito_lleno(comprador):
    comprador.post("/carrito/agregar", data={"id_producto": 1, "cantidad": 2})

    respuesta = comprador.get("/facturas/checkout")
    assert respuesta.status_code == 200

    html = respuesta.get_data(as_text=True)
    assert "Finalizar compra" in html
    # El importe de la linea: 2 x 89.000
    assert "$ 178.000" in html


def test_el_checkout_vacio_no_se_rompe(comprador):
    html = comprador.get("/facturas/checkout").get_data(as_text=True)
    assert "Tu carrito está vacío" in html


def test_el_checkout_dice_a_donde_se_envia_y_cuanto_cuesta(comprador):
    comprador.post("/carrito/agregar", data={"id_producto": 1, "cantidad": 1})

    html = comprador.get("/facturas/checkout").get_data(as_text=True)
    assert "Se enviará a" in html
    assert "Calle 1 Bogotá" in html      # direccion de la cuenta
    assert "a Bogotá" in html            # ciudad de la que sale la tarifa


# ----------------------------------------------------------------------
# Busqueda del catalogo
# ----------------------------------------------------------------------

def test_la_busqueda_encuentra_por_nombre_y_por_codigo(app):
    from app.services.producto_service import ProductoService

    por_nombre = ProductoService.listar(buscar="Arena")
    por_codigo = ProductoService.listar(buscar="GAT-0001")

    assert len(por_nombre) == 1
    assert por_nombre[0].codigo == "GAT-0001"
    assert [p.id_producto for p in por_codigo] == [p.id_producto for p in por_nombre]


def test_la_busqueda_tambien_mira_la_descripcion(app):
    from app.services.producto_service import ProductoService

    assert len(ProductoService.listar(buscar="Producto de prueba")) == 3


# ----------------------------------------------------------------------
# Accesibilidad del modal de login
# ----------------------------------------------------------------------

def test_el_modal_de_login_se_anuncia_como_ventana(client):
    """Sin esto, un lector de pantalla no sabe que hay una ventana abierta."""
    html = client.get("/").get_data(as_text=True)
    assert 'role="dialog"' in html
    assert 'aria-modal="true"' in html
    assert 'aria-labelledby="form-title"' in html


def test_el_modal_cierra_con_escape_y_atrapa_el_tabulador(app):
    """La logica vive en login.js; se comprueba que siga estando."""
    ruta = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "app", "static", "js", "login.js")
    with open(ruta, encoding="utf-8") as f:
        codigo = f.read()

    assert '"Escape"' in codigo          # cierra con Escape
    assert "atraparTabulador" in codigo  # el foco no se escapa de la ventana
    assert "elementoQueAbrio" in codigo  # y vuelve a su sitio al cerrar
