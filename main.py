import os

#Colores
COLOR_PRINCIPAL = "#1B6F78"    # verde azulado (barras principales)
COLOR_SECUNDARIO = "#274060"   # azul oscuro (stock mínimo)
COLOR_ALERTA = "#E4572E"       # rojo anaranjado (stock actual)
COLOR_GRILLA = "#E3E8EA"       # gris claro (líneas de fondo)
COLORES_CATEGORIAS = ["#1B6F78", "#E4572E", "#274060", "#C28E0E",
                      "#3F8F5F", "#7B5E7B", "#2E86AB", "#6B7A8F"]

# en el gráfico de stock crítico se muestran como máximo estos productos
MAX_PRODUCTOS_CRITICOS = 12

#Funciones de apoyo

def cargar_pyplot():
    import matplotlib.pyplot as plt
    return plt
#Se importa matplotlib
def formato_miles(valor,posicion):
    return "{:,.0f}".format(valor)
#Se pone el separador de miles en los numeros
def guardar_o_mostrar(fig, ruta_png, mostrar):
    #Se guarda el grafico como png y si hay ruta lo muestra y lo cierra
    plt = cargar_pyplot()
    fig.tight_layout()
    if ruta_png:
        carpeta = os.path.dirname(ruta_png)
        if carpeta:
            os.makedirs(carpeta, exist_ok=True)
        fig.savefig(ruta_png,dpi=150, bbox_inches="tight")
    if mostrar:
        plt.show()
    plt.close(fig)

#Grafico 1:VENTAS TOTALES POR CATEGORIA  
   
def grafico_ventas_por_categoria(ventas_por_categoria, ruta_png=None, mostrar=True):
    if len(ventas_por_categoria) == 0:
        raise ValueError("No hay datos de ventas para graficar.")

    from matplotlib.ticker import FuncFormatter
    plt = cargar_pyplot()

    categorias = list(ventas_por_categoria.keys())
    totales = list(ventas_por_categoria.values())

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.bar(categorias, totales, color=COLOR_PRINCIPAL, label="Total de ventas", zorder=3)

    for i in range(len(categorias)):
        ax.text(i, totales[i], "{:,.0f}".format(totales[i]),
                ha="center", va="bottom", fontsize=9)

    ax.set_title("Ventas totales por categoría de producto", fontsize=14, fontweight="bold")
    ax.set_xlabel("Categoría")
    ax.set_ylabel("Ventas totales (₡)")
    ax.yaxis.set_major_formatter(FuncFormatter(formato_miles))
    ax.grid(axis="y", color=COLOR_GRILLA, zorder=0)
    ax.set_axisbelow(True)
    ax.margins(y=0.12)
    if len(categorias) > 4:
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    ax.legend(loc="upper right")

    guardar_o_mostrar(fig, ruta_png, mostrar)

#Grafico 2:Stock actual y minimo

def grafico_stock_critico(productos_criticos, ruta_png=None, mostrar=True):
    if len(productos_criticos) == 0:
        raise ValueError("No hay productos con existencias críticas para graficar.")

    plt = cargar_pyplot()
    productos = productos_criticos[:MAX_PRODUCTOS_CRITICOS]

    nombres = []
    actual = []
    minimo = []
    for p in productos:
        nombres.append(str(p["nombre"]))
        actual.append(p["stock"])
        minimo.append(p["stock_minimo"])

    posiciones = list(range(len(productos)))
    alto = 0.38 

    fig, ax = plt.subplots(figsize=(9, max(4.5, 0.65 * len(productos) + 2)))
    arriba = []
    abajo = []
    for y in posiciones:
        arriba.append(y - alto / 2)
        abajo.append(y + alto / 2)
    ax.barh(arriba, actual, height=alto, color=COLOR_ALERTA, label="Stock actual", zorder=3)
    ax.barh(abajo, minimo, height=alto, color=COLOR_SECUNDARIO, label="Stock mínimo", zorder=3)

    for i in range(len(productos)):
        ax.text(actual[i], arriba[i], " " + "{:g}".format(actual[i]), va="center", fontsize=8)
        ax.text(minimo[i], abajo[i], " " + "{:g}".format(minimo[i]), va="center", fontsize=8)
    ax.set_yticks(posiciones)
    ax.set_yticklabels(nombres)
    ax.invert_yaxis()   
    ax.set_title("Productos con existencias críticas: stock actual vs. stock mínimo",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Unidades")
    ax.set_ylabel("Producto")
    ax.grid(axis="x", color=COLOR_GRILLA, zorder=0)
    ax.set_axisbelow(True)
    ax.margins(x=0.1)
    ax.legend(loc="lower right")
    guardar_o_mostrar(fig, ruta_png, mostrar)

#Grafico 3:Distribucion de ventas por categoria

def grafico_distribucion_ventas(ventas_por_categoria, ruta_png=None, mostrar=True):
    categorias = []
    totales = []
    for categoria in ventas_por_categoria:
        if ventas_por_categoria[categoria] > 0:
            categorias.append(categoria)
            totales.append(ventas_por_categoria[categoria])
    if len(totales) == 0:
        raise ValueError("No hay datos de ventas para graficar.")

    plt = cargar_pyplot()

    colores = []
    for i in range(len(categorias)):
        colores.append(COLORES_CATEGORIAS[i % len(COLORES_CATEGORIAS)])
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    porciones, textos, porcentajes = ax.pie(
        totales, colors=colores, autopct="%1.1f%%", startangle=90, pctdistance=0.78,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
        textprops={"color": "white", "fontsize": 10, "fontweight": "bold"})
    ax.legend(porciones, categorias, title="Categoría", loc="center left",
              bbox_to_anchor=(1.0, 0.5))
    ax.set_title("Distribución porcentual de las ventas por categoría",
                 fontsize=14, fontweight="bold")
    ax.axis("equal")

    guardar_o_mostrar(fig, ruta_png, mostrar)
