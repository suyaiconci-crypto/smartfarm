import json
import os
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="SmartFarm - Conci",
    layout="wide",
    page_icon="sf1.png",
    initial_sidebar_state="collapsed",
)

# =================================================================
# REPLICACIÓN DE CONFIGURACIÓN DE LA APP PRINCIPAL
# =================================================================
# Obtener el ID de la aplicación para crear una ruta única en la simulación de Firestore
app_id = os.environ.get('__app_id', 'smartfarm_default_app_id')
FIREBASE_COLLECTION_PATH = f'artifacts/{app_id}/public/data/client_scores'
DATA_FILE = "firestore_simulation.json"


# Inicialización de la simulación de la base de datos
def save_to_json():
    """Guarda el diccionario de datos de Firestore simulado en el archivo JSON."""
    try:
        if 'firestore_data' in st.session_state:
            with open(DATA_FILE, 'w') as f:
                json.dump(st.session_state.firestore_data, f, indent=4)
    except Exception as e:
        st.error(f"Error al guardar datos simulados en JSON: {e}")


if 'db_initialized' not in st.session_state:
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                st.session_state.firestore_data = json.load(f)
        else:
            st.session_state.firestore_data = {}
    except:
        st.session_state.firestore_data = {}

    if FIREBASE_COLLECTION_PATH not in st.session_state.firestore_data:
        st.session_state.firestore_data[FIREBASE_COLLECTION_PATH] = {}
        save_to_json()
    st.session_state.db_initialized = True


# =================================================================
# FUNCIONES DE INTERACCIÓN CON FIREBASE (SIMULADAS)
# =================================================================

def load_client_data_db():
    """Simula la obtención de todos los documentos de la colección de Firestore."""
    collection_data = st.session_state.firestore_data.get(FIREBASE_COLLECTION_PATH, {})
    return list(collection_data.values())


def save_client_data_db(doc_id, record):
    """Simula guardar un nuevo documento en Firestore."""

    # 1. Verificar si el ID ya existe
    collection_data = st.session_state.firestore_data.get(FIREBASE_COLLECTION_PATH, {})
    if doc_id in collection_data:
        st.error(f"El ID de Cliente '{doc_id}' ya existe. Por favor, usa un ID único.")
        return False

    # 2. Agregar el ID al registro y guardar
    record['ID_Cliente'] = doc_id
    st.session_state.firestore_data[FIREBASE_COLLECTION_PATH][doc_id] = record
    save_to_json()
    st.success(
        f"Puntuación del cliente '{record['Cliente']}' de '{record['Categoria_Evaluacion']}' guardada exitosamente.")
    return True


def update_client_record_db(doc_id, updated_record):
    """Simula la actualización de un documento existente en Firestore."""
    if doc_id in st.session_state.firestore_data[FIREBASE_COLLECTION_PATH]:
        st.session_state.firestore_data[FIREBASE_COLLECTION_PATH][doc_id].update(updated_record)
        save_to_json()
        return True
    return False


def delete_client_record_db(doc_id):
    """Simula la eliminación de un documento en Firestore."""
    if doc_id in st.session_state.firestore_data[FIREBASE_COLLECTION_PATH]:
        del st.session_state.firestore_data[FIREBASE_COLLECTION_PATH][doc_id]
        save_to_json()
        return True
    return False


# --- CONFIGURACIÓN DE PUNTOS Y DATOS MULTI-CATEGORÍA ---

SUCURSAL_OPTIONS = ["Córdoba", "Sinsacate", "Pilar", "Arroyito", "Santa Rosa"]
PERFIL_OPTIONS = ["Tipo 1", "Tipo 2", "Tipo 3"]

