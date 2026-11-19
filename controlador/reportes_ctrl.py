#reportes_ctrl.py

import math
import os

from modelo import producto, venta, persistencia
from vista import consola, graficos

CARPETA_GRAFICOS = os.path.join(persistencia.RAIZ_PROYECTO, "evidencias", "graficos")


def _es_numero(valor):
    """Comprueba si un texto representa un número válido (rechaza nan e inf)."""
    try:
        return math.isfinite(float(valor))
    except (ValueError, TypeError):
        return False


def _analizar_inventario():
    """
    Revisa inventario.csv sin modificarlo.
    Devuelve un reporte de registros corregidos, descartados y marcados.
    """
    filas, incidencias = persistencia.leer_filas_crudas(
        persistencia.RUTA_INVENTARIO,
        persistencia.ENCABEZADOS_INVENTARIO
    )

    reporte = {
        "leidos": len(filas),
        "corregidos": 0,
        "descartados": 0,
        "marcados": 0,
        "detalle": [],
        "duplicados": {},
    }

    codigos_vistos = {}

    campos_obligatorios = [
        "codigo",
        "nombre",
        "categoria",
        "stock",
        "stock_minimo",
        "precio_compra",
        "precio_venta",
    ]

    for fila in filas:
        numero = fila.get("_numero_fila", "?")
        codigo_original = fila.get("codigo", "")
        codigo = str(codigo_original).strip()

        #Detecta espacios adicionales y valores de vencimiento en blanco
        hubo_correccion = False

        for campo in persistencia.ENCABEZADOS_INVENTARIO:
            valor = fila.get(campo)

            if valor is not None and valor != valor.strip():
                hubo_correccion = True

        fecha = str(fila.get("fecha_vencimiento") or "").strip()
        if fecha.upper() == "N/A":
            hubo_correccion = True

        if hubo_correccion:
            reporte["corregidos"] += 1
            reporte["detalle"].append(
                "Fila " + str(numero)
                + ": se identificaron espacios adicionales o una fecha N/A."
            )

        #Revisar campos obligatorios.
        campos_vacios = [
            campo for campo in campos_obligatorios
            if fila.get(campo) is None or str(fila[campo]).strip() == ""
        ]

        if campos_vacios:
            reporte["descartados"] += 1
            reporte["detalle"].append(
                "Fila " + str(numero)
                + ": registro incompleto. Campos vacíos: "
                + ", ".join(campos_vacios) + "."
            )
            continue

        #verificar que el codigo este en mayuscula.
        valido, mensaje = producto.validar_codigo(codigo)

        if not valido:
            reporte["marcados"] += 1
            reporte["detalle"].append(
                "Fila " + str(numero) + ": código marcado. " + mensaje
            )

        # Detectar códigos duplicados.
        if codigo in codigos_vistos:
            reporte["duplicados"].setdefault(
                codigo, [codigos_vistos[codigo]]
            ).append(numero)

            reporte["marcados"] += 1
            reporte["detalle"].append(
                "Fila " + str(numero)
                + ": código duplicado " + codigo + "."
            )
        else:
            codigos_vistos[codigo] = numero

        campos_numericos = (
            "stock",
            "stock_minimo",
            "precio_compra",
            "precio_venta",
        )

        numeros_validos = True

        for campo in campos_numericos:
            if not _es_numero(fila.get(campo)):
                numeros_validos = False
                reporte["descartados"] += 1
                reporte["detalle"].append(
                    "Fila " + str(numero)
                    + ": valor numérico inválido en " + campo + "."
                )
                break

        if not numeros_validos:
            continue

        stock = int(float(fila["stock"]))
        stock_minimo = int(float(fila["stock_minimo"]))
        precio_compra = float(fila["precio_compra"])
        precio_venta = float(fila["precio_venta"])

        if stock < 0 or stock_minimo < 0:
            reporte["descartados"] += 1
            reporte["detalle"].append(
                "Fila " + str(numero)
                + ": se encontraron cantidades negativas."
            )
            continue

        if precio_compra < 0 or precio_venta < 0:
            reporte["descartados"] += 1
            reporte["detalle"].append(
                "Fila " + str(numero)
                + ": se encontraron precios negativos."
            )
            continue

        if precio_venta < precio_compra:
            reporte["marcados"] += 1
            reporte["detalle"].append(
                "Fila " + str(numero)
                + ": el precio de venta es menor que el precio de compra."
            )

    for incidencia in incidencias:
        reporte["detalle"].append(incidencia)

    return reporte


def generar_reporte_calidad():
    """Analiza el CSV y muestra el reporte de calidad de datos."""
    reporte = _analizar_inventario()
    consola.mostrar_reporte_calidad(reporte)

    if reporte["duplicados"]:
        consola.mostrar_mensaje(
            "\nSe encontraron códigos repetidos."
        )
        if consola.pedir_confirmacion(
            "¿Desea consolidar los duplicados que tengan los mismos datos?"
        ):
            consolidar_duplicados()


