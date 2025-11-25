import json
import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(
    page_title="SmartFarm - Conci",
    layout="wide",
    page_icon="sf1.png",
    initial_sidebar_state="collapsed",
)


# =================================================================
# 1. CONFIGURACIÓN DEL ENTORNO Y DATOS MAESTROS (Transformación)
# =================================================================
# Variables de entorno para simulación de Firestore (mantener)
app_id = os.environ.get('__app_id', 'smartfarm_default_app_id')
FIREBASE_COLLECTION_PATH = f'artifacts/{app_id}/public/data/client_scores'
DATA_FILE = "firestore_simulation.json"

# DICCIONARIO MAESTRO CRUDO (Con claves largas, según lo proporcionado por el usuario)
# Esta estructura se utiliza para la transformación interna.
USER_SCORING_PROFILES_RAW = {
    "Granos": {
        "SCORE_MAX": {
            "**Item 1:** Organización y estandarización de lotes.": 5, "**Item 2:** Línea de guiado.": 5,
            "**Item 3:** Organización altamente conectada.": 10, "**Item 4:** Uso de planificador de trabajo.": 15,
            "**Item 5:** Uso de Operations Center Mobile.": 10, "**Item 6:** JDLink.": 5,
            "**Item 7:** Envío remoto. Mezcla de tanque.": 10, "**Item 8:** % uso de autotrac en Tractor.": 10,
            "**Item 9:** % uso autotrac Cosecha.": 10, "**Item 10:** % uso autotrac Pulverización.": 10,
            "**Item 11:** Uso de funcionalidades avanzadas.": 15, "**Item 12:** Uso de tecnologías integradas.": 10,
            "**Item 13:** Señal de corrección StarFire.": 5, "**Item 14:** Paquete CSC.": 10,
            "**Item 15:** Vinculación de API.": 5, "**Item 16:** JDLink en otra marca.": 15
        },
        "ITEM_DESCRIPTIONS": {
            "**Item 1:** Organización y estandarización de lotes.": "Captura de pantalla desde Operations Center: Configuración/ Campos / Campos / Vista tabla. Excel o PDF de vista anterior. **>>Consideraciones:** En el caso de organizaciones con menos del 50% fuera del estándar, la puntuación de este ítem se restablece a cero. Caso contrario se otorgará el puntaje proporcional correspondiente: 50 a 60 % 1 punto | 60 a 70 % 2 puntos | 70 a 80% 3 puntos | 80 a 90 % 4 puntos | más de 90 % 5 puntos.",
            "**Item 2:** Línea de guiado.": "Captura de pantalla desde Operations Center, de la tabla: Configuración/ Campos/ Filtro <campos sin guiado>; y Captura de pantalla desde Operations Center: Configuración/Campos/Campos totales (sin filtro aplicado). **>>Consideraciones:** Será requisito para obtener los 5 puntos, que el 20% de los lotes cuenten con guiado.",
            "**Item 3:** Organización altamente conectada.": "Al menos un campo con tres tipos de labores cargadas.",
            "**Item 4:** Uso de planificador de trabajo.": "Video demostrativo de los Planes de Trabajo enviados al equipo durante los últimos 12 meses, al menos 4 meses antes de la presentación de la evidencia. **>>Consideraciones:** En los últimos 12 meses tener al menos una operación de cada una de las 3 etapas (siembra - pulverización - cosecha) en la cual se haya utilizando el planificador de trabajo. El trabajo necesariamente debe haber sido enviado al equipo y debe tener al menos un 20% de avance. Cada etapa contabiliza 5 puntos, siendo posible acumular 15 puntos al utilizar el planificador de trabajo en las 3 etapas.",
            "**Item 5:** Uso de Operations Center Mobile.": "Grabación de video que demuestre la navegación en la plataforma Móvil, capturando la pantalla inicial y demostrando información de al menos un equipo y un mapa agronómico y la vista del planificador de trabajo. La ausencia de cualquiera de los ítems descritos anteriormente se considerará puntuación cero para este ítem; y Video del cliente mencionando los beneficios obtenidos al utilizar el Centro de Operaciones, hablando de al menos una ganancia al utilizarlo. **>>Consideraciones:** Al ser un testimonio auténtico y reciente creado para la evaluación de este ítem describiendo la principal funcionalidad utilizada (planificador de trabajo, alertas, analizador de campo) debe incluir un testimonio del cliente y/o miembros de su equipo. Serán descalificados los vídeos grabados que demuestren operaciones del Distribuidor y/o de terceros. Vídeo con una duración mínima de 1,5 minutos y máxima de 3 minutos.",
            "**Item 6:** JDLink.": "Captura de pantalla desde Operations Center de la pestaña Equipo, que demuestre el Servicio de Conectividad JDLink; y Captura pantalla sin fitro, donde se visualice el total de máquinas. **>>Consideraciones:** En el caso de organizaciones con menos del 30% de máquinas con servicio de conectividad activado, la puntuación de este ítem se restablece a cero. Se otorgará el puntaje proporcional correspondiente: 30 a 40 % 1 punto | 40 a 50% 2 puntos | 50 a 60% 3 puntos | 60 a 70 % 4 puntos | más de 70% 5 puntos. Los dispositivos pendientes de transferencia y/o inactivos no se contarán.",
            "**Item 7:** Envío remoto. Mezcla de tanque.": "Captura de pantalla desde Operations Center donde se vea una mezcla de tanque generada; o Captura de pantalla desde SIA evidenciando uso de ordenes de trabajo. **>>Consideraciones:** Para el caso de SIA los puntajes impactarán según se detalla a continuación: 20 a 30% 1 puntos | 30 a 40% 2 puntos | 40 a 50 % 5 puntos | más de 50% 10 puntos.",
            "**Item 8:** % uso de autotrac en Tractor.": "Captura de pantalla en analizador de máquina/ uso de tecnología donde se muestren todos los equipos de la organización. **>>Consideraciones:** Se solicitará en promedio, un 40% de uso de autotrac en tractores de mas de 140 hp.",
            "**Item 9:** % uso autotrac Cosecha.": "Captura de pantalla en analizador de máquina/ uso de tecnología donde se muestren todos los equipos de la organización. **>>Consideraciones:** Se solicitará en promedio, un 70% de uso de autotrac en cosechadoras.",
            "**Item 10:** % uso autotrac Pulverización.": "Captura de pantalla en analizador de máquina/ uso de tecnología donde se muestren todos los equipos de la organización. **>>Consideraciones:** Se solicitará en promedio, un 70% de uso de autotrac en pulverizadoras.",
            "**Item 11:** Uso de funcionalidades avanzadas.": "Reporte de uso de funcionalidades avanzadas: 7 Puntos | Vídeo testimonio de cliente que demuestre el uso de funcionalidades avanzadas: 8 puntos. **>>Consideraciones:** Sólo se considerarán videos que describan la fecha de la operación, la cual debe ser en el año agrícola en curso. El vídeo deberá registrar el testimonio por parte del cliente y/o miembros de su equipo. Serán descalificados los vídeos grabados que demuestren operaciones del Distribuidor y/o de terceros.",
            "**Item 12:** Uso de tecnologías integradas.": "Captura de pantalla desde Operations Center, que evidencie el uso de tecnologías integradas. **>>Consideraciones:** Combine Advisor/ActiveYield: 4 puntos | ExactApply: 3 puntos | Control de sección: 3 puntos",
            "**Item 13:** Señal de corrección StarFire.": "Captura de pantalla desde Operations Center en Analizador de máquina/uso de tecnología. **>>Consideraciones:** Señal de corrección StarFire y/o RTK (SF2, SF3, SF-RTK y RTK) en al menos en una etapa del ciclo productivo. Se obtendrá 1 punto extra dentro del item si se utiliza señal SF-RTK.",
            "**Item 14:** Paquete CSC.": "Factura del paquete contratado.",
            "**Item 15:** Vinculación de API.": "Captura de pantalla desde Operations Center: Configuración / Conexiones / Seleccionar la herramienta conectada / Administrar / Organizaciones conectadas. **>>Consideraciones:** La fecha de conexión, que debe ser mayor a 4 meses desde la fecha de envío del informe.",
            "**Item 16:** JDLink en otra marca.": "Captura de pantalla desde <Equipos> en Operations Center."
        }
    },
    "Ganadería": {
        "SCORE_MAX": {  # 13 Ítems - Total Máximo: 130
            "**Item 1:** Organización y estandarización de lotes.": 15,
            "**Item 2:** Digitalizar capa de siembra y mapa de picado.": 10,
            "**Item 3:** Uso de planificador de trabajo.": 20,
            "**Item 4:** Equipo registrados en el Centro de Operaciones.": 5,
            "**Item 5:** Operadores registrados en el Centro de Operaciones.": 5,
            "**Item 6:** Productos registrados en el Centro de Operaciones.": 5,
            "**Item 7:** Uso de Operations Center Mobile.": 10,
            "**Item 8:** JDLink activado en máquinas John Deere.": 10,
            "**Item 9:** Planes de mantenimiento en tractores.": 10,
            "**Item 10:** Mapeo de constituyentes.": 20,
            "**Item 11:** Conectividad alimentación.": 20,
            "**Item 12:** Generación de informes.": 10,
            "**Item 13:** Paquete contratado con el concesionario (CSC).": 10
        },
        "ITEM_DESCRIPTIONS": {
            "**Item 1:** Organización y estandarización de lotes.": "Captura de pantalla desde Operations Center: Configuración/ Campos / Campos / Vista tabla. Excel o PDF de vista anterior. **>>Consideraciones:** En el caso de organizaciones con menos del 50% fuera del estándar, la puntuación de este ítem se restablece a cero. Caso contrario se otorgará el puntaje proporcional correspondiente: 50 a 60 % 1 punto | 60 a 70 % 3 puntos | 70 a 80% 9 puntos | 80 a 90 % 12 puntos | más de 90 % 15 puntos.",
            "**Item 2:** Digitalizar capa de siembra y mapa de picado.": "En al menos un lote tener digitalizada la capa de siembra y mapa de picado , que se evidenciará con una Captura de pantalla en el Analizador de Trabajo con la herramienta <comparar> , en la que se muestre el mapa de siembra y el mapa de picado dentro de la campaña. **>>Consideraciones:** Adicional de 5 puntos si se realizó alguna labor de manera variable (siembra o fertilización). Adicional de 5 puntos si en el lote hay lineas de guiado.",
            "**Item 3:** Uso de planificador de trabajo.": "En los últimos 12 meses tener al menos una operación de cada una de las 3 etapas utilizando el planificador de trabajo. **>>Consideraciones:** Siembra vale 6 puntos | Pulverización 7 puntos | Cosecha 7 puntos | Las 3 etapas acumulan 20 puntos.",
            "**Item 4:** Equipo registrados en el Centro de Operaciones.": "Video demostrativo de la organización donde se vea dos equipos y al menos un implemento asociado a la alimentación en cargador frontal.",
            "**Item 5:** Operadores registrados en el Centro de Operaciones.": "Video que demuestra el registro de al menos un empleado en la pestaña equipo en Operations Center.",
            "**Item 6:** Productos registrados en el Centro de Operaciones.": "Video de la pestaña <Productos> demostrando los químicos, variedades, fertilizantes, mezcla (si se usa), con al menos un producto químico o variedad registrada.",
            "**Item 7:** Uso de Operations Center Mobile.": "Grabación de video que demuestre la navegación en la plataforma Móvil, capturando la pantalla inicial y demostrando información de al menos un equipo y un mapa agronómico y la vista del planificador de trabajo. La ausencia de cualquiera de los ítems descritos anteriormente se considerará puntuación cero para este ítem; y Testimonio de cliente con el beneficio de utilizar el Centro de Operaciones mencionando los beneficios obtenidos al utilizar el Centro de Operaciones, hablando de al menos una ganancia al utilizarlo. **>>Consideraciones:** Al ser un testimonio auténtico y reciente creado para la evaluación de este ítem describiendo la principal funcionalidad utilizada (planificador de trabajo, alertas, analizador de campo) debe incluir un testimonio del cliente y/o miembros de su equipo. Serán descalificados los vídeos grabados que demuestren operaciones del Distribuidor y/o de terceros. Vídeo con una duración mínima de 1,5 minutos y máxima de 3 minutos.",
            "**Item 8:** JDLink activado en máquinas John Deere.": "Captura de pantalla desde Operations Center de la pestaña Equipo, que demuestre el Servicio de Conectividad JDLink; y Captura pantalla sin filtro, donde se visualice el total de máquinas. **>>Consideraciones:** En el caso de organizaciones con menos del 30% de máquinas con servicio de conectividad activado, la puntuación de este ítem se restablece a cero. Se otorgará el puntaje proporcional correspondiente: 30 a 40 % 1 punto | 40 a 50% 2 puntos | 50 a 60% 4 puntos | 60 a 70 % 6 puntos | más de 70% 10 puntos. Los dispositivos pendientes de transferencia y/o inactivos no se contarán.",
            "**Item 9:** Planes de mantenimiento en tractores.": "Captura de pantalla de los planes de mantenimiento asociado a tractores responsables de la alimentación.",
            "**Item 10:** Mapeo de constituyentes.": "10 puntos con al menos un mapa de constituyentes en los últimos 12 meses. 10 puntos por testimonial de importancia de sensado de constituyentes.",
            "**Item 11:** Conectividad alimentación.": "Al menos un tractor con conectividad visible en Operations Center. Evidencia captura de pantalla o video demostrando el recorrido en el patio de comida.",
            "**Item 12:** Generación de informes.": "Captura de pantalla desde Archivos/ Informes donde se visualice al menos un informe de máquina generado en los últimos doce meses. La fecha debe ser mayor a 4 meses desde la fecha de envío del informe.",
            "**Item 13:** Paquete contratado con el concesionario (CSC).": "Factura del paquete contratado."
        }
    },
    "Cultivos de Alto Valor": {
        "SCORE_MAX": {  # 14 Ítems - Total Máximo: 135
            "**Item 1:** Organización y estandarización de lotes.": 15,
            "**Item 2:** Lineas de guiado.": 5,
            "**Item 3:** Tener al menos una labor digitalizada.": 10,
            "**Item 4:** Uso de planificador de trabajo para alguna operación.": 15,
            "**Item 5:** Uso del Operations Center Mobile.": 10,
            "**Item 6:** JDLink activado en máquinas John Deere.": 10,
            "**Item 7:** % uso de autotrac en Tractor.": 20,
            "**Item 8:** Implement Guidance.": 20,
            "**Item 9:** Señal de corrección StarFire.": 10,
            "**Item 10:** Paquete contratado con el concesionario (CSC).": 10,
            "**Item 11:** Equipos Registrados en Operations Center.": 5,
            "**Item 12:** Operadores registrados en Operations Center.": 5,
            "**Item 13:** Productos registrados en el Operations Center.": 5,
            "**Item 14:** Configuración de Alertas Personalizables.": 10
        },
        "ITEM_DESCRIPTIONS": {
            "**Item 1:** Organización y estandarización de lotes.": "Captura de pantalla desde Operations Center: Configuración/ Campos / Campos / Vista tabla. Excel o PDF de vista anterior. **>>Consideraciones:** En el caso de organizaciones con menos del 50% fuera del estándar, la puntuación de este ítem se restablece a cero. Caso contrario se otorgará el puntaje proporcional correspondiente: 50 a 60 % 1 punto | 60 a 70 % 3 puntos | 70 a 80% 9 puntos | 80 a 90 % 12 puntos | más de 90 % 15 puntos.",
            "**Item 2:** Lineas de guiado.": "Captura de pantalla desde Operations Center, de la tabla: Configuración/ Campos/ Filtro <campos sin guiado> y, Captura de pantalla desde Operations Center: Configuración/Campos/Campos totales (sin filtro aplicado). **>>Consideraciones:** Será requisito para obtener los 5 puntos, que el 20% de los lotes cuenten con guiado.",
            "**Item 3:** Tener al menos una labor digitalizada.": "Tener una operación digitalizada. Presentar el pdf del informe del Analizador de Trabajo de cualquier operación, ya sea preparación de suelo, siembra, pulverización o cosecha que se haya realizado.",
            "**Item 4:** Uso de planificador de trabajo para alguna operación.": "Captura de pantalla en la sección planificador de trabajo con al menos un trabajo enviado en los últimos 12 meses",
            "**Item 5:** Uso del Operations Center Mobile.": "Grabación de video que demuestre la navegación en la plataforma Móvil, capturando la pantalla inicial y demostrando información de al menos un equipo y un mapa agronómico y la vista del planificador de trabajo. La ausencia de cualquiera de los ítems descritos anteriormente se considerará puntuación cero para este ítem y, Video del cliente mencionando los beneficios obtenidos al utilizar el Centro de Operaciones, hablando de al menos una ganancia al utilizarlo. **>>Consideraciones:** Al ser un testimonio auténtico y reciente creado para la evaluación de este ítem describiendo la principal funcionalidad utilizada (planificador de trabajo, alertas, analizador de campo) debe incluir un testimonio del cliente y/o miembros de su equipo. Serán descalificados los vídeos grabados que demuestren operaciones del Distribuidor y/o de terceros. Vídeo con una duración mínima de 1,5 minutos y máxima de 3 minutos.",
            "**Item 6:** JDLink activado en máquinas John Deere.": "Captura de pantalla desde Operations Center de la pestaña Equipo, que demuestre el Servicio de Conectividad JDLink; y Captura pantalla sin filtro, donde se visualice el total de máquinas. **>>Consideraciones:** En el caso de organizaciones con menos del 30% de máquinas con servicio de conectividad activado, la puntuación de este ítem se restablece a cero. Se otorgará el puntaje proporcional correspondiente: 30 a 40 % 1 punto | 40 a 50% 2 puntos | 50 a 60% 4 puntos | 60 a 70 % 6 puntos | más de 70% 10 puntos. Los dispositivos pendientes de transferencia y/o inactivos no se contarán.",
            "**Item 7:** % uso de autotrac en Tractor.": "Captura de pantalla en analizador de máquina/ uso de tecnología donde se muestren todos los equipos de la organización. **>>Consideraciones:** Se solicitará en promedio, un 30% de uso de autotrac en tractores de mas de 140 hp.",
            "**Item 8:** Implement Guidance.": "Vídeo testimonio de cliente de funcionalidad avanzada. Solo se considerarán videos que describan la fecha de la operación, la cual debe ser en el año agrícola en curso. El vídeo deberá registrar el testimonio por parte del cliente y/o miembros de su equipo. Serán descalificados los vídeos grabados que demuestren operaciones del Distribuidor y/o de terceros. **>>Consideraciones:** Puede considerarse nivelación para México.",
            "**Item 9:** Señal de corrección StarFire.": "Captura de pantalla desde Operations Center en Analizador de máquina/uso de tecnología. **>>Consideraciones:** Señal de corrección StarFire y/o RTK (SF2, SF3, SF-RTK y RTK) en al menos en una etapa del ciclo productivo. Se obtendrá 1 punto extra dentro del item si se utiliza señal SF-RTK.",
            "**Item 10:** Paquete contratado con el concesionario (CSC).": "Factura del paquete contratado.",
            "**Item 11:** Equipos Registrados en Operations Center.": "Video demostrativo de la organización donde se vea dos equipos y al menos un implemento.",
            "**Item 12:** Operadores registrados en Operations Center.": "Video que demuestra el registro de al menos un empleado en la pestaña equipo en Operations Center.",
            "**Item 13:** Productos registrados en el Operations Center.": "Video de la pestaña Productos demostrando los químicos, variedades, fertilizantes, mezcla (si se usa), con al menos un producto químico o variedad registrada.",
            "**Item 14:** Configuración de Alertas Personalizables.": "Captura de pantalla de alguna alerta personalizable mostrando la fecha que debe ser mayor a 4 meses desde la fecha del envío del informe."
        }
    }
}


