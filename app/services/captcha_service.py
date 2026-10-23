"""
app/services/captcha_service.py

Captcha propio, sin servicios externos.

Se descarto reCAPTCHA de Google a proposito: exige dos claves de API, una
cuenta de Google Cloud y conexion a internet en el equipo donde corre el
proyecto. Este captcha se genera en el servidor con la libreria estandar,
se dibuja como SVG (no necesita Pillow ni ninguna dependencia nueva) y
funciona igual sin internet.

Como funciona
-------------
1. El navegador pide la imagen a /auth/captcha?para=registro.
2. Aqui se sortea un codigo de 5 caracteres, se dibuja en SVG y en la
   sesion queda guardado solo su *hash* con la fecha de vencimiento.
   El texto del codigo nunca viaja al navegador en forma legible: va
   dibujado en la imagen.
3. Al enviar el formulario se compara lo que escribio la persona contra
   ese hash. Acierte o falle, el codigo se consume: cada intento necesita
   una imagen nueva, asi que no se puede probar en bucle.

Cada formulario tiene su propio "proposito" (registro, recuperar, login)
para que el captcha de uno no sirva de respuesta en otro.
"""
import hashlib
import hmac
import random
import time

from flask import current_app, session

# Alfabeto sin caracteres que se confunden al leerlos (0/O, 1/I/L).
ALFABETO = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
LONGITUD = 5
VIGENCIA_SEGUNDOS = 300  # 5 minutos: suficiente para llenar un formulario

CLAVE_SESION = "captcha"
PROPOSITOS = ("registro", "recuperar", "login")

# Medidas del dibujo
ANCHO = 150
ALTO = 50


def _huella(texto):
    """
    Hash del codigo con la SECRET_KEY de la app.

    Se usa hmac (no un sha256 pelado) para que nadie que vea la cookie de
    sesion pueda recalcular el hash de los 31^5 codigos posibles y leer el
    captcha sin mirar la imagen.
    """
    clave = current_app.config["SECRET_KEY"].encode("utf-8")
    return hmac.new(clave, texto.upper().encode("utf-8"), hashlib.sha256).hexdigest()


def _almacen():
    return session.get(CLAVE_SESION, {})


def _guardar(almacen):
    # Reasignar la clave completa es lo que marca la sesion como
    # modificada; mutar el diccionario en sitio no siempre lo hace.
    session[CLAVE_SESION] = almacen


def _normalizar(proposito):
    return proposito if proposito in PROPOSITOS else "registro"


def generar_svg(proposito):
    """
    Sortea un codigo nuevo para ese proposito, lo guarda hasheado en la
    sesion y devuelve el SVG que hay que mostrar.
    """
    proposito = _normalizar(proposito)
    codigo = "".join(random.choice(ALFABETO) for _ in range(LONGITUD))

    almacen = _almacen()
    almacen[proposito] = {"hash": _huella(codigo), "expira": time.time() + VIGENCIA_SEGUNDOS}
    _guardar(almacen)

    return _dibujar(codigo)


def validar(proposito, respuesta):
    """
    True si 'respuesta' coincide con el captcha vigente de ese proposito.

    El codigo se borra siempre, haya acertado o no: un captcha es de un
    solo uso.
    """
    proposito = _normalizar(proposito)
    almacen = _almacen()
    guardado = almacen.pop(proposito, None)
    _guardar(almacen)

    if not guardado:
        return False
    if time.time() > guardado.get("expira", 0):
        return False

    respuesta = (respuesta or "").strip().replace(" ", "")
    if len(respuesta) != LONGITUD:
        return False

    # compare_digest evita que el tiempo de la comparacion delate cuantos
    # caracteres iban bien.
    return hmac.compare_digest(guardado["hash"], _huella(respuesta))


def olvidar(proposito):
    """Descarta el captcha pendiente de un proposito (al cerrar el modal)."""
    almacen = _almacen()
    if almacen.pop(_normalizar(proposito), None) is not None:
        _guardar(almacen)




