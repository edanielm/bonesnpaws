"""
app/services/envio_service.py

Envios de los pedidos: cuanto cuesta mandarlos y en que estado va cada uno.

Por que existe este servicio
----------------------------
La base de datos ya tenia todo el modelo de envios (`envio`,
`transportadora`, el procedimiento `sp_registrar_envio`, la vista
`vista_envios_pendientes`), pero la aplicacion Flask nunca lo usaba: al
comprar se generaba la factura y ahi terminaba todo. El cliente no sabia
cuando le llegaba el pedido y el equipo no tenia donde consultarlo.

Ahora cada venta genera su envio, igual que genera su factura, y el estado
se puede seguir desde "Mis compras" (cliente) y desde el panel (equipo).

Sobre el costo
--------------
Antes el envio costaba siempre $12.000 sin importar a donde fuera. Ahora la
tarifa sale de `Config.ENVIO_TARIFAS` segun la ciudad que aparezca en la
direccion del cliente, y las compras grandes viajan gratis
(`Config.ENVIO_GRATIS_DESDE`). La direccion es texto libre
("Calle 10 #20-30 Bogotá"), asi que la ciudad se detecta buscando dentro de
ella los nombres de la tabla de tarifas.
"""
import unicodedata
from datetime import date, timedelta

from flask import current_app

from app.extensions import db
from app.models import Envio, Transportadora

ESTADOS = ("Pendiente", "En camino", "Entregado")


def _sin_tildes(texto):
    """Minusculas y sin acentos, para comparar 'Medellín' con 'medellin'."""
    limpio = unicodedata.normalize("NFKD", texto or "")
    limpio = limpio.encode("ascii", "ignore").decode("ascii")
    return limpio.lower()


