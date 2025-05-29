import pandas as pd
import openpyxl
import streamlit as st
import io

# ? Intento de reseteo de valores CSS para mejorar la accesibilidad
st.markdown(
    "<style>#text_input_2, .st-ei{border: 1px solid #a8a8a8; border-radius: 0.5rem}</style>",
    unsafe_allow_html=True
)

# ? Instancia de sesiones globales
if "archivo_consolidado" not in st.session_state:
    st.session_state["archivo_consolidado"] = None

if "nombre_archivo" not in st.session_state:
    st.session_state["nombre_archivo"] = None


# ? Fragmentos
# todo: Decorador para procesar mejor la caché
@st.cache_data
# * Formateo de tiempo para primera columna
def formatear_hora_minuto(df):
    """Convierte la primera columna de un DataFrame a datetime, extrae la hora y genera un archivo Excel."""
    df = pd.read_excel(df)
    primera_columna = df.columns[0]

    df[primera_columna] = pd.to_datetime(df[primera_columna], errors="coerce")
    df[primera_columna] = df[primera_columna].apply(
        lambda dt: dt.time() if pd.notnull(dt) else dt
    )
    output = io.BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    output.seek(0)

    wb = openpyxl.load_workbook(output)
    ws = wb.active
    for row in ws.iter_rows(min_row=2, min_col=1, max_col=1):
        for cell in row:
            cell.number_format = "hh:mm"

    output.seek(0)
    return output


@st.cache_data
# * Convertir Dataframe a Excel
def convertirExcel(archivo):
    output = io.BytesIO()
    archivo.to_excel(output, index=True, engine="openpyxl")
    output.seek(0)

    wb = openpyxl.load_workbook(output)
    ws = wb.active

    for row in ws.iter_rows(min_row=2, min_col=1, max_col=1):
        for cell in row:
            cell.number_format = "hh:mm"

    output.seek(0)
    return output

@st.cache_data
# * Consolidar archivo
def consolidarArchivo(archivo):
    archivo_nombre = archivo.name.split(".")[0]
    st.session_state["nombre_archivo"] = archivo_nombre
    df = pd.read_excel(archivo)
    Encabezados = list(df.columns)
    df[Encabezados[0]] = df[Encabezados[0]].astype(str).str.slice(0, 16)
    df = df.groupby(Encabezados[0]).mean()
    st.balloons()
    return df


# ! HEADER

# ? Definir columnas
col1, col2 = st.columns([1, 2], gap="medium", vertical_alignment="center")

# ? Dar contenido a las columnas
# todo: Columna 1
with col1:
    st.image("./assets/logo_conda.png", width=500)

# todo: Columna 2
with col2:
    # * Input para recibir archivo
    archivo = st.file_uploader(
        "✨ Haz clic o arrastra tu archivo aquí para comenzar 🚀",
        ["csv", "xlsx"],
        accept_multiple_files=False,
        help='Sube tu archivo, posteriormente se despliega el botón "Consolidar" para continuar con el proceso.',
    )

    # * Conficional que permite mostrar indicaciones en caso que se encuentre un archivo selecciondo
    if archivo:        
        st.caption("Haz clic sobre ✖️ para eliminar el archivo.")

        # * Al presionar el botón, ejecuta la consolidación
        if st.button(
            "Consolidar :material/sync:",
            use_container_width=True,
            help="Haz clic para empezar a consolidar tu archivo.",
            key="consolidar",
        ):
            # * Enviar dataframe convertido a espacio de almacenamiento global para evitar scope
            st.session_state["archivo_consolidado"] = consolidarArchivo(archivo)

    else:
        # * Recordatorio de accesibilidad para el usuario
        st.caption(
            "<b>Recuerda que:</b> <br/> - Solo puedes seleccionar un único archivo 📄 para este proceso. <br/> - Admite CSV y XLSX hasta 30MB.",
            unsafe_allow_html=True,
        )

st.divider()

# ! BODY - 1ER CASO
# ? Variables globales
archivo_consolidado = st.session_state["archivo_consolidado"]
nombre_archivo= st.session_state["nombre_archivo"]
# ? Condicional que muestra mensaje de inicio en caso de no haber elegido un archivo
# todo: En caso de que el usuario no haya elegido un archivo o lo haya retirado, se mostrará el mensaje
if archivo == None or nombre_archivo == None:
    st.write(
        "Aquí se mostrará el archivo 📄 que hayas seleccionado haciendo clic sobre el botón de arriba 👆"
    )
    
elif nombre_archivo != None:
    # ! BODY - 2DO CASE
    # ? Se organiza el cuerpo del contenido a partir de tabs
    tab_Info, tab_Data = st.tabs(
        [
            "Características e información del archivo :material/info:",
            "Vista previa de datos procesados :material/table:",
        ]
    )
    with tab_Info:
        # ? Expander de logs
        with st.expander("Historial de procesos :material/update:", expanded=True):
            # * Mensaje de consolidación
            st.success('Consolidación realizada con éxito ✅')
            
            st.info('Dirígete a la pestaña "Vista previa de datos procesados :material/table:" para ver tus datos procesados...')
            
            # * Mensajes de formateo
            st.warning("Formateando datos ⌛")
            
            archivo_convertido = convertirExcel(archivo_consolidado)
            
            st.success("Datos formateados ✅")
            
            st.warning("Preparando archivo en Excel (.xlsx)")
            
            archivo_formateado = formatear_hora_minuto(archivo_convertido)

            
            st.success("Archivo procesado y listo para descargar en formato Excel (.xlsx)")
        
        # * Primer tab: Características del archivo
        st.write(f"<b>Nombre del archivo:</b> {nombre_archivo}", unsafe_allow_html=True)
        st.download_button("Descargar en formato Excel :material/download:", data=archivo_formateado, file_name=f"Consolidado_{nombre_archivo}.xlsx")

        
        st.download_button("Descargar en CSV :material/download:", data=archivo_formateado, file_name=f"Consolidado_{nombre_archivo}.csv", key="descarga")
            

    with tab_Data:        
        # ? Mostrar tabla de datos consolidados
        st.caption("<b>Esta es una simple exposición de los datos. En el archivo que se descarga, las fechas se encuentran formateadas </b> ✅", unsafe_allow_html=True)
        st.write(archivo_consolidado)

# ! Secuencia

# st.session_state["archivo_consolidado"]

# archivo_convertido = convertirExcel(st.session_state["archivo_consolidado"])

# archivo_formateado = formatear_hora_minuto(archivo_convertido)

# st.download_button("Descargar", data=archivo_formateado, file_name="test.xlsx")
