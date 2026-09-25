"""
Actualizador del tablero de granos y hacienda.

Va a buscar los datos a las fuentes oficiales, los guarda en datos/datos.json
y vuelve a generar index.html con esos datos adentro.

Reglas que respeta, en orden de importancia:

1. No inventa ni completa ningun numero. Si no lo pudo leer, no lo escribe.
2. Si una fuente falla, conserva el ultimo dato bueno que ya estaba guardado
   y marca ese bloque como desactualizado, con el error literal.
3. Cruza cada fuente contra una segunda consulta y guarda el resultado del
   control, ande bien o ande mal.

Se corre asi:   python3 actualizar.py
Y para volver a dibujar el tablero con los datos ya guardados, sin salir a la
red (sirve para retocar el diseno sin molestar a las fuentes):

    python3 actualizar.py --sin-bajar
"""

import datetime as dt
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

RAIZ = os.path.dirname(os.path.abspath(__file__))
DIR_DATOS = os.path.join(RAIZ, "datos")
ARCHIVO_DATOS = os.path.join(DIR_DATOS, "datos.json")
PLANTILLA = os.path.join(RAIZ, "plantilla.html")
SALIDA = os.path.join(RAIZ, "index.html")
DIR_CRUDO = os.path.join(RAIZ, "proceso", "corridas")

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

CAC = "https://www.cac.bcr.com.ar"
SIO = "https://siocarnes.magyp.gob.ar"
BCR = "https://www.bcr.com.ar"

# Cámara Arbitral de Cereales de Rosario: ids del formulario de consultas.
GRANOS = [
    ("Soja", 13, "soja"),
    ("Maíz", 3, "maiz"),
    ("Trigo", 8, "trigo"),
    ("Girasol", 9, "girasol"),
    ("Sorgo", 6, "sorgo"),
]

# SIO Carnes: ids de categoria del monitor bovino.
HACIENDA = [
    ("Novillo", 1, ["novillo"]),
    ("Novillito", 2, ["novillito"]),
    ("Vaquillona", 3, ["vaquillona"]),
    ("Ternero", 4, ["ternero", "ternera"]),
    ("Vaca", 5, ["vaca"]),
    ("Toro", 6, ["toro"]),
]

VENTANA_DIAS = 28          # las "ultimas semanas" que pidio Santiago
DIAS_PARA_VIEJO = 3        # mas de esto sin rueda nueva y el dato es viejo
UMBRAL_DEFINITIVO = 0.70   # % del volumen tipico para considerar firme la hacienda


def contexto_ssl():
    """El Python del sistema en esta Mac no siempre encuentra los certificados."""
    try:
        ctx = ssl.create_default_context()
        if ctx.cert_store_stats().get("x509_ca", 0) > 0:
            return ctx
    except Exception:
        pass
    for ruta in ("/etc/ssl/cert.pem", "/usr/local/etc/openssl/cert.pem"):
        if os.path.exists(ruta):
            return ssl.create_default_context(cafile=ruta)
    return ssl.create_default_context()


CTX = contexto_ssl()


def bajar(url, datos=None, referer=None, timeout=60):
    cabeceras = {"User-Agent": UA, "Accept-Language": "es-AR,es;q=0.9"}
    if referer:
        cabeceras["Referer"] = referer
        cabeceras["X-Requested-With"] = "XMLHttpRequest"
    cuerpo = datos.encode("utf-8") if datos is not None else None
    if cuerpo is not None:
        cabeceras["Content-Type"] = "application/x-www-form-urlencoded"
    pedido = urllib.request.Request(url, data=cuerpo, headers=cabeceras)
    with urllib.request.urlopen(pedido, timeout=timeout, context=CTX) as r:
        return r.read().decode("utf-8", errors="replace")


def a_numero(texto):
    """'$560.000,00' -> 560000.0 . Devuelve None si no hay numero."""
    if texto is None:
        return None
    limpio = re.sub(r"[^0-9,.\-]", "", texto)
    limpio = limpio.replace(".", "").replace(",", ".")
    if not re.search(r"\d", limpio):
        return None
    try:
        return float(limpio)
    except ValueError:
        return None


def sin_tags(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]*>", " ", html)).strip()


