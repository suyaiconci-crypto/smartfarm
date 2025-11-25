import json
import os
import pandas as pd
import streamlit as st
import uuid
import plotly.express as px

st.set_page_config(
    page_title="Proyectos Agronomy Analyzer",
    layout="wide",
    page_icon="📋",
    initial_sidebar_state="expanded"
)

# =================================================================
# 1. CONFIGURACIÓN DEL ENTORNO Y DATOS MAESTROS
# =================================================================
# Variables de entorno para simulación de Firestore
app_id = os.environ.get('__app_id', 'smartfarm_default_app_id')
DATA_FILE = "firestore_simulation.json"

# RUTAS DE COLECCIÓN (Las rutas deben ser únicas para cada tipo de dato)
SCORES_COLLECTION_PATH = f'artifacts/{app_id}/public/data/client_scores'
PROJECTS_COLLECTION_PATH = f'artifacts/{app_id}/public/data/agronomy_projects'

PROTOCOLOS_AA = [
    "Pulverizadora PLA", "Sembradora PLA", "Sembradora JD",
    "ExactApply", "AutoPath", "S700 Combine Advisor", "S7 Automation",
    "Autotrac Turn Automation", "Machine Sync", "HarvestLab", "Grain Sensing"
]

ESTADOS_PROYECTO = ["No Iniciado", "En Proceso", "Completado"]


# =================================================================
# 2. FUNCIONES DE SIMULACIÓN DE FIRESTORE
# =================================================================

def load_firestore_data():
    """Carga todos los datos de la simulación de Firestore desde el archivo JSON."""
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}
    except Exception:
        return {}


def save_firestore_data(data):
    """Guarda los datos en el archivo JSON."""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        st.error(f"Error al guardar datos: {e}")


def load_client_scores_data():
    """Carga los datos de clientes (scores) para obtener la lista de clientes."""
    firestore_data = load_firestore_data()
    return list(firestore_data.get(SCORES_COLLECTION_PATH, {}).values())


def load_agronomy_projects():
    """Carga los proyectos de Agronomy Analyzer registrados."""
    firestore_data = load_firestore_data()
    # Retorna una lista de documentos de proyecto
    return list(firestore_data.get(PROJECTS_COLLECTION_PATH, {}).values())


def get_latest_project_for_client(client_name):
    """Busca el proyecto más reciente para un cliente dado."""
    all_projects = load_agronomy_projects()
    client_projects = [p for p in all_projects if p.get('Cliente') == client_name]

    if not client_projects:
        return None, None  # No project found

    # Ordenar por fecha de registro descendente para obtener el último
    try:
        df_projects = pd.DataFrame(client_projects)
        df_projects['Fecha_Registro_dt'] = pd.to_datetime(df_projects['Fecha_Registro'], errors='coerce')
        # Filtra Nulos antes de ordenar
        df_projects = df_projects.dropna(subset=['Fecha_Registro_dt'])
        latest_project = df_projects.sort_values(by='Fecha_Registro_dt', ascending=False).iloc[0].to_dict()
    except Exception as e:
        # Fallback a la clasificación de strings si hay un error o no hay datos
        client_projects.sort(key=lambda x: x.get('Fecha_Registro', '2000-01-01'), reverse=True)
        latest_project = client_projects[0]

    return latest_project.get('id'), latest_project


# =================================================================
# 3. LÓGICA DE CARGA DE ESTADO (SESSION STATE)
# =================================================================

def initialize_session_state(first_client):
    """Inicializa todas las claves de session_state con valores seguros."""
    if 'current_project_id' not in st.session_state:
        st.session_state.current_project_id = None
        st.session_state.protocol_default = PROTOCOLOS_AA[0]
        st.session_state.nombre_default = ''
        st.session_state.ubicacion_default = ''

        # Valores de Etapa por defecto
        st.session_state.plan_status_default = ESTADOS_PROYECTO[0]
        st.session_state.plan_hours_default = 0
        st.session_state.reco_status_default = ESTADOS_PROYECTO[0]
        st.session_state.reco_hours_default = 0
        st.session_state.informe_status_default = ESTADOS_PROYECTO[0]
        st.session_state.informe_hours_default = 0

        # Control de UI
        st.session_state.select_cliente_widget = first_client
        st.session_state.form_key_suffix = 0
        st.session_state.initial_load_done = False


