import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components

st.set_page_config(page_title="Dashboard Arte Color", layout="wide")
st.title("📊 Dashboard Comercial - Arte Color")

@st.cache_data
def cargar_datos():
    return pd.read_csv("BDD_ArteColor_Ventas.csv", parse_dates=["venta_fecha"])

df = cargar_datos()

# Asegurar tipos y columnas auxiliares
df['sucursal_nombre'] = df['sucursal_nombre'].astype(str)
df['año'] = df['venta_fecha'].dt.year
df['mes'] = df['venta_fecha'].dt.month
df['mes_nombre'] = df['venta_fecha'].dt.strftime('%B')  # nombre completo del mes

# Diccionario de meses en español
nombre_meses = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}
nombre_a_numero = {v: k for k, v in nombre_meses.items()}


# Sidebar: filtros
with st.sidebar:
    # Filtro de sucursal
    sucursales_disponibles = sorted(df['sucursal_nombre'].unique())
    sucursal_seleccionada = st.selectbox("Selecciona la sucursal", ["Todas las sucursales"] + sucursales_disponibles)

    # Filtro de año
    años_disponibles = sorted(df['año'].unique())
    año_seleccionado = st.selectbox("Selecciona el año", ["Todos los años"] + años_disponibles)

    # Filtro de mes (con nombres y opción predeterminada)
    if año_seleccionado != "Todos los años":
        df_anyo = df[df['año'] == año_seleccionado]
        meses_disponibles = sorted(df_anyo['mes'].unique())
        meses_nombres = [nombre_meses[m] for m in meses_disponibles]
        mes_nombre_a_numero = {v: k for k, v in nombre_meses.items()}

        mes_nombre_seleccionado = st.selectbox("Selecciona el mes", ["Todos los meses"] + meses_nombres)
        if mes_nombre_seleccionado != "Todos los meses":
            mes_seleccionado = mes_nombre_a_numero[mes_nombre_seleccionado]
        else:
            mes_seleccionado = None
    else:
        mes_seleccionado = None

    # Chatbot integrado
    st.markdown("---")
    st.markdown("### 🤖 Asistente de Ventas")
    st.markdown("Haz tus preguntas sobre ventas, productos o clientes usando lenguaje natural.")
    components.iframe(
        src="https://www.stack-ai.com/embed/9b857357-678c-4dfd-b342-88b2b127154a/9c2cd531-7214-48e1-b26c-f360eee236d4/685d6e70733ab95a834b5b67",
        height=600,
        width=300
    )


# Aplicar filtros
if año_seleccionado != "Todos los años":
    df_anual = df[df['año'] == año_seleccionado]
    df_filtrado = df_anual.copy()
    if mes_seleccionado:
        df_filtrado = df_filtrado[df_filtrado['mes'] == mes_seleccionado]
else:
    df_anual = df.copy()
    df_filtrado = df.copy()

if sucursal_seleccionada != "Todas las sucursales":
    df_anual = df_anual[df_anual['sucursal_nombre'] == sucursal_seleccionada]
    df_filtrado = df_filtrado[df_filtrado['sucursal_nombre'] == sucursal_seleccionada]

# KPIs
st.markdown("### Indicadores Clave")
ventas_totales = df_filtrado['detalle_valor_total'].sum()
transacciones = df_filtrado['venta_numero'].nunique()
ticket = ventas_totales / transacciones if transacciones else 0
clientes_unicos = df_filtrado['cliente_nombre'].nunique()
unidades_vendidas = df_filtrado['detalle_cantidad'].sum()

col1, col2, col3, col4, col5 = st.columns([1.3, 0.8, 0.8, 0.8, 0.8])

with col1:
    st.metric("Ventas Totales", f"${ventas_totales:,.2f}")
with col2:
    st.metric("N° Transacciones", transacciones)
with col3:
    st.metric("Ticket Promedio", f"${ticket:,.2f}")
with col4:
    st.metric("Clientes Únicos", clientes_unicos)
with col5:
    st.metric("Unidades Vendidas", f"{unidades_vendidas:,}")

# --- Gráfico 1: Ventas Totales por Mes o Día
st.subheader("📈 Ventas Totales")