def iso(fecha_ar):
    """'23/09/2026' o '9/9/2026' -> '2026-09-23'."""
    partes = re.findall(r"\d+", fecha_ar)
    if len(partes) != 3:
        return None
    d, m, a = (int(p) for p in partes)
    try:
        return dt.date(a, m, d).isoformat()
    except ValueError:
        return None


def habiles(desde, hasta):
    n, d = 0, desde
    while d < hasta:
        if d.weekday() < 5:
            n += 1
        d += dt.timedelta(days=1)
    return n


# ----------------------------------------------------------------------------
# GRANOS - Camara Arbitral de Cereales de Rosario
# ----------------------------------------------------------------------------

def pizarra_del_dia():
    """Lee la pizarra publicada hoy: fecha de rueda, precio, dolar y marcas."""
    html = bajar(CAC + "/es/precios-de-pizarra")
    guardar_crudo("cac-pizarra.html", html)

    m = re.search(r"Precios Pizarra del d[íi]a\s*([\d/]+)", html)
    if not m:
        raise ValueError("no encontre la fecha de la pizarra en la pagina")
    fecha = iso(m.group(1))

    tc = None
    m = re.search(r"TC BNA Divisas Comprador\s*([\d/]+)\s*:\s*\$\s*([\d.,]+)", html)
    if m:
        tc = {"fecha": iso(m.group(1)), "valor": a_numero(m.group(2))}

    tableros = {}
    for bloque in re.findall(r'<div class="board board-([a-z]+)[^"]*">(.*?)</div>\s*</div>\s*</div>',
                             html, re.S):
        clave, cuerpo = bloque
        zona_precio = re.search(r'<div class="price">(.*?)</div>', cuerpo, re.S)
        if not zona_precio:
            continue
        crudo = zona_precio.group(1)
        tableros[clave] = {
            "precio": a_numero(re.sub(r"\(E\)", "", sin_tags(crudo))),
            "estimativo": "(E)" in crudo,
            "sin_cotizacion": "S/C" in crudo,
            "usd": a_numero(sin_tags(re.search(r"<strong>US\$</strong>(.*?)</div>",
                                               cuerpo, re.S).group(1)).replace("(E)", ""))
                   if re.search(r"<strong>US\$</strong>(.*?)</div>", cuerpo, re.S) else None,
        }
    if not tableros:
        raise ValueError("no encontre ningun tablero de precios en la pagina")
    return {"fecha": fecha, "tc_bna": tc, "tableros": tableros}


def bolsa_rosario():
    """Las ultimas 5 ruedas republicadas por la Bolsa de Comercio de Rosario.

    Es otro sitio y otra publicacion que la pizarra de la Camara, y tiene una
    particularidad util: donde la Camara publica un estimativo, la Bolsa pone
    S/C. Eso permite controlar la marca de firmeza, no solo el numero.
    """
    html = bajar(BCR + "/es/mercados/mercado-de-granos/cotizaciones/cotizaciones-locales-0")
    guardar_crudo("bcr-cotizaciones-locales.html", html)
    tabla = re.search(r"<table.*?</table>", html, re.S)
    if not tabla:
        raise ValueError("no encontre la tabla de cotizaciones locales en la BCR")

    filas = []
    for tr in re.findall(r"<tr.*?</tr>", tabla.group(0), re.S):
        filas.append([sin_tags(c) for c in re.findall(r"<t[hd].*?</t[hd]>", tr, re.S)])
    if not filas or len(filas[0]) < 3:
        raise ValueError("la tabla de la BCR no tiene la forma esperada")

    fechas = [iso(f) for f in filas[0][2:]]
    salida = {}
    for fila in filas[1:]:
        nombre = fila[0].strip()
        valores = {}
        for i, fecha in enumerate(fechas):
            if fecha is None or i + 2 >= len(fila):
                continue
            celda = fila[i + 2]
            valores[fecha] = {"sin_cotizacion": "S/C" in celda.upper(),
                              "precio": a_numero(celda)}
        salida[nombre] = valores
    return salida


