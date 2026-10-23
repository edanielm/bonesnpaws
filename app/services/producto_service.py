"""
app/services/producto_service.py
Reglas de negocio para el catalogo de productos.

Sobre el codigo del producto
----------------------------
Cada producto se identifica de cara al negocio por su `codigo` (PER-0001,
GAT-0012, ...), no por un consecutivo automatico. La tabla `producto` ya no
tiene AUTO_INCREMENT: antes, guardar dos veces el mismo articulo generaba dos
filas con id distinto y el catalogo terminaba duplicado. Ahora el codigo es
UNIQUE en la base de datos, asi que el duplicado se rechaza.

La validacion esta en dos sitios a proposito, igual que con precio y stock:
aqui, para poder mostrarle un mensaje claro a quien esta usando el panel, y
en la base de datos (UNIQUE + trigger trg_producto_bi), como ultima linea de
defensa si el dato entra por phpMyAdmin o por un script suelto.
"""
import re
import unicodedata

from flask import current_app
from sqlalchemy.exc import OperationalError

from app.extensions import db
from app.models import Producto, Categoria

# Prefijo cuando la categoria no da uno utilizable
PREFIJO_POR_DEFECTO = "PRD"
LARGO_MAXIMO_CODIGO = 20

# Largo minimo de palabra que indexa MySQL en un indice FULLTEXT de InnoDB
# (variable innodb_ft_min_token_size, 3 por defecto). Por debajo de eso el
# indice no tiene nada que buscar y hay que caer al LIKE de siempre.
LARGO_MINIMO_FULLTEXT = 3

# Caracteres con significado propio dentro de MATCH ... AGAINST en modo
# booleano (+ obligatorio, - excluye, * comodin...). Se quitan del texto que
# escribe el usuario para que 'PER-0001' no se interprete como "PER pero no
# 0001", que devolveria resultados equivocados.
_OPERADORES_FULLTEXT = re.compile(r'[+\-><()~*"@]')


class ProductoService:

    # ------------------------------------------------------------------
    # Busqueda del catalogo
    # ------------------------------------------------------------------

    @staticmethod
    def _aplicar_busqueda(query, buscar, forzar_like=False):
        """
        Filtra el catalogo por lo que escribio la persona.

        En MySQL usa el indice FULLTEXT `ft_producto_busqueda` sobre
        (nombre, descripcion): un `LIKE '%texto%'` no puede aprovechar
        ningun indice y obliga a recorrer la tabla entera, mientras que
        MATCH ... AGAINST si lo usa.

        Se cae al LIKE de siempre en dos casos:
          - el motor no es MySQL (las pruebas corren sobre SQLite, que no
            tiene FULLTEXT);
          - el termino es mas corto que el minimo que indexa MySQL, donde
            el indice no encontraria nada.

        En ambos caminos se busca tambien por codigo con LIKE: es como el
        equipo identifica un producto cuando lo tiene delante (etiqueta,
        factura, remision) y los codigos llevan guion, que FULLTEXT parte
        en dos.
        """
        termino = (buscar or "").strip()
        if not termino:
            return query

        like = f"%{termino}%"
        por_codigo = Producto.codigo.ilike(like)

        palabras = _OPERADORES_FULLTEXT.sub(" ", termino).split()
        usa_fulltext = (
            not forzar_like
            and db.engine.dialect.name == "mysql"
            and palabras
            and all(len(p) >= LARGO_MINIMO_FULLTEXT for p in palabras)
        )

        if usa_fulltext:
            # Cada palabra se marca como obligatoria (+) y con comodin al
            # final (*), para que "alim" encuentre "alimento" igual que lo
            # hacia el LIKE.
            expresion = " ".join(f"+{palabra}*" for palabra in palabras)
            por_texto = db.text(
                "MATCH (producto.nombre, producto.descripcion) "
                "AGAINST (:termino_ft IN BOOLEAN MODE)"
            ).bindparams(termino_ft=expresion)
            return query.filter(db.or_(por_texto, por_codigo))

        return query.filter(
            db.or_(Producto.nombre.ilike(like), Producto.descripcion.ilike(like), por_codigo)
        )

    @staticmethod
    def _query_catalogo(id_categoria=None, buscar=None, incluir_inactivos=False,
                        forzar_like=False):
        """Consulta base del catalogo, compartida por listar() y listar_paginado()."""
        query = Producto.query
        if not incluir_inactivos:
            query = query.filter_by(activo=True)
        if id_categoria:
            query = query.filter_by(id_categoria=id_categoria)
        query = ProductoService._aplicar_busqueda(query, buscar, forzar_like)
        return query.order_by(Producto.nombre)

    @staticmethod
    def _ejecutar_con_respaldo(construir):
        """
        Ejecuta una consulta del catalogo y, si MySQL se queja del indice
        FULLTEXT, la repite con el LIKE de siempre.

        Es la red de seguridad para una base que todavia no tiene aplicada la
        migracion `migracion_producto_autoincrement.sql`: sin el indice,
        MATCH ... AGAINST falla con el error 1191 ("Can't find FULLTEXT index
        matching the column list") y el buscador se caeria entero. Asi, como
        mucho, la busqueda es mas lenta, pero nunca deja de funcionar.

        `construir` recibe forzar_like y devuelve el resultado ya ejecutado.
        """
        try:
            return construir(False)
        except OperationalError:
            db.session.rollback()
            return construir(True)

    @staticmethod
    def listar(id_categoria=None, buscar=None, incluir_inactivos=False):
        return ProductoService._ejecutar_con_respaldo(
            lambda forzar_like: ProductoService._query_catalogo(
                id_categoria, buscar, incluir_inactivos, forzar_like
            ).all()
        )

    @staticmethod
    def listar_paginado(id_categoria=None, buscar=None, incluir_inactivos=False,
                        pagina=1, por_pagina=None):
        """
        Lo mismo que listar(), pero de a una pagina.

        Antes el catalogo traia todas las filas de golpe en cada visita.
        Devuelve el objeto Pagination de Flask-SQLAlchemy: `.items` son los
        productos de esta pagina y el resto (`.pages`, `.has_next`...) lo usa
        la barra de paginacion de las plantillas.
        """
        if por_pagina is None:
            por_pagina = current_app.config["PRODUCTOS_POR_PAGINA"]

        return ProductoService._ejecutar_con_respaldo(
            lambda forzar_like: ProductoService._query_catalogo(
                id_categoria, buscar, incluir_inactivos, forzar_like
            ).paginate(page=pagina or 1, per_page=por_pagina, error_out=False)
        )

    @staticmethod
    def contar(activo=None):
        """
        Cuantos productos hay, contando en la base de datos en vez de traer
        las filas para medirlas en Python. `activo=True` cuenta los
        publicados y `activo=False` los eliminados (borrado logico).
        """
        query = db.session.query(db.func.count(Producto.id_producto))
        if activo is not None:
            query = query.filter(Producto.activo == activo)
        return int(query.scalar() or 0)

    @staticmethod
    def obtener(id_producto):
        return db.get_or_404(Producto, id_producto)

    @staticmethod
    def obtener_por_codigo(codigo):
        return Producto.query.filter_by(codigo=ProductoService.normalizar_codigo(codigo)).first()

    @staticmethod
    def listar_categorias():
        return Categoria.query.order_by(Categoria.nombre).all()

    # ------------------------------------------------------------------
    # Codigo unico del producto
    # ------------------------------------------------------------------

    @staticmethod
    def normalizar_codigo(codigo):
        """
        Mayusculas y sin espacios sobrantes. Es lo que hace util al UNIQUE:
        sin esto 'per-0001', 'PER-0001 ' y 'PER-0001' serian tres codigos
        distintos para la base de datos, y el mismo producto entraria tres
        veces. El trigger trg_producto_bi aplica esta misma normalizacion.
        """
        return (codigo or "").strip().upper()

    @staticmethod
    def prefijo_de(id_categoria):
        """Iniciales de la categoria: Perros -> PER, Gatos -> GAT, Otros -> OTR."""
        categoria = db.session.get(Categoria, id_categoria) if id_categoria else None
        if not categoria:
            return PREFIJO_POR_DEFECTO
        # Se quitan las tildes para que 'Baño' no produzca un codigo raro
        sin_tildes = unicodedata.normalize("NFKD", categoria.nombre)
        letras = "".join(c for c in sin_tildes if c.isalpha() and c.isascii()).upper()
        return letras[:3] or PREFIJO_POR_DEFECTO

    @staticmethod
    def sugerir_codigo(id_categoria=None):
        """
        Siguiente codigo libre de la categoria (PER-0001, PER-0002, ...).
        Es solo una propuesta para el formulario: quien crea el producto
        puede escribir el codigo del proveedor si lo prefiere.
        """
        prefijo = ProductoService.prefijo_de(id_categoria)
        codigos = (
            db.session.query(Producto.codigo)
            .filter(Producto.codigo.like(f"{prefijo}-%"))
            .all()
        )

        mayor = 0
        for (codigo,) in codigos:
            sufijo = codigo.rsplit("-", 1)[-1]
            if sufijo.isdigit():
                mayor = max(mayor, int(sufijo))

        return f"{prefijo}-{mayor + 1:04d}"

    @staticmethod
    def _validar_codigo(codigo, id_actual=None):
        """
        Devuelve el codigo normalizado o lanza ValueError con el motivo.
        `id_actual` es el producto que se esta editando: su propio codigo no
        cuenta como duplicado de si mismo.
        """
        codigo = ProductoService.normalizar_codigo(codigo)

        if not codigo:
            raise ValueError("El producto debe tener un código único.")
        if len(codigo) > LARGO_MAXIMO_CODIGO:
            raise ValueError(
                f"El código no puede tener más de {LARGO_MAXIMO_CODIGO} caracteres."
            )

        existente = Producto.query.filter_by(codigo=codigo).first()
        if existente and existente.id_producto != id_actual:
            raise ValueError(
                f"Ya existe un producto con el código {codigo}: «{existente.nombre}». "
                f"Cada producto debe tener un código distinto."
            )

        return codigo

    @staticmethod
    def _validar(precio, stock):
        """
        Mismas reglas que aplican los triggers trg_producto_bi / trg_producto_bu
        (ver database/objetos.sql). Se comprueban aqui para poder mostrar un
        mensaje al usuario; el trigger queda como ultima linea de defensa por si
        el dato entra por fuera de la aplicacion (phpMyAdmin, un script, etc.).
        """
        if precio is not None and precio <= 0:
            raise ValueError("El precio del producto debe ser mayor que cero.")
        if stock is not None and stock < 0:
            raise ValueError("El stock del producto no puede ser negativo.")

    @staticmethod
    def crear(codigo, nombre, descripcion, precio, stock, id_categoria, id_proveedor):
        ProductoService._validar(precio, stock)
        codigo = ProductoService._validar_codigo(codigo)
        # El id interno lo asigna la base de datos (AUTO_INCREMENT). Antes lo
        # calculaba la aplicacion con MAX(id_producto)+1, lo que fallaba si
        # dos personas del equipo guardaban un producto a la vez: las dos
        # leian el mismo maximo y la segunda chocaba con la llave primaria.
        # Quien impide productos duplicados no es el id sino el UNIQUE de
        # `codigo`, que sigue igual.
        producto = Producto(
            codigo=codigo,
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            id_categoria=id_categoria,
            id_proveedor=id_proveedor,
        )
        db.session.add(producto)
        db.session.commit()
        return producto

    @staticmethod
    def actualizar(id_producto, **campos):
        producto = db.get_or_404(Producto, id_producto)
        ProductoService._validar(campos.get("precio"), campos.get("stock"))
        if campos.get("codigo") is not None:
            campos["codigo"] = ProductoService._validar_codigo(
                campos["codigo"], id_actual=id_producto
            )
        for clave, valor in campos.items():
            if valor is not None and hasattr(producto, clave):
                setattr(producto, clave, valor)
        db.session.commit()
        return producto

    @staticmethod
    def eliminar(id_producto):
        """
        Borrado logico: un producto ya vendido no se puede borrar de verdad,
        porque sus lineas de `detalle` son parte del historico de facturas y
        la llave foranea detalle -> producto no permite dejarlas huerfanas.

        "Eliminar" pone activo=False en vez de borrar la fila: el producto
        desaparece de la tienda y del catalogo activo del panel, pero su
        registro se conserva (nombre, precio, etc. siguen apareciendo en las
        facturas viejas). Se puede deshacer con reactivar().
        """
        producto = db.get_or_404(Producto, id_producto)
        producto.activo = False
        db.session.commit()

    @staticmethod
    def reactivar(id_producto):
        producto = db.get_or_404(Producto, id_producto)
        producto.activo = True
        db.session.commit()

    @staticmethod
    def descontar_stock(id_producto, cantidad):
        producto = db.get_or_404(Producto, id_producto)
        if producto.stock < cantidad:
            raise ValueError(f"Stock insuficiente para '{producto.nombre}'.")
        producto.stock -= cantidad
        db.session.commit()