def load_project_data_callback():
    """Callback para cargar datos del último proyecto al cambiar el cliente y refrescar el estado."""
    client_name = st.session_state.get('select_cliente_widget')

    if not client_name:
        return

    # CRÍTICO: Incrementar el sufijo de la clave del formulario ANTES de cargar
    # Esto garantiza que todos los widgets del formulario se reconstruyan con los nuevos defaults.
    st.session_state.form_key_suffix += 1

    doc_id, project_data = get_latest_project_for_client(client_name)

    if project_data:
        st.session_state.current_project_id = doc_id

        # Info base
        st.session_state.protocol_default = project_data.get('Protocolo', PROTOCOLOS_AA[0])
        st.session_state.nombre_default = project_data.get('Nombre_Evaluacion', '')
        st.session_state.ubicacion_default = project_data.get('Ubicacion_Evaluacion', '')

        # Etapas
        st.session_state.plan_status_default = project_data.get('Planificacion_Estado', ESTADOS_PROYECTO[0])
        st.session_state.plan_hours_default = int(project_data.get('Planificacion_Horas', 0))
        st.session_state.reco_status_default = project_data.get('Recopilacion_Estado', ESTADOS_PROYECTO[0])
        st.session_state.reco_hours_default = int(project_data.get('Recopilacion_Horas', 0))
        st.session_state.informe_status_default = project_data.get('Informe_Estado', ESTADOS_PROYECTO[0])
        st.session_state.informe_hours_default = int(project_data.get('Informe_Horas', 0))

        st.toast(f"Datos del último proyecto '{project_data.get('Nombre_Evaluacion')}' cargados para edición.")
    else:
        # Set clean defaults if no project found
        st.session_state.current_project_id = None
        st.session_state.protocol_default = PROTOCOLOS_AA[0]
        st.session_state.nombre_default = ''
        st.session_state.ubicacion_default = ''
        st.session_state.plan_status_default = ESTADOS_PROYECTO[0]
        st.session_state.plan_hours_default = 0
        st.session_state.reco_status_default = ESTADOS_PROYECTO[0]
        st.session_state.reco_hours_default = 0
        st.session_state.informe_status_default = ESTADOS_PROYECTO[0]
        st.session_state.informe_hours_default = 0

        st.toast(f"No hay proyectos registrados para {client_name}. Ingresa uno nuevo.")


# =================================================================
# 4. INTERFAZ Y LÓGICA DE CARGA (INIT & UI)
# =================================================================

st.set_page_config(
    page_title="SmartFarm - Conci",
    layout="wide",
    page_icon="sf1.png",
    initial_sidebar_state="collapsed",
)

st.title("📋 Registro de Proyectos Agronomy Analyzer")

client_scores_data = load_client_scores_data()

if not client_scores_data:
    st.info("No hay clientes cargados. Por favor, registra clientes en la primera hoja.")
    st.stop()

# Convertir los datos de clientes a DataFrame
df_clients = pd.DataFrame(client_scores_data)
df_unique_clients = df_clients[['Cliente', 'Sucursal', 'Categoria_Evaluacion']].drop_duplicates(
    subset=['Cliente']).reset_index(drop=True)
client_names = df_unique_clients['Cliente'].unique().tolist()
first_client = client_names[0] if client_names else None

# Inicialización segura
initialize_session_state(first_client)

# Carga inicial de datos para el primer cliente al iniciar la página
if not st.session_state.initial_load_done and client_names:
    st.session_state.select_cliente_widget = first_client
    load_project_data_callback()
    st.session_state.initial_load_done = True
    st.rerun()  # Forzar rerun solo en la carga inicial

# --- SELECCIÓN DE CLIENTE (FUERA DEL FORMULARIO) ---
st.subheader("Selección y Carga de Proyecto")