def historico_grano(id_producto, desde, hasta):
    """Recorre la consulta historica paginada. Devuelve [(fecha, precio, estimativo)]."""
    filas, pagina, vistas = [], 1, set()   # ojo: el pager del sitio arranca en 1, no en 0
    while pagina < 10:
        url = (CAC + "/es/precios-de-pizarra/consultas?" + urllib.parse.urlencode({
            "product": id_producto, "type": "any", "period": "day",
            "date_start": desde.isoformat(), "date_end": hasta.isoformat(),
            "page": pagina}))
        html = bajar(url)
        tabla = re.search(r"<table.*?</table>", html, re.S)
        if not tabla:
            break
        nuevas = 0
        for tr in re.findall(r"<tr.*?</tr>", tabla.group(0), re.S):
            celdas = re.findall(r"<td.*?</td>", tr, re.S)
            if len(celdas) < 3:
                continue
            fecha = iso(sin_tags(celdas[0]))
            precio = a_numero(sin_tags(celdas[2]))
            if not fecha or precio is None or fecha in vistas:
                continue
            vistas.add(fecha)
            filas.append({"fecha": fecha, "precio": precio,
                          "estimativo": "(E)" in sin_tags(celdas[1])})
            nuevas += 1
        if nuevas == 0 or "page=%d" % (pagina + 1) not in html.replace("&amp;", "&"):
            break
        pagina += 1
    filas.sort(key=lambda f: f["fecha"])
    return filas


def traer_granos(hoy):
    pizarra = pizarra_del_dia()
    try:
        bolsa = bolsa_rosario()
        error_bolsa = None
    except Exception as e:
        bolsa, error_bolsa = {}, "%s: %s" % (type(e).__name__, e)
    desde = hoy - dt.timedelta(days=VENTANA_DIAS + 4)
    items, controles = [], []

    for nombre, id_producto, clave in GRANOS:
        serie = historico_grano(id_producto, desde, hoy)
        if not serie:
            raise ValueError("la consulta historica de %s volvio vacia" % nombre)
        ultimo, anterior = serie[-1], (serie[-2] if len(serie) > 1 else None)
        tablero = pizarra["tableros"].get(clave, {})

        firmeza = "estimativo" if ultimo["estimativo"] else "definitivo"
        item = {
            "nombre": nombre,
            "unidad": "$/t",
            "fecha": ultimo["fecha"],
            "precio": ultimo["precio"],
            "firmeza": firmeza,
            "sin_cotizacion": bool(tablero.get("sin_cotizacion")),
            "usd": tablero.get("usd"),
            "anterior": anterior,
            "serie": serie[-VENTANA_DIAS:],
        }
        if anterior and anterior["precio"]:
            item["var_abs"] = ultimo["precio"] - anterior["precio"]
            item["var_pct"] = (ultimo["precio"] / anterior["precio"] - 1) * 100
        items.append(item)

        # CONTROL 1: la pizarra del dia contra la consulta historica, misma fecha.
        del_tablero = tablero.get("precio")
        if pizarra["fecha"] == ultimo["fecha"] and del_tablero is not None:
            coincide = abs(del_tablero - ultimo["precio"]) < 0.5
            controles.append({
                "que": "%s: pizarra del día vs. consulta histórica (%s)" % (nombre, ultimo["fecha"]),
                "ok": coincide,
                "detalle": "pizarra $%s · histórico $%s" % (
                    format(del_tablero, ",.2f"), format(ultimo["precio"], ",.2f")),
            })
        else:
            controles.append({
                "que": "%s: pizarra del día vs. consulta histórica" % nombre,
                "ok": None,
                "detalle": "no comparables: la pizarra es del %s y el histórico llega al %s" % (
                    pizarra["fecha"], ultimo["fecha"]),
            })

        # CONTROL 2: la Camara contra la Bolsa de Comercio de Rosario (otro sitio).
        if error_bolsa:
            controles.append({
                "que": "%s: Cámara vs. Bolsa de Comercio de Rosario" % nombre,
                "ok": None,
                "detalle": "la Bolsa no respondió — " + error_bolsa,
            })
        else:
            comunes = [d for d in serie if d["fecha"] in bolsa.get(nombre, {})]
            iguales, choques = 0, []
            for d in comunes:
                b = bolsa[nombre][d["fecha"]]
                if b["precio"] is not None and not b["sin_cotizacion"]:
                    if abs(b["precio"] - d["precio"]) < 0.5 and not d["estimativo"]:
                        iguales += 1
                    elif abs(b["precio"] - d["precio"]) >= 0.5:
                        choques.append("%s: cámara $%s vs bolsa $%s" % (
                            d["fecha"], format(d["precio"], ",.2f"), format(b["precio"], ",.2f")))
                    else:
                        iguales += 1
                elif b["sin_cotizacion"]:
                    if d["estimativo"]:
                        iguales += 1
                    else:
                        choques.append("%s: la cámara lo da como pizarra firme y la bolsa dice S/C"
                                       % d["fecha"])
            controles.append({
                "que": "%s: Cámara vs. Bolsa de Comercio de Rosario" % nombre,
                "ok": (len(choques) == 0) if comunes else None,
                "detalle": ("%d de %d ruedas comunes coinciden" % (iguales, len(comunes))
                            + ("" if not choques else " · " + " · ".join(choques[:2])))
                           if comunes else "no hay ruedas en común para comparar",
            })

        # CONTROL 3: la cuenta en pesos contra la cuenta en dolares de la misma pagina.
        tc = (pizarra.get("tc_bna") or {}).get("valor")
        if tc and tablero.get("usd") and del_tablero:
            esperado = del_tablero / tc
            desvio = abs(esperado - tablero["usd"]) / tablero["usd"] * 100
            controles.append({
                "que": "%s: $/t ÷ dólar BNA = US$/t" % nombre,
                "ok": desvio < 1.0,
                "detalle": "calculado US$%.2f · publicado US$%.2f (desvío %.2f%%)" % (
                    esperado, tablero["usd"], desvio),
            })

    return {
        "ok": True,
        "fuente": "Cámara Arbitral de Cereales de Rosario",
        "url": CAC + "/es/precios-de-pizarra",
        "fuente_control": "Bolsa de Comercio de Rosario — Cotizaciones Locales",
        "url_control": BCR + "/es/mercados/mercado-de-granos/cotizaciones/cotizaciones-locales-0",
        "rueda": max(i["fecha"] for i in items),
        "tc_bna": pizarra.get("tc_bna"),
        "items": items,
        "controles": controles,
    }


