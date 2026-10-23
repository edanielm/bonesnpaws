"""
app/extensions.py

Instancias compartidas de extensiones (SQLAlchemy). Se declaran aqui,
separadas de __init__.py, para que app/models/*.py puedan hacer
`from app.extensions import db` sin generar imports circulares.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
