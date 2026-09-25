# Tablero de cotizaciones de granos y hacienda en pie

## Qué construí

Un tablero web de una sola pantalla con las cotizaciones del mercado argentino de granos (soja, maíz, trigo, girasol, sorgo) y de hacienda bovina en pie (novillo, novillito, vaquillona, ternero, vaca, toro). De cada cosa muestra a cuánto cerró la última rueda, cuánto se movió contra la rueda anterior, cómo viene en las últimas semanas y qué tan firme es ese dato: definitivo, estimativo, provisorio o viejo.

Es un archivo HTML suelto: abre con doble clic, sin instalar nada y sin servidor. Los datos viajan adentro del archivo. Un script aparte (`actualizar.py`) sale a buscar las cotizaciones a las fuentes oficiales y vuelve a generar el tablero.

Está hecho para que el responsable de la empresa y los stakeholders abran una pantalla a la mañana y no tengan que entrar a ningún sitio.

**Archivos**

| Archivo | Qué es |
|---|---|
| `index.html` | El tablero. Es lo que se abre. Se genera solo. |
| `actualizar.py` | Va a buscar los datos, los controla y regenera el tablero. |
| `plantilla.html` | El molde del tablero, sin datos. |
| `.github/workflows/actualizar.yml` | La tarea que actualiza el tablero sola, dos veces por día. |
| `datos/datos.json` | El último dato bueno de cada mercado. |
| `proceso/BITACORA.md` | La bitácora de la sesión, escrita mientras pasaba. |
| `proceso/evidencia/` | Capturas de las pruebas. |
| `proceso/corridas/` | El HTML crudo que devolvieron las fuentes, como respaldo. |

**Cómo se usa**

Para cualquier persona de la empresa: se abre el link y listo. No hay nada que instalar, que descargar ni que apretar. La página se rehace sola dos veces por día con lo último que publicaron las fuentes; el sello de arriba a la derecha dice de cuándo es el dato que se está viendo.

Para actualizarla a mano hay dos caminos. Desde GitHub, sin terminal: pestaña **Actions → Actualizar cotizaciones → Run workflow**. Desde la Mac:

```
python3 actualizar.py               # trae los datos y regenera el tablero
python3 actualizar.py --sin-bajar   # solo redibuja con lo ya guardado, sin red
```

**De dónde salen los datos**

