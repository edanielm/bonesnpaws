from app.extensions import db
from app.models.rol import ROL_ADMINISTRADOR, ROL_VENDEDOR


class Empleado(db.Model):
    """
    Personal de la tienda. Cada empleado tiene un rol (ver app/models/rol.py)
    que decide a que partes del panel entra:

        Administrador -> estadisticas, cuentas de clientes y catalogo
        Vendedor      -> catalogo y consulta de clientes

    Todos entran por el mismo formulario de login que los clientes; lo que
    los distingue es la tabla en la que esta su cuenta y el rol que traen.
    """
    __tablename__ = "empleado"

    id_empleado = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), nullable=False, unique=True)
    contrasena = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(20))
    # Por defecto Vendedor: el permiso mas restringido, para que un empleado
    # nuevo nunca quede como administrador por descuido.
    id_rol = db.Column(
        db.Integer, db.ForeignKey("rol.id_rol"), nullable=False, default=2, server_default="2"
    )
    # Un empleado que ya no sigue en la empresa no se borra (sus facturas son
    # parte del historico de ventas): se desactiva. Bloquea su login y cierra
    # cualquier sesion que ya tuviera abierta (ver decoradores.py).
    activo = db.Column(db.Boolean, nullable=False, default=True, server_default="1")

    facturas = db.relationship("Factura", backref="empleado", lazy=True)

    @property
    def nombre_rol(self):
        return self.rol.nombre if self.rol else ROL_VENDEDOR

    @property
    def es_administrador(self):
        return self.nombre_rol == ROL_ADMINISTRADOR

    @property
    def es_vendedor(self):
        return self.nombre_rol == ROL_VENDEDOR

    def to_dict(self):
        return {
            "id_empleado": self.id_empleado,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "correo": self.correo,
            "telefono": self.telefono,
            "rol": self.nombre_rol,
            "activo": self.activo,
        }
