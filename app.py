import pandas as pd
import streamlit as st
import io

# Estado inicial
if "archivo_disponible" not in st.session_state:
    st.session_state["archivo_disponible"] = False

if "archivo_consolidado" not in st.session_state:
    st.session_state["archivo_consolidado"] = None


def saveValue():
    st.session_state["archivo_disponible"] = True


def convertirExcel(archivo, nombre_archivo="archivo"):
    output = io.BytesIO()
    archivo.to_excel(output, index=True)
    output.seek(0)  # Mueve el cursor al inicio del archivo
    return output


def consolidarArchivo(archivo, nombre_archivo="Consolidado"):
    saveValue()
    st.text("Consolidando datos... ⏳")
    
    df = pd.read_excel(archivo)
    Encabezados = list(df.columns)
    
    df[Encabezados[0]] = df[Encabezados[0]].astype(str).str.slice(0, 16)
    df = df.groupby(Encabezados[0]).mean()

    st.session_state["archivo_consolidado"] = df
    st.balloons()


col1, col2 = st.columns([1, 2], gap="medium", vertical_alignment="center")

with col1:
    st.image("./assets/logo_conda.png", width=500)

with col2:
    archivo = st.file_uploader(
        "✨ Haz clic o arrastra tu archivo aquí para comenzar 🚀",
        ["csv", "xlsx"],
        accept_multiple_files=False,
        help='Sube tu archivo, posteriormente se despliega el botón "consolidar" para continuar con el proceso.'
    )

    if archivo:
        st.caption("Haz clic sobre ✖️ para eliminar el archivo.")
    
        consolidar = st.button(
            "Consolidar :material/sync:",
            on_click=consolidarArchivo,
            use_container_width=True,
            help="Haz clic para empezar a consolidar tu archivo.",
            key="consolidar",
            args=(archivo,)
        )
    else:
        st.caption(
            "<b>Recuerda que:</b> <br/> - Solo puedes seleccionar un único archivo 📄 para este proceso. <br/> - Admite CSV y XLSX hasta 30MB.",
            unsafe_allow_html=True,
        )

st.divider()

if "archivo_consolidado" in st.session_state and st.session_state["archivo_consolidado"] is not None:
    archivo = st.session_state["archivo_consolidado"]
    archivo_Excel = convertirExcel(archivo)
    
    st.download_button(
        label="📥 Descargar archivo consolidado",
        data=archivo_Excel,
        file_name="Consolidados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.text("Aquí se mostrará tu archivo 📄 una vez se haya concluido con la consolidación de datos.")
