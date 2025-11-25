import streamlit as st

# Generar menú de páginas
def generarMenu():
    with st.sidebar:
        st.page_link('SmartFarm.py', label='Inicio')
        st.page_link('pages/1_Puntuación_SmartFarm.py', label='Cargar Datos Clientes')
        st.page_link('pages/2_Análisis_de_Puntuación.py', label='Generar Informe')
        st.page_link('pages/3_Gestión_de_Ventas.py', label='Gestión de Ventas')