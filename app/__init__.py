"""
app/__init__.py

Application factory. Crea y configura la instancia de Flask, inicializa
SQLAlchemy y registra todos los Blueprints (rutas) del proyecto.
"""
from flask import Flask

from app.config import Config
from app.extensions import db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    with app.app_context():
        from app import models  # noqa: F401  (registra los modelos en SQLAlchemy)

    # --- Filtros de formato para las plantillas (pesos, monto en letras) ---
    from app.formato import registrar_filtros
    registrar_filtros(app)

    # --- Blueprints ---
    from app.routes.main_routes import main_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.perfil_routes import perfil_bp
    from app.routes.carrito_routes import carrito_bp
    from app.routes.factura_routes import factura_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.chatbot_routes import chatbot_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(perfil_bp)
    app.register_blueprint(carrito_bp)
    app.register_blueprint(factura_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chatbot_bp)

    # --- Contexto global para templates ---
    @app.context_processor
    def inject_globals():
        from flask import session, url_for
        from app.models import ROL_ADMINISTRADOR
        return {
            # Nombre de quien tiene la sesion abierta, sea cliente o del
            # equipo. La barra superior muestra el mismo chip de perfil
            # para todos; lo que cambia es lo que hay detras.
            "usuario_logueado": session.get("nombre") or session.get("nombre_admin"),
            "id_usuario_sesion": session.get("id_usuario"),
            "admin_logueado": session.get("nombre_admin"),
            "rol_sesion": session.get("rol"),
            "es_staff": "id_empleado" in session,
            "es_administrador": session.get("rol") == ROL_ADMINISTRADOR,
            # Imagen de respaldo local (no depende de internet ni de que la
            # carpeta uploads/ haya viajado con el proyecto a este equipo).
            "img_placeholder": url_for("static", filename="img/sin-imagen.svg"),
        }

    return app
