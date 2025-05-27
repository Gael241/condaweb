import time
import streamlit as st

if "archivo_disponible" not in st.session_state:
    st.session_state["archivo_disponible"] = False


def saveValue():
    st.session_state["archivo_disponible"] = True


col1, col2 = st.columns([1, 2], gap="medium", vertical_alignment="center")

subCol1, subCol2 = st.columns(2)

with col1:
    st.image("./assets/logo_conda.png", width=500)

with col2:
    archivo = st.file_uploader(
        "Selecciona o arrastra un archivo para empezar 📁...", ["csv", "xlsx"], accept_multiple_files=False, help="Haz clic o arrastra un archivo sobre el espacio en gris."
    )

    if archivo:
        consolidar = st.button(
            "Consolidar :material/sync:", on_click=saveValue, use_container_width=100, help="Haz clic para empezar a consolidar tus datos", key="archivo"
        )
        eliminar = st.button("Eliminar archivo:material/delete:", help="Haz clic para eliminar tu archivo ✖️")

st.divider()

try:
    if consolidar:
        st.balloons()

    if st.session_state["archivo_disponible"]:
        st.download_button("Descargar :material/download:", file_name="archivo.csv", data="Mi contenido", help="Haz clic para descargar tu archivo consolidado.")
except:
    st.text("Aquí se mostrará el archivo una vez se termine la consolidación de datos")
