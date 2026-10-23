"""
app/services/admin_service.py

Reglas de negocio del panel de administracion: estadisticas de ventas y
gestion de las cuentas de clientes.

Sigue la misma "Regla de Oro" del resto del proyecto: las rutas no calculan
nada, solo llaman aqui. Todas las agregaciones se resuelven en la base de
datos (SUM/COUNT/GROUP BY) en vez de traer las filas y sumarlas en Python.
"""
from datetime import date

from flask import current_app
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import Cliente, Factura, Detalle, Producto, Carrito, CarritoProducto, Empleado, Rol


MESES_ES = [
    "ene", "feb", "mar", "abr", "may", "jun",
    "jul", "ago", "sep", "oct", "nov", "dic",
]


def _f(valor):
    """Numeric/Decimal de MySQL -> float, tratando None como 0."""
    return float(valor) if valor is not None else 0.0


class AdminService:

    # ------------------------------------------------------------------
    # ESTADISTICAS DE VENTAS
    # ------------------------------------------------------------------

    @staticmethod
    def resumen_ventas():
        """
        Indicadores principales del negocio: cuanto se ha vendido, cuantas
        facturas hay, cuanto vale la compra promedio y como va el mes actual
        comparado con el mes pasado.
        """
        total_ventas, num_facturas = (
            db.session.query(
                db.func.coalesce(db.func.sum(Factura.total), 0),
                db.func.count(Factura.numero_factura),
            ).first()
        )
        total_ventas = _f(total_ventas)
        num_facturas = int(num_facturas or 0)

        unidades = db.session.query(
            db.func.coalesce(db.func.sum(Detalle.cantidad), 0)
        ).scalar()

        hoy = date.today()
        mes_actual = AdminService._ventas_de_mes(hoy.year, hoy.month)
        anio_prev, mes_prev = (hoy.year - 1, 12) if hoy.month == 1 else (hoy.year, hoy.month - 1)
        mes_anterior = AdminService._ventas_de_mes(anio_prev, mes_prev)

        # Variacion mes a mes. Si el mes pasado fue 0 no hay porcentaje que
        # calcular (seria division por cero), asi que se devuelve None y la
        # plantilla muestra un guion.
        if mes_anterior > 0:
            variacion = round((mes_actual - mes_anterior) / mes_anterior * 100, 1)
        else:
            variacion = None

        return {
            "total_ventas": total_ventas,
            "num_facturas": num_facturas,
            "ticket_promedio": total_ventas / num_facturas if num_facturas else 0.0,
            "unidades_vendidas": int(unidades or 0),
            "ventas_mes": mes_actual,
            "ventas_mes_anterior": mes_anterior,
            "variacion_mes": variacion,
            "num_clientes": db.session.query(db.func.count(Cliente.id_usuario)).scalar() or 0,
            "num_productos": db.session.query(db.func.count(Producto.id_producto)).scalar() or 0,
            "productos_agotados": db.session.query(db.func.count(Producto.id_producto))
                                            .filter(Producto.stock == 0).scalar() or 0,
            "productos_stock_bajo": db.session.query(db.func.count(Producto.id_producto))
                                              .filter(Producto.stock > 0, Producto.stock <= 5).scalar() or 0,
        }

    @staticmethod
    def _ventas_de_mes(anio, mes):
        total = (
            db.session.query(db.func.coalesce(db.func.sum(Factura.total), 0))
            .filter(db.extract("year", Factura.fecha) == anio)
            .filter(db.extract("month", Factura.fecha) == mes)
            .scalar()
        )
        return _f(total)

    @staticmethod
    def ventas_por_mes(cantidad_meses=6):
        """
        Serie para el grafico de barras: los ultimos N meses en orden
        cronologico. Los meses sin ventas se incluyen en cero para que el
        grafico no quede con huecos.
        """
        hoy = date.today()
        periodos = []
        anio, mes = hoy.year, hoy.month
        for _ in range(cantidad_meses):
            periodos.append((anio, mes))
            anio, mes = (anio - 1, 12) if mes == 1 else (anio, mes - 1)
        periodos.reverse()

        filas = (
            db.session.query(
                db.extract("year", Factura.fecha).label("anio"),
                db.extract("month", Factura.fecha).label("mes"),
                db.func.sum(Factura.total).label("total"),
                db.func.count(Factura.numero_factura).label("facturas"),
            )
            .group_by("anio", "mes")
            .all()
        )
        mapa = {(int(f.anio), int(f.mes)): (_f(f.total), int(f.facturas)) for f in filas}

        serie = []
        for anio, mes in periodos:
            total, facturas = mapa.get((anio, mes), (0.0, 0))
            serie.append({
                "anio": anio,
                "mes": mes,
                "etiqueta": MESES_ES[mes - 1],
                "total": total,
                "facturas": facturas,
            })

        # Alto de cada barra en % respecto al mes mas alto de la serie
        tope = max((p["total"] for p in serie), default=0)
        for punto in serie:
            punto["pct"] = round(punto["total"] / tope * 100, 1) if tope else 0
        return serie

    @staticmethod
    def ventas_por_metodo_pago():
        filas = (
            db.session.query(
                Factura.metodo_pago,
                db.func.count(Factura.numero_factura).label("facturas"),
                db.func.sum(Factura.total).label("total"),
            )
            .group_by(Factura.metodo_pago)
            .all()
        )
        datos = [
            {"metodo": f.metodo_pago, "facturas": int(f.facturas), "total": _f(f.total)}
            for f in filas
        ]
        datos.sort(key=lambda d: d["total"], reverse=True)
        tope = max((d["total"] for d in datos), default=0)
        for d in datos:
            d["pct"] = round(d["total"] / tope * 100, 1) if tope else 0
        return datos

    @staticmethod
    def top_productos(limite=5):
        filas = (
            db.session.query(
                Producto.nombre,
                db.func.sum(Detalle.cantidad).label("unidades"),
                db.func.sum(Detalle.subtotal_producto).label("ingresos"),
            )
            .join(Detalle, Detalle.id_producto == Producto.id_producto)
            .group_by(Producto.id_producto, Producto.nombre)
            .order_by(db.desc("unidades"))
            .limit(limite)
            .all()
        )
        datos = [
            {"nombre": f.nombre, "unidades": int(f.unidades or 0), "ingresos": _f(f.ingresos)}
            for f in filas
        ]
        tope = max((d["unidades"] for d in datos), default=0)
        for d in datos:
            d["pct"] = round(d["unidades"] / tope * 100, 1) if tope else 0
        return datos

    @staticmethod
    def facturas_recientes(limite=10):
        """Ultimas facturas con el nombre del cliente ya resuelto."""
        filas = (
            db.session.query(Factura, Cliente)
            .join(Cliente, Cliente.id_usuario == Factura.id_usuario)
            .order_by(Factura.fecha.desc(), Factura.numero_factura.desc())
            .limit(limite)
            .all()
        )
        return [{"factura": f, "cliente": c} for f, c in filas]

    # ------------------------------------------------------------------
    # PERSONAL DE LA TIENDA
    # ------------------------------------------------------------------

    @staticmethod
    def resumen_empleado(id_empleado):
        """
        Actividad de un empleado, para su perfil: cuantas ventas ha
        atendido, cuanto suman y cuando fue la ultima. Equivale a la vista
        `vista_equipo` de la base de datos (ver database/objetos.sql).
        """
        facturas, facturado, ultima = (
            db.session.query(
                db.func.count(Factura.numero_factura),
                db.func.coalesce(db.func.sum(Factura.total), 0),
                db.func.max(Factura.fecha),
            )
            .filter(Factura.id_empleado == id_empleado)
            .first()
        )

        facturas = int(facturas or 0)
        facturado = _f(facturado)
        return {
            "ventas_atendidas": facturas,
            "total_facturado": facturado,
            "ticket_promedio": facturado / facturas if facturas else 0.0,
            "ultima_venta": ultima,
        }

    # ------------------------------------------------------------------
    # GESTION DE CUENTAS DE CLIENTES
    # ------------------------------------------------------------------

    @staticmethod
    def _query_clientes(buscar=None):
        """
        Consulta base de las cuentas de clientes con su actividad de compra
        resumida, ordenada por cuanto han gastado. Compartida por
        listar_clientes() y listar_clientes_paginado().
        """
        query = (
            db.session.query(
                Cliente,
                db.func.count(Factura.numero_factura).label("compras"),
                db.func.coalesce(db.func.sum(Factura.total), 0).label("gastado"),
                db.func.max(Factura.fecha).label("ultima_compra"),
            )
            .outerjoin(Factura, Factura.id_usuario == Cliente.id_usuario)
            .group_by(Cliente.id_usuario)
        )

        if buscar:
            like = f"%{buscar}%"
            query = query.filter(
                db.or_(
                    Cliente.nombre.ilike(like),
                    Cliente.apellido.ilike(like),
                    Cliente.correo.ilike(like),
                    Cliente.id_usuario.ilike(like),
                )
            )

        return query.order_by(db.desc("gastado"), Cliente.nombre)

    @staticmethod
    def _fila_cliente(fila):
        cliente, compras, gastado, ultima = fila
        return {
            "cliente": cliente,
            "compras": int(compras or 0),
            "gastado": _f(gastado),
            "ultima_compra": ultima,
        }

    @staticmethod
    def listar_clientes(buscar=None):
        """
        Todos los clientes con su actividad de compra resumida. `buscar`
        filtra por nombre, apellido, documento o correo.
        """
        return [AdminService._fila_cliente(f) for f in AdminService._query_clientes(buscar).all()]

    @staticmethod
    def listar_clientes_paginado(buscar=None, pagina=1, por_pagina=None):
        """
        Lo mismo que listar_clientes(), pero de a una pagina: el panel ya
        tiene mas de cien cuentas sembradas y traerlas todas en cada visita
        no escala.

        Devuelve (filas_de_esta_pagina, objeto_paginacion) para que la
        plantilla pinte la tabla y la barra de paginas.
        """
        if por_pagina is None:
            por_pagina = current_app.config["USUARIOS_POR_PAGINA"]

        paginacion = AdminService._query_clientes(buscar).paginate(
            page=pagina or 1, per_page=por_pagina, error_out=False
        )
        return [AdminService._fila_cliente(f) for f in paginacion.items], paginacion

    @staticmethod
    def detalle_cliente(id_usuario):
        """Ficha completa de un cliente: sus datos, sus compras y su carrito."""
        cliente = db.get_or_404(Cliente, id_usuario)

        facturas = (
            Factura.query.filter_by(id_usuario=id_usuario)
            .order_by(Factura.fecha.desc(), Factura.numero_factura.desc())
            .all()
        )

        gastado = sum(_f(f.total) for f in facturas)
        unidades = (
            db.session.query(db.func.coalesce(db.func.sum(Detalle.cantidad), 0))
            .join(Factura, Factura.numero_factura == Detalle.numero_factura)
            .filter(Factura.id_usuario == id_usuario)
            .scalar()
        )
        items_carrito = (
            db.session.query(db.func.coalesce(db.func.sum(CarritoProducto.cantidad), 0))
            .join(Carrito, Carrito.id_carrito == CarritoProducto.id_carrito)
            .filter(Carrito.id_usuario == id_usuario)
            .scalar()
        )

        return {
            "cliente": cliente,
            "facturas": facturas,
            "num_compras": len(facturas),
            "gastado": gastado,
            "ticket_promedio": gastado / len(facturas) if facturas else 0.0,
            "unidades": int(unidades or 0),
            "items_carrito": int(items_carrito or 0),
        }

    @staticmethod
    def eliminar_cliente(id_usuario):
        """
        Elimina la cuenta de un cliente junto con su carrito.

        Un cliente que ya tiene facturas NO se puede borrar: sus ventas son
        parte del historico contable y de las estadisticas del panel, y la
        llave foranea factura -> cliente no permite dejarlas huerfanas.
        En ese caso se lanza ValueError y la ruta lo muestra como aviso.
        """
        cliente = db.get_or_404(Cliente, id_usuario)

        num_facturas = (
            db.session.query(db.func.count(Factura.numero_factura))
            .filter(Factura.id_usuario == id_usuario)
            .scalar()
        )
        if num_facturas:
            raise ValueError(
                f"No se puede eliminar a {cliente.nombre} {cliente.apellido}: "
                f"tiene {num_facturas} compra(s) registradas en el historial de ventas."
            )

        # El carrito si se borra: no es informacion contable.
        carritos = Carrito.query.filter_by(id_usuario=id_usuario).all()
        for carrito in carritos:
            CarritoProducto.query.filter_by(id_carrito=carrito.id_carrito).delete()
            db.session.delete(carrito)

        nombre = f"{cliente.nombre} {cliente.apellido}"
        db.session.delete(cliente)
        db.session.commit()
        return nombre

    # ------------------------------------------------------------------
    # GESTION DE PERSONAL (EMPLEADOS)
    #   Solo el Administrador crea cuentas de equipo o les quita el acceso
    #   (ver @requiere_admin en admin_routes.py). El registro publico
    #   (/auth/registro) solo abre cuentas de cliente.
    # ------------------------------------------------------------------

    @staticmethod
    def listar_roles():
        return Rol.query.order_by(Rol.id_rol).all()

    @staticmethod
    def listar_empleados(incluir_inactivos=True):
        query = Empleado.query
        if not incluir_inactivos:
            query = query.filter_by(activo=True)
        return query.order_by(Empleado.nombre).all()

    @staticmethod
    def obtener_empleado(id_empleado):
        return db.get_or_404(Empleado, id_empleado)

    @staticmethod
    def crear_empleado(nombre, apellido, correo, contrasena, telefono, id_rol):
        """
        Da de alta una cuenta de personal (administrador o vendedor). El
        correo debe ser unico entre todo el equipo y la contrasena se
        guarda siempre hasheada (a diferencia de los datos semilla viejos
        en texto plano; ver AuthService).
        """
        correo = (correo or "").strip()
        if not correo:
            raise ValueError("El correo es obligatorio.")
        if Empleado.query.filter_by(correo=correo).first():
            raise ValueError(f"Ya existe una cuenta de personal con el correo {correo}.")
        if not contrasena or len(contrasena) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")
        if not nombre or not apellido:
            raise ValueError("El nombre y el apellido son obligatorios.")
        if not db.session.get(Rol, id_rol):
            raise ValueError("El rol seleccionado no existe.")

        empleado = Empleado(
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            contrasena=generate_password_hash(contrasena),
            telefono=telefono,
            id_rol=id_rol,
        )
        db.session.add(empleado)
        db.session.commit()
        return empleado

    @staticmethod
    def actualizar_empleado(id_empleado, nombre=None, apellido=None, correo=None, telefono=None, id_rol=None):
        """
        Edita los datos de un empleado, incluyendo su rol: bajar a alguien
        de Administrador a Vendedor es la forma de quitarle permisos sin
        cerrarle del todo el acceso al panel (para eso esta desactivar_empleado).
        """
        empleado = db.get_or_404(Empleado, id_empleado)

        if correo is not None:
            correo = correo.strip()
            if not correo:
                raise ValueError("El correo es obligatorio.")
            existente = Empleado.query.filter_by(correo=correo).first()
            if existente and existente.id_empleado != id_empleado:
                raise ValueError(f"Ya existe otra cuenta de personal con el correo {correo}.")

        if id_rol is not None and not db.session.get(Rol, id_rol):
            raise ValueError("El rol seleccionado no existe.")

        campos = {"nombre": nombre, "apellido": apellido, "correo": correo, "telefono": telefono, "id_rol": id_rol}
        for clave, valor in campos.items():
            if valor is not None:
                setattr(empleado, clave, valor)
        db.session.commit()
        return empleado

    @staticmethod
    def desactivar_empleado(id_empleado, id_empleado_actual=None):
        """
        Quita el acceso a un empleado que ya no sigue en la empresa: no
        puede volver a iniciar sesion (AuthService.login_empleado exige
        activo=True) y si tenia una sesion abierta la pierde en su
        siguiente clic (ver requiere_staff en decoradores.py).

        No se borra la cuenta: sus facturas son parte del historico de
        ventas y la llave foranea factura -> empleado no permite dejarlas
        huerfanas. Se puede revertir con reactivar_empleado.
        """
        if id_empleado_actual is not None and int(id_empleado) == int(id_empleado_actual):
            raise ValueError("No puedes desactivar tu propia cuenta mientras tienes la sesión abierta.")

        empleado = db.get_or_404(Empleado, id_empleado)
        empleado.activo = False
        db.session.commit()

    @staticmethod
    def reactivar_empleado(id_empleado):
        empleado = db.get_or_404(Empleado, id_empleado)
        empleado.activo = True
        db.session.commit()
