import pandas as pd
import openpyxl
import streamlit as st
import os
import io
from openpyxl.styles import NamedStyle, numbers
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from datetime import datetime, timedelta
import tempfile

# ? Variables globales con mensaje
mensaje_inicio = "Aquí se mostrará el archivo 📄 una vez haya terminado de consolidarse. Para comenzar, haz clic sobre el botón de arriba 👆 o arrastra tu archivo ✊"

# ? Instancia de sesiones globales
if "archivo_consolidado" not in st.session_state:
    st.session_state["archivo_consolidado"] = None

if "nombre_archivo" not in st.session_state:
    st.session_state["nombre_archivo"] = None

if "archivo_extension" not in st.session_state:
    st.session_state["archivo_extension"] = None

if "df_consolidado" not in st.session_state:
    st.session_state["df_consolidado"] = None

if "archivo_procesado_xlsx" not in st.session_state:
    st.session_state["archivo_procesado_xlsx"] = None

if "archivo_procesado_csv" not in st.session_state:
    st.session_state["archivo_procesado_csv"] = None

if "flag" not in st.session_state:
    st.session_state["flag"] = False

@st.dialog("Aviso")
def alert(message):
    st.write(f"## {message}")

def leer_datos(archivo):
    """
    Lee los datos del archivo subido por Streamlit y preprocesa la columna de fechas.
    
    Args:
        archivo: Objeto de archivo subido por Streamlit
        
    Returns:
        tuple: DataFrame con datos y nombre del archivo sin extensión
    """
    nombre_archivo = archivo.name.split(".")[0]
    extension = archivo.name.split(".")[1].lower()
    
    # Leer el archivo según su extensión
    if extension == 'xlsx' or extension == 'xls':
        df = pd.read_excel(archivo)
    elif extension == 'csv':

        try:
            df = pd.read_csv(archivo, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(archivo, encoding='latin1')
            except:
                df = pd.read_csv(archivo, encoding='ISO-8859-1')
        
        if len(df.columns) == 1:
            for delimiter in [';', '\t', '|']:
                try:
                    df = pd.read_csv(archivo, sep=delimiter, encoding='utf-8')
                    if len(df.columns) > 1:
                        break
                except:
                    continue
        
        num_columns = df.shape[1]
        if num_columns <= 1:
            alert("El archivo no es válido para el sistema. Asegúrate de haber subido un archivo con código UTF-8 o extraído desde SCADA.")
            st.session_state["flag"] = True
            st.cache_data.clear()
            return
    else:
        raise ValueError(f"Formato de archivo no soportado: {extension}. Use xlsx o csv")
    
    encabezados = list(df.columns)
    df[encabezados[0]] = df[encabezados[0]].astype(str).str.slice(0, 16)
    
    return df, nombre_archivo


def consolidar_datos(df):
    """
    Para consolidar los datos, se agrupan los registros por fecha y calculando la media.
    
    Args:
        df (DataFrame): DataFrame con los datos a consolidar
        
    Returns:
        DataFrame: DataFrame consolidado
    """

    encabezados = list(df.columns)
    df_consolidado = df.groupby(encabezados[0]).mean()
    
    return df_consolidado


def convertir_fechas(df):
    """
    Convierte las fechas en el índice del DataFrame a formato datetime.
    
    Args:
        df (DataFrame): DataFrame con fechas en texto plano como índice
        
    Returns:
        DataFrame: DataFrame con fechas en formato datetime como índice
    """
    df.index = pd.to_datetime(df.index, errors='coerce')
    
    return df


@st.cache_data
def guardar_excel_bytes(df):
    """
    Guarda el DataFrame en un objeto BytesIO en formato Excel.
    
    Args:
        df (DataFrame): DataFrame a guardar
        
    Returns:
        BytesIO: Objeto BytesIO con el archivo Excel
    """
    output = io.BytesIO()
    df.to_excel(output)
    output.seek(0)
    
    return output


@st.cache_data
def guardar_csv_bytes(df, encoding='cp1252'):
    """
    Guarda el DataFrame en un objeto BytesIO en formato CSV.
    
    Args:
        df (DataFrame): DataFrame a guardar
        encoding (str): Codificación a utilizar
        
    Returns:
        BytesIO: Objeto BytesIO con el archivo CSV
    """

    df_csv = df.reset_index()
    

    fecha_col = df_csv.columns[0]
    df_csv[fecha_col] = df_csv[fecha_col].dt.strftime('%d/%m/%Y %H:%M')
    
    output = io.BytesIO()
    df_csv.to_csv(output, index=False, encoding=encoding, sep=',')
    output.seek(0)
    
    return output


@st.cache_data
def aplicar_formato_fecha_bytes(output_excel):
    """
    Aplica formato de fecha DD/MM/AAAA HH:MM a la primera columna del archivo Excel
    y ajusta el ancho de la columna para evitar que se vean corrompidas.
    
    Args:
        output_excel (BytesIO): Objeto BytesIO con el archivo Excel
        
    Returns:
        BytesIO: Objeto BytesIO con el archivo Excel formateado
    """

    output = io.BytesIO(output_excel.getvalue())
    output.seek(0)
    

    wb = openpyxl.load_workbook(output)
    ws = wb.active

    date_style = NamedStyle(name='datetime')
    date_style.number_format = 'DD/MM/YYYY HH:MM'

    for row in range(2, ws.max_row + 1): # Empezar desde 2 para evitar el encabezado
        cell = ws.cell(row=row, column=1)
        cell.style = date_style
    
    ws.column_dimensions['A'].width = 20
    
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        
        adjusted_width = (max_length + 2)
        
        if column_letter == 'A':
            adjusted_width = max(adjusted_width, 20)
        
        ws.column_dimensions[column_letter].width = adjusted_width
    
    output_formateado = io.BytesIO()
    wb.save(output_formateado)
    output_formateado.seek(0)
    
    return output_formateado


@st.cache_data
def procesar_contenido_excel(output_excel):
    """
    Procesa más a fondo el contenido del archivo Excel para solucionar problemas de fechas.
    
    Args:
        output_excel (BytesIO): Objeto BytesIO con el archivo Excel
        
    Returns:
        BytesIO: Objeto BytesIO con el archivo Excel procesado
    """
    output = io.BytesIO(output_excel.getvalue())
    output.seek(0)
    
    wb = openpyxl.load_workbook(output)
    ws = wb.active
    
    date_style = NamedStyle(name="datetime_format")
    date_style.number_format = "DD/MM/YYYY HH:MM"
    
    for row in range(2, ws.max_row + 1):
        cell = ws.cell(row=row, column=1)
        if isinstance(cell.value, (int, float)):
            fecha = datetime.fromordinal(693594 + int(cell.value))
            hora = int((cell.value % 1) * 24)
            minuto = int((cell.value % 1 * 1440) % 60)
            
            minuto = (minuto // 5) * 5
            
            if minuto >= 60:
                fecha += timedelta(hours=1)
                minuto = 0
                
            fecha = fecha.replace(hour=hora, minute=minuto, second=0)
            cell.value = fecha
        
        cell.style = date_style
    
    output_procesado = io.BytesIO()
    wb.save(output_procesado)
    output_procesado.seek(0)
    
    return output_procesado


@st.cache_data
def consolidarArchivo(archivo):
    """
    Consolida los registros del archivo utilizando el nuevo motor.
    """
    try:
        df, nombre_archivo = leer_datos(archivo)
        
        st.session_state["nombre_archivo"] = nombre_archivo
        st.session_state["archivo_extension"] = archivo.name.split(".")[1]
        
        df_consolidado = consolidar_datos(df)
        df_consolidado = convertir_fechas(df_consolidado)
        
        
        st.session_state["df_consolidado"] = df_consolidado
        
        output_excel = guardar_excel_bytes(df_consolidado)
        output_excel_formateado = aplicar_formato_fecha_bytes(output_excel)
        output_excel_procesado = procesar_contenido_excel(output_excel_formateado)
        
        output_csv = guardar_csv_bytes(df_consolidado)
        
        st.session_state["archivo_procesado_xlsx"] = output_excel_procesado
        st.session_state["archivo_procesado_csv"] = output_csv
        
        st.balloons()
        return df_consolidado
        
    except Exception as e:
        st.error(f"Error durante la consolidación. Por favor, suba un archivo extraído desde _SCADA_ con código UTF-8...")
        return None


# ! HEADER
st.set_page_config(
    page_title="CONDA web",
    page_icon=":material/update:"
)

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

    # * Condicional que permite mostrar indicaciones en caso que se encuentre un archivo selecciondo
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
            "<b>Recuerda que:</b> <br/> - Solo puedes seleccionar un único archivo 📄 para este proceso. <br/> - Admite CSV y XLSX hasta 190MB.",
            unsafe_allow_html=True,
        )

st.divider()

# ! BODY - 1ER CASO
# ? Variables globales
archivo_consolidado = st.session_state["archivo_consolidado"]
nombre_archivo = st.session_state["nombre_archivo"]
archivo_extension = st.session_state["archivo_extension"]
df_consolidado = st.session_state.get("df_consolidado")
archivo_procesado_xlsx = st.session_state.get("archivo_procesado_xlsx")
archivo_procesado_csv = st.session_state.get("archivo_procesado_csv")

# ?[testing] Testing variables
# todo [testing] En caso que el archivo haya sido subido, instancia las variables
if archivo:
    nombre_session_testing = f"{nombre_archivo}.{archivo_extension}" if nombre_archivo and archivo_extension else None
    nombre_archivo_testing = archivo.name

# ? Condicional que muestra mensaje de inicio en caso de no haber elegido un archivo
# todo: En caso de que el usuario no haya elegido un archivo o lo haya retirado, se mostrará el mensaje
if archivo is None or nombre_archivo is None:
    st.write(mensaje_inicio)

# todo [testing] Si los nombres son diferentes, significa que el usuario ha cambiado de archivo
elif nombre_archivo_testing != nombre_session_testing:
    print(
        f"Los nombres son diferentes: Archivo que ha sido pasado: {nombre_archivo_testing}  Archivo en caché: {nombre_session_testing}"
    )
    st.write(mensaje_inicio)
    st.warning("Se ha detectado un archivo distinto al que se encuentra en caché, ¡hora de drenar información!")

    st.cache_data.clear()

elif nombre_archivo is not None:
    # ! BODY - 2DO CASE - TABS
    # ? Se organiza el cuerpo del contenido a partir de tabs
    st.success(
        '¡Consolidación hecha con éxito! En la pestaña "Historial de procesos :material/update:" puede observar los procesos que son realizados para su archivo...'
    )
    tab_Info, tab_Data, tab_Logs = st.tabs(
        [
            "Características e información del archivo :material/info:",
            "Vista previa de datos procesados :material/table:",
            "Historial de procesos :material/update:",
        ]
    )

    # ! Tab Data - Muestra tabla consolidada
    with tab_Data:
        st.subheader("Vista previa de datos procesados :material/table:")
        # ? Mostrar tabla de datos consolidados
        st.caption(
            "<b>Esta es una simple exposición de tus datos consolidados. En el archivo que se descarga, las fechas se encuentran formateadas </b> ✅",
            unsafe_allow_html=True,
        )
        st.write(df_consolidado)

        st.error(
            "Pase el mouse sobre la tabla para interactuar con ella: Puede buscar en los registros de la tabla haciendo clic sobre la lupa en la parte superior derecha o hacerla más grande, pero no descargue el archivo por este medio."
        )

    # ! Tab info - Se muestra el historial de procesos
    with tab_Info:

        # ! Ejecución
        # ? Historial de procesos
        with tab_Logs:
            st.subheader("Historial de procesos")
            st.caption(
                '<b>Al finalizar este proceso, podrás descargar tu archivo en "Características e información del archivo" que se encuentra en la primera pestaña.</b>',
                unsafe_allow_html=True,
            )

            # * Mensaje de consolidación
            st.success("Consolidación realizada con éxito ✅")

            st.info(
                'Dirígete a la pestaña "Vista previa de datos procesados :material/table:" para ver tus datos procesados...'
            )

            # * Mensajes de formateo
            st.warning("Formateando datos ⌛")
            st.success("Datos formateados ✅")

            st.warning("Preparando archivos")
            st.success("Archivo Excel con fechas correctamente formateadas ✅")
            st.success("Archivo CSV con fechas correctamente formateadas ✅")

            st.success(
                "Archivos procesados y listos para descargar"
            )

            st.caption(
                '<b>Su archivo se ha procesado de forma exitosa. Para descargar, modificar el nombre o extensión del archivo, dirígete a "Características e información del archivo "</b>',
                unsafe_allow_html=True,
            )

        # ? Características del archivo
        tab_Info.subheader("Características e información del archivo :material/info:")
        st.caption(
            "<b>Aquí puedes ver los detalles de tu archivo o modificarlos según tus necesidades.</b>",
            unsafe_allow_html=True,
        )
        with st.expander(
            "Editar características del archivo :material/edit:", expanded=True
        ):
            # ? Formulario
            with st.form("Archivo"):
                nombre_archivo = st.text_input(
                    "📁 Nombre del archivo",
                    placeholder=f"Consolidado_{nombre_archivo}",
                    value=nombre_archivo,
                    help="Agrega un nombre específico a tu archivo",
                )

                archivo_extension = st.selectbox(
                    "Selecciona el formato que desees para el archivo",
                    ["xlsx", "csv"],
                    index=0,
                )

                st.error(
                    'Haz clic en "Aplicar cambios" para guardar de forma correcta los cambios realizados.'
                )
                if st.form_submit_button("Aplicar cambios"):
                    st.toast("Los cambios han sido registrados")

        # ? Datos del archivo
        # * Primer tab: Características del archivo
        st.write(f"<b>Nombre del archivo:</b> {nombre_archivo}", unsafe_allow_html=True)
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
        if archivo_extension == "csv" and archivo_procesado_csv:
            st.download_button(
                label=f"Descargar en formato csv :material/download:",
                data=archivo_procesado_csv,
                file_name=f"Consolidado_{nombre_archivo}.csv",
                mime="text/csv",
            )

            st.error(
                "Si abre el archivo con formato CSV en Excel, ajuste la primera celda ('A') para observar los datos."
            )
                
        # * En caso de ser xlsx
        elif archivo_procesado_xlsx:
            st.download_button(
                f"Descargar en formato {archivo_extension} :material/download:",
                data=archivo_procesado_xlsx,
                file_name=f"Consolidado_{nombre_archivo}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

st.divider()

# ! Footer
label, button = st.columns(2, gap="medium", vertical_alignment="center")

with label: 
    st.write(f"<h6>Realiza la consolidación desde tu computadora, sin conexión a internet y con más potencia...</h6>", unsafe_allow_html=True)

with button:
    st.link_button("**Descargar CONDA app**", "#", type="primary", use_container_width=True, icon="💾")
