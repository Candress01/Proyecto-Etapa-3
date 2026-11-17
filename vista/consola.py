def dinero(valor):
    # Hace que el valor sea con 2 decimales y con separador de miles
    return "{:,.2f}".format(valor)

    #MENU   

def mostrar_menu_principal():
    print("")
    print("=" * 50)
    print("Sistema de inventarios y punto de venta")
    print("1. Registrar producto")
    print("2. Actualizar stock")
    print("3. Realizar venta")
    print("4. Consultar alerta de stock")
    print("5. Consultar inventario")
    print("6. Consultar ventas del dia")
    print("7. Consultar lista de productos")
    print("8. Generar reporte de graficos")
    print("9. Salir")

def mostrar_menu_inventario():
    print("")
    print("=" * 30)
    print("Menu de inventario:")
    print("1. Ver inventario completo")
    print("2. Filtrar inventario")
    print("3. Ordenar inventario")
    print("4. Reporte de calidad de datos")
    print("5. Volver")

def mostrar_menu_filtros():
    print("")
    print("Filtrar mediante:")
    print("1. Categoria")
    print("2. Rango de precio")
    print("3. Estado de stock")

def mostrar_lista_categorias(categorias):
    print("")
    print("Categorias disponibles:")
    if len(categorias) == 0:
        print("No hay categorias registradas.")
        return
    contador = 1
    for categoria in categorias:
        print(str(contador) + ". " + str(categoria))
        contador = contador + 1
    print("0. Cancelar") 

def mostrar_menu_estados_stock():
    print("")
    print("Estado de stock:")
    print("1. Disponible")
    print("2. Agotado")
    print("3. Bajo")


def mostrar_menu_orden_campo():
    print("")
    print("Ordenar por:")
    print("1. Nombre")
    print("2. Stock")
    print("3. Precio")


def mostrar_menu_orden_sentido():
    print("")
    print("Orden:")
    print("1. Ascendente")
    print("2. Descendente")


def mostrar_menu_graficos():
    print("")
    print("Reportes gráficos:")
    print("1. Ventas totales por categoría")
    print("2. Stock actual vs stock mínimo")
    print("3. Distribución de ventas por categoría")
    print("4. Volver")

def pedir_opcion_menu():
   # Devuelve lo que el usuario ingresa como opción del menú
   return input("Ingrese una opción: ")

def pedir_dato(mensaje):
    # Pregunta al usuario por un dato y lo devuelve como texto
    return input(mensaje + ": ")

def pedir_confirmacion(mensaje):
    # Solicita al usuario que responda con Si o no y repite la pregunta hasta que se haga
    while True:
        respuesta = input(mensaje + " (si/no): ").strip().lower()
        if respuesta in "(si or sí)":
            return True
        elif respuesta == "no":
            return False
        else:
            mostrar_error("Responder con Si o No")

    #MENSAJES

def mostrar_mensaje(texto):
    print(texto)
    # Muestra cuando el proceso esta correcto o con error

def mostrar_exito(texto):
    print("Correcto: " + texto)
def mostrar_error(texto):
    print("Error: " + texto)
def mostrar_despedida():
    print("Programa finalizado.")

    #INVENTARIO

def mostrar_inventario(productos,codigos_stock_bajo,titulo="Inventario"):
    # El controlador manda los codigos con stock bajo y se marca con *
    print("")
    print(titulo )
    if len(productos) == 0:
        print("El inventario está vacío")
        return
    print("Codigo".ljust(10) + "Nombre".ljust(20)+ "Categoria".ljust(15) + "Stock".rjust(10) + "Minimo".rjust(10)+ "Precio".rjust(14)+ "Vencimiento".rjust(15))
    print("-" * 94)
    for p in productos:
        fecha = str(p["fecha_vencimiento"])
        if fecha =="":
            fecha = "N/A"
        fila = str(p["codigo"]).ljust(10) + str(p["nombre"])[:19].ljust(20) + str(p["categoria"])[:14].ljust(15) + str(p["stock"]).rjust(10) + str(p["stock_minimo"]).rjust(10) + dinero(p["precio_venta"]).rjust(14) + fecha.rjust(15)
        if p["codigo"] in codigos_stock_bajo:
            fila += " *"
        print(fila)
    if len(codigos_stock_bajo) > 0:
        print("* = Producto con stock bajo o en un minimo de stock")

       #List de productos que hay en el catalogo 
