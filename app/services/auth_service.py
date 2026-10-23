"""
app/services/auth_service.py

Reglas de negocio de autenticacion. Las rutas solo delegan aqui.

Hay un solo punto de entrada, AuthService.login(), porque en el sitio existe
un unico formulario de inicio de sesion para todos: clientes, administradores
y vendedores. Las cuentas siguen viviendo en dos tablas distintas (`cliente`
y `empleado`, cada una con sus llaves foraneas al historial), asi que login()
es el que se encarga de mirar en ambas y decir de que tipo es la cuenta.

Nota sobre contrasenas: los datos semilla de 'cliente'/'empleado' en
bandp.sql vienen en texto plano (ej. '123456'). Los registros NUEVOS
siempre se guardan hasheados con Werkzeug.

Restablecer una contrasena olvidada no se maneja aqui sino en
`app/services/recuperacion_service.py`, porque ya no es solo comparar dos
datos: implica generar un codigo, mandarlo por correo y controlar su
vencimiento.

Para que esas contrasenas heredadas dejen de estar en texto plano sin
romper los datos existentes, la migracion ocurre sola: cuando alguien
entra con una contrasena guardada en texto plano, se verifica, se
reescribe hasheada y a partir de ahi esa cuenta ya solo tiene hash. Es la
"migracion perezosa" de `_verificar_contrasena`. Para migrar todas las
cuentas de una vez, sin esperar a que cada quien inicie sesion, esta el
script `database/migrar_contrasenas.py`.
"""
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.models import Cliente, Empleado

# Tipos de cuenta. No son el rol: dicen en que tabla vive el usuario.
# Un 'empleado' ademas trae un rol (Administrador / Vendedor).
TIPO_CLIENTE = "cliente"
TIPO_EMPLEADO = "empleado"

# Prefijos con los que Werkzeug marca sus hashes. Si el valor guardado no
# empieza por uno de estos, es una contrasena heredada en texto plano.
PREFIJOS_HASH = ("pbkdf2:", "scrypt:", "argon2:")


def esta_hasheada(contrasena_guardada):
    """True si el valor guardado ya es un hash y no texto plano."""
    return (contrasena_guardada or "").startswith(PREFIJOS_HASH)


def _verificar_contrasena(contrasena_plana, usuario):
    """
    Comprueba la contrasena de un Cliente o un Empleado.

    Si la cuenta todavia tenia la contrasena en texto plano (dato semilla) y
    esta es correcta, se reescribe hasheada en ese mismo momento: la cuenta
    queda migrada sin que la persona tenga que hacer nada y sin tocar el
    resto de la fila.
    """
    guardada = usuario.contrasena or ""

    if esta_hasheada(guardada):
        return check_password_hash(guardada, contrasena_plana)

    if contrasena_plana != guardada:
        return False

    usuario.contrasena = generate_password_hash(contrasena_plana)
    db.session.commit()
    return True


class AuthService:

    @staticmethod
    def login(correo, contrasena):
        """
        Login unico para todo el mundo: cliente, administrador o vendedor
        entran por el mismo formulario y esta funcion averigua quien es.

        Busca la cuenta primero entre los clientes y luego entre los
        empleados. Devuelve (tipo, usuario) -> ('cliente', Cliente) o
        ('empleado', Empleado), y (None, None) si las credenciales no
        corresponden a nadie.

        La ruta no necesita saber que hay dos tablas: solo mira el tipo que
        recibe para decidir a donde mandar a la persona.
        """
        cliente = AuthService.login_cliente(correo, contrasena)
        if cliente:
            return TIPO_CLIENTE, cliente

        empleado = AuthService.login_empleado(correo, contrasena)
        if empleado:
            return TIPO_EMPLEADO, empleado

        return None, None

    @staticmethod
    def login_cliente(correo, contrasena):
        cliente = Cliente.query.filter_by(correo=correo).first()
        if cliente and _verificar_contrasena(contrasena, cliente):
            return cliente
        return None

    @staticmethod
    def login_empleado(correo, contrasena):
        # activo=True excluye a quien ya no sigue en la empresa: aunque
        # escriba bien su contrasena, una cuenta desactivada no entra.
        empleado = Empleado.query.filter_by(correo=correo, activo=True).first()
        if empleado and _verificar_contrasena(contrasena, empleado):
            return empleado
        return None

    @staticmethod
    def registrar_cliente(id_usuario, nombre, apellido, correo, contrasena, telefono, direccion):
        if db.session.get(Cliente, id_usuario):
            raise ValueError("Ya existe un usuario registrado con ese numero de documento.")
        if Cliente.query.filter_by(correo=correo).first():
            raise ValueError("Ese correo ya esta registrado.")

        nuevo = Cliente(
            id_usuario=id_usuario,
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            contrasena=generate_password_hash(contrasena),
            telefono=telefono,
            direccion=direccion,
        )
        db.session.add(nuevo)
        db.session.commit()
        return nuevo
