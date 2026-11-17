# modelo/venta.py
# ventas en memoria, cálculo de impuestos y totales
# Regla MVC: aquí no hay print ni input ni lectura de archivos
# Una venta es un diccionario con estas claves (son las que usa vista/consola.py):
# numero_factura, fecha, subtotal, total_impuestos, total_general,
# productos_vendidos = lista de items
# Cada item: codigo, nombre, cantidad, precio_venta, subtotal, impuestos, total

from datetime import datetime

TASA_IMPUESTO = 0.13   # 13 % de IVA
FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"

ventas = []   # ventas cargadas del CSV + las de esta sesión


def construir_item(p, cantidad):
    # Arma un item de factura a partir de un producto y la cantidad vendida
    subtotal = round(p["precio_venta"] * cantidad, 2)
    impuestos = round(subtotal * TASA_IMPUESTO, 2)
    return {
        "codigo": p["codigo"],
        "nombre": p["nombre"],
        "cantidad": cantidad,
        "precio_venta": p["precio_venta"],
        "subtotal": subtotal,
        "impuestos": impuestos,
        "total": round(subtotal + impuestos, 2),
    }


def generar_numero_factura():
    # F-0001, F-0002... Toma el número más alto que ya existe (no la cantidad
    # de ventas) para no repetir facturas después de cargar el CSV.
    mayor = 0
    for v in ventas:
        texto = str(v["numero_factura"]).replace("F-", "")
        if texto.isdigit() and int(texto) > mayor:
            mayor = int(texto)
    return "F-" + str(mayor + 1).zfill(4)


def crear_venta(items):
    # Calcula los totales y devuelve la venta lista para guardar y facturar
    subtotal = round(sum(i["subtotal"] for i in items), 2)
    impuestos = round(sum(i["impuestos"] for i in items), 2)
    return {
        "numero_factura": generar_numero_factura(),
        "fecha": datetime.now().strftime(FORMATO_FECHA),
        "productos_vendidos": items,
        "subtotal": subtotal,
        "total_impuestos": impuestos,
        "total_general": round(subtotal + impuestos, 2),
    }


def cargar_ventas(lista):
    ventas.clear()
    ventas.extend(lista)


def agregar_venta(una_venta):
    ventas.append(una_venta)


def obtener_ventas():
    return list(ventas)


def ventas_del_dia(fecha=None):
    # Ventas de una fecha "AAAA-MM-DD" (por defecto, hoy)
    if fecha is None:
        fecha = datetime.now().strftime("%Y-%m-%d")
    return [v for v in ventas if str(v["fecha"]).startswith(fecha)]
