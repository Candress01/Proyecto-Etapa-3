from modelo import producto, persistencia
from vista import consola


def registrar_producto():
    consola.mostrar_mensaje("REGISTRAR PRODUCTO")

    codigo = consola.pedir_dato("Código del producto").strip()
    valido, motivo = producto.validar_codigo(codigo)

    if not valido:
        consola.mostrar_error(motivo)
        return

    if producto.existe_codigo(codigo):
        consola.mostrar_error("Ya existe un producto con ese código.")
        return

    nombre = consola.pedir_dato("Nombre").strip()
    categoria = consola.pedir_dato("Categoría").strip()

    if nombre == "" or categoria == "":
        consola.mostrar_error("El nombre y la categoría son obligatorios.")
        return

    try:
        stock = int(consola.pedir_dato("Stock inicial"))
        stock_minimo = int(consola.pedir_dato("Stock mínimo"))
        precio_compra = float(consola.pedir_dato("Precio de compra"))
        precio_venta = float(consola.pedir_dato("Precio de venta"))
    except ValueError:
        consola.mostrar_error("Los valores numéricos ingresados no son válidos.")
        return

    if stock < 0 or stock_minimo < 0:
        consola.mostrar_error("El stock no puede ser negativo.")
        return

    if precio_compra < 0 or precio_venta < 0:
        consola.mostrar_error("Los precios no pueden ser negativos.")
        return

    fecha = consola.pedir_dato(
        "Fecha de vencimiento (AAAA-MM-DD o N/A)"
    ).strip()

    nuevo = {
        "codigo": codigo,
        "nombre": nombre,
        "categoria": categoria,
        "stock": stock,
        "stock_minimo": stock_minimo,
        "precio_compra": precio_compra,
        "precio_venta": precio_venta,
        "fecha_vencimiento": "" if fecha.upper() == "N/A" else fecha,
    }

    if producto.agregar_producto(nuevo):
        try:
            persistencia.guardar_inventario(producto.obtener_productos())
            consola.mostrar_exito("Producto registrado correctamente.")
        except OSError as error:
            producto.catalogo.remove(nuevo)
            consola.mostrar_error("No se pudo guardar el producto: " + str(error))
    else:
        consola.mostrar_error("No se pudo registrar el producto.")


def actualizar_stock():
    consola.mostrar_mensaje("ACTUALIZAR STOCK")

    codigo = consola.pedir_dato("Código del producto").strip()
    valido, motivo = producto.validar_codigo(codigo)

    if not valido:
        consola.mostrar_error(motivo)
        return

    p = producto.buscar_producto(codigo)

    if p is None:
        consola.mostrar_error("El producto no existe.")
        return

    try:
        cantidad = int(
            consola.pedir_dato("Cantidad que desea agregar al stock")
        )
    except ValueError:
        consola.mostrar_error("La cantidad debe ser un número entero.")
        return

    if cantidad <= 0:
        consola.mostrar_error("La cantidad debe ser mayor que cero.")
        return

    stock_anterior = p["stock"]

    if producto.aumentar_stock(codigo, cantidad):
        try:
            persistencia.guardar_inventario(producto.obtener_productos())
            consola.mostrar_exito(
                "Stock actualizado. Existencias actuales: " + str(p["stock"])
            )
        except OSError as error:
            p["stock"] = stock_anterior
            consola.mostrar_error("No se pudo guardar el cambio: " + str(error))


def consultar_alerta_stock():
    alertas = []

    for p in producto.obtener_productos():
        if p["stock"] <= p["stock_minimo"]:
            if p["stock"] == 0:
                mensaje = "El producto está agotado."
                tipo = "stock_bajo"
            elif p["stock"] == p["stock_minimo"]:
                mensaje = "El producto llegó exactamente al stock mínimo."
                tipo = "stock_minimo"
            else:
                mensaje = "El producto está por debajo del stock mínimo."
                tipo = "stock_bajo"

            alertas.append({
                "tipo_alerta": tipo,
                "codigo_producto": p["codigo"],
                "mensaje": mensaje,
            })

    consola.mostrar_alertas(alertas)


def consultar_inventario():
    productos = producto.obtener_productos()
    codigos_bajos = []

    for p in productos:
        if p["stock"] <= p["stock_minimo"]:
            codigos_bajos.append(p["codigo"])

    consola.mostrar_inventario(productos, codigos_bajos)


def consultar_lista_productos():
    consola.mostrar_lista_productos(producto.obtener_productos())