# ----------------------------------------------------------------------
# Dibujo
# ----------------------------------------------------------------------
# Los caracteres NO se dibujan con <text>: un <text> deja el codigo
# escrito en el XML de la imagen, y entonces leerlo es una sola expresion
# regular sobre la respuesta de /auth/captcha. Aqui cada caracter se traza
# con <path>, usando la fuente de lineas de _GLIFOS, asi que en el SVG solo
# hay coordenadas.
#
# La rejilla de los glifos es x de 0 a 10 (ancho) e y de 0 a 14 (alto,
# creciendo hacia abajo), y cada caracter es una lista de polilineas.
_GLIFOS = {
    "A": [[(0, 14), (5, 0), (10, 14)], [(2, 9), (8, 9)]],
    "B": [[(0, 0), (0, 14)], [(0, 0), (6, 0), (9, 3), (6, 7), (0, 7)],
          [(0, 7), (6, 7), (9, 10), (6, 14), (0, 14)]],
    "C": [[(10, 3), (7, 0), (3, 0), (0, 4), (0, 10), (3, 14), (7, 14), (10, 11)]],
    "D": [[(0, 0), (0, 14)], [(0, 0), (5, 0), (9, 4), (9, 10), (5, 14), (0, 14)]],
    "E": [[(10, 0), (0, 0), (0, 14), (10, 14)], [(0, 7), (7, 7)]],
    "F": [[(10, 0), (0, 0), (0, 14)], [(0, 7), (7, 7)]],
    "G": [[(10, 3), (7, 0), (3, 0), (0, 4), (0, 10), (3, 14), (7, 14), (10, 10), (10, 8), (5, 8)]],
    "H": [[(0, 0), (0, 14)], [(10, 0), (10, 14)], [(0, 7), (10, 7)]],
    "J": [[(8, 0), (8, 10), (5, 14), (2, 14), (0, 10)]],
    "K": [[(0, 0), (0, 14)], [(9, 0), (0, 8)], [(3, 6), (10, 14)]],
    "M": [[(0, 14), (0, 0), (5, 8), (10, 0), (10, 14)]],
    "N": [[(0, 14), (0, 0), (10, 14), (10, 0)]],
    "P": [[(0, 14), (0, 0), (6, 0), (9, 3), (6, 7), (0, 7)]],
    "Q": [[(10, 4), (7, 0), (3, 0), (0, 4), (0, 10), (3, 14), (7, 14), (10, 10), (10, 4)],
          [(6, 10), (10, 14)]],
    "R": [[(0, 14), (0, 0), (6, 0), (9, 3), (6, 7), (0, 7)], [(4, 7), (10, 14)]],
    "S": [[(10, 2), (7, 0), (3, 0), (0, 3), (3, 6), (7, 8), (10, 11), (7, 14), (3, 14), (0, 12)]],
    "T": [[(0, 0), (10, 0)], [(5, 0), (5, 14)]],
    "U": [[(0, 0), (0, 10), (3, 14), (7, 14), (10, 10), (10, 0)]],
    "V": [[(0, 0), (5, 14), (10, 0)]],
    "W": [[(0, 0), (2, 14), (5, 5), (8, 14), (10, 0)]],
    "X": [[(0, 0), (10, 14)], [(10, 0), (0, 14)]],
    "Y": [[(0, 0), (5, 7), (10, 0)], [(5, 7), (5, 14)]],
    "Z": [[(0, 0), (10, 0), (0, 14), (10, 14)]],
    "2": [[(0, 3), (3, 0), (7, 0), (10, 3), (10, 6), (0, 14), (10, 14)]],
    "3": [[(1, 2), (4, 0), (8, 0), (10, 3), (6, 7), (10, 10), (8, 13), (4, 14), (0, 12)]],
    "4": [[(7, 14), (7, 0), (0, 10), (10, 10)]],
    "5": [[(10, 0), (1, 0), (0, 6), (6, 6), (10, 9), (8, 13), (3, 14), (0, 12)]],
    "6": [[(9, 1), (5, 0), (1, 4), (0, 10), (3, 14), (7, 14), (10, 11), (8, 7), (3, 7), (0, 10)]],
    "7": [[(0, 0), (10, 0), (4, 14)]],
    "8": [[(3, 7), (1, 4), (3, 0), (7, 0), (9, 4), (7, 7), (3, 7)],
          [(7, 7), (10, 10), (7, 14), (3, 14), (0, 10), (3, 7)]],
    "9": [[(9, 6), (6, 8), (2, 7), (0, 4), (2, 1), (6, 0), (9, 2), (10, 6), (9, 11), (5, 14), (1, 13)]],
}

GLIFO_ANCHO = 10
GLIFO_ALTO = 14

# La imagen trae su propio fondo claro y tintas oscuras en vez de heredar
# los colores del sitio: asi se lee igual en modo claro y en modo oscuro.
FONDO = "#f8fafc"
_TINTAS = ("#1f2937", "#9d174d", "#1e3a8a", "#065f46")

MARGEN_X = 10


