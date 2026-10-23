from app.extensions import db


class Producto(db.Model):
    __tablename__ = "producto"

    # Llave numerica interna, AUTO_INCREMENT en la base de datos: la asigna
    # el motor, no la aplicacion. Se conserva porque `detalle` y
    # `carrito_producto` la referencian desde el historial de ventas.
    # Quien identifica al producto de cara al negocio es `codigo`.
    id_producto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Identificador de negocio del producto (PER-0001, GAT-0012...). Es UNIQUE
    # en la base de datos: es lo que impide cargar dos veces el mismo articulo.
    codigo = db.Column(db.String(20), nullable=False, unique=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255))
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    id_categoria = db.Column(db.Integer, db.ForeignKey("categoria.id_categoria"), nullable=False)
    id_proveedor = db.Column(db.Integer, db.ForeignKey("proveedor.id_proveedor"), nullable=False)
    # Borrado logico: un producto ya vendido no se puede borrar de verdad
    # (la llave foranea detalle -> producto lo impide). "Eliminar" pone
    # activo=False en vez de borrar la fila, para conservar su registro.
    activo = db.Column(db.Boolean, nullable=False, default=True, server_default="1")

    imagenes = db.relationship(
        "ImagenProducto",
        back_populates="producto",
        order_by="ImagenProducto.fecha_carga",
        cascade="all, delete-orphan",
    )

    @property
    def imagen_principal(self):
        """
        La foto marcada como principal; si ninguna lo esta, la mas antigua
        cargada; si el producto no tiene fotos, None.
        """
        for imagen in self.imagenes:
            if imagen.es_principal:
                return imagen
        return self.imagenes[0] if self.imagenes else None

    @property
    def imagen_url(self):
        """
        Respaldo local para plantillas que no dependen de un servicio
        externo ni de internet cuando el producto no tiene fotos.
        """
        principal = self.imagen_principal
        return principal.ruta_imagen if principal else "/static/img/sin-imagen.svg"

    def to_dict(self):
        return {
            "id_producto": self.id_producto,
            "codigo": self.codigo,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "precio": float(self.precio),
            "stock": self.stock,
            "id_categoria": self.id_categoria,
            "categoria": self.categoria.nombre if self.categoria else None,
            "id_proveedor": self.id_proveedor,
            "imagen_url": self.imagen_url,
            "imagenes": [imagen.to_dict() for imagen in self.imagenes],
            "activo": self.activo,
        }
