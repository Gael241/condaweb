import pandas as pd
import streamlit as st
import io

if "archivo_disponible" not in st.session_state:
    st.session_state["archivo_disponible"] = False

if "archivo_consolidado" not in st.session_state:
    st.session_state["archivo_consolidado"] = None

if "nombre_archivo" not in st.session_state:
    st.session_state["nombre_archivo"] = None


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

    tab_info, tab_data, tab_logs = st.tabs(
        [
            "Información :material/info:",
            "Datos :material/table:",
            "Logs :material/update:",
        ]
    )

    with tab_logs:
        st.success(
            "Consolidación hecha con éxito ✅",
        )

    with tab_data:
        st.text(f"Nombre del archivo: {st.session_state["nombre_archivo"]}")
        st.session_state["archivo_consolidado"]

    archivo_Excel = convertirExcel(st.session_state["archivo_consolidado"])

    with tab_logs:
        st.success("Conversión exitosa ✅")

    with tab_info:
        
        with st.expander("Editar archivo", icon=":material/edit:"):
            with st.form(key="dataForm", border=False):
                st.caption("<b>❗ Es posible omitir el registro de este formulario formulario.</b>", unsafe_allow_html=True)
                nombre_archivo = str(
                    st.text_input(
                        "📄 Ingresa el nombre del archivo.",
                        value=st.session_state["nombre_archivo"],
                        help='Por defecto, el archivo contiene el nombre original con el prefijo "Consolidados"'
                    )
                )
                st.caption("Agrega un nombre específico a tu archivo: Isla_Mujeres, Cárcamo_del_becario, Solidaridad...")
                
                tipo_archivo = st.selectbox("📁 Selecciona el tipo de formato que deseas.", ["csv", "xlsx"], index=1, help="Por defecto, el archivo que se exporta se encuentra en formato Excel.")
                
                st.text("Aplica los cambios en este botón.")
                boton = st.form_submit_button("Aplicar cambios", help="Aplica los cambios que registraste.")
                if boton:
                    st.toast("Cambios aplicados ✅")
                st.caption('<b>"Aplicar cambios" permite que los datos se registren en el archivo.</b>', unsafe_allow_html=True)

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
