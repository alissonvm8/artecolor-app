import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Arte Color", layout="wide")

st.title("📊 Dashboard Comercial - Arte Color")

# Cargar los datos
@st.cache_data
def cargar_datos():
    return pd.read_csv("detalle_ventas.csv", parse_dates=["venta_fecha"])

df = cargar_datos()

# Filtro por año
df["Año"] = df["venta_fecha"].dt.year
año_seleccionado = st.selectbox("Selecciona el año", sorted(df["Año"].unique(), reverse=True))

df_filtrado = df[df["Año"] == año_seleccionado]

# Ventas por mes
df_filtrado["Mes"] = df_filtrado["venta_fecha"].dt.strftime('%B')
ventas_mes = df_filtrado.groupby("Mes")["detalle_valor_total"].sum().reset_index()

fig1 = px.bar(ventas_mes, x="Mes", y="detalle_valor_total", title="Ventas por Mes")
st.plotly_chart(fig1, use_container_width=True)

# Top 5 productos más vendidos
top_productos = df_filtrado.groupby("producto_nombre")["detalle_cantidad"].sum().reset_index().sort_values(by="detalle_cantidad", ascending=False).head(5)

fig2 = px.bar(top_productos, x="producto_nombre", y="detalle_cantidad", title="Top 5 productos más vendidos")
st.plotly_chart(fig2, use_container_width=True)
