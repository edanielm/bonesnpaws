from app.extensions import db


class Factura(db.Model):
    __tablename__ = "factura"

    numero_factura = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    iva = db.Column(db.Numeric(10, 2), nullable=False)
    costo_envio = db.Column(db.Numeric(10, 2), nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    id_usuario = db.Column(db.String(11), db.ForeignKey("cliente.id_usuario"), nullable=False)
    id_empleado = db.Column(db.Integer, db.ForeignKey("empleado.id_empleado"), nullable=False)
    metodo_pago = db.Column(
        db.Enum("Tarjeta", "PSE", "Transferencia", name="metodo_pago_enum"),
        nullable=False,
        default="Tarjeta",
    )

    detalles = db.relationship("Detalle", backref="factura", lazy=True)
    envio = db.relationship("Envio", backref="factura", uselist=False, lazy=True)


class Detalle(db.Model):
    __tablename__ = "detalle"

    id_detalle = db.Column(db.Integer, primary_key=True)
    numero_factura = db.Column(db.Integer, db.ForeignKey("factura.numero_factura"), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey("producto.id_producto"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal_producto = db.Column(db.Numeric(10, 2), nullable=False)

    producto = db.relationship("Producto", lazy=True)
