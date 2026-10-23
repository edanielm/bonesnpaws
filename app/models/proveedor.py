from app.extensions import db


class Proveedor(db.Model):
    __tablename__ = "proveedor"

    id_proveedor = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    correo = db.Column(db.String(100))
    asesor = db.Column(db.String(100), nullable=False, default="")

    productos = db.relationship("Producto", backref="proveedor", lazy=True)
