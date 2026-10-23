import os
from io import BytesIO

from flask import (
    Blueprint, current_app, render_template, request, abort, send_file,
)

from app.services import manual_service
from app.services.producto_service import ProductoService

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    # El limite se aplica en la consulta, no cortando la lista en Python:
    # antes la portada traia el catalogo entero para mostrar solo 8.
    destacados = ProductoService.listar_paginado(pagina=1, por_pagina=8).items
    categorias = ProductoService.listar_categorias()
    return render_template("index.html", productos=destacados, categorias=categorias)


@main_bp.route("/productos")
def productos():
    id_categoria = request.args.get("categoria", type=int)
    buscar = request.args.get("q", type=str)
    # El catalogo se sirve de a una pagina en vez de traer todas las filas
    # en cada visita (ver ProductoService.listar_paginado).
    paginacion = ProductoService.listar_paginado(
        id_categoria=id_categoria,
        buscar=buscar,
        pagina=request.args.get("pagina", default=1, type=int),
    )
    categorias = ProductoService.listar_categorias()
    return render_template(
        "productos/listar.html",
        productos=paginacion.items,
        paginacion=paginacion,
        categorias=categorias,
        categoria_actual=id_categoria,
        buscar=buscar or "",
    )


@main_bp.route("/productos/<int:id_producto>")
def producto_detalle(id_producto):
    producto = ProductoService.obtener(id_producto)
    if not producto.activo:
        abort(404)
    return render_template("productos/detalle.html", producto=producto)


@main_bp.route("/categorias")
def categorias():
    lista = ProductoService.listar_categorias()
    return render_template("categorias/listar.html", categorias=lista)


@main_bp.route("/acerca")
def acerca():
    return render_template("acerca.html", empresa=current_app.config["EMPRESA"])


@main_bp.route("/contacto")
def contacto():
    return render_template("contacto.html", empresa=current_app.config["EMPRESA"])


@main_bp.route("/manual")
def manual():
    """
    Manual de usuario en PDF.

    Va sin decorador a proposito: es publico. Quien no sabe como crear una
    cuenta es justamente quien mas lo necesita, asi que exigir sesion para
    leerlo seria al reves.

    Se manda `as_attachment=False` para que se abra dentro del navegador en
    vez de descargarse de una: asi se puede hojear desde el telefono sin
    tener que guardar un archivo. El boton de descargar lo pone el propio
    visor del navegador.
    """
    contenido, nombre = manual_service.obtener(
        current_app.config,
        logo=os.path.join(current_app.static_folder, "img", "logo.png"),
        # En desarrollo se rehace en cada visita para ver los cambios sin
        # reiniciar; en produccion se arma una vez y se reutiliza.
        recargar=current_app.debug,
    )

    return send_file(
        BytesIO(contenido),
        mimetype="application/pdf",
        as_attachment=False,
        download_name=nombre,
    )
