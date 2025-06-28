# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# Título de la app
st.title("Dashboard de Ventas - Arte Color")
st.subheader("Visualización de indicadores clave de ventas")

# Cargar datos
@st.cache_data
def cargar_datos():
    return pd.read_csv("BDD_ArteColor_Ventas.csv", parse_dates=["venta_fecha"])

df = cargar_datos()

# Preprocesamiento
df['mes'] = df['venta_fecha'].dt.to_period('M').astype(str)
ventas_por_mes = df.groupby('mes')['detalle_valor_total'].sum().reset_index()

# Gráfico de barras
fig = px.bar(ventas_por_mes, x='mes', y='detalle_valor_total',
             labels={'mes': 'Mes', 'detalle_valor_total': 'Ventas Totales ($)'},
             title='Ventas Totales por Mes',
             color='detalle_valor_total')

st.plotly_chart(fig)

# Mostrar tabla si se desea
if st.checkbox("Mostrar tabla de datos"):
    st.dataframe(ventas_por_mes)