# ----------------------------------------------------------------------------
# HACIENDA - SIO Carnes (MAGyP + AFIP + SENASA)
# ----------------------------------------------------------------------------

def ultima_fecha_sio():
    crudo = bajar(SIO + "/MonitorSioCarnes/GetUltimaFecha", datos="idAnimal=1",
                  referer=SIO + "/MonitorSioCarnes/MonitorSioCarnes?idAnimal=1&animal=BOVINO")
    d = json.loads(crudo)
    return iso(d["Desde"]), iso(d["Hasta"])


def monitor_categoria(id_categoria, dia_ar):
    url = SIO + "/api/Reportes/GetDatosMonitor?" + urllib.parse.urlencode({
        "dia": dia_ar, "categoria": id_categoria,
        "subcatergoria": -1, "zona": -1, "raza": -1})   # el sitio lo escribe asi
    return json.loads(bajar(url, referer=SIO + "/MonitorSioCarnes/MonitorSioCarnes?idAnimal=1&animal=BOVINO"))


def resumen_precios(desde, hasta):
    """desde inclusivo, hasta EXCLUSIVO (asi lo trata el sitio)."""
    url = SIO + "/GrillaSIOCarnes/GetResumenPrecios?" + urllib.parse.urlencode({
        "desde": desde.strftime("%d/%m/%Y"), "hasta": hasta.strftime("%d/%m/%Y"),
        "id_zona": "", "id_Animal": 1})
    return json.loads(bajar(url, referer=SIO + "/GrillaSIOCarnes/ResumenPrecios"))


def por_categoria(filas):
    """Agrupa las subcategorias de SIO en las seis categorias del tablero."""
    salida = {}
    for nombre, _id, palabras in HACIENDA:
        cabezas, suma = 0, 0.0
        for f in filas:
            texto = f.get("Subcategoria", "").lower()
            if not texto.startswith("bovino "):
                continue
            resto = texto[len("bovino "):]
            primera = resto.split()[0] if resto.split() else ""
            if primera not in palabras:
                continue
            c = a_numero(f.get("CabezasComercializadas")) or 0
            p = a_numero(f.get("PrecioPromedioKg"))
            if p is None:
                continue
            cabezas += c
            suma += c * p
        salida[nombre] = {"cabezas": int(cabezas),
                          "promedio": (suma / cabezas) if cabezas else None}
    return salida


