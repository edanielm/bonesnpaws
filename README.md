# 🐾 Bones & Paws

Tienda web de productos para mascotas, construida en **Python + Flask + MySQL/MariaDB**
siguiendo estrictamente la arquitectura MVC del *Blueprint Profesional Flask*
(rutas delgadas → servicios con la lógica de negocio → modelos SQLAlchemy → base de datos).

---

## 1. Estructura del proyecto

```
bonesandpaws/
├── app/
│   ├── models/          # Una clase SQLAlchemy por tabla de bandp.sql
│   ├── services/         # Logica de negocio (auth, captcha, correo, recuperacion, productos, carrito, facturas, envios, imagenes, admin, PDF de factura y manual)
│   ├── formato.py        # Pesos colombianos, monto en letras y consecutivo de factura
│   ├── routes/            # Controladores delgados (Blueprints de Flask)
│   ├── templates/         # Vistas Jinja2, agrupadas por modulo
│   │   ├── productos/, categorias/, perfil/, facturas/, admin/
│   │   ├── perfil/        # cliente.html y empleado.html: el mismo /perfil segun quien entre
│   │   ├── _iconos.html   # Macro con todos los iconos SVG de linea del sitio
│   │   └── base.html      # Layout comun + modal flotante de login (unico para todos)
│   ├── static/
│   │   ├── css/            # style.css (tema), login.css (modal), factura.css (documento e impresion)
│   │   ├── js/              # app.js (interactividad + menu movil), login.js (modal), password.js (ojito), tema.js
│   │   ├── img/             # logo, foto de portada y SVG locales de respaldo
│   │   └── uploads/         # Imagenes subidas desde el panel admin
│   ├── config.py
│   └── extensions.py
├── database/
│   ├── schema.sql          # Estructura (bandp.sql + columnas y tabla rol aprobadas)
│   ├── seed.sql             # Datos originales + imagenes + codigos de producto + roles
│   ├── objetos.sql           # Vistas, funciones, procedimientos y triggers
│   ├── init_db.py            # Reconstruccion determinista de la BD (la borra y recrea)
│   ├── MIGRACIONES.md        # Que hace cada migracion y como saber si ya se aplico
│   ├── migracion_*.sql        # Cambios de esquema, uno por archivo
│   └── migrar_contrasenas.py  # Cifra las contrasenas que quedaron en texto plano
├── docs/
│   └── objetos_bd.md        # Documentacion de vistas/procedimientos/triggers
├── tests/
├── .env.example              # Plantilla de configuracion (el .env real no se comparte)
├── requirements.txt
├── instalar.py               # Instalacion completa en un equipo nuevo
├── verificar.py              # Diagnostico del entorno (--correo prueba el envio)
└── run.py                    # Punto de entrada unico
```

