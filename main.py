from modelo import persistencia
from vista import consola
from controlador import inventario_ctrl,ventas_ctrl,reportes_ctrl

def cargar_datos():

    #Carga el inventario y ventas csv ademas devuelve false si no se pudo leer
    try:
        resumen = resumen = persistencia.cargar_datos_iniciales()
    except (OSError, UnicodeDecodeError) as error:
        consola.mostrar_error("No se pudo cargar los archivos CSV: " + str(error))
        return False

    for nombre in resumen["archivos_creados"]:
        consola.mostrar_mensaje("Se creo " + nombre + " con los encabezados.")

    consola.mostrar_exito(
        str(resumen["productos_cargados"]) + " productos y "
        + str(resumen["ventas_cargadas"]) + " ventas cargadas."
    )

    for incidencia in resumen["incidencias"]:
        consola.mostrar_error(incidencia)
    #Reporte de calida de datos
    try:
        reportes_ctrl.generar_reporte_calidad()
    except OSError as error:
        consola.mostrar_error("No se puede generar el reporte de calidad: " + str(error))

    return True

def main():
    if not cargar_datos():
        return

     #Cada opcion del menu llama a una funcion del controlador
    acciones = {
        "1": inventario_ctrl.registrar_producto,
        "2": inventario_ctrl.actualizar_stock,
        "3": ventas_ctrl.realizar_venta,
        "4": inventario_ctrl.consultar_alertas_stock,
        "5": inventario_ctrl.menu_inventario,
        "6": ventas_ctrl.consultar_ventas_dia,
        "7": inventario_ctrl.consultar_lista_productos,
        "8": reportes_ctrl.generar_reporte_graficos,}     

    while True:
        consola.mostrar_menu_principal()
        opcion = consola.pedir_opcion_menu().strip()

        if opcion == "9":
            consola.mostrar_despedida()
            break
        elif opcion in acciones:
            acciones[opcion]()
        else:
            consola.mostrar_error("Opción no es valida")
if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("")
        consola.mostrar_despedida()