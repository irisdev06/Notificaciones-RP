import streamlit as st
import pandas as pd
import xlsxwriter
from datetime import datetime
from io import BytesIO


# ------------------ Función que crea la columna de alerta ------------------
def columna_alertavencimiento(archivo):
    df = pd.read_excel(archivo, sheet_name="REVISION PENSION 2025")

    if "FECHA DE ULTIMA REVISION" not in df.columns:
        st.error("⚠️ La columna 'FECHA DE ULTIMA REVISION' no está en la hoja REVISION PENSION 2025.")
        return None

    # Convertir a fechas
    df["FECHA DE ULTIMA REVISION"] = pd.to_datetime(df["FECHA DE ULTIMA REVISION"], errors="coerce")
    hoy = pd.to_datetime(datetime.now().date())

    def evaluar_fecha(x):
        if pd.isnull(x):
            return "SIN FECHA"
        fecha_vencimiento = x + pd.DateOffset(years=3)
        dias_restantes = (fecha_vencimiento - hoy).days

        if dias_restantes <= 15:
            return "ALERTA ROJA"
        elif dias_restantes <= 30:
            return "ALERTA AMARILLA"
        elif dias_restantes <= 90:
            return "ALERTA VERDE"
        else:
            return "EN TÉRMINOS"

    df["ALERTA DE VENCIMIENTO"] = df["FECHA DE ULTIMA REVISION"].apply(evaluar_fecha)
    return df


# ------------------ Helper: convertir índice de columna a letra Excel ------------------
def colnum_to_excel(col_idx):
    """0-based column index -> Excel column letter (A, B, ..., Z, AA, AB, ...)"""
    s = ""
    while col_idx >= 0:
        s = chr(col_idx % 26 + 65) + s
        col_idx = col_idx // 26 - 1
    return s


# ------------------ Color usando XlsxWriter (más robusto) ------------------
def exportar_con_estilo(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="REVISION PENSION 2025")
        workbook = writer.book
        worksheet = writer.sheets["REVISION PENSION 2025"]

        # Índice de la columna ALERTA DE VENCIMIENTO
        col_idx = df.columns.get_loc("ALERTA DE VENCIMIENTO")

        # Formatos
        formato_rojo = workbook.add_format({"bg_color": "#FF6961", "bold": True})      # rojo
        formato_amarillo = workbook.add_format({"bg_color": "#FFD966", "bold": True})  # amarillo
        formato_verde = workbook.add_format({"bg_color": "#77DD77", "bold": True})     # verde
        formato_gris = workbook.add_format({"bg_color": "#D3D3D3", "italic": True})    # gris
        formato_azul = workbook.add_format({"bg_color": "#9BC2E6"})                    # azul

        # Filas de datos (empezando en 1 porque la fila 0 es encabezado)
        start_row = 1
        end_row = start_row + len(df) - 1

        # Reglas condicionales exactas
        reglas = [
            ("ALERTA ROJA", formato_rojo),
            ("ALERTA AMARILLA", formato_amarillo),
            ("ALERTA VERDE", formato_verde),
            ("SIN FECHA", formato_gris),
            ("EN TÉRMINOS", formato_azul),
        ]

        for texto, formato in reglas:
            worksheet.conditional_format(
                start_row, col_idx, end_row, col_idx,
                {"type": "cell", "criteria": "equal to", "value": f'"{texto}"', "format": formato}
            )

        # Encabezado con color distintivo
        formato_encabezado = workbook.add_format(
            {"bg_color": "#5A6772", "bold": True, "font_color": "white"}
        )
        worksheet.write(0, col_idx, df.columns[col_idx], formato_encabezado)

    output.seek(0)
    return output

# ------------------ Función principal/orquestadora ------------------
def procesar_archivos():
    st.write("📂 Cargar archivo Excel para revisión de vencimientos")

    archivo = st.file_uploader("Sube el archivo Excel", type=["xlsx", "xls"])

    if archivo is not None:
        try:
            df = columna_alertavencimiento(archivo)
            if df is not None:
                st.dataframe(df, use_container_width=True)

                # Exportar con estilo rosado en Excel
                output = exportar_con_estilo(df)
                st.download_button(
                    "⬇️ Descargar archivo con estilo",
                    data=output,
                    file_name="archivo_procesado.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
        except Exception as e:
            st.error(f"❌ Error al procesar el archivo: {e}")