current_client_key = st.session_state.get('select_cliente_widget', first_client)

safe_index = client_names.index(current_client_key) if current_client_key in client_names else 0

# Este selectbox debe usar el valor que está en session_state para mantener la selección
selected_client_name = st.selectbox(
    "1. Selecciona el Cliente SmartFarm:",
    options=client_names,
    index=safe_index,
    key="select_cliente_widget",
    on_change=load_project_data_callback
)

# Obtener los datos del cliente seleccionado para incluirlos en el registro del proyecto
client_info = {}
if selected_client_name:
    client_info = df_unique_clients[df_unique_clients['Cliente'] == selected_client_name].iloc[0].to_dict()
    st.markdown(f"""
    <div style="padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 20px;">
        **Datos del Cliente Seleccionado:**<br>
        **Sucursal:** {client_info['Sucursal']}<br>
        **Perfil Tecnológico (Categoría):** {client_info['Categoria_Evaluacion']}
    </div>
    """, unsafe_allow_html=True)

# =================================================================
# 5. FORMULARIO DE REGISTRO DE PROYECTO (USANDO DEFAULTS DE SESSION STATE)
# =================================================================
key_suffix = st.session_state.form_key_suffix

if st.session_state.current_project_id:
    st.subheader(f"📝 Actualizar Último Proyecto")
else:
    st.subheader("➕ Registrar Nuevo Protocolo")

# Diccionarios para guardar las claves de los widgets para lectura posterior
stage_widget_keys = {}

# Definición de claves de widgets base
base_widget_keys = {
    'protocol': f"select_protocolo_form_{key_suffix}",
    'nombre': f"nombre_evaluacion_{key_suffix}",
    'ubicacion': f"ubicacion_evaluacion_{key_suffix}"
}


# --- FUNCIÓN DE ENTRADA CON ESTILOS DE COLOR ---
def create_stage_inputs(stage_name, default_status, default_hours, suffix):
    """Crea los selectbox y number_input para una etapa, mostrando el estado actual con color."""

    status_key = f"{stage_name}_estado_{suffix}"
    hours_key = f"{stage_name}_horas_{suffix}"

    # 1. Obtenemos el valor actual (o el default si es la primera carga)
    # Usamos .get() en session_state para manejar el primer render donde la clave aún no existe.
    # Si la clave no está en session_state, usamos el valor default_status.
    current_status = st.session_state.get(status_key, default_status)

    # 2. Mapeo de colores (Verde, Amarillo, Gris)
    color_map = {
        "Completado": ("#4CAF50", "white"),  # Success Green
        "En Proceso": ("#FFC107", "black"),  # Warning Yellow/Amber
        "No Iniciado": ("#E0E0E0", "black")  # Default Light Gray
    }
    bg_color, text_color = color_map.get(current_status, ("#E0E0E0", "black"))

    # Estilo HTML para el título/estado de la etapa
    styled_html = f"""
    <div style="
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 15px;
        margin-bottom: 10px;
        border-radius: 8px; 
        background-color: {bg_color}; 
        color: {text_color};
        font-size: 1.1em;
        font-weight: 700;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    ">
        <span>{stage_name}:</span> 
        <span>{current_status}</span>
    </div>
    """
    st.markdown(styled_html, unsafe_allow_html=True)

    # 3. Input Widgets
    col_status, col_hours = st.columns([3, 2])

    status_index = ESTADOS_PROYECTO.index(default_status) if default_status in ESTADOS_PROYECTO else 0

    with col_status:
        st.caption("Cambiar Estado")
        st.selectbox(
            f"Estado de {stage_name}:",
            options=ESTADOS_PROYECTO,
            index=status_index,
            key=status_key,
            label_visibility="collapsed"  # Ocultamos la etiqueta para que se vea más limpio
        )

    with col_hours:
        st.caption("Horas Dedicadas")
        st.number_input(
            f"Horas Dedicadas a {stage_name} (h):",
            min_value=0,
            step=1,
            value=default_hours,
            key=hours_key,
            label_visibility="collapsed"  # Ocultamos la etiqueta para que se vea más limpio
        )

    return status_key, hours_key


