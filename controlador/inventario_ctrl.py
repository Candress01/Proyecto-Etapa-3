# controlador/inventario_ctrl.py

from datetime import datetime
from controlador import reportes_ctrl
from modelo import producto, persistencia
from vista import consola

DIAS_AVISO_VENCIMIENTO = 30

def _guardar_inventario():
    """Guarda en el CSV los productos que están en memoria."""
    persistencia.guardar_inventario(producto.obtener_productos())


def _pedir_codigo():
    """Solicita y valida un código sin convertirlo a mayúsculas."""
    codigo = consola.pedir_dato("Ingrese el código del producto").strip()
    valido, mensaje = producto.validar_codigo(codigo)

    if not valido:
        consola.mostrar_error(mensaje)
        return None

    return codigo


def registrar_producto():
    """Registra un producto nuevo en el inventario."""
    consola.mostrar_mensaje("\n--- Registrar producto ---")

    codigo = _pedir_codigo()
    if codigo is None:
        return

    if producto.existe_codigo(codigo):
        consola.mostrar_error("Ya existe un producto con ese código.")
        return

    nombre = consola.pedir_dato("Nombre del producto").strip()
    categoria = consola.pedir_dato("Categoría").strip()

    if not nombre or not categoria:
        consola.mostrar_error("El nombre y la categoría no pueden estar vacíos.")
        return

    try:
        stock = int(consola.pedir_dato("Cantidad inicial en stock"))
        stock_minimo = int(consola.pedir_dato("Stock mínimo"))
        precio_compra = float(consola.pedir_dato("Precio de compra"))
        precio_venta = float(consola.pedir_dato("Precio de venta"))
    except ValueError:
        consola.mostrar_error("Debe ingresar números válidos.")
        return

    if stock < 0 or stock_minimo < 0:
        consola.mostrar_error("Las cantidades no pueden ser negativas.")
        return

    if precio_compra < 0 or precio_venta < 0:
        consola.mostrar_error("Los precios no pueden ser negativos.")
        return

    if precio_venta < precio_compra:
        consola.mostrar_error(
            "El precio de venta no puede ser menor que el precio de compra."
        )
        return

    fecha = consola.pedir_dato(
        "Fecha de vencimiento (o escriba N/A si no aplica)"
    ).strip()

    if fecha.upper() == "N/A":
        fecha = ""
 
     valida, mensaje = producto.validar_fecha(fecha)
     if not valida:
         consola.mostrar_error(mensaje)
         return
         
    nuevo = {
        "codigo": codigo,
        "nombre": nombre,
        "categoria": categoria,
        "stock": stock,
        "stock_minimo": stock_minimo,
        "precio_compra": precio_compra,
        "precio_venta": precio_venta,
        "fecha_vencimiento": fecha,
    }

    if producto.agregar_producto(nuevo):
        try:
            _guardar_inventario()
            consola.mostrar_exito("Producto registrado correctamente.")
        except OSError as error:
            # Se revierte el registro si no se pudo guardar el archivo.
            producto.eliminar_producto(codigo)
            consola.mostrar_error("No se pudo guardar el inventario: " + str(error))
    else:
        consola.mostrar_error("No se pudo registrar el producto.")


def actualizar_stock():
    """Permite aumentar o disminuir el stock de un producto."""
    consola.mostrar_mensaje("\n--- Actualizar stock ---")

    codigo = _pedir_codigo()
    if codigo is None:
        return

    existente = producto.buscar_producto(codigo)

    if existente is None:
        consola.mostrar_error("No existe un producto con ese código.")
        return

    consola.mostrar_mensaje(
        "Producto: " + existente["nombre"]
        + " | Stock actual: " + str(existente["stock"])
    )
    consola.mostrar_mensaje("1. Aumentar stock")
    consola.mostrar_mensaje("2. Disminuir stock")

    opcion = consola.pedir_opcion_menu()

    if opcion not in ("1", "2"):
        consola.mostrar_error("Opción no válida.")
        return

    try:
        cantidad = int(consola.pedir_dato("Ingrese la cantidad"))
    except ValueError:
        consola.mostrar_error("La cantidad debe ser un número entero.")
        return

    if cantidad <= 0:
        consola.mostrar_error("La cantidad debe ser mayor que cero.")
        return

    # Se guarda el valor anterior por si ocurre un error al guardar.
    stock_anterior = existente["stock"]

    if opcion == "1":
        resultado = producto.aumentar_stock(codigo, cantidad)
    else:
        resultado = producto.descontar_stock(codigo, cantidad)

    if not resultado:
        consola.mostrar_error(
            "No se pudo actualizar el stock. Verifique la cantidad disponible."
        )
        return

    try:
        _guardar_inventario()
        consola.mostrar_exito(
            "Stock actualizado. Nuevo stock: " + str(existente["stock"])
        )
    except OSError as error:
        existente["stock"] = stock_anterior
        consola.mostrar_error("No se pudo guardar el cambio: " + str(error))

def _alerta_vencimiento(p):
      """Devuelve una alerta si el producto vence pronto o ya venció, si no None."""
      if p["fecha_vencimiento"] == "":
          return None
      try:
          vence = datetime.strptime(p["fecha_vencimiento"], "%Y-%m-%d").date()
      except ValueError:
          return None
      dias = (vence - datetime.now().date()).days
      if dias < 0:
          mensaje = "Producto vencido desde " + p["fecha_vencimiento"] + "."     
      elif dias <= DIAS_AVISO_VENCIMIENTO:
          mensaje = "Vence en " + str(dias) + " días (" + p["fecha_vencimiento"] + ")."
      else:
          return None
      return {"tipo_alerta": "vencimiento", "codigo_producto": p["codigo"], "mensaje": mensaje}

