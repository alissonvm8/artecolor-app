
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Arte Color", layout="wide")
st.title("📊 Dashboard Comercial - Arte Color")

@st.cache_data
def cargar_datos():
    return pd.read_csv("BDD_ArteColor_Ventas.csv", parse_dates=["venta_fecha"], on_bad_lines='skip')

df = cargar_datos()

# Columnas auxiliares
df['año'] = df['venta_fecha'].dt.year
df['mes'] = df['venta_fecha'].dt.month
df['mes_nombre'] = df['venta_fecha'].dt.strftime('%b')

# --- Filtros ---
años_disponibles = sorted(df['año'].unique())
año_seleccionado = st.sidebar.selectbox("Selecciona el año", ["Todos"] + años_disponibles)

if año_seleccionado == "Todos":
    df_anual = df.copy()
    df_filtrado = df.copy()
    mes_seleccionado = None
    st.sidebar.selectbox("Selecciona el mes", ["(Seleccione un año específico)"], disabled=True)
else:
    df_anual = df[df['año'] == año_seleccionado]
    meses_disponibles = sorted(df_anual['mes'].unique())
    mes_seleccionado = st.sidebar.selectbox("Selecciona el mes", meses_disponibles)
    df_filtrado = df_anual[df_anual['mes'] == mes_seleccionado]

# --- Gráfico 1: Ventas Totales por Mes
st.subheader("📈 Ventas Totales por Mes")
if año_seleccionado == "Todos":
    ventas_mensuales = df.groupby(['año', df['venta_fecha'].dt.month]).agg({'detalle_valor_total': 'sum'}).reset_index()
    ventas_mensuales.columns = ['año', 'mes', 'detalle_valor_total']
    fig1 = px.line(ventas_mensuales, x='mes', y='detalle_valor_total', color='año',
                   labels={'mes': 'Mes', 'detalle_valor_total': 'Ventas ($)', 'año': 'Año'})
else:
    ventas_mensuales = df_anual.groupby(df_anual['venta_fecha'].dt.to_period('M')).agg({'detalle_valor_total': 'sum'}).reset_index()
    ventas_mensuales['venta_fecha'] = ventas_mensuales['venta_fecha'].astype(str)
    fig1 = px.line(ventas_mensuales, x='venta_fecha', y='detalle_valor_total',
                   labels={'venta_fecha': 'Mes', 'detalle_valor_total': 'Ventas ($)'})
st.plotly_chart(fig1, use_container_width=True)

# --- KPIs
st.markdown("### 📌 Indicadores Clave")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Ventas Totales", f"${df_anual['detalle_valor_total'].sum():,.2f}")
with col2:
    transacciones = df_anual['venta_numero'].nunique()
    st.metric("N° Transacciones", transacciones)
with col3:
    ticket = df_anual['detalle_valor_total'].sum() / transacciones if transacciones else 0
    st.metric("Ticket Promedio", f"${ticket:,.2f}")

# --- Gráfico 2: Ventas por Sucursal
st.subheader("🏬 Ventas por Sucursal")
ventas_sucursal = df_filtrado[df_filtrado['sucursal_nombre'].notna()]\
    .groupby('sucursal_nombre')['detalle_valor_total'].sum().reset_index()
fig2 = px.bar(ventas_sucursal, x='sucursal_nombre', y='detalle_valor_total',
              labels={'sucursal_nombre': 'Sucursal', 'detalle_valor_total': 'Ventas ($)'})
st.plotly_chart(fig2, use_container_width=True)

# --- Gráfico 3: Top 10 Productos Más Vendidos
st.subheader("📦 Top 10 Productos Más Vendidos por Valor")
productos_top = df_filtrado.groupby('producto_nombre')['detalle_valor_total'].sum().reset_index()
productos_top = productos_top.sort_values(by='detalle_valor_total', ascending=False).head(10)
fig3 = px.bar(productos_top, x='detalle_valor_total', y='producto_nombre',
              orientation='h', labels={'detalle_valor_total': 'Ventas ($)', 'producto_nombre': 'Producto'})
st.plotly_chart(fig3, use_container_width=True)

# --- Gráfico 4: Clientes con Mayor Monto Comprado
st.subheader("👤 Clientes con Mayor Monto Comprado")
clientes_top = df_anual.groupby('cliente_nombre')['detalle_valor_total'].sum().reset_index()
clientes_top = clientes_top.sort_values(by='detalle_valor_total', ascending=False).head(10)
fig4 = px.bar(clientes_top, x='detalle_valor_total', y='cliente_nombre',
              orientation='h', labels={'detalle_valor_total': 'Compras ($)', 'cliente_nombre': 'Cliente'})
st.plotly_chart(fig4, use_container_width=True)
