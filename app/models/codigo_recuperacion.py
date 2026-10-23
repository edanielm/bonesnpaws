from datetime import datetime, timedelta

from app.extensions import db

# Cuanto vive un codigo antes de vencerse y cuantas veces se puede
# escribir mal antes de tener que pedir uno nuevo.
VIGENCIA_MINUTOS = 15
INTENTOS_MAXIMOS = 5


class CodigoRecuperacion(db.Model):
    """
    Codigo de un solo uso que se envia por correo para restablecer la
    contrasena de un cliente.

    Solo se guarda el *hash* del codigo, igual que con las contrasenas:
    quien abra la tabla en phpMyAdmin no puede leer el codigo de nadie ni
    usarlo para entrar a una cuenta.
    """
    __tablename__ = "codigo_recuperacion"

    id_codigo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.String(11), db.ForeignKey("cliente.id_usuario"), nullable=False, index=True)
    codigo_hash = db.Column(db.String(255), nullable=False)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.now)
    expira_en = db.Column(db.DateTime, nullable=False)
    intentos = db.Column(db.Integer, nullable=False, default=0)
    usado = db.Column(db.Boolean, nullable=False, default=False)

    cliente = db.relationship("Cliente", backref="codigos_recuperacion", lazy=True)

    @staticmethod
    def vencimiento_desde_ahora():
        return datetime.now() + timedelta(minutes=VIGENCIA_MINUTOS)

    @property
    def vencido(self):
        return datetime.now() > self.expira_en

    @property
    def agotado(self):
        return self.intentos >= INTENTOS_MAXIMOS

    @property
    def vigente(self):
        return not self.usado and not self.vencido and not self.agotado