# Función para transformar el diccionario complejo en la estructura interna necesaria
def transform_profile(user_profile, prefix):
    score_max = {}
    item_titles = {}
    item_descriptions = {}

    # Itera a través de los ítems en el orden en que aparecen para mapear a claves cortas
    for i, (title, max_score) in enumerate(user_profile["SCORE_MAX"].items()):
        internal_key = f"{prefix}_Item_{i + 1}"

        # score_max y item_titles utilizan la clave interna, pero almacenan el valor máximo y el título completo.
        score_max[internal_key] = max_score
        item_titles[internal_key] = title
        item_descriptions[internal_key] = user_profile["ITEM_DESCRIPTIONS"].get(title, "Descripción no disponible.")

    return {
        "SCORE_MAX": score_max,
        "ITEM_TITLES": item_titles,
        "ITEM_DESCRIPTIONS": item_descriptions
    }


# Aplicar la transformación a los perfiles
SCORING_PROFILES = {
    "Granos": transform_profile(USER_SCORING_PROFILES_RAW["Granos"], "GR"),
    "Ganadería": transform_profile(USER_SCORING_PROFILES_RAW["Ganadería"], "G"),
    "Cultivos de Alto Valor": transform_profile(USER_SCORING_PROFILES_RAW["Cultivos de Alto Valor"], "AV")
}

