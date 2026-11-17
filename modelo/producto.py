# modelo/producto.py
# Curso: II1119 Fundamentos para Tecnologías Digitales - Proyecto Integrador Etapa 3
# Responsabilidad: catálogo de productos en memoria y sus reglas.
# Regla MVC: aquí NO hay print ni input ni lectura de archivos.
# Cada producto es un diccionario con las mismas claves que las columnas de
# inventario.csv: codigo, nombre, categoria, stock, stock_minimo,
# precio_compra, precio_venta, fecha_vencimiento.

import re

catalogo = []   # lista de productos (diccionarios)

# Letras mayúsculas (1 a 3) y 3 números. Ejemplos válidos: L001, B002, PAN001
PATRON_CODIGO = re.compile(r"^[A-Z]{1,3}[0-9]{3}$")


def validar_codigo(codigo):
    # Devuelve (True, "") si el código es válido, o (False, motivo).
    # Corrección del profesor: el código siempre va en MAYÚSCULA;
    # si viene en minúscula (por ejemplo "l001" o "l") es un error.
    texto = str(codigo).strip()
    if texto == "":
        return False, "El código no puede estar vacío."
    if texto != texto.upper():
        return False, "El código debe escribirse en mayúscula (ejemplo: L001)."
    if not PATRON_CODIGO.match(texto):
        return False, "Formato de código inválido. Use letras mayúsculas y 3 números (ejemplo: L001)."
    return True, ""


def cargar_catalogo(productos):
    # Reemplaza el catálogo en memoria (se usa al leer inventario.csv)
    catalogo.clear()
    catalogo.extend(productos)


def obtener_productos():
    # Devuelve una copia de la lista para que no la dañen desde afuera
    return list(catalogo)


def buscar_producto(codigo):
    # Busca el código EXACTO (sin convertir a mayúscula): "l001" no es "L001".
    # Devuelve el producto o None si no existe.
    texto = str(codigo).strip()
    for p in catalogo:
        if p["codigo"] == texto:
            return p
    return None


def existe_codigo(codigo):
    return buscar_producto(codigo) is not None


def agregar_producto(nuevo):
    # Devuelve False si el código ya existe; True si lo agregó.
    if existe_codigo(nuevo["codigo"]):
        return False
    if str(nuevo.get("fecha_vencimiento", "")).strip().upper() == "N/A":
        nuevo["fecha_vencimiento"] = ""
    catalogo.append(nuevo)
    return True


def aumentar_stock(codigo, cantidad):
    p = buscar_producto(codigo)
    if p is None or cantidad <= 0:
        return False
    p["stock"] = p["stock"] + cantidad
    return True


def descontar_stock(codigo, cantidad):
    # False si no existe, si la cantidad no es positiva o si no alcanza el stock
    p = buscar_producto(codigo)
    if p is None or cantidad <= 0 or p["stock"] < cantidad:
        return False
    p["stock"] = p["stock"] - cantidad
    return True


def estado_stock(p):
    # "agotado", "bajo" (en el mínimo o por debajo) o "disponible"
    if p["stock"] <= 0:
        return "agotado"
    if p["stock"] <= p["stock_minimo"]:
        return "bajo"
    return "disponible"