def consolidar_duplicados():
    """
    Consolida registros que tienen el mismo código y los mismos datos,
    excepto el stock. Suma las cantidades y guarda el resultado en el CSV.

    Si los datos de un mismo código son diferentes, no los combina.
    """
    filas, incidencias = persistencia.leer_filas_crudas(
        persistencia.RUTA_INVENTARIO,
        persistencia.ENCABEZADOS_INVENTARIO
    )

    if incidencias:
        for incidencia in incidencias:
            consola.mostrar_error(incidencia)
        return

    grupos = {}
    orden_codigos = []

    for fila in filas:
        codigo = str(fila.get("codigo", "")).strip()

        if codigo not in grupos:
            grupos[codigo] = []
            orden_codigos.append(codigo)

        grupos[codigo].append(fila)

    filas_finales = []
    consolidados = 0

    for codigo in orden_codigos:
        grupo = grupos[codigo]

        if len(grupo) == 1:
            fila = grupo[0]
            filas_finales.append([
                str(fila.get(campo, "") or "").strip()
                for campo in persistencia.ENCABEZADOS_INVENTARIO
            ])
            continue

        #Solo se consolidan códigos válidados y con datos compatibles.
        codigo_valido, _ = producto.validar_codigo(codigo)

        if not codigo_valido:
            for fila in grupo:
                filas_finales.append([
                    str(fila.get(campo, "") or "").strip()
                    for campo in persistencia.ENCABEZADOS_INVENTARIO
                ])
            continue

        try:
            stocks = [int(f["stock"]) for f in grupo]

            if any(stock < 0 for stock in stocks):
                raise ValueError

            # Se compara todo excepto el stock.
            campos_comparar = [
                campo for campo in persistencia.ENCABEZADOS_INVENTARIO
                if campo not in ("stock",)
            ]

            primera = grupo[0]
            compatibles = all(
                all(
                    str(fila.get(campo, "") or "").strip()
                    == str(primera.get(campo, "") or "").strip()
                    for campo in campos_comparar
                )
                for fila in grupo[1:]
            )

            if not compatibles:
                for fila in grupo:
                    filas_finales.append([
                        str(fila.get(campo, "") or "").strip()
                        for campo in persistencia.ENCABEZADOS_INVENTARIO
                    ])
                continue

            fila_consolidada = [
                str(primera.get(campo, "") or "").strip()
                for campo in persistencia.ENCABEZADOS_INVENTARIO
            ]

            indice_stock = persistencia.ENCABEZADOS_INVENTARIO.index("stock")
            fila_consolidada[indice_stock] = str(sum(stocks))

            filas_finales.append(fila_consolidada)
            consolidados += len(grupo) - 1

        except (ValueError, TypeError, KeyError):
            for fila in grupo:
                filas_finales.append([
                    str(fila.get(campo, "") or "").strip()
                    for campo in persistencia.ENCABEZADOS_INVENTARIO
                ])

    if consolidados == 0:
        consola.mostrar_mensaje(
            "No se encontraron duplicados compatibles para consolidar."
        )
        return

    try:
        persistencia.escribir_csv(
            persistencia.RUTA_INVENTARIO,
            persistencia.ENCABEZADOS_INVENTARIO,
            filas_finales
        )

        productos, incidencias = persistencia.leer_inventario()
        producto.cargar_catalogo(productos)

        consola.mostrar_exito(
            "Se consolidaron " + str(consolidados)
            + " registros duplicados."
        )

        for incidencia in incidencias:
            consola.mostrar_error(incidencia)

    except OSError as error:
        consola.mostrar_error(
            "No se pudo guardar la consolidación: " + str(error)
        )


def _ventas_por_categoria():
    """Suma el total de cada venta por categoría, cruzando con el catálogo."""
    categorias = {p["codigo"]: p["categoria"] for p in producto.obtener_productos()}
    totales = {}
    for una_venta in venta.obtener_ventas():
        for item in una_venta["productos_vendidos"]:
            categoria = categorias.get(item["codigo"], "Sin categoría")
            totales[categoria] = round(totales.get(categoria, 0) + item["total"], 2)
    return totales


def _productos_criticos():
    """Productos agotados o en/bajo el mínimo, los más urgentes primero."""
    criticos = [p for p in producto.obtener_productos()
                if producto.estado_stock(p) != "disponible"]
    return sorted(criticos, key=lambda p: p["stock"] - p["stock_minimo"])


def generar_reporte_graficos():
    """Menú de gráficos: muestra y guarda los .png en evidencias/graficos/."""
    while True:
        consola.mostrar_menu_graficos()
        opcion = consola.pedir_opcion_menu()

        if opcion == "4":
            return

        try:
            if opcion == "1":
                graficos.grafico_ventas_por_categoria(
                    _ventas_por_categoria(),
                    os.path.join(CARPETA_GRAFICOS, "ventas_por_categoria.png"))
            elif opcion == "2":
                graficos.grafico_stock_critico(
                    _productos_criticos(),
                    os.path.join(CARPETA_GRAFICOS, "stock_critico.png"))
            elif opcion == "3":
                graficos.grafico_distribucion_ventas(
                    _ventas_por_categoria(),
                    os.path.join(CARPETA_GRAFICOS, "distribucion_ventas.png"))
            else:
                consola.mostrar_error("Opción no válida.")
        except ValueError as error:  # no hay datos para graficar
            consola.mostrar_error(str(error))
        except ImportError:
            consola.mostrar_error("matplotlib no está instalado. "
                                  "Ejecute: pip install -r requirements.txt")
        except OSError as error:
            consola.mostrar_error("No se pudo guardar el gráfico: " + str(error))
