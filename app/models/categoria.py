from app.extensions import db


class Categoria(db.Model):
    __tablename__ = "categoria"

    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    productos = db.relationship("Producto", backref="categoria", lazy=True)

    def to_dict(self):
        return {"id_categoria": self.id_categoria, "nombre": self.nombre}
