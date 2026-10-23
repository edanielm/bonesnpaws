"""
wsgi.py

Punto de entrada para Vercel (y cualquier servidor WSGI, ej. gunicorn).

Vercel busca una variable `app` de nivel superior en app.py, index.py,
server.py, main.py o wsgi.py de la raiz. El proyecto usa una application
factory (create_app) dentro del paquete app/, asi que aqui se crea la
instancia. No se llama "app.py" para no chocar con el paquete app/.

En Vercel no hay .env: las variables se cargan desde el panel del proyecto
(Settings > Environment Variables). En local, load_dotenv lee el .env si
existe y no hace nada si no.

Para desarrollo local se sigue usando:  python run.py
"""
import os

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

from app import create_app  # noqa: E402  (tras cargar el .env)

app = create_app()