def generar_alertas_stock():
    """
    Genera alertas para productos agotados o con stock igual o inferior
    al mínimo establecido.
    """
    alertas = []

    for p in producto.obtener_productos():
        if p["stock"] <= 0:
            alertas.append({
                "tipo_alerta": "agotado",
                "codigo_producto": p["codigo"],
                "mensaje": "Producto agotado. Stock actual: 0.",
            })
        elif p["stock"] <= p["stock_minimo"]:
            alertas.append({
                "tipo_alerta": "stock_minimo",
                "codigo_producto": p["codigo"],
                "mensaje": (
                    "Stock actual: " + str(p["stock"])
                    + ". Stock mínimo: " + str(p["stock_minimo"]) + "."
                ),
            })
        
    alerta = _alerta_vencimiento(p)
      if alerta is not None:
         alertas.append(alerta)
    return alertas

def consultar_alertas_stock():
    """Muestra los productos que necesitan reposición."""
    alertas = generar_alertas_stock()
    consola.mostrar_alertas(alertas)


def consultar_inventario():
    """Muestra el inventario completo."""
    productos = producto.obtener_productos()
    codigos_bajo = [
        p["codigo"] for p in productos
        if p["stock"] <= p["stock_minimo"]
    ]

    consola.mostrar_inventario(
        productos,
        codigos_bajo,
        "Inventario completo"
    )


def consultar_lista_productos():
    """Muestra el catálogo de productos."""
    consola.mostrar_lista_productos(producto.obtener_productos())


def filtrar_inventario():
    """Filtra los productos por categoría, precio o estado de stock."""
    productos = producto.obtener_productos()

    if not productos:
        consola.mostrar_mensaje("No hay productos para filtrar.")
        return

    consola.mostrar_menu_filtros()
    opcion = consola.pedir_opcion_menu()

    filtrados = []

    if opcion == "1":
        categorias = sorted(set(p["categoria"] for p in productos))
        consola.mostrar_lista_categorias(categorias)

        try:
            seleccion = int(consola.pedir_dato("Seleccione una categoría"))
        except ValueError:
            consola.mostrar_error("Debe ingresar un número.")
            return

        if seleccion == 0:
            return

        if seleccion < 1 or seleccion > len(categorias):
            consola.mostrar_error("La categoría seleccionada no existe.")
            return

        categoria = categorias[seleccion - 1]
        filtrados = [
            p for p in productos if p["categoria"] == categoria
        ]

    elif opcion == "2":
        try:
            minimo = float(consola.pedir_dato("Precio mínimo"))
            maximo = float(consola.pedir_dato("Precio máximo"))
        except ValueError:
            consola.mostrar_error("Los precios deben ser números.")
            return

        if minimo < 0 or maximo < minimo:
            consola.mostrar_error("El rango de precios no es válido.")
            return

        filtrados = [
            p for p in productos
            if minimo <= p["precio_venta"] <= maximo
        ]

    elif opcion == "3":
        consola.mostrar_menu_estados_stock()
        estado_opcion = consola.pedir_opcion_menu()

        estados = {
            "1": "disponible",
            "2": "agotado",
            "3": "bajo",
        }

        if estado_opcion not in estados:
            consola.mostrar_error("Estado seleccionado no válido.")
            return

        estado = estados[estado_opcion]
        filtrados = [
            p for p in productos
            if producto.estado_stock(p) == estado
        ]

    else:
        consola.mostrar_error("Opción de filtro no válida.")
        return

    codigos_bajo = [
        p["codigo"] for p in filtrados
        if p["stock"] <= p["stock_minimo"]
    ]

    consola.mostrar_inventario(
        filtrados,
        codigos_bajo,
        "Resultado del filtro"
    )


def ordenar_inventario():
    """Ordena por nombre, stock o precio, ascendente o descendente."""
    productos = producto.obtener_productos()

    if not productos:
        consola.mostrar_mensaje("No hay productos para ordenar.")
        return

    consola.mostrar_menu_orden_campo()
    campo_opcion = consola.pedir_opcion_menu()

    campos = {
        "1": "nombre",
        "2": "stock",
        "3": "precio_venta",
    }

    if campo_opcion not in campos:
        consola.mostrar_error("Campo de ordenamiento no válido.")
        return

    consola.mostrar_menu_orden_sentido()
    sentido = consola.pedir_opcion_menu()

    if sentido not in ("1", "2"):
        consola.mostrar_error("Orden seleccionado no válido.")
        return

 def _clave(p):
        valor = p[campos[campo_opcion]]
        return valor.lower() if isinstance(valor, str) else valor

    productos_ordenados = sorted(productos, key=_clave, reverse=(sentido == "2"))

    codigos_bajo = [
        p["codigo"] for p in productos_ordenados
        if p["stock"] <= p["stock_minimo"]
    ]

    consola.mostrar_inventario(
        productos_ordenados,
        codigos_bajo,
        "Inventario ordenado"
    )


def menu_inventario():
    """Menú de consultas y operaciones del inventario."""
    while True:
        consola.mostrar_menu_inventario()
        opcion = consola.pedir_opcion_menu()

        if opcion == "1":
            consultar_inventario()
        elif opcion == "2":
            filtrar_inventario()
        elif opcion == "3":
            ordenar_inventario()
        elif opcion == "4":
            reportes_ctrl.generar_reporte_calidad()
        elif opcion == "5":
            return
        else:
            consola.mostrar_error("Opción no válida.")
