"""
app/formato.py

Formato de cifras para la presentacion: pesos colombianos y el monto
escrito en letras que lleva toda factura de venta.

Se registran como filtros de Jinja en create_app(), asi que en cualquier
plantilla se puede escribir:

    {{ factura.total | pesos }}          ->  $ 137.910
    {{ factura.total | pesos_letras }}   ->  CIENTO TREINTA Y SIETE MIL
                                             NOVECIENTOS DIEZ PESOS M/CTE

Tambien los usa el generador de PDF, para que el documento impreso y la
pagina web muestren exactamente las mismas cifras.
"""

# 0 a 29 son irregulares en espanol y se listan uno por uno
_UNIDADES = [
    "CERO", "UNO", "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO",
    "NUEVE", "DIEZ", "ONCE", "DOCE", "TRECE", "CATORCE", "QUINCE", "DIECISEIS",
    "DIECISIETE", "DIECIOCHO", "DIECINUEVE", "VEINTE", "VEINTIUNO", "VEINTIDOS",
    "VEINTITRES", "VEINTICUATRO", "VEINTICINCO", "VEINTISEIS", "VEINTISIETE",
    "VEINTIOCHO", "VEINTINUEVE",
]

_DECENAS = ["", "", "", "TREINTA", "CUARENTA", "CINCUENTA",
            "SESENTA", "SETENTA", "OCHENTA", "NOVENTA"]

_CENTENAS = ["", "CIENTO", "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS",
             "QUINIENTOS", "SEISCIENTOS", "SETECIENTOS", "OCHOCIENTOS",
             "NOVECIENTOS"]


def pesos(valor):
    """
    Formato de moneda colombiana: separador de miles con punto y sin
    decimales, porque el peso no se factura en centavos.

        137910.0  ->  '$ 137.910'
    """
    try:
        entero = int(round(float(valor)))
    except (TypeError, ValueError):
        return "$ 0"
    # Se formatea con comas (lo que sabe hacer Python) y se cambian por puntos
    return "$ " + f"{entero:,}".replace(",", ".")


def _menor_a_mil(n):
    """Convierte 0..999 a letras. No incluye el 'CERO' (lo maneja quien llama)."""
    if n == 0:
        return ""
    if n < 30:
        return _UNIDADES[n]
    if n < 100:
        decena, unidad = divmod(n, 10)
        if unidad == 0:
            return _DECENAS[decena]
        return f"{_DECENAS[decena]} Y {_UNIDADES[unidad]}"
    if n == 100:
        return "CIEN"
    centena, resto = divmod(n, 100)
    if resto == 0:
        return _CENTENAS[centena]
    return f"{_CENTENAS[centena]} {_menor_a_mil(resto)}"


def _apocopar(texto):
    """
    'UNO' se acorta a 'UN' cuando va delante de MIL o MILLONES:
    'VEINTIUNO MIL' no existe, se dice 'VEINTIUN MIL'.
    """
    return texto[:-3] + "UN" if texto.endswith("UNO") else texto


def numero_a_letras(numero):
    """
    Escribe un entero en letras, en mayusculas, como se usa en las facturas.

        0        -> 'CERO'
        1        -> 'UNO'
        1000     -> 'MIL'            (no 'UN MIL')
        21000    -> 'VEINTIUN MIL'   (apocope antes de 'MIL')
        1000000  -> 'UN MILLON'
        2500000  -> 'DOS MILLONES QUINIENTOS MIL'
    """
    try:
        n = int(round(float(numero)))
    except (TypeError, ValueError):
        return "CERO"

    if n < 0:
        return "MENOS " + numero_a_letras(-n)
    if n == 0:
        return "CERO"

    partes = []

    millones, resto = divmod(n, 1_000_000)
    if millones:
        if millones == 1:
            partes.append("UN MILLON")
        else:
            partes.append(f"{_apocopar(numero_a_letras(millones))} MILLONES")

    miles, unidades = divmod(resto, 1000)
    if miles:
        if miles == 1:
            partes.append("MIL")
        else:
            partes.append(f"{_apocopar(_menor_a_mil(miles))} MIL")

    if unidades:
        partes.append(_menor_a_mil(unidades))

    return " ".join(partes)


def pesos_letras(valor):
    """
    Monto en letras tal como se escribe al pie de una factura colombiana.
    'M/CTE' = moneda corriente.

        137910  ->  'CIENTO TREINTA Y SIETE MIL NOVECIENTOS DIEZ PESOS M/CTE'
    """
    return f"{numero_a_letras(valor)} PESOS M/CTE"


def folio(numero, prefijo="BP"):
    """
    Consecutivo de la factura con prefijo y ceros a la izquierda, como se
    numeran las facturas de verdad:  42 -> 'BP-000042'.
    """
    try:
        return f"{prefijo}-{int(numero):06d}"
    except (TypeError, ValueError):
        return f"{prefijo}-{numero}"


def registrar_filtros(app):
    """Deja los formatos disponibles como filtros de Jinja."""
    app.jinja_env.filters["pesos"] = pesos
    app.jinja_env.filters["letras"] = numero_a_letras
    app.jinja_env.filters["pesos_letras"] = pesos_letras
    app.jinja_env.filters["folio"] = folio
