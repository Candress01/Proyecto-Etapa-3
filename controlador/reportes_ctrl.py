from modelo import producto, venta
from vista import consola, graficos


def _ventas_por_categoria():
    totales = {}
    productos = producto.obtener_productos()

    categorias_por_codigo = {}
    for p in productos:
        categorias_por_codigo[p["codigo"]] = p["categoria"]

    for una_venta in venta.obtener_ventas():
        for item in una_venta["productos_vendidos"]:
            codigo = item["codigo"]
            categoria = categorias_por_codigo.get(codigo, "Sin categoría")

            if categoria not in totales:
                totales[categoria] = 0

            totales[categoria] += item["subtotal"]

    return totales


def _productos_criticos():
    criticos = []

    for p in producto.obtener_productos():
        if p["stock"] <= p["stock_minimo"]:
            criticos.append(p)

    return criticos


def generar_ventas_categoria():
    datos = _ventas_por_categoria()

    if not datos:
        consola.mostrar_error("No hay ventas registradas para generar el gráfico.")
        return

    try:
        graficos.grafico_ventas_por_categoria(datos)
    except (ValueError, ImportError) as error:
        consola.mostrar_error("No se pudo generar el gráfico: " + str(error))


def generar_stock_critico():
    datos = _productos_criticos()

    if not datos:
        consola.mostrar_mensaje("No hay productos con stock crítico.")
        return

    try:
        graficos.grafico_stock_critico(datos)
    except (ValueError, ImportError) as error:
        consola.mostrar_error("No se pudo generar el gráfico: " + str(error))


def generar_distribucion_ventas():
    datos = _ventas_por_categoria()

    if not datos:
        consola.mostrar_error("No hay ventas registradas para generar el gráfico.")
        return

    try:
        graficos.grafico_distribucion_ventas(datos)
    except (ValueError, ImportError) as error:
        consola.mostrar_error("No se pudo generar el gráfico: " + str(error))


def menu_reportes():
    while True:
        consola.mostrar_menu_graficos()
        opcion = consola.pedir_opcion_menu().strip()

        if opcion == "1":
            generar_ventas_categoria()
        elif opcion == "2":
            generar_stock_critico()
        elif opcion == "3":
            generar_distribucion_ventas()
        elif opcion == "4":
            return
        else:
            consola.mostrar_error("Opción inválida.")