# --- FIN FUNCIÓN DE ENTRADA CON ESTILOS DE COLOR ---


with st.form("agronomy_project_form"):
    # --- Info Base (Usando las claves definidas arriba) ---
    col_sel_protocolo, _ = st.columns([1, 1])
    with col_sel_protocolo:
        protocol_index = PROTOCOLOS_AA.index(
            st.session_state.protocol_default) if st.session_state.protocol_default in PROTOCOLOS_AA else 0
        st.selectbox(
            "2. Selecciona el Protocolo (Agronomy Analyzer):",
            options=PROTOCOLOS_AA,
            index=protocol_index,
            key=base_widget_keys['protocol']
        )

    col_nombre, col_ubicacion = st.columns(2)

    with col_nombre:
        st.text_input(
            "3. Nombre de la Evaluación/Proyecto",
            value=st.session_state.nombre_default,
            placeholder="Ej: Implementación AutoPath Campaña 2024",
            key=base_widget_keys['nombre']
        )

    with col_ubicacion:
        st.text_input(
            "4. Ubicación de la Evaluación (Lote/Campo)",
            value=st.session_state.ubicacion_default,
            placeholder="Ej: Lote 5 'El Dorado'",
            key=base_widget_keys['ubicacion']
        )

    st.markdown("---")

    # --- Seguimiento de Etapas (Llamando a la función mejorada) ---
    st.subheader("5. Seguimiento de Etapas y Tiempos")

    stage_widget_keys['plan_status'], stage_widget_keys['plan_hours'] = create_stage_inputs(
        "Planificación",
        st.session_state.plan_status_default,
        st.session_state.plan_hours_default,
        key_suffix
    )
    st.markdown("---")

    stage_widget_keys['reco_status'], stage_widget_keys['reco_hours'] = create_stage_inputs(
        "Recopilación de Datos",
        st.session_state.reco_status_default,
        st.session_state.reco_hours_default,
        key_suffix
    )
    st.markdown("---")

    stage_widget_keys['informe_status'], stage_widget_keys['informe_hours'] = create_stage_inputs(
        "Generación de Informe",
        st.session_state.informe_status_default,
        st.session_state.informe_hours_default,
        key_suffix
    )
    st.markdown("---")

    submit_label = "Actualizar Proyecto" if st.session_state.current_project_id else "Guardar Nuevo Proyecto"
    submitted = st.form_submit_button(submit_label)

    if submitted:
        # LECTURA CRÍTICA DE TODOS LOS VALORES DEL FORMULARIO A TRAVÉS DE SESSION STATE
        selected_protocol = st.session_state[base_widget_keys['protocol']]
        evaluation_name = st.session_state[base_widget_keys['nombre']]
        evaluation_location = st.session_state[base_widget_keys['ubicacion']]

        plan_status = st.session_state[stage_widget_keys['plan_status']]
        plan_hours = st.session_state[stage_widget_keys['plan_hours']]
        reco_status = st.session_state[stage_widget_keys['reco_status']]
        reco_hours = st.session_state[stage_widget_keys['reco_hours']]
        informe_status = st.session_state[stage_widget_keys['informe_status']]
        informe_hours = st.session_state[stage_widget_keys['informe_hours']]

        # 1. Validación
        if not selected_client_name or not evaluation_name.strip() or not evaluation_location.strip():
            # MENSAJE DE ERROR DETALLADO PARA DEBUGGING
            st.error(
                f"Error de validación. Cliente: {selected_client_name}. Nombre Capturado: '{evaluation_name.strip()}', Ubicación Capturada: '{evaluation_location.strip()}'")
            st.error("Por favor, completa los campos obligatorios (Cliente, Nombre y Ubicación).")
        else:
            # 2. Decidir si es UPDATE o CREATE
            doc_id = st.session_state.current_project_id if st.session_state.current_project_id else str(uuid.uuid4())
            action_type = "Actualizado" if st.session_state.current_project_id else "Guardado"

            # Sumar las horas totales
            total_hours = plan_hours + reco_hours + informe_hours

            new_project_document = {
                "id": doc_id,
                "Cliente": selected_client_name,
                "Sucursal": client_info.get('Sucursal', 'N/A'),
                "Perfil_Tecnologico": client_info.get('Categoria_Evaluacion', 'N/A'),
                "Protocolo": selected_protocol,
                "Nombre_Evaluacion": evaluation_name.strip(),
                "Ubicacion_Evaluacion": evaluation_location.strip(),

                # Campos de Seguimiento
                "Planificacion_Estado": plan_status,
                "Planificacion_Horas": plan_hours,
                "Recopilacion_Estado": reco_status,
                "Recopilacion_Horas": reco_hours,
                "Informe_Estado": informe_status,
                "Informe_Horas": informe_hours,
                "Total_Horas": total_hours,

                "Fecha_Registro": pd.to_datetime('now').strftime('%Y-%m-%d %H:%M:%S')
            }

            # 3. Cargar datos existentes y guardar/actualizar el proyecto
            firestore_data = load_firestore_data()
            if PROJECTS_COLLECTION_PATH not in firestore_data:
                firestore_data[PROJECTS_COLLECTION_PATH] = {}

            # Sobrescribir el documento completo usando doc_id como clave.
            firestore_data[PROJECTS_COLLECTION_PATH][doc_id] = new_project_document

            # 4. Guardar en la simulación de Firestore
            save_firestore_data(firestore_data)

            st.success(
                f"¡Proyecto '{evaluation_name.strip()}' para {selected_client_name} {action_type} con éxito! ID: {doc_id[:8]}...")

            # Si fue un GUARDADO (nuevo), actualizamos el ID de sesión
            if action_type == "Guardado":
                st.session_state.current_project_id = doc_id

            # RECARGA: Forzar la recarga de datos al session_state y rotar la clave del formulario
            load_project_data_callback()
            st.rerun()

