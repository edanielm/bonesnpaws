"""
app/models/imagen_producto.py

Fotos de un producto. Un producto puede tener varias filas aqui; `es_principal`
marca cual se usa como miniatura en catalogo, listado admin, detalle y carrito.

Se relaciona con `Producto` por `id_producto` (la llave numerica interna), la
misma convencion que usan `Detalle` y `CarritoProducto`: `codigo` sigue siendo
solo el identificador de negocio del producto, no una llave foranea real.
Ver database/schema.sql y database/migracion_imagen_producto.sql.
"""
from app.extensions import db


class ImagenProducto(db.Model):
    __tablename__ = "imagen_producto"

    id_imagen = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey("producto.id_producto"), nullable=False)
    # Ruta servida por Flask ("/static/uploads/productos/xxx.jpg") o URL externa.
    ruta_imagen = db.Column(db.String(255), nullable=False)
    es_principal = db.Column(db.Boolean, nullable=False, default=False, server_default="0")
    fecha_carga = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    producto = db.relationship("Producto", back_populates="imagenes")

    def to_dict(self):
        return {
            "id_imagen": self.id_imagen,
            "id_producto": self.id_producto,
            "ruta_imagen": self.ruta_imagen,
            "es_principal": self.es_principal,
        }
