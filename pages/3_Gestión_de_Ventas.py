import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import plotly.express as px
import uuid  # Para generar IDs únicos para cada venta
import utilidades as util

# Configuración inicial de la página Streamlit
st.set_page_config(
    page_title="SmartFarm - Conci",
    layout="wide",
    page_icon="sf1.png",
    initial_sidebar_state="collapsed",
)

# Configurar Menu
util.generarMenu()

# =================================================================
# REPLICACIÓN DE CONFIGURACIÓN Y FUNCIONES DE BD
# =================================================================
# Variables globales para simular la persistencia de datos de Firestore
app_id = os.environ.get('__app_id', 'smartfarm_default_app_id')

# Definiciones de rutas de colecciones
SCORE_COLLECTION_PATH = f'artifacts/{app_id}/public/data/client_scores'
SALES_COLLECTION_PATH = f'artifacts/{app_id}/public/data/client_sales'
SALES_DOC_ID = 'all_sales_records'  # ID único del documento que contiene la lista de ventas

DATA_FILE = "firestore_simulation.json"


def save_to_json():
    """Guarda el diccionario de datos de Firestore simulado en el archivo JSON."""
    try:
        if 'firestore_data' in st.session_state:
            with open(DATA_FILE, 'w') as f:
                json.dump(st.session_state.firestore_data, f, indent=4)
    except Exception as e:
        st.error(f"Error al guardar datos simulados en JSON: {e}")


if 'db_initialized_sales' not in st.session_state:
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                st.session_state.firestore_data = json.load(f)
        else:
            st.session_state.firestore_data = {}
    except:
        st.session_state.firestore_data = {}

    # Inicializa la colección de clientes si no existe (para lectura de nombres)
    if SCORE_COLLECTION_PATH not in st.session_state.firestore_data:
        st.session_state.firestore_data[SCORE_COLLECTION_PATH] = {}

    # Inicializa la colección de ventas
    if SALES_COLLECTION_PATH not in st.session_state.firestore_data:
        st.session_state.firestore_data[SALES_COLLECTION_PATH] = {}

    # Inicializa el documento de ventas si no existe
    if SALES_DOC_ID not in st.session_state.firestore_data[SALES_COLLECTION_PATH]:
        st.session_state.firestore_data[SALES_COLLECTION_PATH][SALES_DOC_ID] = {'records': []}
        save_to_json()

    st.session_state.db_initialized_sales = True


def load_all_client_data():
    """Carga los datos de todos los clientes (solo para obtener nombres)."""
    return st.session_state.firestore_data.get(SCORE_COLLECTION_PATH, {})


def load_sales_db():
    """Carga la lista de registros de ventas."""
    return st.session_state.firestore_data.get(SALES_COLLECTION_PATH, {}).get(SALES_DOC_ID, {}).get('records', [])


def save_sales_db(sales_list):
    """Guarda la lista completa de registros de ventas."""
    st.session_state.firestore_data[SALES_COLLECTION_PATH][SALES_DOC_ID] = {'records': sales_list}
    save_to_json()
    st.session_state['sales_data_df'] = pd.DataFrame(sales_list)  # Actualiza el estado de la sesión
    return True


# --- FUNCIÓN DE UTILIDAD PARA OBTENER NOMBRES ---
def get_client_names_map():
    """Retorna un mapeo de Nombre -> ID para el selector."""
    all_clients = load_all_client_data()
    return {
        data.get('Cliente', f"Cliente sin nombre ({id})"): data.get('ID_Cliente')
        for id, data in all_clients.items() if data.get('Cliente')
    }


# --- FUNCIÓN DE UTILIDAD PARA OBTENER DATOS Y ALMACENAR EN SESIÓN ---
@st.cache_data
def get_sales_dataframe(records):
    """Crea o actualiza el DataFrame de ventas desde los registros brutos."""
    if not records:
        # Crea un DF vacío con las columnas esperadas si no hay registros
        empty_cols = ['ID_Venta', 'ID_Cliente', 'Cliente', 'Tipo de Venta', 'Estado de Venta', 'Detalle', 'Monto',
                      'Fecha Registro']
        return pd.DataFrame(columns=empty_cols)
    return pd.DataFrame(records)


# =================================================================
# LÓGICA DE LA PÁGINA
# =================================================================

st.title("💸 Gestión de Prospectos y Ventas SmartFarm")
st.subheader("Registra, edita y analiza el progreso comercial por cliente.")

client_names_map = get_client_names_map()
# Cargar datos de ventas brutos
raw_sales_records = load_sales_db()

