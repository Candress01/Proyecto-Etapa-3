# leer y escribir los archivos CSV (inventario.csv y ventas.csv)
# aquí no hay print ni input, los errores se devuelven como datos
# y es el controlador que decide qué mostrar

import csv
import os
import shutil

from modelo import producto, venta

CODIFICACION = "utf-8"

# La carpeta datos/ está en la raíz del proyecto (al lado de main.py)
RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA_DATOS = os.path.join(RAIZ_PROYECTO, "datos")
RUTA_INVENTARIO = os.path.join(CARPETA_DATOS, "inventario.csv")
RUTA_VENTAS = os.path.join(CARPETA_DATOS, "ventas.csv")

ENCABEZADOS_INVENTARIO = [
    "codigo", "nombre", "categoria", "stock", "stock_minimo",
    "precio_compra", "precio_venta", "fecha_vencimiento",
]
ENCABEZADOS_VENTAS = [
    "numero_factura", "fecha", "codigo_producto", "cantidad",
    "subtotal", "impuestos", "total",
]

# Funciones generales

def asegurar_archivo(ruta, encabezados):
    # Crea el archivo con sus encabezados si no existe (o si está vacío).
    # Devuelve True si tuvo que crearlo, False si ya existía.
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    if not os.path.exists(ruta) or os.path.getsize(ruta) == 0:
        with open(ruta, "w", newline="", encoding=CODIFICACION) as archivo:
            csv.writer(archivo).writerow(encabezados)
        return True
    return False


def leer_filas_crudas(ruta, encabezados):
    # Devuelve (filas, incidencias), cada fila es un diccionario con texto
    # como viene en el archivo sin convertir sirve también para el
    # módulo de limpieza de datos.
    # Se lee con utf-8-sig para tolerar archivos guardados desde Excel (con BOM).
    asegurar_archivo(ruta, encabezados)
    filas = []
    incidencias = []
    with open(ruta, newline="", encoding="utf-8-sig") as archivo:
        lector = csv.DictReader(archivo)
        faltantes = [c for c in encabezados if c not in (lector.fieldnames or [])]
        if faltantes:
            incidencias.append("Encabezados incorrectos en " + os.path.basename(ruta)
                               + ". Faltan: " + ", ".join(faltantes))
            return [], incidencias
        numero_fila = 1
        for fila in lector:
            numero_fila += 1
            fila["_numero_fila"] = numero_fila
            filas.append(fila)
    return filas, incidencias


def escribir_csv(ruta, encabezados, filas):
    # Escribe todo el archivo, primero escribe en un archivo temporal y luego
    # lo reemplaza, así si algo falla a la mitad no se corrompe el archivo real.
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    ruta_temporal = ruta + ".tmp"
    with open(ruta_temporal, "w", newline="", encoding=CODIFICACION) as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(encabezados)
        for fila in filas:
            escritor.writerow(fila)
    os.replace(ruta_temporal, ruta)

# Inventario

def _fila_a_producto(fila):
# Convierte una fila de texto a un producto, lanza ValueError si hay
 # campos vacíos o con formato inválido.
for campo in ("codigo", "nombre", "categoria", "stock", "stock_minimo",
            "precio_compra", "precio_venta"):
     if fila.get(campo) is None or fila[campo].strip() == "":
              raise ValueError("campo vacío: " + campo)
      stock = int(float(fila["stock"]))
      stock_minimo = int(float(fila["stock_minimo"]))
      precio_compra = float(fila["precio_compra"])
      precio_venta = float(fila["precio_venta"])
      if stock < 0 or stock_minimo < 0:
          raise ValueError("cantidades negativas")
      if precio_compra < 0 or precio_venta < 0:
          raise ValueError("precios negativos")
      return {
          "codigo": fila["codigo"].strip(),
          "nombre": fila["nombre"].strip(),
          "categoria": fila["categoria"].strip(),
          "stock": stock,
          "stock_minimo": stock_minimo,
          "precio_compra": precio_compra,
          "precio_venta": precio_venta,
          "fecha_vencimiento": (fila.get("fecha_vencimiento") or "").strip(),
      }

def leer_inventario():
    # Devuelve (productos, incidencias). Las filas inválidas se saltan
    # y quedan anotadas en incidencias, el programa no se cae
    asegurar_archivo(RUTA_INVENTARIO, ENCABEZADOS_INVENTARIO)
    filas, incidencias = leer_filas_crudas(RUTA_INVENTARIO, ENCABEZADOS_INVENTARIO)
    productos = []
    codigos_vistos = set()
    for fila in filas:
        try:
            p = _fila_a_producto(fila)
            if p["codigo"] in codigos_vistos:
                raise ValueError("código duplicado " + p["codigo"] + " (se conserva el primero)")
            codigos_vistos.add(p["codigo"])
            productos.append(p)
        except (ValueError, TypeError, OverflowError) as error:  # 
            incidencias.append("inventario.csv fila " + str(fila["_numero_fila"])
                               + ": " + str(error))
    return productos, incidencias


