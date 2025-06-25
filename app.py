import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt

# Configuración general
st.set_page_config(page_title="Dashboard de Ventas - Arte Color", layout="wide")

# Título
st.title("📊 Dashboard de Ventas - Arte Color")

# Cargar datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("ventas_artecolor.csv", parse_dates=['venta_fecha'])
    df['mes'] = df['venta_fecha'].dt.to_period('M').astype(str)
    df['anio'] = df['venta_fecha'].dt.year
    df['trimestre'] = df['venta_fecha'].dt.to_period("Q").astype(str)
    df['semestre'] = df['venta_fecha'].dt.month.apply(lambda x: 1 if x <= 6 else 2)
    return df

df = cargar_datos()

# Barra lateral
st.sidebar.header("Filtros")
sucursal = st.sidebar.selectbox("Seleccionar sucursal", options=["Todas"] + sorted(df["sucursal_nombre"].unique()))
periodo = st.sidebar.selectbox("Filtrar por:", ["Año", "Trimestre", "Mes"])

# Filtro por sucursal
if sucursal != "Todas":
    df = df[df["sucursal_nombre"] == sucursal]

# Agrupación por periodo
if periodo == "Año":
    agrupado = df.groupby("anio")["detalle_valor_total"].sum().reset_index()
    x_col = "anio"
elif periodo == "Trimestre":
    agrupado = df.groupby("trimestre")["detalle_valor_total"].sum().reset_index()
    x_col = "trimestre"
else:
    agrupado = df.groupby("mes")["detalle_valor_total"].sum().reset_index()
    x_col = "mes"

# KPIs
total_ventas = df["detalle_valor_total"].sum()
total_transacciones = df["venta_numero"].nunique()
ticket_promedio = total_ventas / total_transacciones if total_transacciones else 0

col1, col2, col3 = st.columns(3)
col1.metric("💰 Ventas totales", f"${total_ventas:,.2f}")
col2.metric("🧾 Nº Transacciones", total_transacciones)
col3.metric("📌 Ticket Promedio", f"${ticket_promedio:,.2f}")

# Gráfico de ventas por periodo
st.subheader("📈 Evolución de Ventas")
fig_ventas = px.line(agrupado, x=x_col, y="detalle_valor_total", markers=True, labels={"detalle_valor_total": "Ventas"})
st.plotly_chart(fig_ventas, use_container_width=True)

# Ventas por sucursal
st.subheader("🏪 Comparación por Sucursal")
ventas_sucursal = df.groupby("sucursal_nombre")["detalle_valor_total"].sum().reset_index()
fig_sucursal = px.bar(ventas_sucursal, x="sucursal_nombre", y="detalle_valor_total", labels={"detalle_valor_total": "Ventas"})
st.plotly_chart(fig_sucursal, use_container_width=True)

# Productos más vendidos
st.subheader("🛒 Productos más vendidos")
top_productos = df.groupby("producto_nombre")["detalle_cantidad"].sum().nlargest(10).reset_index()
fig_productos = px.bar(top_productos, x="detalle_cantidad", y="producto_nombre", orientation="h", labels={"detalle_cantidad": "Cantidad"})
st.plotly_chart(fig_productos, use_container_width=True)

# Marcas más vendidas por valor
st.subheader("🏷️ Marcas con mayor facturación")
top_marcas = df.groupby("marca_nombre")["detalle_valor_total"].sum().nlargest(10).reset_index()
fig_marcas = px.bar(top_marcas, x="detalle_valor_total", y="marca_nombre", orientation="h", labels={"detalle_valor_total": "Valor total"})
st.plotly_chart(fig_marcas, use_container_width=True)

# Clientes frecuentes
st.subheader("👥 Clientes frecuentes por monto comprado")
top_clientes = df.groupby("cliente_nombre")["detalle_valor_total"].sum().nlargest(10).reset_index()
fig_clientes = alt.Chart(top_clientes).mark_bar().encode(
    x=alt.X("detalle_valor_total:Q", title="Total comprado"),
    y=alt.Y("cliente_nombre:N", sort='-x', title="Cliente")
).properties(height=400)
st.altair_chart(fig_clientes, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("🔧 *Prototipo de visualización desarrollado para la tesis de Ingeniería en Sistemas - Arte Color*")