def mostrar_lista_productos(productos):
    print("")
    print("Lista de productos:")
    if len(productos) == 0:
        print("No hay productos registrados.")
        return
    print("Codigo".ljust(10) + "Nombre".ljust(20) + "Categoria".ljust(15) + "Precio de venta".rjust(18))
    print("-" * 63)
    for p in productos:
        print(str(p["codigo"]).ljust(10) + str(p["nombre"])[:19].ljust(20) + str(p["categoria"])[:14].ljust(15) + dinero(p["precio_venta"]).rjust(18))
    print("Total de productos: " + str(len(productos)))


    #CALIDAD DE DATOS

def mostrar_reporte_calidad(reporte):
    print("")
    print("Reporte de calidad de datos:")
    if reporte is None or len(reporte) == 0:
        print("No hay reporte disponible.")
        return
    if "leidos" in reporte:
        print("Registros leidos: " + str(reporte["leidos"]))
    print("Registros corregidos: " + str(reporte.get("corregidos", 0)))
    print("Registros descartados: " + str(reporte.get("descartados", 0)))
    print("Registros marcados: " + str(reporte.get("marcados", 0)))
    detalle = reporte.get("detalle", [])
    if len(detalle) > 0:
        print("Detalle:")
        for linea in detalle:
             print("- " + str(linea))

    #VENTAS

def mostrar_productos_vendidos(items):
#Muestra cada producto del carrito
    print("Codigo".ljust(10) + "Producto".ljust(20) + "Cantidad".rjust(10) + "Precio ".rjust(15) + "Subtotal".rjust(15))
    print("-" * 70)
    for item in items:
        print(str(item["codigo"]).ljust(10) + str(item["nombre"])[:19].ljust(20) + str(item["cantidad"]).rjust(10) + dinero(item["precio_venta"]).rjust(15) + dinero(item["subtotal"]).rjust(15))
    print("-" * 70)

def mostrar_totales(venta):
    print("Subtotal: " + dinero(venta["subtotal"]))
    print("Impuestos(13%): " + dinero(venta["total_impuestos"]))
    print("TOTAL: " + dinero(venta["total_general"]))

def mostrar_resumen_venta(venta):
    print("")
    print("Resumen de la venta:")
    mostrar_productos_vendidos(venta["productos_vendidos"])
    mostrar_totales(venta)

def mostrar_factura(venta):
    print("")
    print("=" * 70)
    print("FACTURA N° " + str(venta["numero_factura"]))
    print("Fecha: " + str(venta["fecha"]))
    print("=" * 70)
    mostrar_productos_vendidos(venta["productos_vendidos"])
    mostrar_totales(venta)
    print("=" * 70)

def mostrar_ventas_del_dia(ventas,total_dia):
    print("")
    print("Ventas del día:")
    if len(ventas) == 0:
        print("No se han realizado ventas hoy.")
        return
    print("Factura".ljust(10) + "Fecha".ljust(20) + "Impuestos".rjust(15) + "Total".rjust(15))
    print("-" * 60)
    for v in ventas:
        print(str(v["numero_factura"]).ljust(10) + str(v["fecha"]).ljust(20) + dinero(v["total_impuestos"]).rjust(15) + dinero(v["total_general"]).rjust(15))
    print("-" * 60)
    print("Cantidad de ventas: " + str(len(ventas)))
    print("Total ACUMULADO: " + dinero(total_dia))


    #ALERTAS
def mostrar_alertas(alertas):
    print("")
    print("Alertas de stock:")
    if len(alertas) == 0:
        print("No hay alertas de stock.")
        return
    for a in alertas:
        if a["tipo_alerta"] in ("Agotado","stock_bajo"):
            tipo = "Agotado"
        elif a["tipo_alerta"] == "stock_minimo":
            tipo = "Stock en mínimo"
        else:
            tipo = "Vencimiento"
        print("[" + tipo + "] Producto " + str(a["codigo_producto"]) + ": " + a["mensaje"])
    print("Total de alertas: " + str(len(alertas)))
    