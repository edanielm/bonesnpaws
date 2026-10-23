"""
app/services/imagen_service.py

Fotos de producto: guardado en disco (o referencia a una URL externa) y su
registro en la tabla `imagen_producto`. Reemplaza al esquema anterior de una
sola imagen por producto (columna `producto.imagen_url`).

Sobre el archivo en disco
--------------------------
Un archivo subido queda en app/static/uploads/productos/ de ESTE equipo; al
mover el proyecto a otro computador hay que copiar tambien esa carpeta junto
con el codigo. Una URL externa (ej. un enlace directo de Imgur) en cambio
viaja sola con el dump de la base de datos, sin depender de archivos locales.
Ambas opciones estan disponibles por eso; se recomienda Imgur cuando el
proyecto se vaya a compartir entre equipos.

Sobre "la imagen principal"
----------------------------
Cada producto puede tener varias fotos, pero solo una marcada `es_principal`
(la miniatura que se ve en catalogo, listado admin, detalle y carrito). La
primera foto que se le carga a un producto queda como principal automatica;
las siguientes no, salvo que se pida explicitamente con `marcar_principal`.
"""
import os
import uuid

from flask import current_app
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import ImagenProducto

SUBCARPETA = "productos"


def _extension_permitida(nombre_archivo):
    ext = nombre_archivo.rsplit(".", 1)[-1].lower() if "." in nombre_archivo else ""
    return ext in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]


def _tamano_archivo(archivo):
    archivo.stream.seek(0, os.SEEK_END)
    tamano = archivo.stream.tell()
    archivo.stream.seek(0)
    return tamano


