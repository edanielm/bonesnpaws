"""
app/models/catalogos.py

Tablas de catalogo puro (sin logica propia), siguiendo el mismo patron
que 'categoria': metodo_pago, transportadora.
"""
from app.extensions import db


class MetodoPago(db.Model):
    __tablename__ = "metodo_pago"

    id_metodo = db.Column(db.Integer, primary_key=True)
    nombre_metodo = db.Column(db.String(20), nullable=False)


class Transportadora(db.Model):
    __tablename__ = "transportadora"

    id_transportadora = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))

    envios = db.relationship("Envio", backref="transportadora", lazy=True)


class Envio(db.Model):
    __tablename__ = "envio"

    id_envio = db.Column(db.Integer, primary_key=True)
    numero_factura = db.Column(db.Integer, db.ForeignKey("factura.numero_factura"), nullable=False, unique=True)
    id_transportadora = db.Column(db.Integer, db.ForeignKey("transportadora.id_transportadora"), nullable=False)
    numero_guia = db.Column(db.String(50), nullable=False, unique=True)
    fecha_envio = db.Column(db.Date)
    fecha_entrega_estimada = db.Column(db.Date)
    fecha_entrega_real = db.Column(db.Date)
    estado = db.Column(
        db.Enum("Pendiente", "En camino", "Entregado", name="envio_estado_enum"),
        default="Pendiente",
    )
