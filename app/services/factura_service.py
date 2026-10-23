"""
app/services/factura_service.py

Implementa el caso de uso "Registrar Venta" descrito en el blueprint:
Ruta -> Servicio (valida stock y calcula total) -> Modelo -> Base de Datos.
"""
from datetime import date

from flask import current_app

from app.extensions import db
from app.models import Factura, Detalle, Pse, Tarjeta, TransferenciaBancaria
from app.services.carrito_service import CarritoService
from app.services.envio_service import EnvioService


# Fila admin/sistema sembrada en `empleado`, a la que se le atribuyen las
# ventas de la tienda en linea. Vive en Config para no repetir el numero
# suelto; se deja este alias por si la app se usa fuera de un contexto Flask.
ID_EMPLEADO_SISTEMA = 999


class FacturaService:

    @staticmethod
    def registrar_venta(id_usuario, iva_porcentaje, metodo_pago, datos_pago):
        """
        Crea la factura y su detalle a partir del carrito del cliente,
        descuenta stock y guarda el detalle del metodo de pago elegido.
        """
        totales = CarritoService.calcular_totales(id_usuario, iva_porcentaje)
        items = totales["items"]
        if not items:
            raise ValueError("El carrito esta vacio.")

        # 1. Validar stock de cada item (Regla de Oro: sin logica en las rutas)
        for item in items:
            if item.producto.stock < item.cantidad:
                raise ValueError(f"Stock insuficiente para '{item.producto.nombre}'.")

        # El numero de factura lo asigna la base de datos (AUTO_INCREMENT),
        # no la aplicacion. Antes se calculaba con MAX(numero_factura)+1:
        # si dos clientes pagaban al mismo tiempo, ambos leian el mismo
        # maximo y el segundo chocaba con una factura ya existente.
        factura = Factura(
            fecha=date.today(),
            subtotal=totales["subtotal"],
            iva=totales["iva"],
            costo_envio=totales["costo_envio"],
            total=totales["total"],
            id_usuario=id_usuario,
            id_empleado=current_app.config.get("ID_EMPLEADO_SISTEMA", ID_EMPLEADO_SISTEMA),
            metodo_pago=metodo_pago,
        )
        db.session.add(factura)
        db.session.flush()  # la BD asigna numero_factura antes del commit final

        # 2. Detalle de factura.
        #    El stock NO se descuenta aqui: lo hace el trigger `trg_detalle_ai`
        #    de la base de datos (ver database/objetos.sql). Se dejo un solo
        #    responsable para que no se descuente dos veces.
        for item in items:
            detalle = Detalle(
                numero_factura=factura.numero_factura,
                id_producto=item.id_producto,
                cantidad=item.cantidad,
                precio_unitario=item.producto.precio,
                subtotal_producto=float(item.producto.precio) * item.cantidad,
            )
            db.session.add(detalle)

        # 3. Detalle del metodo de pago
        FacturaService._guardar_detalle_pago(factura.numero_factura, metodo_pago, datos_pago, totales["total"])

        # 4. Envio: cada venta genera su guia, igual que genera su factura.
        #    Asi el cliente puede seguir su pedido desde "Mis compras" y el
        #    equipo desde el panel.
        EnvioService.crear_para_factura(factura.numero_factura)

        # 5. Vaciar carrito
        from app.models import CarritoProducto
        CarritoProducto.query.filter(
            CarritoProducto.id_producto.in_([i.id_producto for i in items])
        ).filter(
            CarritoProducto.id_carrito.in_([i.id_carrito for i in items])
        ).delete(synchronize_session=False)

        db.session.commit()
        return factura

    @staticmethod
    def _guardar_detalle_pago(numero_factura, metodo_pago, datos_pago, monto):
        """
        Guarda el detalle del medio de pago en la tabla que corresponda.
        Los id de estas tablas tambien los asigna la base de datos
        (AUTO_INCREMENT), no un MAX()+1 calculado aqui.
        """
        if metodo_pago == "PSE":
            db.session.add(Pse(
                numero_factura=numero_factura,
                banco=datos_pago.get("banco", "No especificado"),
                monto=monto,
            ))
        elif metodo_pago == "Tarjeta":
            db.session.add(Tarjeta(
                numero_factura=numero_factura,
                # De la tarjeta solo se conservan los ultimos 4 digitos.
                numero_tarjeta=datos_pago.get("numero_tarjeta", "0000")[-4:].rjust(16, "*"),
                cvv="***",
                fecha_vencimiento=datos_pago.get("fecha_vencimiento") or date.today(),
                franquicia=datos_pago.get("franquicia", "No especificada"),
                monto=monto,
            ))
        elif metodo_pago == "Transferencia":
            db.session.add(TransferenciaBancaria(
                numero_factura=numero_factura,
                banco=datos_pago.get("banco", "No especificado"),
                numero_cuenta=datos_pago.get("numero_cuenta", "No especificada"),
                titular=datos_pago.get("titular", "No especificado"),
                monto=monto,
            ))

    @staticmethod
    def historial_cliente(id_usuario):
        return (
            Factura.query.filter_by(id_usuario=id_usuario)
            .order_by(Factura.fecha.desc())
            .all()
        )

    @staticmethod
    def listar_todas():
        return Factura.query.order_by(Factura.fecha.desc()).all()