class ImagenService:

    # ------------------------------------------------------------------
    # Archivo en disco
    # ------------------------------------------------------------------

    @staticmethod
    def _validar_archivo(archivo):
        """Extension permitida y tamano dentro del limite; si no, ValueError."""
        if not archivo or not archivo.filename:
            raise ValueError("No se seleccionó ningún archivo.")
        if not _extension_permitida(archivo.filename):
            raise ValueError("Formato de imagen no permitido (usa png, jpg, jpeg, gif o webp).")

        limite = current_app.config["MAX_IMAGE_SIZE"]
        tamano = _tamano_archivo(archivo)
        if tamano == 0:
            raise ValueError("El archivo está vacío.")
        if tamano > limite:
            raise ValueError(f"La imagen supera el tamaño máximo permitido ({limite // (1024 * 1024)} MB).")

    @staticmethod
    def _guardar_archivo(archivo):
        """Guarda el archivo subido en static/uploads/productos/ y devuelve su ruta publica."""
        if current_app.config.get("EN_VERCEL"):
            # En Vercel el disco es de solo lectura (y lo que se escribe en
            # /tmp se pierde): la foto no sobreviviria. Se pide el enlace.
            raise ValueError(
                "En el sitio publicado no se pueden subir archivos: "
                "pega el enlace directo de la imagen (ej. Imgur)."
            )
        ImagenService._validar_archivo(archivo)
        nombre_seguro = secure_filename(archivo.filename)
        nombre_unico = f"{uuid.uuid4().hex}_{nombre_seguro}"
        carpeta = os.path.join(current_app.config["UPLOAD_FOLDER"], SUBCARPETA)
        os.makedirs(carpeta, exist_ok=True)
        archivo.save(os.path.join(carpeta, nombre_unico))
        return f"/static/uploads/{SUBCARPETA}/{nombre_unico}"

    @staticmethod
    def _validar_url_externa(url_externa):
        url_externa = url_externa.strip()
        if not (url_externa.startswith("http://") or url_externa.startswith("https://")):
            raise ValueError("El enlace de la imagen debe comenzar con http:// o https://")
        return url_externa

    @staticmethod
    def _eliminar_archivo_fisico(ruta_imagen):
        """Borra el archivo del disco si la ruta es un upload local; ignora URLs externas."""
        prefijo = "/static/uploads/"
        if not ruta_imagen or not ruta_imagen.startswith(prefijo):
            return
        # Misma base que usa _guardar_archivo (UPLOAD_FOLDER), no static_folder:
        # son iguales por defecto, pero UPLOAD_FOLDER es la config real de donde
        # se guardo el archivo.
        ruta_absoluta = os.path.join(current_app.config["UPLOAD_FOLDER"], ruta_imagen[len(prefijo):])
        try:
            os.remove(ruta_absoluta)
        except OSError:
            pass

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------

    @staticmethod
    def listar(id_producto):
        """Todas las fotos de un producto, de la mas antigua a la mas reciente."""
        return (
            ImagenProducto.query.filter_by(id_producto=id_producto)
            .order_by(ImagenProducto.fecha_carga)
            .all()
        )

    @staticmethod
    def obtener_principal(id_producto):
        """La foto marcada como principal, o la mas antigua si ninguna lo esta."""
        principal = ImagenProducto.query.filter_by(id_producto=id_producto, es_principal=True).first()
        if principal:
            return principal
        return (
            ImagenProducto.query.filter_by(id_producto=id_producto)
            .order_by(ImagenProducto.fecha_carga)
            .first()
        )

    # ------------------------------------------------------------------
    # Alta, actualizacion y borrado
    # ------------------------------------------------------------------

    @staticmethod
    def _desmarcar_otras_principales(id_producto):
        ImagenProducto.query.filter_by(id_producto=id_producto, es_principal=True).update(
            {"es_principal": False}
        )

    @staticmethod
    def agregar(id_producto, archivo=None, url_externa=None, marcar_principal=False):
        """
        Sube un archivo o referencia una URL externa y la asocia al producto.
        La primera foto de un producto queda como principal automaticamente.
        Si no se envia archivo ni URL, no hace nada y devuelve None.
        """
        if archivo and archivo.filename:
            ruta = ImagenService._guardar_archivo(archivo)
        elif url_externa and url_externa.strip():
            ruta = ImagenService._validar_url_externa(url_externa)
        else:
            return None

        es_primera = ImagenProducto.query.filter_by(id_producto=id_producto).count() == 0
        es_principal = es_primera or marcar_principal
        if es_principal:
            ImagenService._desmarcar_otras_principales(id_producto)

        imagen = ImagenProducto(id_producto=id_producto, ruta_imagen=ruta, es_principal=es_principal)
        db.session.add(imagen)
        db.session.commit()
        return imagen

    @staticmethod
    def reemplazar(id_imagen, archivo=None, url_externa=None):
        """Cambia el archivo o enlace de una foto ya existente, conservando su lugar y si es principal."""
        imagen = db.get_or_404(ImagenProducto, id_imagen)

        if archivo and archivo.filename:
            nueva_ruta = ImagenService._guardar_archivo(archivo)
        elif url_externa and url_externa.strip():
            nueva_ruta = ImagenService._validar_url_externa(url_externa)
        else:
            raise ValueError("No se envió un archivo nuevo ni un enlace.")

        ruta_anterior = imagen.ruta_imagen
        imagen.ruta_imagen = nueva_ruta
        db.session.commit()
        ImagenService._eliminar_archivo_fisico(ruta_anterior)
        return imagen

    @staticmethod
    def marcar_principal(id_imagen):
        """Marca una foto como la principal del producto y desmarca las demas."""
        imagen = db.get_or_404(ImagenProducto, id_imagen)
        ImagenService._desmarcar_otras_principales(imagen.id_producto)
        imagen.es_principal = True
        db.session.commit()
        return imagen

    @staticmethod
    def eliminar(id_imagen):
        """
        Borra el registro y, si es un archivo local, tambien el archivo fisico.
        Si la foto eliminada era la principal, promueve a principal la siguiente
        mas antigua (si queda alguna), para que el producto no se quede sin
        miniatura mientras tenga otras fotos cargadas.
        """
        imagen = db.get_or_404(ImagenProducto, id_imagen)
        id_producto = imagen.id_producto
        era_principal = imagen.es_principal
        ruta = imagen.ruta_imagen

        db.session.delete(imagen)
        db.session.commit()
        ImagenService._eliminar_archivo_fisico(ruta)

        if era_principal:
            siguiente = (
                ImagenProducto.query.filter_by(id_producto=id_producto)
                .order_by(ImagenProducto.fecha_carga)
                .first()
            )
            if siguiente:
                siguiente.es_principal = True
                db.session.commit()