> **¿Primera vez en este computador?** Ve directo a
> [2. Instalación en un equipo nuevo](#2-instalación-en-un-equipo-nuevo):
> es un solo comando, `python instalar.py`.

---

## 2. Instalación en un equipo nuevo

### 2.1 Requisitos previos

Solo dos cosas, y ambas se instalan una vez por computador:

| Requisito | Cómo conseguirlo |
|---|---|
| **Python 3.9 o superior** | [python.org/downloads](https://www.python.org/downloads/) — en Windows marca la casilla **"Add Python to PATH"** durante la instalación. |
| **MySQL o MariaDB** | Lo más simple es [XAMPP](https://www.apachefriends.org/es/index.html): al abrir su Panel de Control, pulsa **Start** en la fila **MySQL**. También sirve WAMP, Laragon o MySQL nativo. |

Todo lo demás (Flask, el conector de MySQL, etc.) lo instala el proyecto solo.

### 2.2 Instalación con un solo comando

Abre una terminal **dentro de la carpeta del proyecto** y ejecuta:

```bash
python instalar.py
```

Eso hace, de corrido:

1. Comprueba la versión de Python.
2. Crea el entorno virtual `.venv`.
3. Instala las dependencias de `requirements.txt` dentro de ese entorno.
4. Crea tu archivo `.env` con una `SECRET_KEY` aleatoria, preguntándote los datos
   de tu MySQL (con Enter aceptas los de XAMPP: `root` sin contraseña).
5. Crea la base de datos `bandp` completa ejecutando `database/init_db.py`.
6. Verifica que todo quedó bien y te dice cómo arrancar.

Variantes útiles:

```bash
python instalar.py --auto              # sin preguntas, valores por defecto
python instalar.py --sin-bd            # no tocar la base de datos
python instalar.py --regenerar-clave   # solo generar una SECRET_KEY nueva
```

> **Si prefieres hacerlo a mano**, los pasos equivalentes son:
> `python -m venv .venv` → activar el entorno → `pip install -r requirements.txt`
> → copiar `.env.example` a `.env` y editarlo → `python database/init_db.py`.

### 2.3 Ejecutar el servidor

```bash
python run.py
```

La tienda queda en **http://localhost:5000** y el panel en **http://localhost:5000/admin**.

Antes de arrancar, `run.py` revisa el entorno. Si falta algo (MySQL apagado, base
de datos sin crear, dependencias sin instalar) no lanza un traceback: dice qué
falta y cómo arreglarlo. Para saltarse ese chequeo: `python run.py --sin-chequeo`.

### 2.4 Cuando algo no funciona

```bash
python verificar.py
```

Revisa, en orden, la versión de Python, las dependencias, el `.env`, si el
servidor MySQL responde, si el usuario y contraseña son correctos, si la base
`bandp` existe con todas sus tablas y datos, y si están creados los objetos
programables. Cada punto que falle viene con la instrucción concreta para
resolverlo.

Problemas típicos al estrenar equipo:

| Síntoma | Causa y solución |
|---|---|
| `No hay ningun servidor MySQL en localhost:3306` | MySQL está apagado. En XAMPP: Panel de Control → **Start** en MySQL. |
| `MySQL rechazo el usuario o la contrasena` | Tu MySQL tiene otra contraseña. Edita `DB_PASSWORD` en `.env`. |
| `La base de datos 'bandp' no existe` | Ejecuta `python database/init_db.py`. |
| `Unknown column 'producto.codigo' in 'field list'` (o `empleado.id_rol`) | La base `bandp` quedó de una versión anterior del proyecto. Ejecuta `python database/init_db.py`: la borra y la reconstruye. Ver **«Base a medias»** aquí abajo. |
| `Faltan dependencias de Python` | Ejecuta `python instalar.py`. |
| El puerto 5000 está ocupado | Cambia `FLASK_PORT` en `.env` (por ejemplo a `5001`). |
| El correo de recuperación no llega | `python verificar.py --correo` manda una prueba y dice exactamente qué falló. |

#### Base a medias

`init_db.py` **borra la base y la vuelve a crear**. Eso es lo que significa
«reconstrucción determinista»: queda exactamente como la describen
`schema.sql` + `seed.sql` + `objetos.sql`, venga de donde venga.

Hasta el Sprint 5 no lo hacía: usaba `CREATE DATABASE IF NOT EXISTS` y seguía
derecho. Sobre una base `bandp` que ya existía, cada `CREATE TABLE` fallaba con
«ya existe», se contaba como un aviso y **el esquema viejo se quedaba tal
cual**. El resultado era una base mezclada —las tablas nuevas creadas, las
viejas sin las columnas nuevas— que arrancaba bien y reventaba al primer
`SELECT`:

```
Unknown column 'producto.codigo' in 'field list'
```

Pide confirmación antes de borrar, salvo con `--forzar`:

```bash
python database/init_db.py            # pregunta antes de borrar
python database/init_db.py --forzar   # no pregunta (lo usa instalar.py)
```

> Antes de reconstruir, si tienes datos propios que quieras conservar:
>
> ```bash
> mysqldump -u root -p bandp > respaldo_bandp.sql
> ```

### 2.5 Cómo mover el proyecto a otro computador

Copia **toda la carpeta** (por USB, Drive, o `git clone`) y en el equipo nuevo
ejecuta `python instalar.py`. Nada más.

Dos carpetas **no** deben viajar, y por eso están en `.gitignore`:

- **`.venv/`** — un entorno virtual guarda rutas absolutas del equipo que lo creó.
  Si lo copias, su `python.exe` no arranca en el equipo nuevo. `instalar.py`
  detecta un `.venv` roto y lo recrea automáticamente.
- **`__pycache__/`** — bytecode compilado, y el de una versión de Python no sirve
  en otra. Se regenera solo.

El archivo **`.env`** tampoco se comparte (lleva la contraseña de MySQL de cada
equipo); lo que se comparte es `.env.example` como plantilla.

Las imágenes del catálogo de ejemplo son **archivos SVG locales**
(`app/static/img/placeholder-*.svg`), no enlaces a un servicio externo, para que
el sitio se vea igual incluso en un equipo sin internet o detrás del firewall de
una institución.

---

## 3. Accesos de prueba

Todos entran por **el mismo formulario**: el modal de login del sitio (botón
"Iniciar sesión" en la barra superior). No hay una pantalla aparte para el
personal — la dirección vieja `/admin/login` se conserva pero solo redirige a
la portada con ese modal abierto.

| Rol | Correo / usuario | Contraseña | Al entrar llega a |
|---|---|---|---|
| Cliente (dato semilla) | `juan.perez@gmail.com` | `123456` | La tienda (`/`) |
| Administrador | `admin` | `admin123` | Estadísticas (`/admin/`) |
| Vendedor | `vendedor` | `vendedor123` | Catálogo (`/admin/productos`) |

### Roles

Los roles viven en la tabla **`rol`** y cada fila de `empleado` apunta a uno
mediante `empleado.id_rol` (por defecto `2`, Vendedor: el permiso más
restringido, para que un empleado nuevo no quede como administrador por
descuido). Los clientes siguen en su propia tabla `cliente` y no tienen rol.

| Puede… | Administrador | Vendedor | Cliente |
|---|---|---|---|
| Comprar en la tienda | — | — | ✅ |
| Gestionar el catálogo de productos | ✅ | ✅ | — |
| Consultar cuentas de clientes | ✅ | ✅ | — |
| Ver estadísticas de ventas | ✅ | — | — |
| Eliminar cuentas de clientes | ✅ | — | — |

Quien aplica esas reglas son los decoradores de `app/routes/decoradores.py`
(`@requiere_login`, `@requiere_staff`, `@requiere_admin`). Ocultar el enlace de
Estadísticas en el menú del vendedor es cortesía visual, no seguridad: si
escribe `/admin/` a mano, el decorador lo devuelve al catálogo igual.

### Perfil

Hay **una sola dirección de perfil, `/perfil`**, y muestra una cosa u otra
según quién tenga la sesión abierta:

| Quién entra | Qué ve |
|---|---|
| Cliente | Sus datos de contacto (edita teléfono y dirección) y el resumen de sus compras: cuántas lleva, cuánto ha gastado, compra promedio y qué tiene en el carrito. |
| Administrador / Vendedor | Sus datos (edita teléfono), su rol con la lista de lo que ese rol permite y lo que no, cuántas ventas ha atendido y accesos directos a las secciones del panel que sí puede abrir. |

Nombre, documento y correo no se editan desde el perfil: identifican la cuenta
y están enlazados al histórico de facturas. El rol tampoco — nadie se asciende
solo.

### Secciones del panel

| Sección | Ruta | Quién entra | Qué hace |
|---|---|---|---|
| Estadísticas | `/admin/` | Solo Administrador | Ventas totales, número de facturas, ticket promedio, ventas del mes con variación frente al mes anterior, gráfico de los últimos 6 meses, ventas por método de pago, productos más vendidos, estado del inventario y últimas facturas. |
| Usuarios | `/admin/usuarios` | Todo el equipo | Todas las cuentas de clientes con su correo, teléfono, número de compras, total gastado y última compra. Buscador por nombre, documento o correo. Eliminar cuentas: solo Administrador. |
| Productos | `/admin/productos` | Todo el equipo | Alta, edición y borrado del catálogo, con buscador y paginación. |
| Envíos | `/admin/envios` | Todo el equipo | Todas las guías filtradas por estado, con aviso de atrasado. Un clic mueve el envío entre Pendiente / En camino / Entregado. |
| Mi perfil | `/perfil` | Todo el equipo | Ficha propia y rol. |

Desde `/admin/usuarios/<documento>` se ve la ficha completa de un cliente: sus
datos personales, su historial de compras factura por factura y su carrito activo.

**Borrado de cuentas.** Un cliente que ya tiene facturas **no se puede eliminar**:
sus ventas son parte del histórico contable, alimentan las estadísticas y la llave
foránea `factura → cliente` no permite dejarlas huérfanas. La ficha del cliente
explica el bloqueo. Los clientes sin compras sí se eliminan, junto con su carrito.
Toda esa regla vive en `AdminService.eliminar_cliente()`, no en la ruta.

### Factura de venta

Al terminar el pago, el cliente cae directamente en su factura, con formato de
documento formal: membrete con logo, NIT y datos de la tienda, número consecutivo
(`BP-000042`), fecha de expedición, datos del comprador, detalle línea por línea,
desglose de subtotal / IVA / envío, **el total escrito en letras** («CIENTO SETENTA
Y SIETE MIL CUATROCIENTOS DIEZ PESOS M/CTE») y el pie con la aclaración de que es
un proyecto académico.

Dos formas de llevársela, ambas desde la misma página:

| Botón | Qué hace |
|---|---|
| **Descargar PDF** | `GET /facturas/<n>/pdf` genera el PDF en el servidor con ReportLab y lo descarga como `factura-BP-000042.pdf`. |
| **Imprimir** | Abre el diálogo de impresión. La hoja `factura.css` tiene un bloque `@media print` que oculta la barra de navegación, el pie del sitio y los botones, así que sale solo el documento. |

También se llega a cualquier factura desde **Mis compras**, y el administrador puede
abrirlas y descargarlas desde el panel.

**Quién puede ver una factura.** Solo su dueño y un administrador con sesión abierta;
cualquier otro caso responde 403. El número de factura es un consecutivo trivial de
adivinar, así que sin ese control bastaría con cambiar el número en la URL para leer
los datos personales y las compras de otro cliente.

Los datos del vendedor (nombre, NIT, dirección, teléfono) están en un solo lugar,
`Config.EMPRESA` en `app/config.py`, y los usan por igual la página y el PDF.

### Cifras en pesos colombianos

Todo el sitio formatea el dinero con el filtro `pesos`, definido en `app/formato.py`:
separador de miles con **punto** y sin centavos (`$ 137.910`), que es como se escribe
en Colombia. El mismo módulo tiene `pesos_letras` (el monto en letras de la factura) y
`folio` (el consecutivo `BP-000042`). Los tres están registrados como filtros de Jinja,
así que en cualquier plantilla se usan directamente:

```jinja
{{ factura.total | pesos }}
{{ factura.total | pesos_letras }}
{{ factura.numero_factura | folio(config.FACTURA_PREFIJO) }}
```

### Modo claro y modo oscuro

El sitio tiene un interruptor en la barra superior. Todo el color sale de
variables CSS declaradas en `style.css`: `:root` es la paleta clara y
`:root[data-theme="dark"]` la oscura, ambas sobre los mismos tonos de azul y
rosado pastel. `tema.js` se carga en el `<head>` **sin `defer`** a propósito,
para fijar el tema antes del primer pintado y evitar el parpadeo de color al
entrar. La elección se guarda en `localStorage`; si el visitante nunca la ha
tocado, se sigue el modo del sistema operativo.

### Iconos

No se usan emojis en la interfaz. Todos los iconos son SVG de línea definidos en
`app/templates/_iconos.html` como una macro de Jinja:

```jinja
{% from "_iconos.html" import icono %}
{{ icono('carrito') }}
{{ icono('huella', 40) }}
```

Heredan el color del texto con `currentColor`, así que se adaptan solos a los dos
modos sin duplicar código.

### Imagen de cada producto

Al crear o editar un producto desde el panel admin hay **dos formas** de darle
imagen, y ambas guardan una cadena de texto en `producto.imagen_url`:

| Forma | Qué guarda | Portabilidad |
|---|---|---|
| **Enlace (recomendado)** | La URL tal cual, p. ej. de [imgur.com/upload](https://imgur.com/upload) | La URL viaja dentro del dump de la base de datos, así que basta exportar/importar `bandp.sql` para llevarse el catálogo con imágenes incluidas. |
| **Archivo subido** | `/static/uploads/<archivo>` | El archivo queda en el disco de **este** equipo. Si mueves el proyecto, copia también `app/static/uploads/`. |

Si se envían las dos, el archivo tiene prioridad sobre el enlace.

Por eso se **recomienda el enlace** cuando el proyecto se vaya a pasar de un
equipo a otro, tal como pide el enunciado.

Y si una imagen no carga —porque la carpeta `uploads/` no viajó, o porque el
equipo no tiene internet— no se ve el icono roto del navegador: se muestra
`app/static/img/sin-imagen.svg`, un respaldo local.

Los productos del catálogo de ejemplo usan SVG locales por categoría
(`placeholder-perros.svg`, `placeholder-gatos.svg`, `placeholder-otros.svg`),
así que el sitio se ve completo desde la primera ejecución, con o sin internet.

### Peso de las imágenes

Las dos imágenes propias del sitio están optimizadas para el tamaño real al que
se muestran, no al que venían del origen:

| Archivo | Antes | Ahora | Por qué |
|---|---|---|---|
| `hero-gato.jpg` | 2.179 KB (1086×1448 PNG) | **147 KB** (900×1200 JPEG q85) | Es una fotografía sin transparencia: JPEG comprime muchísimo mejor que PNG. Se muestra en un recuadro de ~460 px, así que 900 px de ancho basta incluso en pantallas retina. |
| `logo.png` | 239 KB (605×605) | **15 KB** (256×256) | Se muestra a ~58 px en la barra y a 16 mm en el PDF. Sigue siendo PNG porque necesita el fondo transparente; se le redujo la paleta a 192 colores. |

La portada completa (HTML + CSS + JS + imágenes) pesa **236 KB**, y el PDF de una
factura **44 KB** en vez de 282 KB, porque el logo va incrustado en él.

Los originales sin comprimir quedan en `app/static/img/_originales/` por si hace
falta regenerarlos con otro tamaño o recorte. Esa carpeta está en `.gitignore`:
no viaja al compartir el proyecto, porque la aplicación no la necesita.

> Si reemplazas la foto de portada, guárdala como `app/static/img/hero-gato.jpg`.
> Si el archivo no existe, la portada no se rompe: muestra el degradado pastel con
> el rastro de huellas.

### Captcha

El modal del gato atiende tres formularios, y cada uno trata el captcha según
qué pasa si lo automatizan:

| Formulario | ¿Pide captcha? | Por qué |
|---|---|---|
| **Registro** | Siempre | Sin él, un script abre cuentas en lote y ensucia la tabla `cliente`. |
| **Recuperar contraseña** | Siempre | Cada envío manda un correo de verdad a un cliente de verdad: el botón no puede quedar disponible para automatizar. |
| **Login** | Solo tras **3 fallos seguidos** | A quien escribe bien su contraseña no se le estorba; a un programa que prueba contraseñas una por una se le corta al cuarto intento. |

No se usó **reCAPTCHA de Google**: exige dos claves de API, una cuenta de
Google Cloud y conexión a internet en el equipo donde corre el proyecto — y
este se califica en un salón donde eso no está garantizado. El captcha es
propio (`app/services/captcha_service.py`), se dibuja como **SVG** con la
librería estándar y **no añade ninguna dependencia** (nada de Pillow).

Cómo está hecho, y por qué así:

1. El navegador pide la imagen a `GET /auth/captcha?para=registro`.
2. El servidor sortea 5 caracteres y en la sesión guarda **solo el `hmac` del
   código** con la `SECRET_KEY`, más su vencimiento (5 minutos). El código
   legible nunca se guarda en ninguna parte.
3. Al enviar el formulario se compara lo escrito contra ese hash, sin
   distinguir mayúsculas de minúsculas, y con `hmac.compare_digest` para que
   el tiempo de la comparación no delate cuántos caracteres iban bien.
4. **Acierte o falle, el código se consume.** Cada intento necesita una imagen
   nueva, así que no se puede probar en bucle contra el mismo captcha.

Cada formulario tiene su propio *propósito* (`registro`, `recuperar`, `login`):
resolver el del login no habilita el del registro.

#### Por qué el dibujo no usa `<text>`

El primer intento dibujaba cada carácter con un `<text>` de SVG, y eso **no es
un captcha**: el código queda escrito tal cual dentro del XML de la imagen, así
que leerlo es una sola expresión regular sobre la respuesta de
`/auth/captcha` — ni hace falta mirar el dibujo.

La versión actual trae una **fuente de líneas propia** (`_GLIFOS`): los 31
caracteres del alfabeto definidos como polilíneas sobre una rejilla de 10×14, y
cada uno se emite como un `<path>`. En el SVG no hay un solo carácter, solo
coordenadas. Encima, cada carácter se dibuja con escala, giro e inclinación
sorteados, y **con un temblor por vértice**: sin ese temblor las coordenadas de
una `A` serían siempre las mismas y bastaría compararlas contra la tabla
`_GLIFOS` — que está en el código del proyecto — para resolver el captcha sin
mirar la imagen. De eso se encargan tres pruebas en
`tests/test_auth_captcha_correo.py`.

> **Hasta dónde llega.** Ningún captcha dibujado en el navegador es
> inexpugnable: quien se tome el trabajo de hacer OCR sobre la imagen (o de
> emparejar la geometría de los trazos) lo resuelve. Lo que esto corta es el
> abuso real y barato: el script que envía el formulario sin pedir la imagen, y
> el que la pide y le busca el texto adentro. Para un ataque dirigido la defensa
> que de verdad frena es el límite de intentos, que también está puesto.

> El alfabeto excluye `0`, `O`, `1`, `I` y `L` a propósito: son los caracteres
> que la gente confunde al leerlos, y un captcha que falla a quien **sí** es
> humano no sirve de nada.

> **Accesibilidad.** Un captcha visual es, por definición, una barrera para
> quien no ve la imagen. Esta versión no trae alternativa en audio, así que esa
> limitación queda anotada: el login y el resto del sitio sí se manejan con
> teclado y lector de pantalla, pero crear una cuenta requiere ver el dibujo.

### Manual de usuario

Hay un manual de usuario en PDF en **`/manual`**, enlazado en el pie de todas
las páginas, bajo **Ayuda**. Son 8 páginas con portada, índice y 13 secciones:
crear la cuenta, entrar, recuperar la contraseña, buscar, el carrito, comprar,
la factura, el perfil, el chat, qué hacer si algo falla, los roles del equipo y
los datos de contacto.

**Se abre sin sesión**, a propósito: quien no sabe cómo crear una cuenta es
justamente quien más lo necesita. Pedir sesión para leer el manual sería al
revés.

#### Por qué se genera y no es un archivo suelto en `static/`

El manual nombra datos que viven en la configuración: el correo, el teléfono,
el IVA, desde cuánto el envío es gratis, la tabla de tarifas por ciudad, cuánto
dura el código de recuperación y cuántos intentos de login se perdonan antes de
pedir captcha. Si fuera un PDF hecho a mano, cambiar la tarifa de envío en
`config.py` dejaría el manual **mintiendo** y nadie se enteraría.

Armándolo en `app/services/manual_service.py` con ReportLab —el mismo que ya
genera las facturas, así que no añade ninguna dependencia— esos números salen
de la misma fuente que usa la tienda:

| Dato del manual | De dónde sale |
|---|---|
| Correo, teléfono, Instagram, dirección, horario | `Config.EMPRESA` |
| IVA | `Config.IVA_PORCENTAJE` |
| Tabla de envíos y envío gratis | `Config.ENVIO_TARIFAS`, `ENVIO_GRATIS_DESDE` |
| Duración e intentos del código | `models/codigo_recuperacion.py` |
| Dígitos del código | `recuperacion_service.LONGITUD_CODIGO` |
| Fallos antes de pedir captcha | `auth_routes.INTENTOS_ANTES_DE_CAPTCHA` |

Hay una prueba que cambia `ENVIO_GRATIS_DESDE` y exige que el PDF lo refleje:
si alguien reemplaza esto por un archivo fijo, falla.

#### Detalles de la implementación

- Se usa `BaseDocTemplate` y no `SimpleDocTemplate` porque hacen falta dos
  cosas que aquel no da: una portada sin pie de página y un índice que sepa en
  qué página quedó cada sección.
- El índice se arma solo: `afterFlowable` anota cada título y `multiBuild` hace
  las dos pasadas que eso necesita (una para averiguar las páginas y otra para
  escribirlas).
- El PDF se arma **una sola vez** y queda en memoria; en modo desarrollo se
  rehace en cada visita para ver los cambios sin reiniciar.
- Se sirve `inline`, no como descarga: así se hojea desde el teléfono sin
  guardar un archivo. El botón de descargar lo pone el propio visor.
- Si falta el archivo del logo, el manual se genera igual sin él. Un PDF sin
  logo se lee perfectamente; una excepción ahí dejaría a la gente sin manual.

> **Los símbolos que la fuente no tiene salen mal y nadie avisa.** El PDF se
> dibuja con Helvetica, que solo cubre WinAnsi. ReportLab intenta rescatar lo
> que falta sacándolo de una fuente de símbolos, pero cuando no lo encuentra
> **no falla ni avisa**: dibuja otra cosa. Un `☰` para el botón del menú
> terminó como una letra «n» torcida, y eso solo se vio mirando el PDF
> renderizado. Ahora el menú se nombra con palabras, y hay una prueba que
> recorre el texto del manual y rechaza cualquier carácter fuera de WinAnsi.

### Ver la contraseña que se escribe

Todos los campos de contraseña del sitio llevan un botón de ojito para
revelar lo que se está escribiendo: entrar, registrarse, la contraseña nueva
de la recuperación y el alta de personal del panel.

No está puesto campo por campo en cada plantilla. `app/static/js/password.js`
recorre la página, encuentra **todo** `input[type="password"]` y le monta el
botón encima. Son cinco campos repartidos en dos archivos, y cualquiera que
se agregue mañana lo hereda sin que haya que acordarse de nada. Un
`MutationObserver` atiende además los campos que aparecen después de que la
página cargó.

Detalles que importan:

- El botón es `type="button"`. Sin eso, pulsarlo **enviaría el formulario**.
- Es alcanzable con el tabulador: quien no usa ratón también necesita poder
  revisar lo que escribió.
- Cambiar `type` manda el cursor al principio en varios navegadores, así que
  se devuelve al final para poder seguir escribiendo donde iba.
- Edge inyecta su propio icono de "revelar" en los campos de contraseña; se
  oculta con `::-ms-reveal` o saldrían dos ojos.
- El gato del modal se destapa los ojos cuando la contraseña queda a la
  vista: si se puede leer en pantalla, taparse no tiene sentido. password.js
  lo avisa con un evento y `login.js` lo escucha.

### Sin sesión: aviso, no JSON en pantalla

Entrar sin sesión a `/carrito`, `/facturas/historial` o `/facturas/checkout`
dejaba esto escrito en el navegador, como texto pelado:

```json
{"mensaje": "Debes iniciar sesión para continuar.", "ok": false}
```

La causa estaba en `decoradores.py`: decidía si responder JSON **mirando la
ruta** (`if request.path.startswith("/carrito")`). Y esas rutas no solo las
pide el JavaScript — también se abren con un clic o escribiendo la dirección.

Ahora lo decide una cabecera, `X-Requested-With: XMLHttpRequest`, que
`app.js` pone en cada `fetch`. Navegando se va a la portada con el aviso
arriba y el modal abierto; desde el JavaScript sigue llegando el JSON de
siempre.

De paso se arregló un segundo error en la misma línea: `app.js` comparaba
`data.mensaje === "Debes iniciar sesión."` mientras el servidor mandaba
`"Debes iniciar sesión para continuar."`. Nunca coincidían, así que **agregar
al carrito sin sesión no abría el modal**: mostraba el mensaje del servidor
como si fuera un error cualquiera. Ahora el servidor manda una bandera,
`requiere_login: true`, y el JavaScript mira esa bandera y no el texto —
que se puede reescribir sin romper nada.

### En el teléfono

El sitio se probó renderizándolo a **360 y 390 px** de ancho, que es lo que
mide un teléfono real. Lo que apareció:

| Problema | Qué pasaba | Arreglo |
|---|---|---|
| **No había menú** | Por debajo de 640 px la regla `.nav-links { display: none }` escondía los enlaces **y no había nada que los reemplazara**: desde un teléfono no se podía llegar a Productos, Categorías, Acerca de ni Contacto. | Panel desplegable con botón de menú. Los enlaces y las acciones de sesión se escriben una sola vez (macros de Jinja) y se usan en la barra y en el panel. |
| **La página se iba a lo ancho** | `.nav-actions` medía 289 px y la barra no podía encogerse: `scrollWidth` 533 contra 390 de pantalla. «Regístrate» quedaba fuera y todo el contenido se cortaba a la derecha. | `min-width: 0` en los hijos flex de la barra, el bloque de sesión se muda al panel, y `overflow-x: hidden` en `<html>` como red de seguridad. |
| **Enlaces difíciles de tocar** | Enlaces de una línea de alto: con el ratón se aciertan siempre, con el dedo no. | Relleno vertical en los que son *acciones* (menú, pie, «¿Olvidaste tu contraseña?», teléfono y correo de contacto). |
| **Letra de 10,9 px** | La etiqueta de categoría sobre la foto del producto. | Subida a 0,72 rem (11,5 px). |
| **El modal no cabía** | Con el paso del código son seis campos y el gato ocupa un tercio de la pantalla. | En pantallas bajas la ventana se vuelve desplazable y el gato se achica. |

> `overflow-x: hidden` va en `<html>` y **no** en `<body>`: en `body` rompe la
> barra superior `sticky`.

> Las reglas táctiles usan `@media (pointer: coarse), (max-width: 900px)`. Las
> dos condiciones con coma son un «o»: la primera agarra cualquier pantalla
> táctil —una tablet grande también se toca—, y la segunda cubre los
> navegadores que informan mal su tipo de puntero, cosa que pasa en varios
> Android.

Cómo se comprobó, por si hay que repetirlo: Chrome headless **no baja de
~485 px de ancho de ventana en Windows**, así que no se puede renderizar a
390 px directamente. La vuelta es cargar la página en un `<iframe>` del ancho
exacto que se quiere probar — dentro del iframe el viewport sí mide lo que se
le pida y las media queries responden a eso. Un script dentro de la página
recorre el DOM y reporta lo que se sale, la letra por debajo de 11 px y los
blancos de toque de menos de 32 px.

Lo que queda fijado en `tests/test_interfaz_movil.py` es el HTML y las reglas
CSS de las que todo esto depende — que es lo que se rompe sin darse cuenta al
editar. La parte visual no se puede medir desde pytest.

### Recuperar contraseña

En el login (ícono del gato) hay un enlace **"¿Olvidaste tu contraseña?"**.
Desde el Sprint 5 el flujo es de **dos pasos con un código que llega al
correo**, en vez de cambiar la contraseña ahí mismo:

| Paso | Ruta | Qué pide | Qué hace |
|---|---|---|---|
| 1 | `POST /auth/recuperar/solicitar` | documento + correo + captcha | Comprueba que ambos datos sean de la **misma** cuenta, genera un código de 6 dígitos y lo manda al correo registrado. |
| 2 | `POST /auth/recuperar/confirmar` | código + contraseña nueva | Valida el código y recién ahí reescribe la contraseña. |

La lógica está en `app/services/recuperacion_service.py` y el envío en
`app/services/correo_service.py` (con `smtplib`, de la librería estándar: **no
se instaló Flask-Mail**).

**Un código de 6 dígitos y no un enlace con token** porque el enlace obliga a
que el correo sepa a qué dominio apuntar, y el proyecto corre en `localhost`
con un puerto que cambia de equipo a equipo: un enlace así llegaría roto a
cualquiera que no sea quien lo levantó. Un código que la persona copia en el
mismo formulario donde lo pidió no depende del dominio.

Lo que protege el flujo:

- **Se piden documento + correo, no solo el correo.** Quien no conozca los dos
  datos no puede disparar correos a la cuenta de otra persona.
- **De cada código se guarda solo el hash** (Werkzeug), igual que con las
  contraseñas: quien abra `codigo_recuperacion` en phpMyAdmin no puede leer el
  código de nadie.
- **Vence en 15 minutos** y sirve **una sola vez**.
- **Máximo 5 intentos** por código; al sexto queda quemado y hay que pedir otro.
- **Un solo código vigente a la vez:** pedir uno nuevo anula el anterior.
- **Espera de 60 segundos entre envíos**, para que el botón no se vuelva una
  máquina de spam contra el correo del cliente.
- **Si el correo no sale, el código se borra**, así nadie queda esperando la
  espera de 60 segundos por un código que nunca llegó.
- La pantalla confirma el destino **enmascarado** (`an*************s@gmail.com`),
  no la dirección completa.
- Un error de SMTP se registra en el log del servidor, pero a la persona se le
  muestra un mensaje en español sin el detalle técnico.

#### Configurar la cuenta que envía los correos

Lo único que hay que hacer es rellenar dos valores en `.env`. Con Gmail,
`MAIL_CONTRASENA` **no es la contraseña del correo** sino una *contraseña de
aplicación* de 16 letras — Google bloquea el acceso SMTP con la contraseña
normal desde 2022.

1. Activa la **verificación en dos pasos** de la cuenta de Google
   (<https://myaccount.google.com/security>). Sin esto el paso 2 no aparece.
2. Entra a <https://myaccount.google.com/apppasswords>, crea una contraseña de
   aplicación con el nombre `Bones & Paws` y copia las **16 letras**.
3. Pégalas en `.env` **sin espacios**:

   ```ini
   MAIL_USUARIO=tucorreo@gmail.com
   MAIL_CONTRASENA=abcdefghijklmnop
   ```

4. Reinicia `python run.py` (el `.env` se lee al arrancar, no en cada petición).
5. Compruébalo sin tener que recorrer todo el flujo:

   ```bash
   python verificar.py --correo              # se manda la prueba a sí misma
   python verificar.py --correo otro@correo  # o a donde le digas
   ```

   Si falla, el comando nombra las cuatro causas habituales en orden. La más
   común con diferencia: copiar la contraseña **con los espacios** con que
   Google la muestra. Van las 16 letras seguidas.

| Variable | Para qué | Valor por defecto |
|---|---|---|
| `MAIL_SERVIDOR` | Servidor SMTP | `smtp.gmail.com` |
| `MAIL_PUERTO` | Puerto | `587` |
| `MAIL_USAR_TLS` | Cifra la conexión con STARTTLS (puerto 587) | `True` |
| `MAIL_USAR_SSL` | Cifra desde el saludo inicial (puerto 465) | `False` |
| `MAIL_USUARIO` | Cuenta que envía | *(vacío)* |
| `MAIL_CONTRASENA` | Contraseña de aplicación de 16 letras | *(vacío)* |
| `MAIL_NOMBRE_REMITENTE` | Nombre que se ve en la bandeja | `Bones & Paws` |
| `MAIL_A_CONSOLA` | Sin cuenta configurada: imprimir el correo en consola (`True`) o responder con un error (`False`) | sigue a `FLASK_DEBUG` |

> **Sin cuenta configurada el proyecto no se rompe.** Si `MAIL_USUARIO` queda
> vacío y `MAIL_A_CONSOLA=True`, el correo —con el código incluido— se imprime
> en la consola de Flask y **la recuperación sigue su curso**: el código que
> aparece en la consola sirve de verdad para el paso 2, así que el flujo
> completo se puede demostrar sin credenciales. Con `MAIL_A_CONSOLA=False` se
> responde con un mensaje claro en vez de fingir que el correo salió.
>
> Son excluyentes a propósito. La primera versión hacía las dos cosas —imprimía
> el mensaje **y** devolvía error—, y eso dejaba en la consola un código que el
> servicio acababa de invalidar: inútil y confuso. Dos pruebas fijan ese
> comportamiento.
>
> `MAIL_A_CONSOLA` se lee de `FLASK_DEBUG` (la variable de entorno) y no de
> `app.config["DEBUG"]`, porque Flask reescribe `DEBUG` con lo que reciba
> `app.run(debug=...)`: ese valor no es confiable para decidirlo.

> **`.env` no se comparte** (está en `.gitignore`), así que la contraseña de
> aplicación no viaja con el proyecto. Si alguna vez se filtra, se revoca desde
> la misma página de Google sin tocar la contraseña de la cuenta: eso es
> justamente para lo que sirven las contraseñas de aplicación.

> **Tabla nueva.** El flujo necesita `codigo_recuperacion`. En una base creada
> desde cero con `python database/init_db.py` ya viene; en una base `bandp` que
> ya existía hay que correr la migración:
>
> ```bash
> mysql -u root -p bandp < database/migracion_codigo_recuperacion.sql
> ```
>
> `python verificar.py` avisa si falta.

> **Nota sobre contraseñas.** Los clientes semilla de `bandp.sql` traían la
> contraseña escrita tal cual en la tabla (todos con `123456`): cualquiera que
> abriera `cliente` en phpMyAdmin las leía. Las cuentas creadas desde la
> aplicación nunca tuvieron ese problema — se guardan hasheadas con Werkzeug.
>
> Desde el Sprint 4 esas contraseñas heredadas **se migran solas**: cuando
> alguien entra con una guardada en texto plano, se verifica, se reescribe
> hasheada y esa cuenta ya solo tiene hash. Para migrarlas todas de una vez,
> sin esperar a que cada quien inicie sesión:
>
> ```bash
> python database/migrar_contrasenas.py            # muestra qué haría
> python database/migrar_contrasenas.py --aplicar  # lo hace
> ```
>
> No hace falta saber la contraseña de nadie para cifrarla: lo que está
> guardado *es* la contraseña, así que se le aplica el hash y se reescribe.
> Quien entraba con `123456` sigue entrando con `123456`. Ver
> `app/services/auth_service.py`.

---

## 4. Decisiones de diseño (aprobadas explícitamente)

1. **Modificaciones de esquema**, todas aditivas y ninguna destructiva:
   - `producto.imagen_url VARCHAR(255)` — sin esta columna no había forma de que
     el panel persistiera qué imagen corresponde a cada producto, ya fuera subida
     como archivo o pegada como URL (ej. Imgur).
   - `producto.activo TINYINT(1)` — borrado lógico: un producto ya vendido no se
     puede borrar de verdad (la FK `detalle → producto` lo impide, para no dejar
     facturas históricas huérfanas), así que "Eliminar" lo oculta de la tienda
     conservando la fila.
   - `producto.codigo VARCHAR(20) UNIQUE` y **se quitó el `AUTO_INCREMENT` de
     `producto.id_producto`** (ver punto 2).
   - tabla nueva `rol` y columna `empleado.id_rol` (ver punto 3).
   - tabla nueva `auditoria_producto` (ver punto 8).

2. **Código único de producto.** Guardar dos veces el mismo artículo generaba
   dos filas y el catálogo terminaba duplicado, sin nada que lo impidiera.
   Ahora cada producto se identifica por `codigo` (`PER-0001`, `GAT-0012`,
   `OTR-0007`: prefijo de la categoría + consecutivo), que es **`UNIQUE` en la
   base de datos**. El duplicado se rechaza aunque el dato entre por phpMyAdmin
   o por un script suelto.

   `id_producto` **no se eliminó**: `detalle` y `carrito_producto` lo referencian
   desde el histórico de facturas y quitarlo habría dejado esas ventas huérfanas.
   Se queda como llave numérica interna, con su `AUTO_INCREMENT`.

   > **Corregido en el Sprint 4.** Durante un tiempo se le quitó el
   > `AUTO_INCREMENT` a `id_producto` y el id lo calculaba
   > `ProductoService.crear()` con `MAX(id_producto)+1`, creyendo que así se
   > evitaban los duplicados. No hacía falta —quien los impide es el `UNIQUE`
   > de `codigo`, que sigue puesto— y además abría un problema nuevo: si dos
   > personas del equipo guardaban un producto al mismo tiempo, las dos leían
   > el mismo máximo y la segunda chocaba con la llave primaria. El
   > `AUTO_INCREMENT` está de vuelta (ver §4.2).

   La defensa está en tres capas, de fuera hacia dentro:
   - `ProductoService._validar_codigo()` avisa con un mensaje claro y devuelve el
     formulario con lo que ya se había escrito, sin perder el trabajo;
   - el trigger `trg_producto_bi` / `trg_producto_bu` normaliza a mayúsculas y sin
     espacios (`  per-0001  ` → `PER-0001`), que es lo que hace útil al `UNIQUE`:
     sin eso, tres formas de escribir lo mismo entrarían como tres productos;
   - la restricción `UNIQUE uq_producto_codigo`, que es la que no se puede saltar.

3. **Roles en su propia tabla.** El personal está en `empleado` y cada fila apunta
   a un rol de la tabla `rol` (`Administrador`, `Vendedor`) mediante
   `empleado.id_rol`, con `DEFAULT 2` (Vendedor) para que un empleado nuevo entre
   con el permiso más restringido. Se prefirió una tabla aparte a guardar el rol
   como texto suelto en `empleado`: así los roles son un dato controlado —no se
   pueden escribir mal— y se pueden agregar roles nuevos sin tocar la estructura.
   Los clientes siguen en `cliente` y no tienen rol.

4. **Login y perfil únicos.** Un solo formulario (`/auth/login`) atiende a los tres
   tipos de cuenta y una sola dirección (`/perfil`) muestra la ficha de cada quien.
   `AuthService.login()` es el que busca la cuenta en las dos tablas y dice de qué
   tipo es; las rutas solo miran ese resultado para decidir a dónde mandar a la
   persona. Se descartó unificar `cliente` y `empleado` en una sola tabla de
   usuarios: habría obligado a migrar `factura.id_usuario`, `factura.id_empleado`
   y `carrito.id_usuario`, es decir, reescribir el histórico completo.

5. **Carrito persistente en base de datos**, usando las tablas `carrito` y
   `carrito_producto` ya existentes en `bandp.sql`, en vez de guardar solo en
   sesión Flask.
6. **`metodo_pago`** se usa como catálogo de solo lectura para el selector del
   checkout (igual que `categoria`); no tiene una FK real hacia `factura` en el
   dump original, así que no se fuerza una que no existía.
7. **El control de stock vive en la base de datos**, no en Python. El trigger
   `trg_detalle_ai` es el único que descuenta inventario al vender, y
   `trg_detalle_ad` lo devuelve al anular. Por eso se eliminó la línea
   `item.producto.stock -= item.cantidad` de `factura_service.py`: con el
   trigger puesto, habría descontado dos veces. Da igual si la venta entra por
   la app Flask, por `sp_registrar_venta` o por un `INSERT` desde phpMyAdmin.
8. **`auditoria_producto`**, puramente aditiva: no toca
   ninguna tabla del dump original, solo guarda el rastro de altas, cambios de
   precio, movimientos de stock y bajas que dejan los triggers de `producto`.

---

## 4.1 Vistas, procedimientos almacenados y triggers

Todos viven en **`database/objetos.sql`** y están documentados uno por uno,
con ejemplos de uso y pruebas, en **[`docs/objetos_bd.md`](docs/objetos_bd.md)**.

Resumen:

| Tipo | Cuántos | Ejemplos |
|---|---|---|
| **Vistas** | 10 | `vista_catalogo_productos`, `vista_stock_critico`, `vista_ventas_por_categoria`, `vista_top_productos`, `vista_envios_pendientes`, `vista_equipo` (personal con su rol) |
| **Funciones** | 4 | `fn_stock_disponible`, `fn_estado_stock`, `fn_total_carrito`, `fn_total_comprado_cliente` |
| **Procedimientos** | 10 | `sp_registrar_venta` (venta completa transaccional), `sp_registrar_pago`, `sp_registrar_envio`, `sp_reporte_ventas`, `sp_reponer_stock_masivo` (con CURSOR), `sp_purgar_auditoria` |
| **Triggers** | 14 | Control de stock en `detalle`, validaciones en `producto` / `carrito_producto` / `factura`, fechas de `envio` y auditoría |

Una venta completa, sin pasar por la aplicación:

```sql
CALL sp_agregar_al_carrito('1001', 5, 2);
CALL sp_registrar_venta('1001', 999, 0.19, 12000, 'Tarjeta', @factura);
CALL sp_registrar_envio(@factura, 1, 5, @guia);
SELECT @factura, @guia;
```

Los procedimientos abortan con `SIGNAL SQLSTATE '45000'` y un mensaje en
español cuando algo no cuadra (carrito vacío, stock insuficiente, factura
inexistente…), de modo que la regla de negocio se cumple aunque el dato entre
por fuera de Flask.

---

## 4.2 Sprint 4 — mejoras aplicadas

Las nueve mejoras de este sprint, agrupadas por capa.

### Base de datos

| # | Qué estaba mal | Qué se hizo |
|---|---|---|
| 1 | Las tablas eran **`latin1`** mientras la aplicación se conectaba pidiendo `utf8mb4`. Ese desajuste es la causa típica de que las tildes y la «ñ» se vean mal, y aquí casi todo lleva tilde: nombres, ciudades, descripciones. | Todo el esquema pasa a `utf8mb4` / `utf8mb4_unicode_ci`. Para bases ya creadas: `database/migracion_utf8mb4.sql`. |
| 2 | `producto.id_producto` **no tenía `AUTO_INCREMENT`**: el id lo calculaba la aplicación con `MAX(id)+1`. Si dos personas guardaban a la vez, ambas leían el mismo máximo y la segunda chocaba con la llave primaria. | Se restituye el `AUTO_INCREMENT`. El duplicado de productos lo sigue impidiendo el `UNIQUE` de `codigo`, que es quien de verdad lo hacía. Migración: `database/migracion_producto_autoincrement.sql`. |
| 3 | El buscador usaba `nombre LIKE '%texto%'`, que **no puede aprovechar ningún índice** y recorre la tabla entera. | Índice `FULLTEXT ft_producto_busqueda (nombre, descripcion)` y búsqueda con `MATCH … AGAINST` en MySQL (ver más abajo). |
| 4 | `auditoria_producto` crecía sin límite: recibe una fila por cada movimiento de stock, y cada venta mueve stock. | Procedimiento `sp_purgar_auditoria(dias)`, que conserva lo reciente y descarta lo viejo informando cuántas filas quitó. |
| 5 | Las migraciones eran archivos `.sql` sueltos sin registro de cuál se había aplicado. | `database/MIGRACIONES.md`: qué hace cada una, cuándo ejecutarla y **la consulta para saber si ya está puesta**. |

### Backend

| # | Qué estaba mal | Qué se hizo |
|---|---|---|
| 6 | El mismo patrón `MAX(id)+1` estaba en **factura, detalle, carrito y las tablas de pago**, donde el `AUTO_INCREMENT` nunca se había quitado: el cálculo manual solo añadía el riesgo. | Se eliminó de todos. El id lo asigna el motor, que es el único que puede hacerlo sin condiciones de carrera. |
| 7 | Las tablas `envio` y `transportadora`, con su procedimiento y su vista, **existían pero la aplicación nunca las usaba**: al comprar se generaba la factura y ahí terminaba todo. | `EnvioService` nuevo. Cada venta genera su guía, el cliente sigue su pedido desde «Mis compras» y el equipo lo gestiona en **`/admin/envios`**. |
| 8 | El envío costaba **siempre $12.000**, fuera a donde fuera. | La tarifa sale de la ciudad de la dirección del cliente (`Config.ENVIO_TARIFAS`) y las compras sobre $250.000 no pagan envío. |
| 9 | Los listados traían **todas las filas** en cada visita (ya hay 110 clientes y 85 productos sembrados). | Paginación en el catálogo público, el catálogo del panel y las cuentas de clientes. |
| 10 | Las contraseñas semilla estaban **en texto plano** y el login las aceptaba así indefinidamente. | Se cifran solas al entrar (migración perezosa) y `database/migrar_contrasenas.py` las migra todas de una vez. Nadie cambia su contraseña. |

### Frontend

| # | Qué estaba mal | Qué se hizo |
|---|---|---|
| 11 | Cambiar una cantidad del carrito terminaba en `window.location.reload()`, anulando la ventaja de usar `fetch`. | El servidor responde con los totales recalculados y **solo se repintan los números que cambiaron**. |
| 12 | El botón de pagar no se bloqueaba: un doble clic podía **registrar dos veces la misma compra**. | Estado «ocupado» en agregar al carrito, entrar, registrarse y pagar. |
| 13 | El tope de stock solo se conocía al recibir el error del servidor. | El carrito y el selector `+/−` avisan antes de enviar; la regla se comprueba igual en el servidor, que es donde manda. |
| 14 | El modal de login no se cerraba con **Escape**, el tabulador se escapaba a la página tapada de atrás y el foco no volvía a su sitio. | `role="dialog"`, `aria-modal`, cierre con Escape, foco atrapado dentro de la ventana y devuelto al botón que la abrió. |

### Corrección aparte

`/facturas/checkout` **estaba roto**: la línea `precio * cantidad | pesos`
aplicaba el filtro a la cantidad, porque en Jinja el filtro se evalúa antes
que la multiplicación. Cargar la página de pago con el carrito lleno
reventaba con un `TypeError`. No había ninguna prueba que la cubriera; ahora
sí (`test_el_checkout_carga_con_el_carrito_lleno`).

### Envíos

Cada venta genera su guía automáticamente, con el mismo formato que produce
`sp_registrar_envio` (`BP-000042-001`), y los pedidos se reparten entre las
transportadoras registradas.

| Quién | Dónde | Qué ve |
|---|---|---|
| Cliente | «Mis compras» y su factura | Estado del pedido, número de guía, transportadora y fecha estimada de entrega, con los tres pasos (Pendiente → En camino → Entregado). |
| Equipo | `/admin/envios` | Todas las guías, filtradas por estado, con aviso de **atrasado** si ya pasó la fecha estimada. Un clic mueve el envío de estado. |

Al marcar un envío como *Entregado* se sella la fecha real de entrega, y si
se devuelve a un estado anterior esa fecha se limpia — la misma regla del
trigger `trg_envio_bu`, repetida en Python porque las pruebas corren sobre
SQLite, que no tiene triggers.

### Costo del envío

```
subtotal ≥ $250.000            -> Gratis
ciudad reconocida en la dirección -> tarifa de Config.ENVIO_TARIFAS
ninguna de las anteriores       -> Config.ENVIO_TARIFA_DEFECTO
```

La dirección es texto libre («Calle 10 #20-30 Bogotá»), así que la ciudad se
detecta buscando dentro de ella los nombres de la tabla de tarifas, sin
depender de tildes ni mayúsculas. Bogotá es la más barata ($8.000) y Pasto
la más cara ($16.000).

### Búsqueda del catálogo

```
MySQL + palabras de 3+ letras  ->  MATCH … AGAINST (usa el índice FULLTEXT)
resto de los casos             ->  LIKE '%texto%' de siempre
```

Se cae al `LIKE` cuando el motor no es MySQL (las pruebas corren sobre
SQLite) o cuando el término es más corto que lo que MySQL indexa. El código
del producto (`GAT-0001`) se busca siempre con `LIKE`, porque el guion
FULLTEXT lo parte en dos. Y si la base todavía no tiene el índice creado,
la búsqueda **no se cae**: detecta el error y repite la consulta con `LIKE`.

---

## 5. Flujo de una petición (ejemplo: agregar al carrito)

```
Usuario hace click "Agregar al carrito"
   → JS (app.js) hace POST a /carrito/agregar
      → Ruta (carrito_routes.py) solo extrae datos y llama al servicio
         → Servicio (carrito_service.py) valida stock y aplica la regla de negocio
            → Modelo (SQLAlchemy) hace el INSERT/UPDATE en MySQL
```

Ninguna ruta contiene lógica de negocio: solo reciben la petición HTTP,
delegan al servicio correspondiente y devuelven una respuesta.

---

## 6. Notas para evaluación

- Todo el contenido de la tienda (productos, categorías, clientes, facturas)
  se lee directamente de MySQL a través de SQLAlchemy — no hay datos simulados
  ni JSON como base de datos.
- El login flotante reutiliza el diseño, animaciones y validaciones del
  proyecto "Login Gato" original; el único cambio es su presentación como
  modal con fondo desenfocado (blur) en vez de página completa.
- La navegación pública (inicio, productos, categorías, acerca, contacto) no
  requiere sesión iniciada. Carrito, checkout, perfil e historial de compras
  sí están protegidos y redirigen al login si no hay sesión.
"# Bones-And-Paws" 
"# Bones-And-Paws" 
"# Bones-And-Paws" 
"# Bones-And-Paws" 
"# Bones-And-Paws" 
"# bonesnpaws" 