def traer_hacienda(hoy):
    _desde_sio, hasta_sio = ultima_fecha_sio()
    dia = dt.date.fromisoformat(hasta_sio)
    dia_ar = dia.strftime("%d/%m/%Y")

    # Volumen tipico: las 4 semanas previas, sin los ultimos 3 dias (que estan a medio cargar).
    fin_ventana = dia - dt.timedelta(days=3)
    ini_ventana = fin_ventana - dt.timedelta(days=VENTANA_DIAS)
    tipico = por_categoria(resumen_precios(ini_ventana, fin_ventana))
    dias_habiles = max(1, habiles(ini_ventana, fin_ventana))

    # Cuantas cabezas entraron cada uno de los ultimos dias. Con eso se sabe que
    # tan cargado esta cada dia, que es lo que hace que un precio sea firme o no.
    cabezas_por_dia = {}
    for n in range(9):
        d = dia - dt.timedelta(days=n)
        cabezas_por_dia[d.isoformat()] = por_categoria(
            resumen_precios(d, d + dt.timedelta(days=1)))
    del_dia = cabezas_por_dia.get(dia.isoformat(), {})

    atraso = (hoy - dia).days
    items, controles = [], []

    for nombre, id_categoria, _palabras in HACIENDA:
        datos = monitor_categoria(id_categoria, dia_ar)
        serie = []
        for p in datos.get("precios", []):
            f, v = iso(p.get("fecha", "")), a_numero(p.get("precioPromedio"))
            if f and v is not None:
                serie.append({"fecha": f, "precio": v,
                              "min": a_numero(p.get("precioMinimo")),
                              "max": a_numero(p.get("precioMaximo"))})
        serie.sort(key=lambda x: x["fecha"])

        semanal = []
        for s in datos.get("promedioSemanal", []):
            if s.get("precio"):        # un 0,00 en esta fuente significa "no hubo dato"
                semanal.append({"etiqueta": s.get("descripcion"),
                                "desde": (s.get("fechaDesdeDT") or "")[:10],
                                "precio": float(s["precio"])})
        semanal.sort(key=lambda x: x["desde"])

        if not serie:
            # La fuente no tiene nada para esta categoria. No completo el hueco:
            # lo muestro como hueco y digo por que.
            items.append({
                "nombre": nombre, "unidad": "$/kg vivo", "sin_dato": True,
                "motivo": ("SIO Carnes se arma con liquidaciones de hacienda con destino a "
                           "faena. Para esta categoría la fuente no devolvió ninguna operación."),
                "serie": [], "serie_semanal": semanal,
            })
            controles.append({
                "que": "%s: Monitor vs. Resumen de precios" % nombre,
                "ok": None,
                "detalle": "sin dato en la fuente: no hay nada que controlar",
            })
            continue

        ultimo = serie[-1]
        anterior = serie[-2] if len(serie) > 1 else None

        base = tipico.get(nombre, {}).get("cabezas", 0) / dias_habiles
        for punto in serie:
            c = cabezas_por_dia.get(punto["fecha"], {}).get(nombre, {}).get("cabezas")
            punto["cabezas"] = c
            punto["completitud"] = round(c / base * 100) if (base and c is not None) else None

        firmes = [p for p in serie
                  if p.get("completitud") is not None
                  and p["completitud"] >= UMBRAL_DEFINITIVO * 100]
        ultimo_firme = firmes[-1] if firmes else None

        cabezas = del_dia.get(nombre, {}).get("cabezas", 0)
        proporcion = (cabezas / base) if base else None
        if atraso > DIAS_PARA_VIEJO:
            firmeza = "viejo"
        elif proporcion is None:
            firmeza = "provisorio"
        else:
            firmeza = "definitivo" if proporcion >= UMBRAL_DEFINITIVO else "provisorio"

        item = {
            "nombre": nombre,
            "unidad": "$/kg vivo",
            "fecha": ultimo["fecha"],
            "precio": ultimo["precio"],
            "min": ultimo.get("min"),
            "max": ultimo.get("max"),
            "firmeza": firmeza,
            "cabezas": cabezas,
            "cabezas_tipicas": round(base) if base else None,
            "completitud": round(proporcion * 100) if proporcion is not None else None,
            "anterior": anterior,
            "ultimo_firme": ultimo_firme if (ultimo_firme and ultimo_firme["fecha"] != ultimo["fecha"]) else None,
            "serie": serie,
            "serie_semanal": semanal[-5:],
        }
        if anterior and anterior["precio"]:
            item["var_abs"] = ultimo["precio"] - anterior["precio"]
            item["var_pct"] = (ultimo["precio"] / anterior["precio"] - 1) * 100
        items.append(item)

        # CONTROL: el promedio del Monitor contra el promedio ponderado del Resumen de precios.
        del_resumen = del_dia.get(nombre, {}).get("promedio")
        if del_resumen and ultimo["precio"]:
            desvio = abs(del_resumen - ultimo["precio"]) / ultimo["precio"] * 100
            controles.append({
                "que": "%s: Monitor vs. Resumen de precios (%s)" % (nombre, ultimo["fecha"]),
                "ok": desvio < 2.0,
                "detalle": "monitor $%.2f/kg · resumen ponderado $%.2f/kg sobre %d cabezas (desvío %.2f%%)"
                           % (ultimo["precio"], del_resumen, cabezas, desvio),
            })
        else:
            controles.append({
                "que": "%s: Monitor vs. Resumen de precios" % nombre,
                "ok": None,
                "detalle": "el resumen no devolvió cabezas para esa categoría ese día",
            })

    return {
        "ok": True,
        "fuente": "SIO Carnes — Secretaría de Agricultura (MAGyP), con AFIP y SENASA",
        "url": SIO + "/MonitorSioCarnes/MonitorSioCarnes?idAnimal=1&animal=BOVINO",
        "rueda": hasta_sio,
        "items": items,
        "controles": controles,
    }


