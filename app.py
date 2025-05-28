import pandas as pd
import streamlit as st
import io

if "archivo_disponible" not in st.session_state:
    st.session_state["archivo_disponible"] = False

if "archivo_consolidado" not in st.session_state:
    st.session_state["archivo_consolidado"] = None


@st.cache_data
def convertirExcel(archivo):
    output = io.BytesIO()
    archivo.to_excel(output, index=True)
    output.seek(0)
    return output  # Eliminamos los globos aquí


@st.cache_data
def consolidarArchivo(archivo):
    df = pd.read_excel(archivo)
    Encabezados = list(df.columns)

    df[Encabezados[0]] = df[Encabezados[0]].astype(str).str.slice(0, 16)
    df = df.groupby(Encabezados[0]).mean()

    st.balloons() 
    return df


col1, col2 = st.columns([1, 2], gap="medium", vertical_alignment="center")

with col1:
    st.image("./assets/logo_conda.png", width=500)

with col2:
    archivo = st.file_uploader(
        "✨ Haz clic o arrastra tu archivo aquí para comenzar 🚀",
        ["csv", "xlsx"],
        accept_multiple_files=False,
        help='Sube tu archivo, posteriormente se despliega el botón "Consolidar" para continuar con el proceso.',
    )

    if archivo:
        st.caption("Haz clic sobre ✖️ para eliminar el archivo.")

        if st.button(
            "Consolidar :material/sync:",
            use_container_width=True,
            help="Haz clic para empezar a consolidar tu archivo.",
            key="consolidar",
        ):
            st.session_state["archivo_consolidado"] = consolidarArchivo(archivo)

    else:
        st.caption(
            "<b>Recuerda que:</b> <br/> - Solo puedes seleccionar un único archivo 📄 para este proceso. <br/> - Admite CSV y XLSX hasta 30MB.",
            unsafe_allow_html=True,
        )

st.divider()

if (
    "archivo_consolidado" in st.session_state
    and st.session_state["archivo_consolidado"] is not None
):
    st.success("Consolidación hecha con éxito ✅")
    archivo_Excel = convertirExcel(st.session_state["archivo_consolidado"])

    st.download_button(
        label="📥 Descargar archivo consolidado",
        data=archivo_Excel,
        file_name="Consolidados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="descargar",
    )

else:
    st.text(
        "Aquí se mostrará tu archivo 📄 una vez se haya concluido con la consolidación de datos."
    )