def _polilinea_a_path(puntos):
    """Convierte [(x, y), ...] en el atributo 'd' de un <path>."""
    return "M" + " L".join("%.1f %.1f" % (x, y) for x, y in puntos)


def _trazar_caracter(caracter, cx, cy):
    """
    Un <path> por polilinea del glifo, centrado en (cx, cy) y deformado:
    escala, giro, inclinacion y un temblor por vertice.

    El temblor importa: sin el, las coordenadas de cada caracter serian
    siempre las mismas y bastaria compararlas con la tabla _GLIFOS -que
    esta en el codigo del proyecto- para resolver el captcha sin mirarlo.
    """
    glifo = _GLIFOS[caracter]
    # La escala y el giro van medidos para que el caracter entre completo
    # en los 150x50 de la imagen incluso girado al maximo: un caracter
    # recortado por el borde no se puede leer.
    escala = random.uniform(1.6, 2.0)
    giro = random.uniform(-18, 18)
    inclinacion = random.uniform(-9, 9)
    tinta = random.choice(_TINTAS)
    grosor = random.uniform(2.0, 2.8)

    trazos = []
    for linea in glifo:
        puntos = []
        for x, y in linea:
            # El glifo se centra en su propio (0, 0) antes de transformarlo,
            # para que el giro ocurra alrededor del caracter y no de una
            # esquina.
            px = (x - GLIFO_ANCHO / 2) * escala + random.uniform(-0.9, 0.9)
            py = (y - GLIFO_ALTO / 2) * escala + random.uniform(-0.9, 0.9)
            puntos.append((px, py))
        trazos.append(_polilinea_a_path(puntos))

    return (
        '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f" '
        'stroke-linecap="round" stroke-linejoin="round" '
        'transform="translate(%.1f %.1f) rotate(%.1f) skewX(%.1f)"/>'
        % (" ".join(trazos), tinta, grosor, cx, cy, giro, inclinacion)
    )


def _ruido_de_fondo():
    """
    Rayas curvas y puntos sobre el dibujo. Estorban a un recorte
    automatico, no al ojo humano, que separa sin esfuerzo un trazo grueso
    de una raya tenue.
    """
    piezas = []

    for _ in range(4):
        x1, y1 = random.randint(0, 20), random.randint(0, ALTO)
        x2, y2 = random.randint(ANCHO - 20, ANCHO), random.randint(0, ALTO)
        piezas.append(
            '<path d="M%d %d Q%d %d %d %d" fill="none" stroke="%s" '
            'stroke-opacity="0.30" stroke-width="1.4"/>'
            % (x1, y1, ANCHO // 2, random.randint(0, ALTO), x2, y2, random.choice(_TINTAS))
        )

    for _ in range(26):
        piezas.append(
            '<circle cx="%d" cy="%d" r="%s" fill="%s" fill-opacity="0.30"/>'
            % (random.randint(0, ANCHO), random.randint(0, ALTO),
               random.choice(("1", "1.4", "1.8")), random.choice(_TINTAS))
        )

    # Dos trazos sueltos con la misma pinta que un caracter: quien intente
    # quedarse con "los paths gruesos" se lleva basura mezclada.
    for _ in range(2):
        puntos = [(random.uniform(0, ANCHO), random.uniform(0, ALTO)) for _ in range(3)]
        piezas.append(
            '<path d="%s" fill="none" stroke="%s" stroke-opacity="0.35" '
            'stroke-width="2.2" stroke-linecap="round"/>'
            % (_polilinea_a_path(puntos), random.choice(_TINTAS))
        )

    return piezas


def _dibujar(codigo):
    partes = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
        'viewBox="0 0 %d %d" role="img" aria-label="Codigo de verificacion de %d '
        'caracteres dibujado en una imagen">' % (ANCHO, ALTO, ANCHO, ALTO, LONGITUD),
        '<rect width="%d" height="%d" rx="8" fill="%s"/>' % (ANCHO, ALTO, FONDO),
    ]
    partes.extend(_ruido_de_fondo())

    # len(codigo) y no LONGITUD: asi la funcion sirve igual para dibujar
    # una tira de prueba con otra cantidad de caracteres.
    paso = (ANCHO - 2 * MARGEN_X) / len(codigo)
    for i, caracter in enumerate(codigo):
        cx = MARGEN_X + paso * (i + 0.5) + random.uniform(-1.2, 1.2)
        cy = ALTO / 2 + random.uniform(-2.0, 2.0)
        partes.append(_trazar_caracter(caracter, cx, cy))

    partes.append("</svg>")
    return "".join(partes)
