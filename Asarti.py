import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la conexión a la base de datos
DB_URL = "mysql+pymysql://root@localhost/asartialpaca"
engine = create_engine(DB_URL)

# Configuración de la página
st.set_page_config(page_title="Asartialpaca Dashboard", layout="wide", page_icon=":bar_chart:")
st.title("📊 Dashboard de Gestión - Asartialpaca 🦙")

# Insertar imagen como franja debajo del título
st.markdown(
    """
    <style>
    .custom-image {
        width: 100%;
        height: 150px; /* Ajustar la altura de la imagen */
        object-fit: cover; /* Hacer que la imagen se recorte para encajar */
    }
    </style>
    <img src="https://images.ctfassets.net/86mn0qn5b7d0/featured-img-of-post-139172/0e5e6d5edd923aa442b3bab8c1bcf462/featured-img-of-post-139172.jpg?fm=jpg&fl=progressive&q=50&w=1200" 
         class="custom-image">
    """,
    unsafe_allow_html=True,
)

# Color del fondo del GIF extraído (#8088db)
sidebar_color = "#8088db"  # El color exacto del fondo del GIF
dashboard_color = "#4B0000"  # Nuevo color para el fondo del dashboard
sidebar_title_color = "#2A52BE" 
dashboard_title_color = "#2A52BE"

# Estilo personalizado con CSS
st.markdown(f"""
    <style>
    /* Degradado para el sidebar */
    [data-testid="stSidebar"] {{
        background: {sidebar_color} !important;
    }}
    /* Fondo para el dashboard */
    [data-testid="stAppViewContainer"] {{
        background: {dashboard_color} !important;
    }}
    /* Títulos en el sidebar */
    [data-testid="stSidebar"] h2 {{
        color: {sidebar_title_color} !important;
    }}
    /* Títulos específicos del dashboard */
    h3 {{
        color: {dashboard_title_color};
    }}
    h2 {{
        color: {dashboard_title_color};
    }}
    h1 {{
        color: #E6D5BE;  /* Color crema claro para el título principal */
    }}
    </style>
""", unsafe_allow_html=True)

# Sidebar con gif
st.sidebar.markdown(
    "<div style='text-align: center;'><img src='https://th.bing.com/th/id/R.84a53d26c9a7e657393f143407fd9eda?rik=gW5kpLJlwd2SHQ&pid=ImgRaw&r=0' width='150'></div>", 
    unsafe_allow_html=True
)
st.sidebar.header("🔍 Filtros de búsqueda")

# Consulta general para cargar datos iniciales
with engine.connect() as conn:
    query = text(""" 
        SELECT
            c.id_cliente, c.nombre_cliente, c.apellido_cliente, c.ciudad, DATE(c.fecha_registro) AS fecha_registro,
            p.id_pedido, DATE(p.fecha_pedido) AS fecha_pedido, p.total_pedido, p.direccion_envio,
            pr.id_producto, pr.nombre_producto, pr.precio_producto,
            cat.nombre_categoria, inv.cantidad_disponible, inv.id_ubicacion_almacen,
            f.monto_total, DATE(f.fecha_emision) AS fecha_emision, f.razon_social
        FROM cliente c
        LEFT JOIN pedido p ON c.id_cliente = p.id_cliente
        LEFT JOIN pedido_producto pp ON p.id_pedido = pp.id_pedido
        LEFT JOIN producto pr ON pp.id_producto = pr.id_producto
        LEFT JOIN categoria cat ON pr.id_categoria = cat.id_categoria
        LEFT JOIN inventario inv ON pr.id_producto = inv.id_producto
        LEFT JOIN facturacion f ON f.id_detalle_pedido = p.id_pedido
    """)
    result = conn.execute(query)
    df = pd.DataFrame(result.fetchall(), columns=result.keys())

# Filtros de búsqueda
ciudades = df["ciudad"].dropna().unique()
productos = df["nombre_producto"].dropna().unique()
categorias = df["nombre_categoria"].dropna().unique()

filtro_ciudad = st.sidebar.multiselect("Selecciona Ciudad 🏙", ciudades)
filtro_producto = st.sidebar.multiselect("Selecciona Producto 🛒", productos)
filtro_categoria = st.sidebar.multiselect("Selecciona Categoría 📂", categorias)

