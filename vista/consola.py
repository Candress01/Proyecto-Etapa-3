def dinero(valor):
    # Hace que el valor sea con 2 decimales y con separador de miles
    return "{:,.2f}".format(valor)

    #MENU   

def mostrar_menu_principal():
    print("Sistema de inventarios y punto de venta")
    print("1. Registrar producto")
    print("2. Actualizar stock")
    print("3. Realizar venta")
    print("4. Generar alertas de stock")
    print("5. Consultar inventario")
    print("6. Consultar ventas del dia")
    print("7. Consultar lista de productos")
    print("8. Salir")
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
        if respuesta == "si"or respuesta =="Si":
            return True
        elif respuesta == "no"or respuesta =="No":
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

def mostrar_inventario(productos,codigos_stock_bajo):
    # El controlador manda los codigos con stock bajo y se marca con *
    print("Inventario:")
    if len(productos) == 0:
        print("El inventario está vacío")
        return
    print("Codigo".ljust(10) + "Nombre".ljust(20)+ "Categoria".ljust(15) + "Stock".rjust(10) + "Minimo".rjust(10)+ "Precio".rjust(10)+ "Vencimiento".rjust(15))
    print("-" * 90)
    for p in productos:
        fecha = str(p["fecha_vencimiento"])
        if fecha =="":
            fecha = "N/A"
        fila = str(p["codigo"]).ljust(10) + str(p["nombre"]).ljust(20) + str(p["categoria"]).ljust(15) + str(p["stock"]).rjust(10) + str(p["stock_minimo"]).rjust(10) + dinero(p["precio_venta"]).rjust(10) + fecha.rjust(15)
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
    print("Codigo".ljust(10) + "Nombre".ljust(20) + "Categoria".ljust(15) + "Precio de venta".rjust(10))
    print("-" * 60)
    for p in productos:
        print(str(p["codigo"]).ljust(10) + str(p["nombre"]).ljust(20) + str(p["categoria"]).ljust(15) + dinero(p["precio_venta"]).rjust(10))
    print("Total de productos: " + str(len(productos)))

    #VENTAS

def mostrar_productos_vendidos(items):
#Muestra cada producto del carrito
    print("Codigo".ljust(10) + "Producto".ljust(20) + "Cantidad".rjust(10) + "Precio ".rjust(15) + "Subtotal".rjust(15))
    print("-" * 70)
    for item in items:
        print(str(item["codigo"]).ljust(10) + str(item["nombre"]).ljust(20) + str(item["cantidad"]).rjust(10) + dinero(item["precio_venta"]).rjust(15) + dinero(item["subtotal"]).rjust(15))
        print("-" * 70)
def mostrar__totales(venta):
    print("Subtotal:"+ dinero(venta["subtotal"]))
    print("impuestos(13%):"+ dinero(venta["total_impuestos"]))
    print("TOTAL:"+ dinero(venta["total_general"]))
def mostrar_resumen_venta(venta):
    print("")
    print("Resumen de la venta:")
    mostrar_productos_vendidos(venta["productos_vendidos"])
    mostrar__totales(venta)
def mostrar_facturas(venta):
    print("")
    print("=" * 50)
    print("FACTURA N"+ str(venta["numero_factura"]))
    print("Fecha: " + str(venta["fecha"]))
    mostrar_productos_vendidos(venta["productos_vendidos"])
    mostrar__totales(venta)
    print("=" * 50)
def mostrar_ventas_del_dia(ventas):
    print("")
    print("Ventas del día:")
    if len(ventas) == 0:
        print("No se han realizado ventas hoy.")
        return
    print("Factura".ljust(10) + "Fecha".ljust(20) + "Impuestos".rjust(15) + "Total".rjust(15))
    print("-" * 50)
    for v in ventas:
        print(str(v["numero_factura"]).ljust(10) + str(v["fecha"]).ljust(20) + dinero(v["total_impuestos"]).rjust(15) + dinero(v["total_general"]).rjust(15))
    print("Cantidad de ventas: " + str(len(ventas)))
    print("Total Acumulado: " + dinero(total_dia))

    #ALERTAS
def mostrar_alertas(alertas):
    print("")
    print("Alertas de stock:")
    if len(alertas) == 0:
        print("No hay alertas de stock.")
        return
    for a in alertas:
        if a["tipo_alerta"] == "stock_bajo":
            tipo = "Stock bajo"
        elif a["tipo_alerta"] == "stock_minimo":
            tipo = "Stock en mínimo"
        else:
            tipo = "Vencimiento"
        print("[" + tipo + "] " + "Producto" + str(a["codigo_producto"]) + ": " + a["mensaje"])
    print("Total de alertas: " + str(len(alertas)))
    