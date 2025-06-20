import pandas as pd
import openpyxl
import streamlit as st
import os
import io
from openpyxl.styles import NamedStyle
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from datetime import datetime, timedelta
import tempfile

# ? Variables globales con mensaje
mensaje_inicio = "Aquí se mostrará el archivo 📄 una vez haya terminado de consolidarse. Para comenzar, haz clic sobre el botón de arriba 👆 o arrastra tu archivo ✊"

ruta_exe = (
    r"D:\Documents\Universidad\#6_Cuatrimestre\CONDA\Stage\CONDA_app\CONDA_app.exe"
)

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
    """
    Convierte la primera columna de un DataFrame a formato de fecha y asegura 
    que Excel lo reconozca como fecha formateada.
    """
    # Leer DataFrame si es un archivo
    if not isinstance(df, pd.DataFrame):
        df = pd.read_excel(df)
    
    # Crear buffer para almacenar el archivo Excel
    output = io.BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    output.seek(0)
    
    # Cargar el archivo Excel y formatear la primera columna
    wb = openpyxl.load_workbook(output)
    ws = wb.active
    
    # Crear estilo de fecha personalizado
    date_style = NamedStyle(name='datetime')
    date_style.number_format = "DD/MM/YYYY HH:MM"
    
    # Aplicar el estilo a la columna A (empezando desde A2 para saltar el encabezado)
    for row in ws.iter_rows(min_row=2, min_col=1, max_col=1):
        for cell in row:
            cell.style = date_style
    
    # Ajustar el ancho de la columna A (fechas) para evitar que se vean corrompidas
    ws.column_dimensions['A'].width = 20
    
    # Guardar el archivo en el buffer
    output.seek(0)
    wb.save(output)
    output.seek(0)
    
    return output


@st.cache_data
# * Convertir Dataframe a Excel
def convertirExcel(archivo):
    """
    Convierte un DataFrame a formato Excel con formato adecuado para fechas.
    """
    output = io.BytesIO()
    archivo.to_excel(output, index=True, engine="openpyxl")
    output.seek(0)

    wb = openpyxl.load_workbook(output)
    ws = wb.active

    # Crear estilo de fecha personalizado
    date_style = NamedStyle(name='datetime_format')
    date_style.number_format = "DD/MM/YYYY HH:MM"
    
    # Aplicar el estilo a la columna A desde la segunda fila
    for row in ws.iter_rows(min_row=2, min_col=1, max_col=1):
        for cell in row:
            cell.style = date_style

    # Preparar el buffer para retornarlo
    output.seek(0)
    wb.save(output)
    output.seek(0)
    
    return output


