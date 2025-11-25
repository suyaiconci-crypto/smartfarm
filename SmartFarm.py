import streamlit as st
import json
import os
import uuid
import utilidades as util

# Configurar Menu
util.generarMenu()


# =================================================================
# SIMULACIÓN DE LA CONEXIÓN A FIREBASE (Firestore)
# =================================================================

# Variables globales provistas por el entorno
app_id = os.environ.get('__app_id', 'smartfarm_default_app_id')
FIREBASE_COLLECTION_PATH = f'artifacts/{app_id}/public/data/client_scores'
DATA_FILE = "firestore_simulation.json"  # Archivo para persistencia simulada


def init_firestore_db_simulation():
    """Inicializa la base de datos simulada (carga o crea el archivo JSON)."""
    if 'db_initialized' not in st.session_state:
        # Intenta cargar los datos existentes
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r') as f:
                    st.session_state.firestore_data = json.load(f)
            else:
                st.session_state.firestore_data = {}  # Inicializa vacío si no existe
        except Exception as e:
            st.session_state.firestore_data = {}
            st.warning(f"Error al cargar datos simulados: {e}. Inicializando vacío.")

        st.session_state.db_initialized = True

    # Inicialización de la base de datos simulada de la colección específica
    if FIREBASE_COLLECTION_PATH not in st.session_state.firestore_data:
        st.session_state.firestore_data[FIREBASE_COLLECTION_PATH] = {}
        # Guardar inmediatamente para asegurar la estructura
        save_to_json()


def save_to_json():
    """Guarda el diccionario de datos de Firestore simulado en el archivo JSON."""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(st.session_state.firestore_data, f, indent=4)
    except Exception as e:
        st.error(f"Error al guardar datos simulados en JSON: {e}")


# Llamar a la inicialización antes de cualquier uso de st.session_state.firestore_data
init_firestore_db_simulation()

# Configuración inicial de la página Streamlit
st.set_page_config(
    page_title="SmartFarm - Conci",
    layout="wide",
    page_icon="sf1.png",
    initial_sidebar_state="collapsed",
)

# --- Contenido de la Página Principal con Imagen ---
col_text, col_image = st.columns([3, 1])

with col_text:
    st.title("Bienvenidos al Desafío SmartFarm")
    st.markdown("""
    Esta es la aplicación centralizada para gestionar el puntaje y el análisis de la participación de los clientes. 

    **Instrucciones:**
    1. **Puntuación SmartFarm:** Usa la página 'Puntuación SmartFarm' en el menú lateral para ingresar nuevos clientes y sus puntajes.
    2. **Resultados:** La tabla en esa misma página mostrará el seguimiento de todos los clientes de forma persistente.
    3. **Análisis de Puntuación:** Revisa el progreso de cada cliente y gestiona las recomendaciones para mejorar su puntaje.
    4. **Gestión de Ventas:** Carga prospectos y ventas generadas a partir de la táctica de SmartFarm, con edición y KPIs.
    """)

with col_image:
    # Usamos una imagen de placeholder para simular 'sf1.png'
    # Esta es una buena práctica ya que no podemos cargar archivos locales directamente
    st.image(
        "sf1.png",
    )

st.markdown("---")

# Nota: El resto del código de la página principal (si existiera) iría aquí.

# =================================================================
# La tabla de datos de clientes no se incluye aquí ya que este es el archivo principal
# pero las funcionalidades de las otras páginas dependen de la inicialización de la DB.
# =================================================================