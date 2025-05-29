import pandas as pd
import openpyxl
import streamlit as st
import io
from openpyxl.styles import NamedStyle
from datetime import datetime, timedelta
import tempfile

# ? Instancia de sesiones globales
if "archivo_consolidado" not in st.session_state:
    st.session_state["archivo_consolidado"] = None

if "nombre_archivo" not in st.session_state:
    st.session_state["nombre_archivo"] = None

if "archivo_extension" not in st.session_state:
    st.session_state["archivo_extension"] = None


# ? Fragmentos
# todo: Decorador para procesar mejor la caché
@st.cache_data
# * Formateo de tiempo para primera columna
def formatear_hora_minuto(df):
    """Convierte la primera columna de un DataFrame a formato serial de Excel y asegura que Excel lo reconozca como fecha."""
    df = pd.read_excel(df)
    primera_columna = df.columns[0]

    df[primera_columna] = pd.to_datetime(df[primera_columna], errors="coerce")
    df[primera_columna] = df[primera_columna].map(
        lambda x: (x.timestamp() / 86400) + 25569 if pd.notnull(x) else x
    )

    output = io.BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    output.seek(0)

    wb = openpyxl.load_workbook(output)
    ws = wb.active
    for row in ws.iter_rows(min_row=2, min_col=1, max_col=1):
        for cell in row:
            cell.number_format = "DD/MM/YYYY HH:MM:SS"

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
def procesar_excel(archivo):
    wb = openpyxl.load_workbook(archivo)
    hoja = wb.active  # Primera hoja activa

    # Ajustar el ancho de la columna A
    hoja.column_dimensions["A"].width = 25

    # Crear estilo para fecha
    date_style = NamedStyle(name="datetime_format")
    date_style.number_format = "DD/MM/YYYY HH:MM:SS"

    # Iterar sobre la columna A desde la segunda fila
    for fila in hoja.iter_rows(min_row=2, min_col=1, max_col=1):
        for celda in fila:
            if isinstance(
                celda.value, (int, float)
            ):  # Convertir si es un número decimal
                fecha = datetime.fromordinal(693594 + int(celda.value))
                hora = int((celda.value % 1) * 24)
                minuto = int((celda.value % 1 * 1440) % 60)

                # Ajustar minutos al múltiplo de 5 más cercano
                minuto = (minuto // 5) * 5

                if minuto >= 60:
                    fecha += timedelta(hours=1)
                    minuto = 0

                fecha = fecha.replace(
                    hour=hora, minute=minuto, second=0
                )  # Segundos siempre en 0
                celda.value = fecha  # Asegurar que la celda almacene un objeto datetime
                celda.style = date_style  # Aplicar formato

    # Guardar archivo temporal y devolverlo
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
        wb.save(tmp_file.name)
        return tmp_file.name


@st.cache_data
# * Consolidar archivo
def consolidarArchivo(archivo):
    archivo_nombre = archivo.name.split(".")[0]
    archivo_extension = archivo_nombre
    archivo_extension = archivo.name.split(".")[1]
    st.session_state["archivo_extension"] = archivo_extension
    st.session_state["nombre_archivo"] = archivo_nombre
    if archivo_extension == "xlsx":
        df = pd.read_excel(archivo)
        Encabezados = list(df.columns)
        df[Encabezados[0]] = df[Encabezados[0]].astype(str).str.slice(0, 16)
        df = df.groupby(Encabezados[0]).mean()
    else:
        df = pd.read_csv(archivo)
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
nombre_archivo = st.session_state["nombre_archivo"]
archivo_extension = st.session_state["archivo_extension"]

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

    # ! Tab Data - Muestra tabla consolidada
    with tab_Data:
        # ? Mostrar tabla de datos consolidados
        st.caption(
            "<b>Esta es una simple exposición de los datos. En el archivo que se descarga, las fechas se encuentran formateadas </b> ✅",
            unsafe_allow_html=True,
        )
        st.write(archivo_consolidado)

    # ! Tab info - Se muestran características y datos del archivo
    with tab_Info:
        st.caption(
            'Al final de esta pantalla se encuentra el botón "Descargar :material/download:"'
        )

        # ! Ejecución
        # ? Expander de logs
        with st.expander("Historial de procesos :material/update:", expanded=True):
            # * Mensaje de consolidación
            st.success("Consolidación realizada con éxito ✅")

            st.info(
                'Dirígete a la pestaña "Vista previa de datos procesados :material/table:" para ver tus datos procesados...'
            )

            # * Mensajes de formateo
            st.warning("Formateando datos ⌛")

            archivo_convertido = convertirExcel(archivo_consolidado)

            st.success("Datos formateados ✅")

            st.warning("Preparando archivo en Excel (.xlsx)")

            archivo_formateado = formatear_hora_minuto(archivo_convertido)

            archivo_ajustado = procesar_excel(archivo_formateado)

            st.success(
                "Archivo procesado y listo para descargar en formato Excel (.xlsx)"
            )

        # ? Características del archivo
        with st.expander("Editar características del archivo :material/edit:"):
            with st.form("Archivo"):
                nombre_archivo = st.text_input(
                    "📁 Nombre del archivo",
                    placeholder=f"Consolidado_{nombre_archivo}",
                    value=nombre_archivo,
                    help="Agrega un nombre específico a tu archivo",
                )

                archivo_extension = st.selectbox(
                    "Selecciona elformato que desees para el archivo",
                    ["xlsx", "csv"],
                    index=0,
                )

                if st.form_submit_button("Apalicar cambios"):
                    st.toast("Los cambios han sido registrados")

        # ? Expander con los datos del archivo
        with st.expander("Datos del archivo", expanded=True):
            # * Primer tab: Características del archivo
            st.write(
                f"<b>Nombre del archivo:</b> {nombre_archivo}", unsafe_allow_html=True
            )
            st.caption(
                f"El archivo será descargado con la extensión: <i>Consolidado_</i>{nombre_archivo}<i>.{archivo_extension}</i>",
                unsafe_allow_html=True,
            )
            st.write(
                f"<b>Formato del archivo: </b>{archivo_extension}",
                unsafe_allow_html=True,
            )
            st.caption(
                'Si desea modificar el nombre o extensión del archivo, haga clic sobre el apartado "Editar características del archivo :material/edit:"'
            )

        # ? Botón de descargar con valores definidos por el usuario
        # * En caso de ser en formato csv
        if archivo_extension == "csv":
            df = pd.read_excel(archivo_ajustado)
            archivo_csv = f"Consolidado_{nombre_archivo}.csv"
            df.to_csv(archivo_csv, index=False, encoding="utf-8")

            # * Botón para descargar CSV
            st.download_button(
                f"Descargar en formato {archivo_extension} :material/download:",
                data=open(archivo_csv, "rb").read(),
                file_name=archivo_csv,
                mime="text/csv",
            )
            st.caption("Si abre el archivo con formato CSV en Excel, ajuste la primera celda ('A') para observar los datos.")
        else:
            # * En caso de ser xlsx
            with open(archivo_ajustado, "rb") as file:
            # * Botón para descargar EXCEL
                st.download_button(
                    f"Descargar en formato {archivo_extension} :material/download:",
                    data=file,
                    file_name=f"Consolidado_{nombre_archivo}.xlsx",
                )

# ! Secuencia

# st.session_state["archivo_consolidado"]

# archivo_convertido = convertirExcel(st.session_state["archivo_consolidado"])

# archivo_formateado = formatear_hora_minuto(archivo_convertido)

# st.download_button("Descargar", data=archivo_formateado, file_name="test.xlsx")