# =================================================================
# 6. TABLA PERMANENTE DE PROYECTOS REGISTRADOS
# =================================================================

st.markdown("---")
st.header("Historial de Proyectos Agronomy Analyzer")

projects_data = load_agronomy_projects()

if not projects_data:
    st.info("Aún no hay proyectos de Agronomy Analyzer registrados.")
    st.stop()  # Detener la ejecución si no hay datos para el análisis

df_projects = pd.DataFrame(projects_data)

# Asegurar la existencia de las columnas y recalcular Total_Horas
required_cols = ['Planificacion_Estado', 'Planificacion_Horas', 'Recopilacion_Estado', 'Recopilacion_Horas',
                 'Informe_Estado', 'Informe_Horas', 'Total_Horas']
for col in required_cols:
    if col not in df_projects.columns:
        df_projects[col] = 0 if 'Horas' in col else 'No Iniciado'

df_projects['Total_Horas'] = df_projects['Planificacion_Horas'] + df_projects['Recopilacion_Horas'] + df_projects[
    'Informe_Horas']

# Conversión a datetime para ordenar correctamente
df_projects['Fecha_Registro_dt'] = pd.to_datetime(df_projects['Fecha_Registro'], errors='coerce')
df_projects.sort_values(by='Fecha_Registro_dt', ascending=False, inplace=True)
df_projects.drop(columns=['Fecha_Registro_dt'], inplace=True, errors='ignore')

# Definición de las columnas que queremos mostrar y sus nuevos nombres
column_mapping = {
    'Fecha_Registro': 'Fecha de Registro',
    'Cliente': 'Cliente',
    'Sucursal': 'Sucursal',
    'Perfil_Tecnologico': 'Perfil Tecnológico',
    'Protocolo': 'Protocolo AA',
    'Nombre_Evaluacion': 'Nombre del Proyecto',
    'Ubicacion_Evaluacion': 'Ubicación',
    'Planificacion_Estado': 'Planificación (Estado)',
    'Planificacion_Horas': 'Planificación (h)',
    'Recopilacion_Estado': 'Recopilación (Estado)',
    'Recopilacion_Horas': 'Recopilación (h)',
    'Informe_Estado': 'Informe (Estado)',
    'Informe_Horas': 'Informe (h)',
    'Total_Horas': 'Total Horas'
}