# Filtro por rango de fechas (por fecha de pedido)
st.sidebar.subheader("📅 Rango de Fechas")
fecha_inicio = st.sidebar.date_input("Fecha de Inicio", value=pd.to_datetime(df["fecha_pedido"]).min())
fecha_fin = st.sidebar.date_input("Fecha de Fin", value=pd.to_datetime(df["fecha_pedido"]).max())

# Aplicar filtros
df_filtrado = df.copy()
if filtro_ciudad:
    df_filtrado = df_filtrado[df_filtrado["ciudad"].isin(filtro_ciudad)]
if filtro_producto:
    df_filtrado = df_filtrado[df_filtrado["nombre_producto"].isin(filtro_producto)]
if filtro_categoria:
    df_filtrado = df_filtrado[df_filtrado["nombre_categoria"].isin(filtro_categoria)]
if fecha_inicio and fecha_fin:
    df_filtrado = df_filtrado[(df_filtrado["fecha_pedido"] >= fecha_inicio) & (df_filtrado["fecha_pedido"] <= fecha_fin)]

# Ajuste del formato de las fechas
df["fecha_pedido"] = pd.to_datetime(df["fecha_pedido"]).dt.strftime("%Y-%m-%d")
df["fecha_registro"] = pd.to_datetime(df["fecha_registro"]).dt.strftime("%Y-%m-%d")
df["fecha_emision"] = pd.to_datetime(df["fecha_emision"]).dt.strftime("%Y-%m-%d")
df_filtrado["fecha_pedido"] = pd.to_datetime(df_filtrado["fecha_pedido"]).dt.strftime("%Y-%m-%d")
df_filtrado["fecha_registro"] = pd.to_datetime(df_filtrado["fecha_registro"]).dt.strftime("%Y-%m-%d")
df_filtrado["fecha_emision"] = pd.to_datetime(df_filtrado["fecha_emision"]).dt.strftime("%Y-%m-%d")

# Mostrar datos iniciales
st.subheader("📋 Datos Iniciales")
with st.expander("Ver datos iniciales"):
    st.dataframe(df)

# Mostrar datos filtrados
st.subheader("📋 Datos Filtrados")
if df_filtrado.empty:
    st.error("⚠ No hay datos disponibles para los filtros seleccionados.")
else:
    with st.expander("Ver datos filtrados"):
        st.dataframe(df_filtrado)

# Métricas generales
st.header("📈 Indicadores Clave")
col1, col2, col3 = st.columns(3)
with col1:
    total_ventas = df_filtrado["total_pedido"].sum()
    st.metric("Total Ventas 💰", f"Bs. {total_ventas:,.2f}")
with col2:
    cantidad_productos = df_filtrado["cantidad_disponible"].sum()
    st.metric("Cantidad Disponible 📦", cantidad_productos)
with col3:
    clientes_registrados = df_filtrado["id_cliente"].nunique()
    st.metric("Clientes Registrados 👥", clientes_registrados)

# Gráficos dinámicos con filtros aplicados
st.header("📊 Visualizaciones Interactivas")
col4, col5 = st.columns(2)

