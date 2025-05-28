import pandas as pd
import streamlit as st
import io

st.markdown("<style>#text_input_2, .st-ei{border: 1px solid #a8a8a8; border-radius: 0.5rem}</style>", unsafe_allow_html=True)

if "archivo_disponible" not in st.session_state:
    st.session_state["archivo_disponible"] = False

if "archivo_consolidado" not in st.session_state:
    st.session_state["archivo_consolidado"] = None


@st.cache_data
def convertirExcel(archivo):
    output = io.BytesIO()
    archivo.to_excel(output, index=True)
    output.seek(0)
    return output


@st.cache_data
def consolidarArchivo(archivo):
    archivo_nombre = archivo.name.split(".")
    st.session_state["nombre_archivo"] = archivo_nombre[0]
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

            st.session_state["nombre_archivo"] = archivo.name.split(".")[0]
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
    st.caption("Observa el proceso de la consolidación en Logs :material/update:")

    tab_info, tab_data = st.tabs(
        [
            "Características e información del archivo :material/info:",
            "Vista al archivo procesado :material/table:",
        ]
    )

    tab_info.info(
        "Consolidación hecha con éxito ✅... Empezando a transformar el archivo a Excel.",
    )

    with tab_data:
        st.text(f"Nombre del archivo: {st.session_state["nombre_archivo"]}")
        st.session_state["archivo_consolidado"]

    archivo_Excel = convertirExcel(st.session_state["archivo_consolidado"])

    tab_info.success("Conversión exitosa ✅")

    with tab_info:
        with st.expander("Editar características del archivo", icon=":material/input:"):
            with st.form(key="dataForm", border=False):
                nombre_archivo = str(
                    st.text_input(
                        "📄 Editar nombre del archivo.",
                        value=st.session_state["nombre_archivo"],
                        help='Por defecto, el archivo contiene el nombre original con el prefijo "Consolidados"',
                    )
                )

                tipo_archivo = st.selectbox(
                    "📁 Selecciona el tipo de formato que deseas descargar el archivo.",
                    ["Valores separados por comas (csv)", "  Formato Excel (xlsx)"],
                    index=1,
                    help="Por defecto, el archivo que se exporta se encuentra en formato Excel.", key="selector"
                )

                boton = st.form_submit_button(
                    "Confirmar cambios", help="Aplica los cambios que registraste."
                )
                if boton:
                    st.toast("Cambios aplicados ✅")

        tipo_archivo = tipo_archivo.split()[-1].strip("()")

        st.text(f"Nombre del archivo: Consolidado_{nombre_archivo}")
        st.text(f"Tipo de archivo: {tipo_archivo}")
        st.download_button(
            label="📥 Descargar archivo consolidado",
            data=archivo_Excel,
            file_name=f"Consolidado_{nombre_archivo}.{tipo_archivo}",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="descargar",
        )

else:
    st.text(
        "Aquí se mostrará tu archivo 📄 una vez se haya concluido con la consolidación de datos."
    )
