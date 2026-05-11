import io
from fpdf import FPDF

def generar_pdf(texto_narrativa, df_ranking):
    """Compila la narrativa y los datos en un archivo PDF en memoria."""
    pdf = FPDF()
    pdf.add_page()
    
    # Configuración de página y título
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "Reporte de Inteligencia de Costos Bancarios", ln=True, align="C")
    pdf.ln(5)
    
    # Limpiar caracteres Markdown para el PDF básico
    texto_limpio = texto_narrativa.replace("**", "").replace("### 📌 ", "")
    
    # Sección de Narrativa
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "Resumen Ejecutivo:", ln=True)
    pdf.set_font("helvetica", "", 10)
    
    parrafos = texto_limpio.split("\n\n")
    for parrafo in parrafos:
        if parrafo.strip():
            pdf.multi_cell(0, 6, parrafo.strip())
            pdf.ln(3)
            
    pdf.ln(5)
    
    # Sección de Tabla de Ranking
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "Desglose Neto Acumulado por Entidad:", ln=True)
    pdf.set_font("helvetica", "", 10)
    
    # Encabezado de tabla
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(100, 8, "Entidad Bancaria", border=1)
    pdf.cell(50, 8, "Costo Neto Total", border=1, ln=True, align="R")
    pdf.set_font("helvetica", "", 10)
    
    # Filas de tabla
    for _, fila in df_ranking.iterrows():
        pdf.cell(100, 8, str(fila['Banco']), border=1)
        pdf.cell(50, 8, f"$ {fila['Costo']:,.2f}", border=1, ln=True, align="R")
        
    # Exportar a buffer de bytes para Streamlit
    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer
