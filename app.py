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
        "Sube un archivo", ["csv", "xlsx"], accept_multiple_files=False
    )

    if archivo:
        consolidar = st.button(
            "Consolidar :material/sync:", on_click=saveValue, use_container_width=100
        )

st.divider()

try:
    if st.session_state["archivo_disponible"] or consolidar:
        st.balloons()
        st.download_button("Descargar", file_name="archivo.csv", data="Mi contenido")
except:
    st.text("Aquí se mostrará el archivo consolidado")
