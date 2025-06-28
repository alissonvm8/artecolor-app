, on_bad_lines='skip'

import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página
st.set_page_config(layout="wide", page_title="Dashboard Arte Color", page_icon=":bar_chart:")

# Cargar datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("BDD_ArteColor_Ventas.csv", parse_dates=["venta_fecha"])
    df["mes"] = df["venta_fecha"].dt.month
    df["año"] = df["venta_fecha"].dt.year
    return df

df = cargar_datos()

# Filtros
años_disponibles = sorted(df["año"].unique(), reverse=True)
años_opciones = ["Todos"] + [str(a) for a in años_disponibles]
año_seleccionado = st.sidebar.selectbox("Seleccionar Año", años_opciones)

mes_seleccionado = None
if año_seleccionado != "Todos":
    meses_disponibles = sorted(df[df["año"] == int(año_seleccionado)]["mes"].unique())
    mes_seleccionado = st.sidebar.selectbox("Seleccionar Mes", meses_disponibles)
else:
    st.sidebar.selectbox("Seleccionar Mes", ["(Seleccione un año)"], disabled=True)

# Filtrar datos según selección
if año_seleccionado == "Todos":
    df_anual = df.copy()
else:
    df_anual = df[df["año"] == int(año_seleccionado)]
    if mes_seleccionado:
        df_filtrado = df_anual[df_anual["mes"] == int(mes_seleccionado)]
    else:
        df_filtrado = df_anual.copy()

# Gráfico 1: Ventas por mes (líneas)
st.title("📊 Dashboard de Ventas - Arte Color")
st.subheader("1. Ventas Totales por Mes")
ventas_por_mes = df_anual.groupby("mes")["detalle_valor_total"].sum().reset_index()
fig1 = px.line(ventas_por_mes, x="mes", y="detalle_valor_total", markers=True,
               labels={"mes": "Mes", "detalle_valor_total": "Ventas ($)"})
st.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: Ventas por sucursal (barras)
st.subheader("2. Ventas por Sucursal")
if año_seleccionado == "Todos":
    datos_sucursal = df_anual.copy()
else:
    datos_sucursal = df_filtrado.copy()

ventas_sucursal = datos_sucursal.groupby("sucursal_nombre")["detalle_valor_total"].sum().reset_index()
fig2 = px.bar(ventas_sucursal, x="sucursal_nombre", y="detalle_valor_total",
              labels={"sucursal_nombre": "Sucursal", "detalle_valor_total": "Ventas ($)"},
              color_discrete_sequence=["skyblue"])
fig2.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig2, use_container_width=True)

# Gráfico 3: Productos más vendidos
st.subheader("3. Productos Más Vendidos")
ventas_productos = datos_sucursal.groupby("producto_nombre")["detalle_valor_total"].sum().nlargest(10).reset_index()
fig3 = px.bar(ventas_productos, x="producto_nombre", y="detalle_valor_total",
              labels={"producto_nombre": "Producto", "detalle_valor_total": "Ventas ($)"},
              color_discrete_sequence=["lightgreen"])
fig3.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig3, use_container_width=True)

# Gráfico 4: Clientes principales por monto total
st.subheader("4. Clientes con Mayor Monto de Compra")
ventas_clientes = datos_sucursal.groupby("cliente_nombre")["detalle_valor_total"].sum().nlargest(10).reset_index()
fig4 = px.bar(ventas_clientes, x="cliente_nombre", y="detalle_valor_total",
              labels={"cliente_nombre": "Cliente", "detalle_valor_total": "Ventas ($)"},
              color_discrete_sequence=["salmon"])
fig4.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig4, use_container_width=True)