ALL_CATEGORIES = list(SCORING_PROFILES.keys())


# Inicialización de la simulación de la base de datos
def load_client_data_db():
    """Simula la obtención de todos los documentos de la colección de Firestore."""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                firestore_data = json.load(f)
                # La lista de valores de documentos es lo que se convierte a DataFrame
                return list(firestore_data.get(FIREBASE_COLLECTION_PATH, {}).values())
        else:
            return []
    except Exception as e:
        st.error(f"Error al cargar datos simulados: {e}")
        return []


# =================================================================
# 2. INTERFAZ DE FILTRADO Y SELECCIÓN
# =================================================================
st.image(
    "banner_sf.png",
    )
st.title("Resultado SmartFarm ⭐")

data_from_db = load_client_data_db()

if not data_from_db:
    st.info("No hay datos de clientes registrados para analizar.")
    st.stop()

df_full = pd.DataFrame(data_from_db)

col_cat, col_client = st.columns(2)

with col_cat:
    selected_category = st.selectbox(
        "1. Categoría:",
        options=ALL_CATEGORIES,
        index=0
    )

# 3. FILTRADO POR CATEGORÍA
df_filtered = df_full[df_full['Categoria_Evaluacion'] == selected_category].copy()

if df_filtered.empty:
    st.warning(f"No hay clientes registrados en la categoría '{selected_category}'.")
    st.stop()

