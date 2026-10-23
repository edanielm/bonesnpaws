"""
app/models/__init__.py

Importa todos los modelos en un solo lugar para que:
1) SQLAlchemy registre todas las clases/tablas al crear la app.
2) El resto del proyecto pueda hacer `from app.models import Producto, Cliente, ...`
"""
from app.models.categoria import Categoria
from app.models.proveedor import Proveedor
from app.models.producto import Producto
from app.models.imagen_producto import ImagenProducto
from app.models.cliente import Cliente
from app.models.rol import Rol, ROL_ADMINISTRADOR, ROL_VENDEDOR
from app.models.empleado import Empleado
from app.models.factura import Factura, Detalle
from app.models.carrito import Carrito, CarritoProducto
from app.models.catalogos import MetodoPago, Transportadora, Envio
from app.models.pagos import Pse, Tarjeta, TransferenciaBancaria
from app.models.codigo_recuperacion import (
    CodigoRecuperacion,
    INTENTOS_MAXIMOS,
    VIGENCIA_MINUTOS,
)

__all__ = [
    "Categoria",
    "Proveedor",
    "Producto",
    "ImagenProducto",
    "Cliente",
    "Rol",
    "ROL_ADMINISTRADOR",
    "ROL_VENDEDOR",
    "Empleado",
    "Factura",
    "Detalle",
    "Carrito",
    "CarritoProducto",
    "MetodoPago",
    "Transportadora",
    "Envio",
    "Pse",
    "Tarjeta",
    "TransferenciaBancaria",
    "CodigoRecuperacion",
    "INTENTOS_MAXIMOS",
    "VIGENCIA_MINUTOS",
]