if not client_names_map:
    st.warning(
        "⚠️ No hay clientes cargados. Por favor, ve a la página 'Puntuación SmartFarm' para registrar clientes antes de cargar ventas.")
else:
    client_names = sorted(list(client_names_map.keys()))

    # --- 1. CARGA DE NUEVOS DATOS DE VENTA ---
    st.header("1. Carga de Nuevo Prospecto/Venta")
    with st.form("new_sale_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        selected_client_name = col1.selectbox(
            "Cliente:",
            options=client_names,
            index=0,
            placeholder="Seleccione el Cliente",
            key="input_client"
        )

        selected_type = col2.selectbox(
            "Tipo de Venta:",
            options=["Componente", "Activación", "Servicio"],
            key="input_type"
        )

        col3, col4 = st.columns(2)

        selected_status = col3.selectbox(
            "Estado de la Venta:",
            options=["Posible", "Cerrado"],
            key="input_status"
        )

        sale_amount = col4.number_input(
            "Monto (en números):",
            min_value=0.0,
            step=100.0,
            format="%.2f",
            key="input_amount"
        )

        sale_detail = st.text_area(
            "Detalle de la Oportunidad/Venta:",
            max_chars=100,
            placeholder="Ej: Posible venta de componente X para optimización de rendimiento.",
            key="input_detail"
        )

        submitted = st.form_submit_button("➕ Registrar Venta")

        if submitted:
            if selected_client_name and sale_amount > 0:
                client_id = client_names_map[selected_client_name]
                new_record = {
                    'ID_Venta': str(uuid.uuid4()),
                    'ID_Cliente': client_id,
                    'Cliente': selected_client_name,
                    'Tipo de Venta': selected_type,
                    'Estado de Venta': selected_status,
                    'Detalle': sale_detail,
                    'Monto': sale_amount,
                    'Fecha Registro': datetime.now().strftime("%Y-%m-%d %H:%M")
                }

                # Cargar, añadir y guardar
                raw_sales_records.append(new_record)
                if save_sales_db(raw_sales_records):
                    st.success(f"Venta de {selected_client_name} registrada exitosamente.")
                else:
                    st.error("Error al guardar la venta.")
            else:
                st.error("Por favor, complete el cliente y el monto.")

    # --- 2. TABLA DE DATOS Y EDICIÓN ---
    st.header("2. Registros de Ventas y Edición")

    df_sales = get_sales_dataframe(raw_sales_records)

    if df_sales.empty:
        st.info("No hay registros de ventas cargados aún.")
    else:
        # Columna para el filtro
        filter_client_name = st.selectbox(
            "Filtrar Registros por Cliente (opcional):",
            options=["Todos"] + client_names,
            key="filter_client"
        )

        df_display = df_sales.copy()

        if filter_client_name != "Todos":
            df_display = df_display[df_sales['Cliente'] == filter_client_name].reset_index(
                drop=True)  # Importante resetear index para el editor

        # Configuración de columnas para la edición
        column_config = {
            "ID_Venta": st.column_config.TextColumn("ID Venta", disabled=True),
            "ID_Cliente": st.column_config.TextColumn("ID Cliente", disabled=True),
            "Cliente": st.column_config.TextColumn("Cliente", disabled=True),
            "Fecha Registro": st.column_config.DatetimeColumn("Fecha Registro", disabled=True,
                                                              format="YYYY-MM-DD HH:mm"),
            "Tipo de Venta": st.column_config.SelectboxColumn("Tipo de Venta",
                                                              options=["Componente", "Activación", "Servicio"],
                                                              required=True),
            "Estado de Venta": st.column_config.SelectboxColumn("Estado de Venta", options=["Posible", "Cerrado"],
                                                                required=True),
            "Monto": st.column_config.NumberColumn("Monto", format="$%.2f", required=True),
            "Detalle": st.column_config.TextColumn("Detalle", width="large")
        }

        edited_df_display = st.data_editor(
            df_display,
            key="sales_data_editor",
            column_config=column_config,
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic"  # HABILITA EL BOTÓN DE ELIMINAR FILAS
        )

        # Botón para guardar las ediciones y eliminaciones
        if st.button("📝 Guardar Cambios Editados y Eliminaciones"):
            changes = st.session_state.sales_data_editor

            edited_rows = changes.get("edited_rows", {})
            deleted_indices = changes.get("deleted_rows", [])

            # --- 1. PROCESAR ELIMINACIONES ---
            deleted_ids = []
            if deleted_indices:
                # Obtener los IDs de venta de las filas marcadas para eliminación en el DF que se mostró
                deleted_ids = df_display.iloc[deleted_indices]['ID_Venta'].tolist()

            # Filtrar los registros brutos para excluir los eliminados
            current_records_filtered = [
                record for record in raw_sales_records
                if record['ID_Venta'] not in deleted_ids
            ]

            # --- 2. PROCESAR EDICIONES ---
            updated_count = 0

            if edited_rows:
                # Mapear los registros filtrados a su ID de venta para fácil acceso
                records_map = {record['ID_Venta']: record for record in current_records_filtered}

                for idx, edits in edited_rows.items():
                    # Obtener el ID de venta de la fila editada en el DF que se mostró
                    sale_id_to_update = df_display.iloc[idx]['ID_Venta']

                    if sale_id_to_update in records_map:
                        # Aplicar los cambios al registro en el mapa
                        records_map[sale_id_to_update].update(edits)
                        updated_count += 1

                # Convertir el mapa de nuevo a una lista para guardar
                final_records_to_save = list(records_map.values())
            else:
                final_records_to_save = current_records_filtered

            # --- 3. GUARDAR EL RESULTADO FINAL ---
            if save_sales_db(final_records_to_save):
                if deleted_indices:
                    st.info(f"🗑️ Se eliminaron {len(deleted_ids)} registros de ventas.")
                if updated_count > 0:
                    st.success(f"✏️ Se actualizaron {updated_count} registros de ventas.")
                if not deleted_indices and not edited_rows:
                    st.warning("No se detectaron cambios ni eliminaciones para guardar.")
                st.rerun()  # Recargar para ver los cambios reflejados
            else:
                st.error("Error al guardar los cambios.")

    # --- 3. ANÁLISIS Y KPIS ---
    if not df_sales.empty:
        st.header("3. KPIs y Análisis Visual")

        # Filtrar datos si se seleccionó un cliente
        df_analysis = df_sales.copy()
        if filter_client_name != "Todos":
            df_analysis = df_analysis[df_sales['Cliente'] == filter_client_name]

        if df_analysis.empty:
            st.info(f"No hay registros de ventas para el cliente '{filter_client_name}'.")
        else:

            # 3.1 KPIs - Monto total por estado
            st.subheader("Métricas Financieras")

            summary_status = df_analysis.groupby('Estado de Venta')['Monto'].sum().reset_index()

            col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

            monto_cerrado = summary_status[summary_status['Estado de Venta'] == 'Cerrado']['Monto'].sum()
            monto_posible = summary_status[summary_status['Estado de Venta'] == 'Posible']['Monto'].sum()
            total_oportunidad = monto_cerrado + monto_posible

            col_kpi1.metric("Monto Total Cerrado", f"${monto_cerrado:,.2f}")
            col_kpi2.metric("Monto Total Posible", f"${monto_posible:,.2f}")
            col_kpi3.metric("Oportunidad Total (Cerrado + Posible)", f"${total_oportunidad:,.2f}")

            st.markdown("---")

            # 3.2 Gráficos
            col_chart1, col_chart2 = st.columns(2)

            # Gráfico de Torta (Estado de Venta)
            with col_chart1:
                st.subheader("Distribución por Estado de Venta")
                if not summary_status.empty:
                    fig_pie = px.pie(
                        summary_status,
                        values='Monto',
                        names='Estado de Venta',
                        title='Monto Total: Posible vs. Cerrado',
                        color='Estado de Venta',
                        color_discrete_map={'Cerrado': '#4CAF50', 'Posible': '#FFC107'}  # Verde y Amarillo
                    )
                    fig_pie.update_traces(textinfo='percent+value')
                    st.plotly_chart(fig_pie, use_container_width=True)

            # Gráfico de Barras (Tipo de Venta)
            with col_chart2:
                st.subheader("Monto por Tipo de Venta")
                summary_type = df_analysis.groupby('Tipo de Venta')['Monto'].sum().reset_index()

                if not summary_type.empty:
                    fig_bar = px.bar(
                        summary_type,
                        x='Tipo de Venta',
                        y='Monto',
                        title='Monto Generado por Tipo de Venta',
                        color='Tipo de Venta',
                        text_auto=True,
                        labels={'Monto': 'Monto ($)'}
                    )
                    fig_bar.update_layout(yaxis={'tickprefix': '$'})
                    st.plotly_chart(fig_bar, use_container_width=True)