# Cargar la configuración de la categoría seleccionada
current_profile = SCORING_PROFILES[selected_category]
score_max_dict = current_profile["SCORE_MAX"]
item_titles_dict = current_profile["ITEM_TITLES"]
score_cols_internal = list(score_max_dict.keys())
total_max_score = sum(score_max_dict.values())

# Obtener los títulos completos (que son las claves de las columnas en el DataFrame si se cargó correctamente)
score_cols_full_titles = [item_titles_dict[k] for k in score_cols_internal]

# Asegurar que todas las columnas de títulos completos existan para el cálculo (rellenando NaNs con 0)
for col in score_cols_full_titles:
    if col not in df_filtered.columns:
        df_filtered[col] = 0

# CÁLCULO DE PUNTAJE TOTAL Y RENDIMIENTO (USANDO LAS CLAVES COMPLETAS DEL DATAFRAME)
df_filtered['Puntaje Total'] = df_filtered[score_cols_full_titles].sum(axis=1)
df_filtered['Rendimiento (%)'] = (df_filtered['Puntaje Total'] / total_max_score * 100).round(1)

# 4. SELECCIÓN DE CLIENTE
with col_client:
    client_names = df_filtered['Cliente'].unique().tolist()
    selected_client_name = st.selectbox(
        "2. Cliente:",
        options=client_names,
        index=0 if client_names else None
    )