if año_seleccionado == "Todos":
    if sucursal_seleccionada == "Todas":
        ventas_agrupadas = df_filtrado.groupby(['año', 'mes', 'sucursal_nombre'])['detalle_valor_total'].sum().reset_index()
        fig1 = px.line(ventas_agrupadas, x='mes', y='detalle_valor_total', color='sucursal_nombre',
                       facet_col='año',
                       labels={'mes': 'Mes', 'detalle_valor_total': 'Ventas ($)', 'sucursal_nombre': 'Sucursal'})
    else:
        ventas_agrupadas = df_filtrado.groupby(['año', 'mes'])['detalle_valor_total'].sum().reset_index()
        fig1 = px.line(ventas_agrupadas, x='mes', y='detalle_valor_total', color='año',
                       labels={'mes': 'Mes', 'detalle_valor_total': 'Ventas ($)', 'año': 'Año'})
else:
    if mes_seleccionado is None:
        if sucursal_seleccionada == "Todas":
            ventas_agrupadas = df_filtrado.groupby(['mes', 'sucursal_nombre'])['detalle_valor_total'].sum().reset_index()
            fig1 = px.line(ventas_agrupadas, x='mes', y='detalle_valor_total', color='sucursal_nombre',
                           labels={'mes': 'Mes', 'detalle_valor_total': 'Ventas ($)', 'sucursal_nombre': 'Sucursal'})
        else:
            ventas_agrupadas = df_filtrado.groupby('mes')['detalle_valor_total'].sum().reset_index()
            fig1 = px.line(ventas_agrupadas, x='mes', y='detalle_valor_total',
                           labels={'mes': 'Mes', 'detalle_valor_total': 'Ventas ($)'})
    else:
        ventas_diarias = df_filtrado.groupby(df_filtrado['venta_fecha'].dt.day)['detalle_valor_total'].sum().reset_index()
        ventas_diarias.columns = ['día', 'detalle_valor_total']
        fig1 = px.bar(ventas_diarias, x='día', y='detalle_valor_total',
                      labels={'día': 'Día del Mes', 'detalle_valor_total': 'Ventas ($)'})
        
st.plotly_chart(fig1, use_container_width=True)

# --- Gráfico 2: Top 10 Productos Más Vendidos por Valor
st.subheader("Top 10 Productos por Valor")
productos_top = df_filtrado.groupby('producto_nombre')['detalle_valor_total'].sum().reset_index()
productos_top = productos_top.sort_values(by='detalle_valor_total', ascending=False).head(10)
fig3 = px.bar(productos_top, x='detalle_valor_total', y='producto_nombre',
              orientation='h', labels={'detalle_valor_total': 'Ventas ($)', 'producto_nombre': 'Producto'})
st.plotly_chart(fig3, use_container_width=True)

# --- Gráfico 3: Top 10 Productos por Cantidad
st.subheader(" Top 10 Productos por Cantidad Vendida")
productos_cantidad = df_filtrado.groupby('producto_nombre')['detalle_cantidad'].sum().reset_index()
productos_cantidad = productos_cantidad.sort_values(by='detalle_cantidad', ascending=False).head(10)
fig4 = px.bar(productos_cantidad, x='detalle_cantidad', y='producto_nombre',
              orientation='h', labels={'detalle_cantidad': 'Cantidad', 'producto_nombre': 'Producto'})
st.plotly_chart(fig4, use_container_width=True)

# --- Gráfico 4: Clientes con Mayor Monto Comprado
st.subheader("👤 Clientes con Mayor Monto Comprado")
clientes_top = df_filtrado.groupby('cliente_nombre')['detalle_valor_total'].sum().reset_index()
clientes_top = clientes_top.sort_values(by='detalle_valor_total', ascending=False).head(10)
fig5 = px.bar(clientes_top, x='detalle_valor_total', y='cliente_nombre',
              orientation='h', labels={'detalle_valor_total': 'Compras ($)', 'cliente_nombre': 'Cliente'})
st.plotly_chart(fig5, use_container_width=True)

# --- Gráfico 5: Clientes Más Frecuentes por Cantidad Comprada
st.subheader("👥 Clientes Más Frecuentes por Cantidad Comprada")
clientes_frecuentes = df_filtrado.groupby('cliente_nombre')['detalle_cantidad'].sum().reset_index()
clientes_frecuentes = clientes_frecuentes.sort_values(by='detalle_cantidad', ascending=False).head(10)
fig6 = px.bar(clientes_frecuentes, x='detalle_cantidad', y='cliente_nombre',
              orientation='h', labels={'detalle_cantidad': 'Cantidad', 'cliente_nombre': 'Cliente'})
st.plotly_chart(fig6, use_container_width=True)





