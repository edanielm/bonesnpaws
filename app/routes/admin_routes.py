"""
app/routes/admin_routes.py

Panel del equipo (/admin). Las rutas son delgadas: comprueban permisos,
piden los datos a los servicios y renderizan. Toda la logica de negocio
(estadisticas, borrado de cuentas) vive en AdminService.

Este blueprint ya no tiene formulario de login propio: todo el mundo entra
por el unico formulario del sitio (/auth/login). Lo que decide que se ve
aqui adentro es el rol del empleado:

    @requiere_staff -> Administrador y Vendedor (catalogo, consulta de clientes)
    @requiere_admin -> solo Administrador (estadisticas, borrar cuentas)
"""
from datetime import date
from io import BytesIO

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, session,
    current_app, send_file,
)

from app.services.excel_service import ExcelService
from app.services.producto_service import ProductoService
from app.services.imagen_service import ImagenService
from app.services.admin_service import AdminService
from app.services.envio_service import EnvioService, ESTADOS as ESTADOS_ENVIO
from app.routes.decoradores import requiere_staff, requiere_admin

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/login")
def login_form():
    """
    El panel ya no tiene login aparte. Se conserva la ruta para que los
    enlaces guardados sigan funcionando: manda a la portada con el modal
    de inicio de sesion abierto.
    """
    return redirect(url_for("main.index", login=1))


# ----------------------------------------------------------------------
# Estadisticas (solo administrador)
# ----------------------------------------------------------------------

@admin_bp.route("/")
@requiere_admin
def dashboard():
    return render_template(
        "admin/dashboard.html",
        resumen=AdminService.resumen_ventas(),
        serie_meses=AdminService.ventas_por_mes(6),
        metodos_pago=AdminService.ventas_por_metodo_pago(),
        top_productos=AdminService.top_productos(5),
        facturas=AdminService.facturas_recientes(10),
    )


@admin_bp.route("/reporte-ventas.xlsx")
@requiere_admin
def reporte_ventas_excel():
    """Todo lo de ventas en un Excel: resumen, facturas, detalle, productos y clientes."""
    contenido, nombre_archivo = ExcelService.reporte_ventas()
    return send_file(
        BytesIO(contenido),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=nombre_archivo,
    )


# ----------------------------------------------------------------------
# Cuentas de usuarios
#   Consultarlas puede cualquiera del equipo (un vendedor necesita ver los
#   datos de contacto de su cliente); eliminarlas, solo un administrador.
# ----------------------------------------------------------------------

@admin_bp.route("/usuarios")
@requiere_staff
def usuarios():
    buscar = request.args.get("q", type=str)
    usuarios_pagina, paginacion = AdminService.listar_clientes_paginado(
        buscar=buscar,
        pagina=request.args.get("pagina", default=1, type=int),
    )
    return render_template(
        "admin/usuarios.html",
        usuarios=usuarios_pagina,
        paginacion=paginacion,
        buscar=buscar or "",
    )


@admin_bp.route("/usuarios/<id_usuario>")
@requiere_staff
def usuario_detalle(id_usuario):
    return render_template("admin/usuario_detalle.html", **AdminService.detalle_cliente(id_usuario))


@admin_bp.route("/usuarios/<id_usuario>/eliminar", methods=["POST"])
@requiere_admin
def eliminar_usuario(id_usuario):
    try:
        nombre = AdminService.eliminar_cliente(id_usuario)
        flash(f"Cuenta de {nombre} eliminada.", "success")
        return redirect(url_for("admin.usuarios"))
    except ValueError as e:
        flash(str(e), "warning")
        return redirect(url_for("admin.usuario_detalle", id_usuario=id_usuario))


# ----------------------------------------------------------------------
# Catalogo de productos
#   Es el trabajo diario del vendedor, asi que basta con ser del equipo.
# ----------------------------------------------------------------------

