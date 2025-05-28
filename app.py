import time
import streamlit as st

if "archivo_disponible" not in st.session_state:
    st.session_state["archivo_disponible"] = False

if "archivo" not in st.session_state:
    st.session_state["archivo_disponible"] = False


def saveValue():
    st.session_state["archivo_disponible"] = True


col1, col2 = st.columns([1, 2], gap="medium", vertical_alignment="center")

subCol1, subCol2 = st.columns(2)

with col1:
    st.image("./assets/logo_conda.png", width=500)

with col2:
    archivo = st.file_uploader(
        "✨ Haz clic o arrastra tu archivo aquí para comenzar 🚀",
        ["csv", "xlsx"],
        accept_multiple_files=False,
        help='Sube tu archivo, posteriormente se despliega el botón "consolidar" para continuar con el proceso.',
    )

    if archivo:
        st.caption("Haga clic sobre ✖️ para eliminar el archivo.")

        consolidar = st.button(
            "Consolidar :material/sync:",
            on_click=saveValue,
            use_container_width=100,
            help="Haz clic para empezar a consolidar tu archivo.",
            key="archivo",
        )
    else:
        st.caption(
            "<b>Recuerda que:</b> <br/> - Solo puedes seleccionar un único archivo 📄 para este proceso. <br/> - Admite CSV y XLSX hasta 30MB.", unsafe_allow_html=True
        )


st.divider()

try:
    if consolidar:
        st.balloons()

    if st.session_state["archivo_disponible"]:
        st.download_button(
            "Descargar :material/download:",
            file_name="archivo.csv",
            data="Mi contenido",
            help="Haz clic justo aquí para descargar tu archivo consolidado.",
        )
except:
    st.text(
        "Aquí se mostrará tu archivo 📄 una vez se haya concluido con la consolidación de datos."
    )
