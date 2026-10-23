from app.extensions import db


class Cliente(db.Model):
    __tablename__ = "cliente"

    id_usuario = db.Column(db.String(11), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), nullable=False, unique=True)
    contrasena = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(255))

    facturas = db.relationship("Factura", backref="cliente", lazy=True)
    carritos = db.relationship("Carrito", backref="cliente", lazy=True)

    def to_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "correo": self.correo,
            "telefono": self.telefono,
            "direccion": self.direccion,
        }