if not selected_client_name:
    st.info("Selecciona un cliente para continuar.")
    st.stop()

# Obtener los datos del cliente seleccionado
client_data = df_filtered[df_filtered['Cliente'] == selected_client_name].iloc[0]
client_score = client_data['Puntaje Total']
client_performance = client_data['Rendimiento (%)']

st.markdown("---")
st.header(f"Resultados de Puntuación para {selected_client_name}")

# =================================================================
# 5. K P I s y Resumen General (Ajuste de transparencia en Rendimiento)
# =================================================================

# Determinar el color del rendimiento (texto)
if client_performance >= 80:
    color = "green"
elif client_performance >= 50:
    color = "orange"
else:
    color = "red"

col_kpi_1, col_kpi_2, col_kpi_3 = st.columns(3)

with col_kpi_1:
    st.metric("Puntaje Total Obtenido", f"{client_score:.1f} pts", f"Máx. {total_max_score} pts")
with col_kpi_2:
    # Ajuste de transparencia: Usar fondo blanco semi-transparente
    st.markdown(f"""
    <div style="background-color: rgba(255, 255, 255, 0.5); padding: 10px; border-radius: 5px; border: 0px solid #ddd; text-align: center;">
        <p style="font-size: 14px; color: #555; margin-bottom: 0;">Rendimiento General</p>
        <p style="font-size: 32px; font-weight: bold; color: {color}; margin-top: 5px;">{client_performance}%</p>
    </div>
    """, unsafe_allow_html=True)