@admin_bp.route("/productos")
@requiere_staff
def productos():
    buscar = request.args.get("q", type=str)
    paginacion = ProductoService.listar_paginado(
        buscar=buscar,
        incluir_inactivos=True,
        pagina=request.args.get("pagina", default=1, type=int),
        por_pagina=current_app.config["PRODUCTOS_ADMIN_POR_PAGINA"],
    )
    return render_template(
        "admin/productos.html",
        productos=paginacion.items,
        paginacion=paginacion,
        buscar=buscar or "",
        # El contador del encabezado tiene que hablar de todo el catalogo,
        # no solo de la pagina que se esta viendo.
        total_activos=ProductoService.contar(activo=True),
        total_inactivos=ProductoService.contar(activo=False),
    )


def _datos_de_producto(producto):
    """Valores de un producto ya guardado, para pintar el formulario."""
    return {
        "codigo": producto.codigo,
        "nombre": producto.nombre,
        "descripcion": producto.descripcion or "",
        "precio": producto.precio,
        "stock": producto.stock,
        "id_categoria": producto.id_categoria,
        "id_proveedor": producto.id_proveedor,
    }


def _datos_del_formulario():
    """
    Lo que la persona acaba de escribir, para devolverselo cuando el
    guardado falla (codigo repetido, precio invalido...) en vez de
    obligarla a llenar el formulario otra vez. Los archivos de imagen no se
    pueden repoblar (los navegadores no lo permiten por seguridad); si el
    guardado falla, hay que volver a seleccionarlos.
    """
    return {
        "codigo": request.form.get("codigo", ""),
        "nombre": request.form.get("nombre", ""),
        "descripcion": request.form.get("descripcion", ""),
        "precio": request.form.get("precio", ""),
        "stock": request.form.get("stock", ""),
        "id_categoria": request.form.get("id_categoria", type=int),
        "id_proveedor": request.form.get("id_proveedor", ""),
    }


def _guardar_imagenes_del_formulario(id_producto):
    """
    Agrega al producto cada archivo del input multiple 'imagenes' y, si se
    escribio, el enlace externo de 'url_imagen'. Un archivo con nombre vacio
    (input dejado en blanco) se ignora en vez de fallar.
    """
    for archivo in request.files.getlist("imagenes"):
        if archivo and archivo.filename:
            ImagenService.agregar(id_producto, archivo=archivo)

    url_externa = request.form.get("url_imagen")
    if url_externa and url_externa.strip():
        ImagenService.agregar(id_producto, url_externa=url_externa)


@admin_bp.route("/productos/crear", methods=["GET", "POST"])
@requiere_staff
def crear_producto():
    categorias = ProductoService.listar_categorias()
    primera_categoria = categorias[0].id_categoria if categorias else None

    if request.method == "GET":
        return render_template(
            "admin/producto_form.html",
            categorias=categorias,
            es_nuevo=True,
            datos={
                # Se propone un codigo libre para no tener que inventarlo,
                # pero el formulario deja escribir otro (el del proveedor,
                # por ejemplo).
                "codigo": ProductoService.sugerir_codigo(primera_categoria),
                "nombre": "", "descripcion": "", "precio": "", "stock": "",
                "id_categoria": primera_categoria, "id_proveedor": "",
            },
        )

    try:
        producto = ProductoService.crear(
            codigo=request.form.get("codigo"),
            nombre=request.form.get("nombre"),
            descripcion=request.form.get("descripcion"),
            precio=request.form.get("precio", type=float),
            stock=request.form.get("stock", type=int),
            id_categoria=request.form.get("id_categoria", type=int),
            id_proveedor=request.form.get("id_proveedor", type=int),
        )
    except ValueError as e:
        flash(str(e), "danger")
        return render_template(
            "admin/producto_form.html",
            categorias=categorias,
            es_nuevo=True,
            datos=_datos_del_formulario(),
        )

    # El producto ya quedo creado: un problema con las imagenes (formato o
    # tamano invalido) no debe hacer parecer que la creacion entera fallo,
    # o la persona reenviaria el formulario y chocaria con su propio codigo.
    try:
        _guardar_imagenes_del_formulario(producto.id_producto)
        flash("Producto creado correctamente.", "success")
    except ValueError as e:
        flash(f"Producto creado, pero hubo un problema con las imágenes: {e}", "warning")
        return redirect(url_for("admin.editar_producto", id_producto=producto.id_producto))

    return redirect(url_for("admin.productos"))