# Seleccionar y renombrar las columnas
df_projects_display = df_projects.rename(columns=column_mapping)
df_projects_display = df_projects_display[
    [col for col in column_mapping.values() if col in df_projects_display.columns]]

st.dataframe(df_projects_display, use_container_width=True, hide_index=True)

# =================================================================
# 7. DASHBOARDS Y ANÁLISIS DE DATOS
# =================================================================

st.markdown("---")
st.header("📊 Análisis de Proyectos")

# --- 7.1 FILTROS ---
col_filter1, col_filter2 = st.columns(2)

all_clients = ['Todos los Clientes'] + df_projects['Cliente'].unique().tolist()
all_protocols = ['Todos los Protocolos'] + df_projects['Protocolo'].unique().tolist()

with col_filter1:
    filter_client = st.multiselect(
        "Filtrar por Cliente",
        options=all_clients[1:],
        default=all_clients[1:]  # Por defecto, selecciona todos
    )

with col_filter2:
    filter_protocol = st.multiselect(
        "Filtrar por Protocolo AA",
        options=all_protocols[1:],
        default=all_protocols[1:]  # Por defecto, selecciona todos
    )

# Aplicar filtros
df_filtered = df_projects.copy()

if filter_client:
    df_filtered = df_filtered[df_filtered['Cliente'].isin(filter_client)]

if filter_protocol:
    df_filtered = df_filtered[df_filtered['Protocolo'].isin(filter_protocol)]

# --- VALIDACIÓN DE DATOS FILTRADOS ---
if df_filtered.empty:
    st.warning("No hay datos disponibles para los filtros seleccionados.")
    st.stop()

# --- 7.2 KPIs Y GRÁFICOS ---
col_kpi, col_chart = st.columns([1, 2])

# 1. KPI de Horas Totales
total_hours = df_filtered['Total_Horas'].sum()

with col_kpi:
    st.metric(
        label="Horas Totales Dedicadas (Filtrado)",
        value=f"{total_hours:,.0f} h",
        delta="Desde el inicio"
    )
    st.markdown("---")

    # 3. Indicador de Proyectos Terminados (Progreso)
    total_projects = len(df_filtered)
    completed_projects = df_filtered[df_filtered['Informe_Estado'] == 'Completado'].shape[0]
    completion_percentage = (completed_projects / total_projects) if total_projects > 0 else 0

    st.subheader("Proyectos Completados")
    st.info(f"Completado: {completed_projects} de {total_projects} Proyectos")
    st.progress(completion_percentage)

    # El slider ahora es un indicador de progreso (Progress Bar)

# 2. Gráfico de Torta de Desglose de Horas por Etapa
stage_hours = {
    'Planificación': df_filtered['Planificacion_Horas'].sum(),
    'Recopilación de Datos': df_filtered['Recopilacion_Horas'].sum(),
    'Generación de Informe': df_filtered['Informe_Horas'].sum()
}

df_stage_hours = pd.DataFrame(
    list(stage_hours.items()),
    columns=['Etapa', 'Horas']
)

# Colores que coinciden con los estados (verde para informe, amarillo para recopilación, gris para planificación)
color_sequence = ['#4CAF50', '#FFC107', '#E0E0E0']  # Verde, Amarillo, Gris

fig = px.pie(
    df_stage_hours,
    values='Horas',
    names='Etapa',
    title='Desglose de Horas por Etapa del Proyecto',
    hole=.3,  # Efecto dona
    color_discrete_sequence=color_sequence
)

fig.update_traces(textposition='inside', textinfo='percent+label')
fig.update_layout(showlegend=True, margin=dict(l=20, r=20, t=30, b=20))

with col_chart:
    st.plotly_chart(fig, use_container_width=True)