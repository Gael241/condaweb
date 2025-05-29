import pandas as pd
import openpyxl
import streamlit as st
import io

def formatear_hora_minuto(df):
    """Convierte la primera columna de un DataFrame a datetime y extrae solo la hora."""
    primera_columna = df.columns[0]
    primera_columna
    df[primera_columna] = pd.to_datetime(df[primera_columna], errors='coerce')
    df[primera_columna] = df[primera_columna].apply(lambda dt: dt.time() if pd.notnull(dt) else dt)
    return df

def convertir_a_excel(df):
    """Convierte un DataFrame a un archivo Excel en memoria con formato hh:mm."""
    output = io.BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)

    wb = openpyxl.load_workbook(output)
    ws = wb.active
    
    for row in ws.iter_rows(min_row=2, min_col=1, max_col=1):
        for cell in row:
            cell.number_format = 'hh:mm'
    
    output.seek(0)
    return output

st.title("Conversión de Hora en Archivos CSV/XLSX 📄⏰")

archivo = st.file_uploader("Sube tu archivo aquí", ["csv", "xlsx"])

if archivo:
    st.caption("Haz clic sobre ✖️ para eliminar el archivo.")

    if archivo.name.endswith(".csv"):
        df = pd.read_csv(archivo)
    else:
        df = pd.read_excel(archivo)

    df_transformado = formatear_hora_minuto(df)

    st.subheader("Vista previa de datos formateados:")
    st.dataframe(df_transformado)

    archivo_excel = convertir_a_excel(df_transformado)

    st.download_button(
        label="📥 Descargar archivo formateado",
        data=archivo_excel,
        file_name=f"formateado_{archivo.name.split('.')[0]}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

"""if (
    "archivo_consolidado" in st.session_state
    and st.session_state["archivo_consolidado"] is not None
):
    st.caption('Puedes observar tu archivo consolidado en la sección "Vista previa de datos procesados :material/table:"')

    tab_info, tab_data = st.tabs(
        [
            "Características e información del archivo :material/info:",
            "Vista previa de datos procesados:material/table:",
        ]
    )

    tab_info.info(
        "Consolidación hecha con éxito ✅... Empezando a transformar el archivo a Excel ⏰",
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
                    help="Por defecto, el archivo que se exporta se encuentra en formato Excel.",
                    key="selector",
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
    )"""