@admin_bp.route("/productos/<int:id_producto>/editar", methods=["GET", "POST"])
@requiere_staff
def editar_producto(id_producto):
    producto = ProductoService.obtener(id_producto)
    categorias = ProductoService.listar_categorias()

    if request.method == "GET":
        return render_template(
            "admin/producto_form.html",
            categorias=categorias,
            es_nuevo=False,
            producto=producto,
            datos=_datos_de_producto(producto),
        )

    try:
        ProductoService.actualizar(
            id_producto,
            codigo=request.form.get("codigo"),
            nombre=request.form.get("nombre"),
            descripcion=request.form.get("descripcion"),
            precio=request.form.get("precio", type=float),
            stock=request.form.get("stock", type=int),
            id_categoria=request.form.get("id_categoria", type=int),
            id_proveedor=request.form.get("id_proveedor", type=int),
        )
    except ValueError as e:
        flash(str(e), "danger")
        return render_template(
            "admin/producto_form.html",
            categorias=categorias,
            es_nuevo=False,
            producto=producto,
            datos=_datos_del_formulario(),
        )

    # Los datos del producto ya quedaron guardados: un problema con las
    # imagenes no debe ocultar ese cambio ni mandar a llenar el formulario
    # de nuevo, solo avisar que las fotos no se procesaron.
    try:
        _guardar_imagenes_del_formulario(id_producto)
        flash("Producto actualizado correctamente.", "success")
    except ValueError as e:
        flash(f"Producto actualizado, pero hubo un problema con las imágenes: {e}", "warning")

    return redirect(url_for("admin.editar_producto", id_producto=id_producto))


@admin_bp.route("/productos/<int:id_producto>/eliminar", methods=["POST"])
@requiere_staff
def eliminar_producto(id_producto):
    ProductoService.eliminar(id_producto)
    flash("Producto eliminado. Su registro se conserva para el historial de ventas.", "success")
    return redirect(url_for("admin.productos"))


@admin_bp.route("/productos/<int:id_producto>/reactivar", methods=["POST"])
@requiere_staff
def reactivar_producto(id_producto):
    ProductoService.reactivar(id_producto)
    flash("Producto reactivado.", "success")
    return redirect(url_for("admin.productos"))


# ----------------------------------------------------------------------
# Fotos de un producto (galeria dentro del formulario de edicion)
# ----------------------------------------------------------------------

@admin_bp.route("/productos/<int:id_producto>/imagenes/<int:id_imagen>/principal", methods=["POST"])
@requiere_staff
def marcar_imagen_principal(id_producto, id_imagen):
    ImagenService.marcar_principal(id_imagen)
    flash("Imagen principal actualizada.", "success")
    return redirect(url_for("admin.editar_producto", id_producto=id_producto))


@admin_bp.route("/productos/<int:id_producto>/imagenes/<int:id_imagen>/eliminar", methods=["POST"])
@requiere_staff
def eliminar_imagen_producto(id_producto, id_imagen):
    ImagenService.eliminar(id_imagen)
    flash("Imagen eliminada.", "success")
    return redirect(url_for("admin.editar_producto", id_producto=id_producto))


# ----------------------------------------------------------------------
# Envios
#   Seguimiento de los pedidos despachados. Es trabajo diario de quien
#   atiende la tienda, asi que basta con ser del equipo.
# ----------------------------------------------------------------------

@admin_bp.route("/envios")
@requiere_staff
def envios():
    estado = request.args.get("estado", type=str)
    return render_template(
        "admin/envios.html",
        envios=EnvioService.listar(estado=estado),
        resumen=EnvioService.resumen(),
        estado_actual=estado or "",
        estados=ESTADOS_ENVIO,
        hoy=date.today(),  # para marcar como atrasados los que ya vencieron
    )


@admin_bp.route("/envios/<int:id_envio>/estado", methods=["POST"])
@requiere_staff
def cambiar_estado_envio(id_envio):
    try:
        envio = EnvioService.actualizar_estado(id_envio, request.form.get("estado"))
        flash(f"Guía {envio.numero_guia}: ahora está «{envio.estado}».", "success")
    except ValueError as e:
        flash(str(e), "warning")
    return redirect(url_for("admin.envios", estado=request.form.get("volver_a") or None))