class EnvioService:

    # ------------------------------------------------------------------
    # Costo del envio
    # ------------------------------------------------------------------

    @staticmethod
    def ciudad_de(direccion):
        """
        La ciudad que se reconoce dentro de una direccion escrita a mano, o
        None si no aparece ninguna de las que tienen tarifa.

        Se recorre de nombre mas largo a mas corto para que 'Santa Marta' no
        pierda contra una ciudad de nombre mas corto contenida en el texto.
        """
        direccion_limpia = _sin_tildes(direccion)
        if not direccion_limpia:
            return None

        ciudades = sorted(current_app.config["ENVIO_TARIFAS"], key=len, reverse=True)
        for ciudad in ciudades:
            if _sin_tildes(ciudad) in direccion_limpia:
                return ciudad
        return None

    @staticmethod
    def calcular_costo(direccion, subtotal=0.0):
        """
        Cuanto cuesta mandar un pedido de `subtotal` a `direccion`.

        Devuelve 0 si la compra supera el minimo de envio gratis; si no, la
        tarifa de la ciudad detectada, o la tarifa por defecto cuando la
        direccion no dice (o no tiene) una ciudad conocida.
        """
        if subtotal <= 0:
            return 0.0
        if subtotal >= current_app.config["ENVIO_GRATIS_DESDE"]:
            return 0.0

        ciudad = EnvioService.ciudad_de(direccion)
        if ciudad:
            return float(current_app.config["ENVIO_TARIFAS"][ciudad])
        return float(current_app.config["ENVIO_TARIFA_DEFECTO"])

    @staticmethod
    def detalle_costo(direccion, subtotal=0.0):
        """
        Lo mismo que calcular_costo() pero explicando el resultado, para que
        el carrito y el checkout puedan decir 'Envio a Medellín' o
        '¡Gratis! Tu compra supera $250.000' en vez de un numero suelto.
        """
        ciudad = EnvioService.ciudad_de(direccion)
        costo = EnvioService.calcular_costo(direccion, subtotal)
        minimo_gratis = current_app.config["ENVIO_GRATIS_DESDE"]
        return {
            "costo_envio": costo,
            "ciudad_envio": ciudad,
            "envio_gratis": subtotal > 0 and subtotal >= minimo_gratis,
            "envio_gratis_desde": minimo_gratis,
            # Cuanto le falta a la compra para que el envio salga gratis.
            "falta_para_envio_gratis": max(0.0, minimo_gratis - subtotal) if subtotal > 0 else 0.0,
        }

    # ------------------------------------------------------------------
    # Alta del envio al facturar
    # ------------------------------------------------------------------

    @staticmethod
    def _siguiente_transportadora(numero_factura):
        """
        Reparte los pedidos entre las transportadoras registradas en vez de
        mandarlos todos por la misma. El reparto es deterministico (depende
        del numero de factura) para que sea reproducible en una demo.
        Devuelve None si no hay transportadoras cargadas.
        """
        transportadoras = Transportadora.query.order_by(Transportadora.id_transportadora).all()
        if not transportadoras:
            return None
        return transportadoras[numero_factura % len(transportadoras)]

    @staticmethod
    def crear_para_factura(numero_factura, dias_estimados=None):
        """
        Genera la guia de una factura recien registrada.

        Mismo formato de guia que `sp_registrar_envio` (BP-000042-001) para
        que el dato se vea igual entre por la aplicacion o por SQL. Las
        fechas se calculan aqui y no se dejan en NULL a proposito: el
        trigger `trg_envio_bi` las rellenaria en MySQL, pero las pruebas
        corren sobre SQLite, que no tiene triggers.

        Devuelve el Envio creado, o None si la factura ya tenia envio o si
        todavia no hay transportadoras cargadas. Nunca lanza excepcion: un
        problema con el envio no puede tumbar una venta que ya se cobro.
        """
        if Envio.query.filter_by(numero_factura=numero_factura).first():
            return None

        transportadora = EnvioService._siguiente_transportadora(numero_factura)
        if not transportadora:
            return None

        dias = dias_estimados or current_app.config["ENVIO_DIAS_ESTIMADOS"]
        hoy = date.today()

        envio = Envio(
            numero_factura=numero_factura,
            id_transportadora=transportadora.id_transportadora,
            numero_guia=f"BP-{numero_factura:06d}-{transportadora.id_transportadora:03d}",
            fecha_envio=hoy,
            fecha_entrega_estimada=hoy + timedelta(days=dias),
            estado="Pendiente",
        )
        db.session.add(envio)
        return envio

    # ------------------------------------------------------------------
    # Consulta y seguimiento
    # ------------------------------------------------------------------

    @staticmethod
    def obtener_por_factura(numero_factura):
        return Envio.query.filter_by(numero_factura=numero_factura).first()

    @staticmethod
    def listar(estado=None):
        """
        Todos los envios para el panel del equipo, del mas reciente al mas
        antiguo. `estado` filtra por 'Pendiente', 'En camino' o 'Entregado'.
        """
        query = Envio.query
        if estado in ESTADOS:
            query = query.filter_by(estado=estado)
        return query.order_by(Envio.numero_factura.desc()).all()

    @staticmethod
    def resumen():
        """Cuantos envios hay en cada estado, para las pestañas del panel."""
        filas = (
            db.session.query(Envio.estado, db.func.count(Envio.id_envio))
            .group_by(Envio.estado)
            .all()
        )
        conteo = {estado: 0 for estado in ESTADOS}
        for estado, cantidad in filas:
            if estado in conteo:
                conteo[estado] = int(cantidad or 0)
        conteo["total"] = sum(conteo[e] for e in ESTADOS)
        return conteo

    @staticmethod
    def actualizar_estado(id_envio, estado):
        """
        Mueve un envio a otro estado. Al marcarlo 'Entregado' se sella la
        fecha real de entrega; si se devuelve a un estado anterior, esa
        fecha se limpia (misma regla que el trigger `trg_envio_bu`, repetida
        aqui porque SQLite no tiene triggers).
        """
        if estado not in ESTADOS:
            raise ValueError("Estado de envío no válido.")

        envio = db.get_or_404(Envio, id_envio)
        envio.estado = estado
        envio.fecha_entrega_real = date.today() if estado == "Entregado" else None
        db.session.commit()
        return envio
