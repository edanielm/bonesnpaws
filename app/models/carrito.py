from app.extensions import db


class Carrito(db.Model):
    __tablename__ = "carrito"

    id_carrito = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.String(11), db.ForeignKey("cliente.id_usuario"), nullable=False)

    items = db.relationship("CarritoProducto", backref="carrito", lazy=True, cascade="all, delete-orphan")


class CarritoProducto(db.Model):
    __tablename__ = "carrito_producto"

    id_carrito = db.Column(db.Integer, db.ForeignKey("carrito.id_carrito"), primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey("producto.id_producto"), primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False)

    producto = db.relationship("Producto", lazy=True)