# Ventas por Producto
with col4:
    st.markdown('<h3 style="color: #E6D5BE;">Ventas por Producto 🛒</h3>', unsafe_allow_html=True)
    
    if df_filtrado.empty or "total_pedido" not in df_filtrado.columns or df_filtrado["total_pedido"].sum() == 0:
        st.warning("⚠ No hay suficientes datos para generar el gráfico de Ventas por Producto.")
    else:
        ventas_por_producto = df_filtrado.groupby("nombre_producto")["total_pedido"].sum().reset_index()
        fig1 = px.bar(
            ventas_por_producto, 
            x="nombre_producto", 
            y="total_pedido", 
            title="Ventas por Producto", 
            color="nombre_producto", 
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig1.update_layout(
            title_font=dict(color="#005F5B"),
            plot_bgcolor="#4B0000", 
            paper_bgcolor="#4B0000"
        )
        st.plotly_chart(fig1, use_container_width=True)

# Ventas por Ciudad
with col5:
    st.markdown('<h3 style="color: #E6D5BE;">Distribución de Ventas por Ciudad 🏙</h3>', unsafe_allow_html=True)
    
    if df_filtrado.empty or "ciudad" not in df_filtrado.columns or df_filtrado["total_pedido"].sum() == 0:
        st.warning("⚠ No hay suficientes datos para generar el gráfico de Distribución de Ventas por Ciudad.")
    else:
        ventas_por_ciudad = df_filtrado.groupby("ciudad")["total_pedido"].sum().reset_index()
        fig2 = px.pie(
            ventas_por_ciudad, 
            names="ciudad", 
            values="total_pedido", 
            title="Ventas por Ciudad", 
            color_discrete_sequence=px.colors.sequential.Plasma
        )
        fig2.update_layout(
            title_font=dict(color="#005F5B"),
            plot_bgcolor="#4B0000", 
            paper_bgcolor="#4B0000"
        )
        st.plotly_chart(fig2, use_container_width=True)

# Relación entre Categorías y Ventas
st.markdown('<h3 style="color: #E6D5BE;">📊 Relación entre Categorías y Ventas</h3>', unsafe_allow_html=True)
if df_filtrado.empty or "nombre_categoria" not in df_filtrado.columns or "total_pedido" not in df_filtrado.columns:
    st.warning("⚠ No hay suficientes datos para generar el gráfico de Relación entre Categorías y Ventas.")
else:
    categorias_ventas = df_filtrado.groupby("nombre_categoria")["total_pedido"].sum().reset_index()
    fig_relacion = px.treemap(
        categorias_ventas,
        path=["nombre_categoria"],
        values="total_pedido",
        title="Relación entre Categorías y Ventas",
        color="total_pedido",
        color_continuous_scale="Rainbow"
    )
    fig_relacion.update_layout(
        title_x=0.5,
        title_font_color="#005F5B",
        plot_bgcolor="#4B0000",
        paper_bgcolor="#4B0000"
    )
    st.plotly_chart(fig_relacion, use_container_width=True)

# Diccionario de consultas
report_queries = {
    "Ventas Totales por Cliente": """
        SELECT c.nombre_cliente, CONCAT(c.nombre_cliente, ' ', c.apellido_cliente) AS cliente, 
               SUM(p.total_pedido) AS total_compras
        FROM cliente AS c
        JOIN pedido AS p ON c.id_cliente = p.id_cliente
        GROUP BY c.id_cliente
        ORDER BY total_compras DESC;
    """,
    "Cantidad de Productos Vendidos por Categoría": """
        SELECT cat.nombre_categoria, SUM(dp.cantidad_producto) AS total_vendidos
        FROM categoria AS cat
        JOIN producto AS prod ON cat.id_categoria = prod.id_categoria
        JOIN detalle_pedido AS dp ON prod.id_producto = dp.id_cliente_pedido
        GROUP BY cat.id_categoria
        ORDER BY total_vendidos DESC;
    """,
    "Descuento Promedio en Promociones": """
        SELECT nombre_promocion, AVG(porcentaje_descuento) AS descuento_promedio
        FROM promocion
        GROUP BY nombre_promocion
        ORDER BY descuento_promedio DESC;
    """,
    "Estado de Pedidos por Método de Pago": """
        SELECT metodo_pago, estado_final_pedido, COUNT(id_historial) AS total_pedidos
        FROM historial
        GROUP BY metodo_pago, estado_final_pedido
        ORDER BY total_pedidos DESC;
    """,
    "Monto Total Facturado por Mes": """
        SELECT DATE_FORMAT(fecha_emision, '%Y-%m') AS mes, SUM(monto_total) AS total_facturado
        FROM facturacion
        GROUP BY mes
        ORDER BY mes DESC;
    """,
    "Promedio de Compra por Cliente": """
        SELECT c.nombre_cliente, c.apellido_cliente, AVG(p.total_pedido) AS promedio_compra
        FROM cliente c
        JOIN pedido p ON c.id_cliente = p.id_cliente
        GROUP BY c.id_cliente
        ORDER BY promedio_compra DESC;
    """,
    "Productos más Vendidos": """
        SELECT p.nombre_producto, SUM(dp.cantidad_producto) AS total_vendido
        FROM pedido_producto pp
        JOIN producto p ON pp.id_producto = p.id_producto
        JOIN detalle_pedido dp ON dp.id_cliente_pedido = pp.id_pedido
        GROUP BY p.nombre_producto
        ORDER BY total_vendido DESC;
    """,
    "Empleados por Cargo": """
        SELECT ce.nombre_cargo, COUNT(e.id_empleado) AS total_empleados
        FROM cargo_empleado ce
        JOIN empleado e ON ce.id_cargo_empleado = e.id_cargo_empleado
        GROUP BY ce.id_cargo_empleado
        ORDER BY total_empleados DESC;
    """,
    "Historial de Estados de Carritos de Compras": """
        SELECT estado_carrito, COUNT(id_carrito_compras) AS total_carritos
        FROM carrito_compras
        GROUP BY estado_carrito
        ORDER BY total_carritos DESC;
    """,
    "Ingresos Generados por Promociones": """
        SELECT p.nombre_promocion, SUM(p.porcentaje_descuento * dp.cantidad_producto * pr.precio_producto / 100) AS ingresos_promocion
        FROM promocion AS p
        JOIN producto AS pr ON p.id_producto = pr.id_producto
        JOIN pedido_producto AS pp ON pr.id_producto = pp.id_producto
        JOIN detalle_pedido AS dp ON pp.id_pedido = dp.id_cliente_pedido
        GROUP BY p.id_promocion
        ORDER BY ingresos_promocion DESC;
    """
}
with engine.connect() as conn:
    for report_name, query in report_queries.items():
        # Ejecutar consulta y convertir resultado a DataFrame
        result = conn.execute(text(query))
        report_df = pd.DataFrame(result.fetchall(), columns=result.keys())

        # Mostrar datos en Streamlit con color de título verde
        col1, col2 = st.columns([2, 3])
        with col1:
            st.markdown(f"<h4 style='color:#E6D5BE;'>{report_name}</h4>", unsafe_allow_html=True)
            
            if report_df.empty:
                st.warning(f"⚠ No hay suficientes datos disponibles para el reporte: {report_name}.")
            else:
                st.dataframe(report_df, use_container_width=True)

        # Generar gráficos personalizados si hay datos disponibles
        with col2:
            if report_df.empty:
                st.warning(f"⚠ No hay datos para generar el gráfico asociado a: {report_name}.")
            else:
                if "Ventas Totales por Cliente" in report_name:
                    # Mapa de Calor
                    fig = px.density_heatmap(
                        report_df,
                        x="cliente",
                        y="total_compras",
                        z="total_compras",
                        title="Mapa de Calor: Ventas Totales por Cliente",
                        color_continuous_scale="Spectral"
                    )
                    fig.update_layout(
                        title_x=0.5,
                        title_font_color="#005F5B",
                        plot_bgcolor="#4B0000",  # Fondo del gráfico
                        paper_bgcolor="#4B0000",  # Fondo del área del gráfico
                        font=dict(color="white")  # Asegura que el texto sea visible en el fondo oscuro
                    )
                    st.plotly_chart(fig, use_container_width=True)

                elif "Cantidad de Productos Vendidos" in report_name:
                    # Gráfico de Barras
                    fig = px.bar(
                        report_df,
                        x="nombre_categoria",
                        y="total_vendidos",
                        title="Gráfico de Barras: Productos Vendidos por Categoría",
                        text_auto=True,
                        color="nombre_categoria",
                        color_discrete_sequence=px.colors.qualitative.Dark2
                    )
                    fig.update_layout(
                        title_x=0.5,
                        title_font_color="#005F5B",
                        plot_bgcolor="#4B0000",  
                        paper_bgcolor="#4B0000"  
                    )
                    st.plotly_chart(fig, use_container_width=True)

                elif "Descuento Promedio" in report_name:
                    # Gráfico de Dispersión con Línea de Tendencia
                    fig = px.scatter(
                        report_df,
                        x="nombre_promocion",
                        y="descuento_promedio",
                        title="Gráfico de Dispersión: Descuento Promedio",
                        trendline="ols",
                        color="nombre_promocion",
                        color_discrete_sequence=px.colors.qualitative.Bold
                    )
                    fig.update_layout(
                        title_x=0.5,
                        title_font_color="#005F5B",
                        plot_bgcolor="#4B0000",  
                        paper_bgcolor="#4B0000"  
                    )
                    st.plotly_chart(fig, use_container_width=True)

                elif "Estado de Pedidos" in report_name:
                    # Gráfico Circular (Sunburst)
                    fig = px.sunburst(
                        report_df,
                        path=["metodo_pago", "estado_final_pedido"],
                        values="total_pedidos",
                        title="Sunburst: Estado de Pedidos por Método de Pago",
                        color="total_pedidos",
                        color_continuous_scale="Inferno"
                    )
                    fig.update_layout(
                        title_x=0.5,
                        title_font_color="#005F5B",
                        plot_bgcolor="#4B0000",  
                        paper_bgcolor="#4B0000"  
                    )
                    st.plotly_chart(fig, use_container_width=True)

                elif "Monto Total Facturado" in report_name:
                    # Gráfico de Área
                    fig = px.area(
                        report_df,
                        x="mes",
                        y="total_facturado",
                        title="Gráfico de Área: Monto Total Facturado por Mes",
                        color_discrete_sequence=["#3E4B8D"]
                    )
                    fig.update_layout(
                        title_x=0.5,
                        title_font_color="#005F5B",
                        plot_bgcolor="#4B0000",  
                        paper_bgcolor="#4B0000"  
                    )
                    st.plotly_chart(fig, use_container_width=True)

                elif "Promedio de Compra" in report_name:
                    # Convertir tamaño a numérico
                    report_df["promedio_compra"] = pd.to_numeric(report_df["promedio_compra"], errors="coerce")
                    # Gráfico de Burbuja
                    fig = px.scatter(
                        report_df,
                        x="nombre_cliente",
                        y="promedio_compra",
                        size="promedio_compra",
                        color="nombre_cliente",
                        title="Gráfico de Burbuja: Promedio de Compra por Cliente",
                        color_discrete_sequence=px.colors.qualitative.Set1  
                    )
                    fig.update_traces(marker=dict(opacity=1))

                    fig.update_layout(
                        title_x=0.5,
                        title_font_color="#005F5B",
                        plot_bgcolor="#4B0000",  
                        paper_bgcolor="#4B0000"  
                    )
                    st.plotly_chart(fig, use_container_width=True)

                elif "Productos más Vendidos" in report_name:
                    # Gráfico de Barras Apiladas
                    fig = px.bar(
                        report_df,
                        x="nombre_producto",
                        y="total_vendido",
                        color="nombre_producto",
                        title="Gráfico de Barras Apiladas: Productos Más Vendidos",
                        text_auto=True,
                        color_discrete_sequence=px.colors.qualitative.Vivid
                    )
                    fig.update_layout(
                        title_x=0.5,
                        title_font_color="#005F5B",
                        plot_bgcolor="#4B0000",  
                        paper_bgcolor="#4B0000"  
                    )
                    st.plotly_chart(fig, use_container_width=True)

                elif "Empleados por Cargo" in report_name:
                    # Gráfico Circular
                    fig = px.pie(
                        report_df,
                        names="nombre_cargo",
                        values="total_empleados",
                        title="Gráfico Circular: Empleados por Cargo",
                        color_discrete_sequence=px.colors.qualitative.Dark24
                    )
                    fig.update_layout(
                        title_x=0.5,
                        title_font_color="#005F5B",
                        plot_bgcolor="#4B0000",  
                        paper_bgcolor="#4B0000"  
                    )
                    st.plotly_chart(fig, use_container_width=True)

                elif "Historial de Estados de Carritos" in report_name:
                    # Histograma
                    fig = px.histogram(
                        report_df,
                        x="estado_carrito",
                        y="total_carritos",
                        title="Histograma: Estados de Carritos de Compras",
                        color="estado_carrito",
                        color_discrete_sequence=px.colors.sequential.Plasma
                    )
                    fig.update_layout(
                        title_x=0.5,
                        title_font_color="#005F5B",
                        plot_bgcolor="#4B0000",  
                        paper_bgcolor="#4B0000"  
                    )
                    st.plotly_chart(fig, use_container_width=True)

                elif "Ingresos Generados por Promociones" in report_name:
                    # Box Plot
                    fig = px.box(
                        report_df,
                        x="nombre_promocion",
                        y="ingresos_promocion",
                        title="Gráfico Box Plot: Ingresos Generados por Promociones",
                        color="nombre_promocion",
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig.update_layout(
                        title_x=0.5,
                        title_font_color="#005F5B",
                        plot_bgcolor="#4B0000", 
                        paper_bgcolor="#4B0000"  
                    )
                    st.plotly_chart(fig, use_container_width=True)