def guardar_inventario(productos):
    filas = []
    for p in productos:
        filas.append([
            p["codigo"], p["nombre"], p["categoria"], p["stock"], p["stock_minimo"],
            p["precio_compra"], p["precio_venta"], p["fecha_vencimiento"],
        ])
    escribir_csv(RUTA_INVENTARIO, ENCABEZADOS_INVENTARIO, filas)

# Ventas (en el CSV hay una fila por cada producto de la factura)

def _venta_a_filas(una_venta):
    filas = []
    for item in una_venta["productos_vendidos"]:
        filas.append([
            una_venta["numero_factura"], una_venta["fecha"], item["codigo"],
            item["cantidad"], item["subtotal"], item["impuestos"], item["total"],
        ])
    return filas


def leer_ventas(nombres_por_codigo=None):
    # Devuelve (ventas, incidencias), agrupa las filas por numero_factura
    # nombres_por_codigo (opcional) es un diccionario codigo -> nombre para que
    # las ventas históricas también puedan mostrar el nombre del producto.
    if nombres_por_codigo is None:
        nombres_por_codigo = {}
    asegurar_archivo(RUTA_VENTAS, ENCABEZADOS_VENTAS)
    filas, incidencias = leer_filas_crudas(RUTA_VENTAS, ENCABEZADOS_VENTAS)
    por_factura = {}
    orden = []
    for fila in filas:
        try:
            numero = fila["numero_factura"].strip()
            if numero == "":
                raise ValueError("campo vacío: numero_factura")
            cantidad = int(fila["cantidad"])
            subtotal = float(fila["subtotal"])
            impuestos = float(fila["impuestos"])
            total = float(fila["total"])
            codigo = fila["codigo_producto"].strip()
            if cantidad <= 0:
                raise ValueError("cantidad no positiva")
        except (ValueError, TypeError, AttributeError) as error:
            incidencias.append("ventas.csv fila " + str(fila["_numero_fila"])
                               + ": " + str(error))
            continue
        if numero not in por_factura:
            por_factura[numero] = {
                "numero_factura": numero,
                "fecha": (fila.get("fecha") or "").strip(),
                "productos_vendidos": [],
            }
            orden.append(numero)
        por_factura[numero]["productos_vendidos"].append({
            "codigo": codigo,
            "nombre": nombres_por_codigo.get(codigo, ""),
            "cantidad": cantidad,
            "precio_venta": round(subtotal / cantidad, 2),
            "subtotal": subtotal,
            "impuestos": impuestos,
            "total": total,
        })
    ventas = []
    for numero in orden:
        una_venta = por_factura[numero]
        items = una_venta["productos_vendidos"]
        una_venta["subtotal"] = round(sum(i["subtotal"] for i in items), 2)
        una_venta["total_impuestos"] = round(sum(i["impuestos"] for i in items), 2)
        una_venta["total_general"] = round(sum(i["total"] for i in items), 2)
        ventas.append(una_venta)
    return ventas, incidencias


def agregar_venta_csv(una_venta):
    # Agrega las filas de una venta nueva al final de ventas.csv
    asegurar_archivo(RUTA_VENTAS, ENCABEZADOS_VENTAS)
    with open(RUTA_VENTAS, "a", newline="", encoding=CODIFICACION) as archivo:
        escritor = csv.writer(archivo)
        for fila in _venta_a_filas(una_venta):
            escritor.writerow(fila)


def guardar_ventas(ventas):
    # Reescribe todo ventas.csv (por si algún módulo corrige o elimina ventas)
    filas = []
    for una_venta in ventas:
        filas.extend(_venta_a_filas(una_venta))
    escribir_csv(RUTA_VENTAS, ENCABEZADOS_VENTAS, filas)

# Carga inicial (se llama una sola vez al arrancar el programa)

def cargar_datos_iniciales():
    # Crea los archivos si no existen, lee ambos CSV y llena las listas en
    # memoria de producto.py y venta.py.
    # Devuelve un diccionario con el resumen para que el controlador lo muestre:
    #  productos_cargados, ventas_cargadas, archivos_creados, incidencias
    creados = []
    if asegurar_archivo(RUTA_INVENTARIO, ENCABEZADOS_INVENTARIO):
        creados.append("inventario.csv")
    if asegurar_archivo(RUTA_VENTAS, ENCABEZADOS_VENTAS):
        creados.append("ventas.csv")
    shutil.copy(RUTA_INVENTARIO, RUTA_INVENTARIO + ".bak")

    productos, incidencias = leer_inventario()
    producto.cargar_catalogo(productos)

    nombres = {p["codigo"]: p["nombre"] for p in productos}
    ventas, incidencias_ventas = leer_ventas(nombres)
    venta.cargar_ventas(ventas)

    return {
        "productos_cargados": len(productos),
        "ventas_cargadas": len(ventas),
        "archivos_creados": creados,
        "incidencias": incidencias + incidencias_ventas,
    }
