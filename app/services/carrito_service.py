"""
app/services/carrito_service.py

Carrito persistente en base de datos (tablas 'carrito' y 'carrito_producto'
ya existentes en bandp.sql), en vez de solo sesion, tal como se decidio.
Cada cliente tiene, como maximo, un carrito activo; se reutiliza si ya existe.
"""
from app.extensions import db
from app.models import Carrito, CarritoProducto, Cliente, Producto
from app.services.envio_service import EnvioService


class CarritoService:

    @staticmethod
    def _obtener_o_crear_carrito(id_usuario):
        carrito = Carrito.query.filter_by(id_usuario=id_usuario).first()
        if not carrito:
            # El id lo asigna la base de datos (AUTO_INCREMENT). Antes se
            # calculaba aqui con MAX(id_carrito)+1: si dos clientes creaban
            # su carrito a la vez, los dos leian el mismo maximo y el
            # segundo chocaba con una llave primaria repetida.
            carrito = Carrito(id_usuario=id_usuario)
            db.session.add(carrito)
            db.session.commit()
        return carrito

    @staticmethod
    def obtener_items(id_usuario):
        carrito = CarritoService._obtener_o_crear_carrito(id_usuario)
        return carrito.items

    @staticmethod
    def agregar_producto(id_usuario, id_producto, cantidad=1):
        producto = db.get_or_404(Producto, id_producto)
        if not producto.activo:
            raise ValueError("Ese producto ya no esta disponible.")
        if cantidad < 1:
            raise ValueError("La cantidad debe ser al menos 1.")
        if producto.stock < cantidad:
            raise ValueError("No hay suficiente stock disponible.")

        carrito = CarritoService._obtener_o_crear_carrito(id_usuario)
        item = CarritoProducto.query.filter_by(
            id_carrito=carrito.id_carrito, id_producto=id_producto
        ).first()

        if item:
            # Lo que ya estaba en el carrito cuenta para el stock: agregar 3
            # unidades de algo de lo que quedan 4 y ya se llevaban 2 no puede
            # dejar 5 reservadas.
            if item.cantidad + cantidad > producto.stock:
                raise ValueError(
                    f"Solo quedan {producto.stock} unidad(es) y ya tienes "
                    f"{item.cantidad} en el carrito."
                )
            item.cantidad += cantidad
        else:
            item = CarritoProducto(
                id_carrito=carrito.id_carrito, id_producto=id_producto, cantidad=cantidad
            )
            db.session.add(item)

        db.session.commit()
        return item

    @staticmethod
    def actualizar_cantidad(id_usuario, id_producto, cantidad):
        """
        Cambia cuantas unidades de un producto hay en el carrito. Bajar de 1
        equivale a quitarlo. No se puede pedir mas de lo que hay en
        inventario: el navegador ya limita el campo, pero la regla se
        comprueba tambien aqui, que es donde de verdad manda.
        """
        carrito = CarritoService._obtener_o_crear_carrito(id_usuario)
        item = CarritoProducto.query.filter_by(
            id_carrito=carrito.id_carrito, id_producto=id_producto
        ).first_or_404()

        if cantidad < 1:
            db.session.delete(item)
        else:
            if cantidad > item.producto.stock:
                raise ValueError(
                    f"Solo quedan {item.producto.stock} unidad(es) de "
                    f"«{item.producto.nombre}»."
                )
            item.cantidad = cantidad
        db.session.commit()

    @staticmethod
    def eliminar_producto(id_usuario, id_producto):
        carrito = CarritoService._obtener_o_crear_carrito(id_usuario)
        item = CarritoProducto.query.filter_by(
            id_carrito=carrito.id_carrito, id_producto=id_producto
        ).first_or_404()
        db.session.delete(item)
        db.session.commit()

    @staticmethod
    def vaciar(id_usuario):
        carrito = CarritoService._obtener_o_crear_carrito(id_usuario)
        CarritoProducto.query.filter_by(id_carrito=carrito.id_carrito).delete()
        db.session.commit()

    @staticmethod
    def calcular_totales(id_usuario, iva_porcentaje):
        """
        Subtotal, IVA, envio y total del carrito de un cliente.

        El envio ya no es un valor fijo: lo calcula EnvioService a partir de
        la ciudad que aparece en la direccion del cliente, y sale gratis si
        la compra supera el minimo configurado. Se devuelven tambien los
        datos que explican ese cobro (ciudad detectada, cuanto falta para el
        envio gratis) para que el carrito pueda mostrarlos.
        """
        items = CarritoService.obtener_items(id_usuario)
        subtotal = sum(float(i.producto.precio) * i.cantidad for i in items)
        iva = round(subtotal * iva_porcentaje, 2)

        cliente = db.session.get(Cliente, id_usuario)
        envio = EnvioService.detalle_costo(cliente.direccion if cliente else None, subtotal)
        total = subtotal + iva + envio["costo_envio"]

        return {
            "items": items,
            "subtotal": round(subtotal, 2),
            "iva": iva,
            "total": round(total, 2),
            **envio,
        }
