from app.extensions import db


# Nombres de los roles tal como estan sembrados en la tabla `rol`.
# Se usan como constantes para que el resto del proyecto no compare contra
# cadenas sueltas escritas a mano en cada archivo.
ROL_ADMINISTRADOR = "Administrador"
ROL_VENDEDOR = "Vendedor"


class Rol(db.Model):
    """
    Catalogo de roles del personal. Define que puede hacer un empleado
    dentro del panel: el Administrador entra a todo, el Vendedor solo al
    catalogo y a la consulta de clientes.
    """
    __tablename__ = "rol"

    id_rol = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    descripcion = db.Column(db.String(255))

    empleados = db.relationship("Empleado", backref="rol", lazy=True)

    def __repr__(self):
        return f"<Rol {self.nombre}>"