# ----------------------------------------------------------------------------

def guardar_crudo(nombre, texto):
    os.makedirs(DIR_CRUDO, exist_ok=True)
    sello = dt.date.today().isoformat()
    with open(os.path.join(DIR_CRUDO, "%s-%s" % (sello, nombre)), "w", encoding="utf-8") as f:
        f.write(texto)


def leer_guardado():
    if os.path.exists(ARCHIVO_DATOS):
        with open(ARCHIVO_DATOS, encoding="utf-8") as f:
            return json.load(f)
    return {}


def render(datos):
    with open(PLANTILLA, encoding="utf-8") as f:
        plantilla = f.read()
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write(plantilla.replace("/*__DATOS__*/null", json.dumps(datos, ensure_ascii=False)))
    print("index.html regenerado")


def main():
    if "--sin-bajar" in sys.argv:
        datos = leer_guardado()
        if not datos:
            print("no hay datos/datos.json todavia: hay que correrlo sin --sin-bajar", file=sys.stderr)
            return 1
        render(datos)
        return 0

    hoy = dt.date.today()
    previo = leer_guardado()
    nuevo = {"actualizado": dt.datetime.now().isoformat(timespec="seconds"),
             "ventana_dias": VENTANA_DIAS}
    hubo_falla = False

    for clave, traer in (("granos", traer_granos), ("hacienda", traer_hacienda)):
        try:
            bloque = traer(hoy)
            bloque["actualizado"] = nuevo["actualizado"]
            nuevo[clave] = bloque
            print("OK   %-9s rueda %s · %d items" % (clave, bloque["rueda"], len(bloque["items"])))
        except Exception as e:
            hubo_falla = True
            literal = "%s: %s" % (type(e).__name__, e)
            print("FALLA %-8s %s" % (clave, literal), file=sys.stderr)
            viejo = previo.get(clave)
            if viejo:
                viejo = dict(viejo)
                viejo["ok"] = False
                viejo["error"] = literal
                viejo["intento"] = nuevo["actualizado"]
                nuevo[clave] = viejo
                print("     conservo el ultimo dato bueno del %s" % viejo.get("actualizado"))
            else:
                nuevo[clave] = {"ok": False, "error": literal,
                                "intento": nuevo["actualizado"], "items": []}
                print("     no hay dato guardado previo: el bloque queda vacio")

    os.makedirs(DIR_DATOS, exist_ok=True)
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(nuevo, f, ensure_ascii=False, indent=1)

    if os.path.exists(PLANTILLA):
        render(nuevo)
    else:
        print("no existe plantilla.html: solo actualice datos/datos.json")

    return 1 if hubo_falla else 0


if __name__ == "__main__":
    sys.exit(main())
