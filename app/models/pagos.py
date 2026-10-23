"""
app/models/pagos.py

Detalle del metodo de pago usado en cada factura. Cada tabla se enlaza
1 a 1 con 'factura' via numero_factura, tal como esta definido en bandp.sql.
"""
from app.extensions import db


class Pse(db.Model):
    __tablename__ = "pse"

    id_pse = db.Column(db.Integer, primary_key=True)
    numero_factura = db.Column(db.Integer, db.ForeignKey("factura.numero_factura"), nullable=False, unique=True)
    banco = db.Column(db.String(100), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)


class Tarjeta(db.Model):
    __tablename__ = "tarjeta"

    id_tarjeta = db.Column(db.Integer, primary_key=True)
    numero_factura = db.Column(db.Integer, db.ForeignKey("factura.numero_factura"), nullable=False, unique=True)
    numero_tarjeta = db.Column(db.String(20), nullable=False)
    cvv = db.Column(db.String(4), nullable=False)
    fecha_vencimiento = db.Column(db.Date, nullable=False)
    franquicia = db.Column(db.String(50), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)


class TransferenciaBancaria(db.Model):
    __tablename__ = "transferencia_bancaria"

    id_transferencia = db.Column(db.Integer, primary_key=True)
    numero_factura = db.Column(db.Integer, db.ForeignKey("factura.numero_factura"), nullable=False, unique=True)
    banco = db.Column(db.String(100), nullable=False)
    numero_cuenta = db.Column(db.String(30), nullable=False)
    titular = db.Column(db.String(100), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