with col_kpi_3:
    st.metric("Sucursal Registrada", client_data['Sucursal'])

# =================================================================
# 6. TABLA DE ANÁLISIS DETALLADO POR ÍTEM
# =================================================================

st.subheader("Puntuación Detallada por Ítem")
st.caption("Comparativa de la puntuación obtenida vs. la puntuación máxima posible para cada criterio.")

detailed_results = []
for internal_key in score_cols_internal:
    max_score = score_max_dict[internal_key]

    # Usar el título completo para obtener el puntaje del DataFrame
    item_title_full = item_titles_dict[internal_key]
    client_score_item = client_data.get(item_title_full, 0)  # Acceso con la clave de título completo

    # Calcular el % de cumplimiento
    achievement_percent = (client_score_item / max_score * 100).round(1) if max_score > 0 else 0

    # Obtener el título descriptivo para la tabla
    item_title = item_title_full.replace('**', '')

    detailed_results.append({
        'Ítem de Evaluación': item_title,
        'Puntaje Máx.': max_score,
        'Puntaje Obtenido': client_score_item,
        '% de Cumplimiento': f"{achievement_percent}%"
    })

df_detailed = pd.DataFrame(detailed_results)
st.table(df_detailed)

# =================================================================
# 7. GRÁFICO RADAR (Cumplimiento vs. Máximo)
# =================================================================