| | Fuente primaria | Segunda fuente (control) |
|---|---|---|
| Granos | [Cámara Arbitral de Cereales de Rosario](https://www.cac.bcr.com.ar/es/precios-de-pizarra) — pizarra del día y consulta histórica | [Bolsa de Comercio de Rosario, Cotizaciones Locales](https://www.bcr.com.ar/es/mercados/mercado-de-granos/cotizaciones/cotizaciones-locales-0) |
| Hacienda | [SIO Carnes](https://siocarnes.magyp.gob.ar/MonitorSioCarnes/MonitorSioCarnes?idAnimal=1&animal=BOVINO) — Secretaría de Agricultura (MAGyP), con AFIP y SENASA | El Resumen de precios por subcategoría del mismo SIO, ponderado por cabezas |

## Cómo se lo pedí

Los pedidos de Santiago, textuales, en orden, con su ortografía.

**Pedido 1 — 2026-09-25, 12:26** (llegó como imagen de una hoja y como texto):

> Contexto: Administro una empresa agropecuaria. No sé programar y no voy a
> escribir una línea de código: yo describo, decido y corrijo el rumbo; vos
> investigás, programás y probás.
>
> QUÉ QUIERO CONSTRUIR
> Un tablero web de una sola pantalla con las cotizaciones del mercado
> argentino de granos y de hacienda en pie. Quiero abrirlo a la mañana y ver,
> sin entrar a ningún sitio: a cuánto cerró cada cosa en la última rueda,
> cuánto se movió contra la rueda anterior, cómo viene en las últimas semanas,
> y qué tan firme es cada dato (si es definitivo, provisorio, estimativo o
> viejo). Es para mí y para los stakeholders de la empresa.
>
> LÍMITES
>
> * Escala una tarde. Si algo se estira, achicá el alcance y decímelo.
> * Sin instalar nada para verlo: tiene que abrirse con doble clic o desde un
> link.
>
> LOS DATOS
> No te doy las fuentes: encontralas vos y verificá que sirvan antes de usarlas.
> Quiero datos oficiales del mercado, no estimaciones de terceros. Reglas:
>
> * Nunca inventes un número ni lo completes de memoria. Si una fuente no
> responde, el tablero conserva el último dato bueno y avisa en pantalla que
> está desactualizado.
> * Buscá una segunda fuente para controlar la primera, y contame qué control
> hace y qué no puede detectar.
> * Antes de leer un sitio, fijate si lo permite.
>
> CÓMO QUIERO TRABAJAR
>
> * Antes de empezar hacéme hasta 3 preguntas, las que más cambien el
> resultado. Después arrancá.
> * No cambies el alcance sin preguntarme. Si se te ocurre algo que yo no pedí,
> proponémelo en dos líneas y esperá mi respuesta. No lo construyas primero.
> * Cuando algo te falle, no lo escondas: pegá el error textual, decime qué
> probaste y qué vas a intentar.
> * Pedime permiso antes de usar una clave mía, tocar algo fuera de la carpeta
> del proyecto o publicar cualquier cosa.
>
> QUÉ QUIERO QUE DOCUMENTES MIENTRAS PASA (no al final)
> Un archivo proceso/BITACORA.md que vayas llevando durante la sesión, con:
> cada pedido mío textual y con mi ortografía, qué hiciste con él, cada
> herramienta que usaste, qué observaste y cómo eso te cambió el plan, y cada
> falla con el error literal. No lo edites después para que quede lindo.
>
> EL README
> En la raíz, con estos títulos exactos y nada más: "Qué construí", "Cómo se lo
> pedí", "Qué funciona", "Qué falta o qué falló", "Qué aprendí".
> En "Cómo se lo pedí" van mis pedidos textuales, todos, en orden, sin
> resumirlos ni mejorarlos.
> "Qué aprendí" y la explicación de qué entendí yo del trabajo con agentes las
> escribo yo: dejá el título y debajo las preguntas que me tenga que contestar.
> No escribas nada en primera persona en mi nombre.
>
> EL CIERRE
> Cuando esté andando quiero publicarlo en un repositorio público de GitHub con
> GitHub Pages. Tengo GitHub Desktop instalado y mi usuario es sspp404. Guiame
> paso a paso, uno por vez, y esperá mi confirmación antes de seguir. Al final
> verificá vos que el link de Pages abra de verdad.

**Pedido 2 — 2026-09-25, 12:31.** Respondió las tres preguntas eligiendo opciones de una lista, sin escribir texto. Eligió: granos y hacienda completo (las cinco mercaderías y las seis categorías); los datos se actualizan corriendo el actualizador y el tablero muestra la fecha; ventana de las últimas 4 semanas.

**Pedido 3 — 2026-09-25, 13:12:**

> proba tambien con la bolsa de cereales de rosario

**Pedido 4 — 2026-09-25, 13:20:**

> Estoy en remote, dame un link para abrirlo

**Pedido 5 — 2026-09-25, 13:22:**

> Dónde está el botón para actualizar día a día?

**Pedido 6 — 2026-09-25, 13:28:**

> Si, hacelo. Tiene que ser simple para cualquier miembro de la empresa

## Qué funciona

Probado el 2026-09-25. Las capturas de cada prueba están en `proceso/evidencia/`.

**El tablero abre con doble clic.** Sin servidor, sin instalar nada, protocolo `file://`. Los datos están embebidos en el propio `index.html`, que es justamente lo que permite que funcione así y también desde un link. Entra completo en una pantalla de 1440×950: once fichas, sin scroll para ver los precios. Cero errores de consola. Modo oscuro incluido (`proceso/evidencia/tablero-modo-oscuro.png`).

**Trae datos oficiales reales.** En la corrida del 2026-09-25: granos de la rueda del 23/09 (23 ruedas de historia por mercadería) y hacienda de la rueda del 24/09, con el promedio semanal de las últimas 5 semanas que publica SIO.

**La firmeza de cada dato sale de la fuente, no de una interpretación.** En granos, la Cámara marca ella misma `(E)` cuando no hubo operaciones y publica un estimativo: ese día la ficha dice `estimativo`. En hacienda, SIO carga las liquidaciones con días de rezago, así que el tablero calcula qué porcentaje del volumen habitual ya entró ese día y marca `provisorio` cuando falta. La ficha muestra el porcentaje y las cabezas, y además el último cierre firme, para que se vea de dónde sale la etiqueta.

**Si una fuente se cae, conserva el último dato bueno y avisa.** Probado rompiendo a propósito el host de la Cámara. El actualizador imprimió:

```
FALLA granos   URLError: <urlopen error [Errno 8] nodename nor servname provided, or not known>
     conservo el ultimo dato bueno del 2026-09-25T12:59:59
OK   hacienda  rueda 2026-09-24 · 6 items
```

y el tablero quedó con los precios de granos en pantalla, una franja roja arriba con el error textual y el sello "con fallas". Captura: `proceso/evidencia/tablero-fuente-caida.png`.

**Ningún número se inventa.** Cuando la fuente no tiene el dato, la ficha queda vacía y explica el motivo. Es el caso de Ternero: SIO Carnes se arma con liquidaciones de hacienda con destino a faena y el ternero va a invernada, así que esa categoría no existe en la fuente. Se muestra igual, marcada `SIN DATO`.

**La actualización automática está escrita y probada hasta donde se puede probar sin el repositorio.** Es una tarea de GitHub Actions que corre a las 07:00 y a las 18:00 de Argentina, vuelve a generar el tablero y lo publica, más un botón "Run workflow" para correrla a mano desde el navegador. Verificado localmente: el YAML es válido, y la lógica de publicación se probó en un repositorio de prueba en los dos casos —sin cambios imprime `Sin cambios: la rueda es la misma` y no commitea; con cambios commitea—. Si una fuente no responde, la tarea igual publica el tablero con el último dato bueno y el aviso rojo, y además deja la corrida marcada en rojo en GitHub para que se entere el dueño del repositorio.

**Los 16 controles corren en cada actualización y quedan a la vista** en el panel "Control contra la segunda fuente" del propio tablero. En la corrida del 2026-09-25: 15 coinciden y 1 queda en N/D (Ternero, no hay nada que controlar).

**Qué hace cada control y qué no puede detectar**

| Control | Qué compara | Qué detecta | Qué NO puede detectar |
|---|---|---|---|
| Cámara vs. Bolsa de Comercio de Rosario | El precio de cada rueda en dos sitios distintos, y además la marca: donde la Cámara pone `(E)`, la Bolsa pone `S/C` | Que se haya leído mal un número, que una de las dos publicaciones esté desfasada, y que la etiqueta de estimativo esté bien puesta | Un error de la Cámara en el origen: las dos publican el mismo dato de base, así que un error de ella aparece igual en las dos |
| Pizarra del día vs. consulta histórica | El mismo precio en dos páginas distintas de la Cámara | Páginas cacheadas, una consulta que quedó atrasada, errores de lectura del HTML | Lo mismo: es el mismo organismo |
| $/t ÷ dólar BNA = US$/t | La cuenta contra el valor en dólares que publica la propia pizarra | Que se haya leído mal el precio, el dólar o la conversión | Que la Cámara haya publicado mal el par |
| Monitor vs. Resumen de precios (hacienda) | El promedio por categoría del Monitor contra el promedio ponderado por cabezas de las subcategorías | Que un endpoint devuelva otra cosa, que la agrupación de subcategorías esté mal, diferencias entre los dos cálculos de SIO | Un error de SIO en el origen, o un sesgo de la fuente misma (ver abajo) |

**Antes de leer cada sitio se miró si lo permite.** Se pidió el `robots.txt` de las seis candidatas antes de leer ninguna página. Dos quedaron descartadas por eso o por no poder verificarlo: la Bolsa de Cereales de Buenos Aires (devuelve 403 con un desafío de Cloudflare, no se esquivó) y la Cámara Arbitral de Cereales de Bahía Blanca, que hubiera sido la mejor segunda fuente independiente para granos y sin embargo se descartó porque su `robots.txt` dice `Disallow: /` para todo el sitio.

## Qué falta o qué falló

**Falló y quedó sin resolver**

- **El Mercado Agroganadero de Cañuelas es inalcanzable desde acá.** Era la fuente natural de hacienda en pie. Cuatro intentos con `curl` (con y sin `www`, con y sin TLS, y el `robots.txt`) devolvieron siempre `curl: (28) Connection timed out after 25000 milliseconds` / `HTTP 000`. El dominio resuelve (`188.114.97.2`, Cloudflare) y en la misma sesión otros sitios contestaron, así que no es la red. También se probó con el navegador de la app: `navigation to https://mercadoagroganadero.com.ar was denied or failed`. Se cambió de fuente a SIO Carnes.
- **El Índice Novillo del Ministerio está abandonado.** El CSV de datos abiertos descarga bien pero su última fila es `2019-01-31`, y el endpoint en vivo (`/IndiceNovillo/GetPrecios`) devuelve `[]`. Era la mejor candidata a control independiente de hacienda.
- **`matbarofex.com.ar` no respondió** en ninguno de los tres intentos (`HTTP 000`).

**Limitaciones de lo que sí quedó funcionando**

- **Los dos controles son del mismo organismo.** Para granos, la Cámara y la Bolsa de Comercio de Rosario son dos sitios distintos pero publican el mismo dato de base. Para hacienda, los dos endpoints son de SIO. Con las fuentes que quedaron disponibles no se consiguió un control verdaderamente independiente. El tablero lo dice en pantalla, no solo acá.
- **No hay ternero.** Explicado arriba. Si la empresa necesita precio de invernada, hace falta otra fuente, que no se buscó porque excedía lo pedido.
- **Hacienda no es el precio de un mercado concentrador, es el promedio país de las liquidaciones de faena.** Es un número oficial y auditable, pero no es lo mismo que la pizarra de Cañuelas. Para un tomador de decisiones de la empresa, la diferencia importa y conviene tenerla presente.
- **El dato de hacienda de los últimos días es flojo.** El día 24/09 tenía entre 4% y 42% del volumen habitual cargado según la categoría. El tablero lo marca `provisorio` y muestra el último cierre firme, pero el número grande de esas fichas se va a mover.
- **El umbral que separa "definitivo" de "provisorio" (70% del volumen habitual) lo fijó el agente, no la fuente.** Es el único criterio del tablero que no sale de un organismo oficial.
- **Los días hábiles se cuentan de lunes a viernes, sin feriados.** En una semana con feriado, el "volumen habitual" queda algo subestimado.

**Falta**

- **La tarea automática todavía no corrió de verdad.** No existe hasta que el repositorio esté en GitHub. Lo probado es el YAML y la lógica de commit en local; falta ver una corrida real y confirmar que el horario y los permisos de escritura están bien.
- Que Santiago mire el tablero y pida sus cambios.
- Publicarlo en GitHub con Pages y verificar que el link abra.

## Qué aprendí

Esta sección la escribe Santiago. Abajo quedan las preguntas a contestar; el agente no escribe nada acá.

1. Vos pediste un tablero de cotizaciones y el agente eligió las fuentes, descartó tres y armó los controles. ¿En qué momento de todo eso tomaste vos una decisión y en qué momento decidió él? ¿Dónde te hubiera gustado decidir y no te preguntó?

2. El agente trabaja en un ciclo de planear, actuar, observar y volver a planear. Buscá en `proceso/BITACORA.md` un momento donde lo que observó le cambió el plan (hay varios: el rezago de carga de SIO, el `(E)` de la Cámara, el ternero que no existe). Contá con tus palabras qué pasó ahí y por qué el agente no podía haberlo previsto antes de mirar.

3. El agente tuvo ocho fallas anotadas. Tres eran del mundo (sitios caídos, un dataset abandonado, un sitio que prohíbe leerlo) y tres eran errores propios (la paginación, el día suelto de SIO, la prueba que dio por fallada sin haber recargado). ¿Cambia en algo tu confianza en el resultado saber que están todas escritas? ¿Preferirías no verlas?

4. Las herramientas que usó fueron: leer y escribir archivos, correr comandos en la terminal, pedir páginas web, buscar en internet y abrir un navegador para mirar. ¿Cuál de esas te parece la que más cambió lo que pudo hacer, y qué no habría podido hacer sin ella?

5. El tablero muestra un número que dice "provisorio" y otro que dice "definitivo". Esa diferencia no la inventó el agente para granos (la marca la Cámara) pero sí fijó él el corte para hacienda. ¿Te alcanza esa distinción para usar el tablero en una decisión de la empresa, o necesitás algo más?

6. Si mañana tuvieras que pedirle esto mismo a un agente desde cero, ¿qué le dirías distinto en el primer mensaje?