# ----------------------------------------------------------------------
# Personal de la tienda (solo administrador)
#   Crear cuentas de equipo o quitarles el acceso es una decision de
#   administrador, igual que borrar una cuenta de cliente.
# ----------------------------------------------------------------------

@admin_bp.route("/empleados")
@requiere_admin
def empleados():
    return render_template("admin/empleados.html", empleados=AdminService.listar_empleados())


def _datos_del_formulario_empleado():
    """Lo que la persona acaba de escribir, para devolverselo si el guardado falla."""
    return {
        "nombre": request.form.get("nombre", ""),
        "apellido": request.form.get("apellido", ""),
        "correo": request.form.get("correo", ""),
        "telefono": request.form.get("telefono", ""),
        "id_rol": request.form.get("id_rol", type=int),
    }


@admin_bp.route("/empleados/crear", methods=["GET", "POST"])
@requiere_admin
def crear_empleado():
    roles = AdminService.listar_roles()

    if request.method == "GET":
        return render_template(
            "admin/empleado_form.html",
            roles=roles,
            es_nuevo=True,
            datos={
                "nombre": "", "apellido": "", "correo": "", "telefono": "",
                "id_rol": roles[-1].id_rol if roles else None,  # el mas restringido por defecto
            },
        )

    try:
        AdminService.crear_empleado(
            nombre=request.form.get("nombre"),
            apellido=request.form.get("apellido"),
            correo=request.form.get("correo"),
            contrasena=request.form.get("contrasena"),
            telefono=request.form.get("telefono"),
            id_rol=request.form.get("id_rol", type=int),
        )
        flash("Cuenta de personal creada correctamente.", "success")
    except ValueError as e:
        flash(str(e), "danger")
        return render_template(
            "admin/empleado_form.html", roles=roles, es_nuevo=True, datos=_datos_del_formulario_empleado()
        )

    return redirect(url_for("admin.empleados"))


@admin_bp.route("/empleados/<int:id_empleado>/editar", methods=["GET", "POST"])
@requiere_admin
def editar_empleado(id_empleado):
    empleado = AdminService.obtener_empleado(id_empleado)
    roles = AdminService.listar_roles()

    if request.method == "GET":
        return render_template(
            "admin/empleado_form.html",
            roles=roles,
            es_nuevo=False,
            empleado=empleado,
            datos={
                "nombre": empleado.nombre, "apellido": empleado.apellido,
                "correo": empleado.correo, "telefono": empleado.telefono or "",
                "id_rol": empleado.id_rol,
            },
        )

    try:
        AdminService.actualizar_empleado(
            id_empleado,
            nombre=request.form.get("nombre"),
            apellido=request.form.get("apellido"),
            correo=request.form.get("correo"),
            telefono=request.form.get("telefono"),
            id_rol=request.form.get("id_rol", type=int),
        )
        flash("Datos del empleado actualizados.", "success")
    except ValueError as e:
        flash(str(e), "danger")
        return render_template(
            "admin/empleado_form.html", roles=roles, es_nuevo=False, empleado=empleado,
            datos=_datos_del_formulario_empleado(),
        )

    return redirect(url_for("admin.empleados"))


@admin_bp.route("/empleados/<int:id_empleado>/desactivar", methods=["POST"])
@requiere_admin
def desactivar_empleado(id_empleado):
    try:
        AdminService.desactivar_empleado(id_empleado, id_empleado_actual=session.get("id_empleado"))
        flash("El empleado ya no tiene acceso al panel.", "success")
    except ValueError as e:
        flash(str(e), "warning")
    return redirect(url_for("admin.empleados"))


@admin_bp.route("/empleados/<int:id_empleado>/reactivar", methods=["POST"])
@requiere_admin
def reactivar_empleado(id_empleado):
    AdminService.reactivar_empleado(id_empleado)
    flash("Acceso del empleado restablecido.", "success")
    return redirect(url_for("admin.empleados"))
