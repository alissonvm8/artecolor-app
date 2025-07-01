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

# Columnas auxiliares
df['año'] = df['venta_fecha'].dt.year
df['mes'] = df['venta_fecha'].dt.month
df['mes_nombre'] = df['venta_fecha'].dt.strftime('%b')

# Sidebar: Filtros y Chatbot
años_disponibles = sorted(df['año'].unique())
nombre_meses = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}
nombre_a_numero = {v: k for k, v in nombre_meses.items()}  # inverso para filtrar

with st.sidebar:
    año_seleccionado = st.selectbox("Selecciona el año", ["Todos"] + años_disponibles)

    if año_seleccionado != "Todos":
        meses_disponibles = sorted(df[df['año'] == año_seleccionado]['mes'].unique())
        opciones_meses = ["Todos"] + [nombre_meses[m] for m in meses_disponibles]
        mes_nombre_seleccionado = st.selectbox("Selecciona el mes", opciones_meses)

        # Convertimos el nombre del mes a número si no es "Todos"
        if mes_nombre_seleccionado != "Todos":
            mes_seleccionado = nombre_a_numero[mes_nombre_seleccionado]
        else:
            mes_seleccionado = None
    else:
        mes_seleccionado = None

    st.markdown("---")
    st.markdown("###  Asistente de Ventas")
    st.markdown("Haz tus preguntas sobre ventas, productos o clientes usando lenguaje natural.")
    components.iframe(
        src="https://www.stack-ai.com/embed/9b857357-678c-4dfd-b342-88b2b127154a/9c2cd531-7214-48e1-b26c-f360eee236d4/685d6e70733ab95a834b5b67",
        height=600,
        width=400
    )


# Filtrado de datos
if año_seleccionado != "Todos":
    df_anual = df[df['año'] == año_seleccionado]
    if mes_seleccionado:
        df_filtrado = df_anual[df_anual['mes'] == mes_seleccionado]
    else:
        df_filtrado = df_anual.copy()
else:
    df_anual = df.copy()
    df_filtrado = df.copy()


# --- KPIs considerando año y mes (df_filtrado)
st.markdown("### Indicadores Clave")

ventas_totales = df_filtrado['detalle_valor_total'].sum()
transacciones = df_filtrado['venta_numero'].nunique()
ticket = ventas_totales / transacciones if transacciones else 0
clientes_unicos = df_filtrado['cliente_nombre'].nunique()
unidades_vendidas = df_filtrado['detalle_cantidad'].sum()

# Mostrar los KPIs en una sola fila
col1, , col2, col3, col4, col5 = st.columns([1.3, 0.8, 0.8, 0.8, 0.8])



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


# --- Gráfico 1: Ventas Totales por Mes
st.subheader("Ventas Totales por Mes")
if año_seleccionado == "Todos":
    ventas_mensuales = df.groupby(['año', df['venta_fecha'].dt.month]).agg({'detalle_valor_total': 'sum'}).reset_index()
    ventas_mensuales.columns = ['año', 'mes', 'detalle_valor_total']
    fig1 = px.line(ventas_mensuales, x='mes', y='detalle_valor_total', color='año',
                   labels={'mes': 'Mes', 'detalle_valor_total': 'Ventas ($)', 'año': 'Año'})
else:
    if mes_seleccionado:
        df_mes = df_anual[df_anual['mes'] == mes_seleccionado]
        total_mes = df_mes.groupby(df_mes['venta_fecha'].dt.day).agg({'detalle_valor_total': 'sum'}).reset_index()
        total_mes.columns = ['día', 'detalle_valor_total']
        fig1 = px.bar(total_mes, x='día', y='detalle_valor_total',
                      labels={'día': 'Día del Mes', 'detalle_valor_total': 'Ventas ($)'},
                      title=f"Ventas Diarias - {mes_seleccionado}/{año_seleccionado}")
    else:
        ventas_mensuales = df_anual.groupby(df_anual['venta_fecha'].dt.month).agg({'detalle_valor_total': 'sum'}).reset_index()
        ventas_mensuales.columns = ['mes', 'detalle_valor_total']
        fig1 = px.line(ventas_mensuales, x='mes', y='detalle_valor_total',
                       labels={'mes': 'Mes', 'detalle_valor_total': 'Ventas ($)'})
st.plotly_chart(fig1, use_container_width=True)


# --- Gráfico 2: Ventas por Sucursal
st.subheader("Ventas por Sucursal")
ventas_sucursal = df_filtrado.groupby('sucursal_nombre')['detalle_valor_total'].sum().reset_index()
fig2 = px.bar(ventas_sucursal, x='sucursal_nombre', y='detalle_valor_total',
              labels={'sucursal_nombre': 'Sucursal', 'detalle_valor_total': 'Ventas ($)'})
st.plotly_chart(fig2, use_container_width=True)

# --- Gráfico 4: Clientes con Mayor Monto Comprado
st.subheader("Clientes con Mayor Monto Comprado")
if año_seleccionado != "Todos":
    clientes_top = df_filtrado.groupby('cliente_nombre')['detalle_valor_total'].sum().reset_index()
else:
    clientes_top = df_anual.groupby('cliente_nombre')['detalle_valor_total'].sum().reset_index()

clientes_top = clientes_top.sort_values(by='detalle_valor_total', ascending=False).head(10)
fig4 = px.bar(clientes_top, x='detalle_valor_total', y='cliente_nombre',
              orientation='h', labels={'detalle_valor_total': 'Compras ($)', 'cliente_nombre': 'Cliente'})
st.plotly_chart(fig4, use_container_width=True)

# --- Gráfico 6: Clientes Más Frecuentes (por cantidad comprada)
st.subheader("👥 Clientes Más Frecuentes por Cantidad Comprada")
clientes_frecuentes = df_filtrado.groupby('cliente_nombre')['detalle_cantidad'].sum().reset_index()
clientes_frecuentes = clientes_frecuentes.sort_values(by='detalle_cantidad', ascending=False).head(10)
fig7 = px.bar(clientes_frecuentes, x='detalle_cantidad', y='cliente_nombre',
              orientation='h', labels={'detalle_cantidad': 'Cantidad Comprada', 'cliente_nombre': 'Cliente'})
st.plotly_chart(fig7, use_container_width=True)

# --- Gráfico 5: Top 10 Productos Más Vendidos por Cantidad
st.subheader("📦 Top 10 Productos Más Vendidos por Cantidad")
productos_cantidad = df_filtrado.groupby('producto_nombre')['detalle_cantidad'].sum().reset_index()
productos_cantidad = productos_cantidad.sort_values(by='detalle_cantidad', ascending=False).head(10)
fig6 = px.bar(productos_cantidad, x='detalle_cantidad', y='producto_nombre',
              orientation='h', labels={'detalle_cantidad': 'Cantidad Vendida', 'producto_nombre': 'Producto'})
st.plotly_chart(fig6, use_container_width=True)

# --- Gráfico 3: Top 10 Productos Más Vendidos
st.subheader("Top 10 Productos Más Vendidos por Valor")
productos_top = df_filtrado.groupby('producto_nombre')['detalle_valor_total'].sum().reset_index()
productos_top = productos_top.sort_values(by='detalle_valor_total', ascending=False).head(10)
fig3 = px.bar(productos_top, x='detalle_valor_total', y='producto_nombre',
              orientation='h', labels={'detalle_valor_total': 'Ventas ($)', 'producto_nombre': 'Producto'})
st.plotly_chart(fig3, use_container_width=True)