# Diccionario Maestro que define los items, máximos y descripciones para cada categoría
SCORING_PROFILES = {
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
            "**Item 1:** Organización y estandarización de lotes.": "Captura de pantalla desde Operations Center: Configuración/ Campos / Campos / Vista tabla. Excel o PDF de vista anterior. **>>Consideraciones:**  En el caso de organizaciones con menos del 50% fuera del estándar, la puntuación de este ítem se restablece a cero. Caso contrario se otorgará el puntaje proporcional correspondiente: 50 a 60 % 1 punto | 60 a 70 % 3 puntos | 70 a 80% 9 puntos | 80 a 90 % 12 puntos | más de 90 % 15 puntos.",
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
            "**Item 1:** Organización y estandarización de lotes.": "Captura de pantalla desde Operations Center: Configuración/ Campos / Campos / Vista tabla. Excel o PDF de vista anterior. **>>Consideraciones:**  En el caso de organizaciones con menos del 50% fuera del estándar, la puntuación de este ítem se restablece a cero. Caso contrario se otorgará el puntaje proporcional correspondiente: 50 a 60 % 1 punto | 60 a 70 % 3 puntos | 70 a 80% 9 puntos | 80 a 90 % 12 puntos | más de 90 % 15 puntos.",
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

ALL_CATEGORIES = list(SCORING_PROFILES.keys())
METADATA_COLUMNS = ["ID_Cliente", "Cliente", "Categoria_Evaluacion", "Sucursal", "Perfil Tecnológico"]

# --- 2. FORMULARIO DE INGRESO ---

st.title("📝 Ingreso y Seguimiento de Puntuación SmartFarm")
st.subheader("Registra los datos del cliente y su perfil tecnológico.")

with st.form("client_scoring_form", clear_on_submit=True):
    st.markdown("### Datos de Identificación")

    col1, col2, col3, col4, col5 = st.columns([1.5, 2, 2, 2, 1.5])

    with col1:
        # Selección de la categoría de evaluación (NUEVO)
        scoring_category = st.selectbox(
            "Categoría de Evaluación",
            options=ALL_CATEGORIES,
            index=0
        )

    # Resto de metadatos en otras columnas
    with col2:
        client_id = st.text_input("ID Cliente", placeholder="123456")
    with col3:
        client_name = st.text_input("Cliente", placeholder="Nombre del Cliente")
    with col4:
        branch = st.selectbox("Sucursal", options=SUCURSAL_OPTIONS)
    with col5:
        profile = st.selectbox("Perfil Tecnológico", options=PERFIL_OPTIONS)

    st.markdown("---")
    st.markdown(f"### Puntuación Detallada: {scoring_category}")

    # Cargar los datos dinámicos según la categoría seleccionada
    current_profile = SCORING_PROFILES[scoring_category]
    score_max = current_profile["SCORE_MAX"]
    item_descriptions = current_profile["ITEM_DESCRIPTIONS"]

    scores = {}

    for item, max_score in score_max.items():
        # 1. Slider para la puntuación
        scores[item] = st.slider(
            f"{item} (Máx: {max_score})",
            min_value=0,
            max_value=max_score,
            value=0,
            key=f"slider_{scoring_category}_{item.replace(' ', '_').replace('**', '').replace(':', '')}"
        )

        # 2. Texto descriptivo debajo del slider (st.caption)
        st.caption(f"_{item_descriptions.get(item, 'Detalle no disponible.')}_")

        # Separador visual
        st.markdown("---")

    submitted = st.form_submit_button("💾 Guardar Cliente y Puntuación (Nuevo)")

    if submitted:
        if not client_id:
            st.error("🚨 El campo 'ID Cliente' es obligatorio para guardar el registro.")
        elif not client_name:
            st.error("Por favor, ingresa el nombre del Cliente para guardar el registro.")
        else:
            new_record = {
                "Cliente": client_name,
                "Categoria_Evaluacion": scoring_category,  # Guardar la categoría
                "Sucursal": branch,
                "Perfil Tecnológico": profile
            }
            new_record.update(scores)

            if save_client_data_db(client_id, new_record):
                st.rerun()

            # --- 3. TABLA DE RESULTADOS SEPARADAS POR CATEGORÍA ---
st.markdown("---")
st.header("📋 Clientes Registrados por Categoría")

# Cargar los datos guardados de forma persistente
data_from_db = load_client_data_db()

if data_from_db:
    df_results_full = pd.DataFrame(data_from_db)

    # Botones de acción centralizados
    action_cols = st.columns(1)

    # El data_editor principal será para el borrado/edición general
    with action_cols[0]:
        st.caption("Usa esta tabla para ediciones de **metadatos** y eliminaciones (Editable).")
        # Mostrar todas las columnas necesarias para edición
        base_cols = ["ID_Cliente", "Cliente", "Categoria_Evaluacion", "Sucursal", "Perfil Tecnológico"]

        # Crear una columna de puntaje total, para fines de visualización general
        df_results_full['Puntaje Total'] = 0

        # Obtenemos todas las columnas de puntaje posibles de todos los perfiles
        all_score_columns = []
        for profile_data in SCORING_PROFILES.values():
            all_score_columns.extend(profile_data["SCORE_MAX"].keys())
        all_score_columns = list(set(all_score_columns))  # Eliminar duplicados

        # Aseguramos que todas las columnas de puntaje existan en el DataFrame (rellenando con 0 donde no aplican)
        for col in all_score_columns:
            if col not in df_results_full.columns:
                df_results_full[col] = 0

        # Calcular el puntaje total de forma dinámica
        for index, row in df_results_full.iterrows():
            category = row['Categoria_Evaluacion']
            if category in SCORING_PROFILES:
                score_cols = list(SCORING_PROFILES[category]["SCORE_MAX"].keys())
                df_results_full.loc[index, 'Puntaje Total'] = row[score_cols].sum()

        display_cols = base_cols + ['Puntaje Total']
        df_results_editor = df_results_full[display_cols].copy()

        # Definir configuraciones básicas para edición
        editor_config = {
            "ID_Cliente": st.column_config.Column("ID_Cliente", disabled=True),
            "Categoria_Evaluacion": st.column_config.Column("Categoría", disabled=True),
            "Puntaje Total": st.column_config.Column("Puntaje Total", disabled=True),
            "Sucursal": st.column_config.SelectboxColumn("Sucursal", options=SUCURSAL_OPTIONS),
            "Perfil Tecnológico": st.column_config.SelectboxColumn("Perfil Tecnológico", options=PERFIL_OPTIONS)
        }

        edited_df_display = st.data_editor(
            df_results_editor,
            key="client_editor_master",
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            column_config=editor_config
        )

        if st.button("✅ Aplicar Cambios y Guardar", type="primary"):
            # Lógica de actualización y borrado
            changes = st.session_state.client_editor_master

            # 1. Manejar Eliminaciones
            deleted_indices = changes.get("deleted_rows", [])
            if deleted_indices:
                deleted_count = 0
                for idx in deleted_indices:
                    doc_id_to_delete = df_results_editor.iloc[idx]['ID_Cliente']
                    if delete_client_record_db(doc_id_to_delete):
                        deleted_count += 1
                st.info(f"🗑️ Se eliminaron {deleted_count} cliente(s).")

            # 2. Manejar Actualizaciones/Ediciones (solo metadatos)
            edited_rows = changes.get("edited_rows", {})
            if edited_rows:
                updated_count = 0
                for idx, edits in edited_rows.items():
                    doc_id_to_update = df_results_editor.iloc[idx]['ID_Cliente']

                    # Filtramos para solo guardar los metadatos editables de esta tabla
                    metadata_edits = {k: v for k, v in edits.items() if
                                      k in ["Cliente", "Sucursal", "Perfil Tecnológico"]}

                    if metadata_edits and update_client_record_db(doc_id_to_update, metadata_edits):
                        updated_count += 1
                if updated_count > 0:
                    st.success(f"✏️ Se actualizaron {updated_count} registro(s) (metadatos).")

            st.rerun()

    st.markdown("---")
    # --- Mostrar tablas separadas y detalladas por categoría (Solo visualización) ---

    for category in ALL_CATEGORIES:
        # 1. Filtrar el DataFrame por la categoría actual
        df_filtered = df_results_full[df_results_full['Categoria_Evaluacion'] == category].copy()

        if not df_filtered.empty:
            st.markdown(f"#### Resultados de la Categoría: **{category}**")

            # 2. Obtener las columnas de puntaje específicas para esta categoría
            score_cols_specific = list(SCORING_PROFILES[category]["SCORE_MAX"].keys())
            total_max_score = sum(SCORING_PROFILES[category]["SCORE_MAX"].values())

            st.caption(f"Puntaje Total Máximo Posible: {total_max_score} puntos")

            # 3. Columnas a mostrar en esta tabla
            display_cols_category = ["ID_Cliente", "Cliente", "Sucursal",
                                     "Perfil Tecnológico"] + score_cols_specific + ['Puntaje Total']

            # Asegurar que solo existen las columnas necesarias y rellenar nulos si es necesario (para clientes incompletos)
            df_display = df_filtered[display_cols_category].fillna(0)

            # 4. Mostrar la tabla (usamos st.dataframe para que no interfiera con el editor principal)
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True
            )
            st.markdown("---")


else:
    st.info(
        "Aún no se ha registrado ningún cliente. Utiliza el formulario superior para empezar a cargar registros en las diferentes categorías."

    )
