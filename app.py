import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Arte Color", layout="wide")
st.title("📊 Dashboard de Ventas - Arte Color")

# Cargar datos
@st.cache_data
def cargar_datos():
    return pd.read_csv("BDD_ArteColor_Ventas.csv", parse_dates=["venta_fecha"])

try:
    df = cargar_datos()
    df['mes'] = df['venta_fecha'].dt.to_period('M').astype(str)

    # Agrupar por mes
    ventas_por_mes = df.groupby('mes')['detalle_valor_total'].sum().reset_index()

    # Gráfico
    fig = px.bar(ventas_por_mes, x='mes', y='detalle_valor_total',
                 labels={'mes': 'Mes', 'detalle_valor_total': 'Ventas Totales ($)'},
                 title='Ventas Totales por Mes')

    st.plotly_chart(fig)

    # Opción para mostrar tabla
    if st.checkbox("Mostrar tabla de datos"):
        st.dataframe(ventas_por_mes)

except FileNotFoundError:
    st.error("❌ Error: No se encontró el archivo 'BDD_ArteColor_Ventas.csv'. Asegúrate de que esté en el repositorio y se llame exactamente así.")


