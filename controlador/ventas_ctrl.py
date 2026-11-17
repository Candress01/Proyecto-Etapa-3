# controlador/ventas_ctrl.py
# Curso: II1119 Fundamentos para Tecnologías Digitales - Proyecto Integrador Etapa 3
# Responsabilidad: orquestar el registro de ventas, la facturación y los impuestos.
# Regla MVC: el controlador pide datos a la vista, aplica las reglas con el modelo
# y NO abre archivos directamente (eso lo hace modelo/persistencia.py).

from modelo import producto, venta, persistencia
from vista import consola


def _cantidad_en_carrito(items, codigo):
    total = 0
    for item in items:
        if item["codigo"] == codigo:
            total = total + item["cantidad"]
    return total


def _agregar_al_carrito(items, p, cantidad):
    # Si el producto ya está en el carrito se suma la cantidad a su línea
    for i, item in enumerate(items):
        if item["codigo"] == p["codigo"]:
            items[i] = venta.construir_item(p, item["cantidad"] + cantidad)
            return
    items.append(venta.construir_item(p, cantidad))


def _revertir_stock(items_descontados):
    for item in items_descontados:
        producto.aumentar_stock(item["codigo"], item["cantidad"])


def realizar_venta():
    # Funcionalidad: venta en punto de caja.
    # Fase 1 (bucle): se acumulan los productos en el carrito.
    # Fase 2 (fuera del bucle): se calculan totales, se confirma y se guarda.
    carrito = []

    while True:
        codigo = consola.pedir_dato("Código del producto a vender (o FIN para terminar)").strip()
        if codigo.upper() == "FIN":
            break

        # Corrección del profesor: el código va en mayúscula; si hay error en el
        # código se avisa y se regresa al menú (la venta en curso se cancela).
        valido, motivo = producto.validar_codigo(codigo)
        if not valido:
            consola.mostrar_error(motivo + " Venta cancelada.")
            return

        p = producto.buscar_producto(codigo)
        if p is None:
            consola.mostrar_error("El producto " + codigo + " no existe. Venta cancelada.")
            return

        try:
            cantidad = int(consola.pedir_dato("Cantidad solicitada"))
        except ValueError:
            consola.mostrar_error("La cantidad debe ser un número entero.")
            continue
        if cantidad <= 0:
            consola.mostrar_error("La cantidad debe ser mayor a cero.")
            continue

        disponible = p["stock"] - _cantidad_en_carrito(carrito, codigo)
        if cantidad > disponible:
            consola.mostrar_error("Stock insuficiente. Disponible: " + str(disponible))
            continue

        _agregar_al_carrito(carrito, p, cantidad)
        consola.mostrar_exito("'" + p["nombre"] + "' agregado a la factura.")

    if len(carrito) == 0:
        consola.mostrar_error("Venta cancelada: no se agregó ningún producto.")
        return

    # Fase 2: totales e impuestos (la venta aún no se guarda)
    resumen = venta.crear_venta(carrito)
    consola.mostrar_resumen_venta(resumen)

    if not consola.pedir_confirmacion("¿Confirma la venta e impresión de factura?"):
        consola.mostrar_error("Venta cancelada. El inventario no sufrió cambios.")
        return

    # Se descuenta el stock; si algo falla se revierte todo
    descontados = []
    for item in resumen["productos_vendidos"]:
        if producto.descontar_stock(item["codigo"], item["cantidad"]):
            descontados.append(item)
        else:
            _revertir_stock(descontados)
            consola.mostrar_error("No se pudo descontar el stock de " + item["codigo"] + ". Venta cancelada.")
            return

    # Se guarda en los CSV; si falla la escritura se revierte el stock
    try:
        persistencia.guardar_inventario(producto.obtener_productos())
        persistencia.agregar_venta_csv(resumen)
    except OSError:
        _revertir_stock(descontados)
        consola.mostrar_error("No se pudieron guardar los archivos CSV. Venta cancelada.")
        return

    venta.agregar_venta(resumen)
    consola.mostrar_exito("Venta procesada.")
    consola.mostrar_facturas(resumen)   # la factura muestra los productos vendidos


def consultar_ventas_dia():
    # Funcionalidad: ventas del día
    del_dia = venta.ventas_del_dia()
    consola.mostrar_ventas_del_dia(del_dia)
    if len(del_dia) > 0:
        total_dia = round(sum(v["total_general"] for v in del_dia), 2)
        consola.mostrar_resumen_ventas_del_dia(del_dia, total_dia)