@st.cache_data
def procesar_excel(archivo):
    """
    Procesa un archivo Excel para formatear fechas y ajustar columnas.
    """
    # Cargar el archivo
    wb = openpyxl.load_workbook(archivo)
    ws = wb.active
    
    # Ajustar el ancho de la columna A
    ws.column_dimensions["A"].width = 25
    
    # Crear estilo para fecha
    date_style = NamedStyle(name="datetime_format")
    date_style.number_format = "DD/MM/YYYY HH:MM"
    
    # Iterar sobre la columna A desde la segunda fila
    for row in range(2, ws.max_row + 1):
        cell = ws.cell(row=row, column=1)
        if isinstance(cell.value, (int, float)):
            # Convertir si es un número decimal a fecha datetime
            fecha = datetime.fromordinal(693594 + int(cell.value))
            hora = int((cell.value % 1) * 24)
            minuto = int((cell.value % 1 * 1440) % 60)
            
            # Ajustar minutos al múltiplo de 5 más cercano
            minuto = (minuto // 5) * 5
            
            if minuto >= 60:
                fecha += timedelta(hours=1)
                minuto = 0
                
            fecha = fecha.replace(hour=hora, minute=minuto, second=0)
            cell.value = fecha
        
        # Aplicar formato de fecha
        cell.style = date_style
    
    # Ajustar todas las columnas automáticamente
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        
        # Encontrar la longitud máxima del texto en la columna
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        
        # Aplicar un ancho ajustado con margen
        adjusted_width = (max_length + 2)
        
        # Para la columna A (fechas), aseguramos un ancho mínimo
        if column_letter == 'A':
            adjusted_width = max(adjusted_width, 20)
        
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Guardar archivo temporal y devolverlo
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
        wb.save(tmp_file.name)
        return tmp_file.name


@st.cache_data
# * Consolidar archivo
def consolidarArchivo(archivo):
    """
    Consolida los registros del archivo pasado por argumento agrupando los datos por fecha y calculando la media.
    """
    # Se obtiene el nombre y extensión del archivo
    archivo_nombre = archivo.name.split(".")[0]
    archivo_extension = archivo.name.split(".")[1]
    # Las variables son almacenadas en estados de sesión
    st.session_state["archivo_extension"] = archivo_extension
    st.session_state["nombre_archivo"] = archivo_nombre
    
    # Leer según la extensión
    if archivo_extension == "xlsx":
        df = pd.read_excel(archivo)
    else:  # csv
        # Intentar con diferentes codificaciones y delimitadores comunes
        try:
            df = pd.read_csv(archivo, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(archivo, encoding='latin1')
            except:
                df = pd.read_csv(archivo, encoding='ISO-8859-1')
        
        # Si hay problemas con el delimitador, intenta otros comunes
        if len(df.columns) == 1:
            for delimiter in [';', '\t', '|']:
                try:
                    df = pd.read_csv(archivo, sep=delimiter, encoding='utf-8')
                    if len(df.columns) > 1:
                        break
                except:
                    continue
    
    # Obtener encabezados
    Encabezados = list(df.columns)
    
    # Recortar la primera columna (fechas) a 16 caracteres
    df[Encabezados[0]] = df[Encabezados[0]].astype(str).str.slice(0, 16)
    
    # Consolidar datos agrupando por fecha y calculando medias
    df = df.groupby(Encabezados[0]).mean()
    
    # Convertir el índice a formato datetime
    df.index = pd.to_datetime(df.index, errors='coerce')
    
    # Celebración visual
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

# ?[testing] Testing variables
# todo [testing] En caso que el archivo haya sido subido, instancia las variables
if archivo:
    nombre_session_testing = f"{nombre_archivo}.{archivo_extension}"
    nombre_archivo_testing = archivo.name

# ? Condicional que muestra mensaje de inicio en caso de no haber elegido un archivo
# todo: En caso de que el usuario no haya elegido un archivo o lo haya retirado, se mostrará el mensaje
if archivo == None or nombre_archivo == None:
    st.write(mensaje_inicio)

# todo [testing] Si los nombres son diferentes, significa que el usuario ha cambiado de archivo
elif nombre_archivo_testing != nombre_session_testing:
    print(
        f"Los nombres son diferentes: Archivo que ha sido pasado: {nombre_archivo_testing}  Archivo en caché: {nombre_session_testing}"
    )
    st.write(mensaje_inicio)
    st.cache_data.clear()

elif nombre_archivo != None:
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
        st.write(archivo_consolidado)

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

            archivo_convertido = convertirExcel(archivo_consolidado)

            st.success("Datos formateados ✅")

            st.warning("Preparando archivo en Excel por defecto (.xlsx)")

            archivo_formateado = formatear_hora_minuto(archivo_convertido)

            archivo_ajustado = procesar_excel(archivo_formateado)

            st.success(
                "Archivo procesado y listo para descargar en formato Excel (.xlsx)"
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
                    "Selecciona elformato que desees para el archivo",
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
        # * En caso de ser en formato csv, realizar conversión
        if archivo_extension == "csv":
            df = pd.read_excel(archivo_ajustado)

            buffer = io.BytesIO()
            df.to_csv(buffer, index=False, encoding="cp1252")
            buffer.seek(0)

            st.download_button(
                label=f"Descargar en formato csv :material/download:",
                data=buffer,
                file_name=f"Consolidado_{nombre_archivo}.csv",
                mime="text/csv",
            )

            st.error(
                "Si abre el archivo con formato CSV en Excel, ajuste la primera celda ('A') para observar los datos."
            )
        else:
            # * En caso de ser xlsx
            with open(archivo_ajustado, "rb") as file:
                # * Botón para descargar EXCEL
                st.download_button(
                    f"Descargar en formato {archivo_extension} :material/download:",
                    data=file,
                    file_name=f"Consolidado_{nombre_archivo}.xlsx",
                )