st.subheader("Gráfico de Fortalezas (Cumplimiento por Ítem)")

radar_labels = df_detailed['Ítem de Evaluación'].tolist()
# Convertir el % de cumplimiento a flotante para el gráfico
radar_values = [float(p.strip('%')) for p in df_detailed['% de Cumplimiento'].tolist()]

fig_radar = go.Figure(data=[
    go.Scatterpolar(
        r=radar_values,
        theta=radar_labels,
        fill='toself',
        line_color='rgb(46, 125, 50)',
        fillcolor='rgba(46, 125, 50, 0.4)',
        name=selected_client_name
    )
])

fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 100],
            tickvals=[0, 25, 50, 75, 100],
            ticktext=['0%', '25%', '50%', '75%', '100%'],
            title='Cumplimiento (%)'
        ),
        bgcolor="rgba(0,0,0,0)"
    ),
    showlegend=False,
    title=f"Rendimiento Detallado del Cliente '{selected_client_name}'"
)

st.plotly_chart(fig_radar, use_container_width=True)

# =================================================================
# 8. RECUADRO DE RECOMENDACIONES (Nuevo)
# =================================================================
st.markdown("---")
st.header("📝 Recomendaciones y Plan de Acción")

# Se añade un text_area para la entrada de texto de las recomendaciones.
recommendations = st.text_area(
    "",
    height=150,
    placeholder="Ej: Se recomienda enfocar los esfuerzos en la digitalización de la Línea de Guiado (Item 2), ya que actualmente solo se ha alcanzado un 10% del puntaje máximo. Programar una visita para capacitación en Operations Center...",
    key=f"recommendations_{selected_client_name}_{selected_category}"
    # Clave única para que recuerde el texto por cliente
)

# Opcional: Si deseas guardar las recomendaciones en la base de datos simulada en el futuro,
# necesitarías un botón de guardar y la lógica de Firebase/simulación correspondiente.
# Por ahora, solo es un recuadro de texto.
if recommendations:

    st.success("Recomendaciones listas para la discusión con el cliente.")
