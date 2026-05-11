import io
from fpdf import FPDF

def generar_pdf(texto_narrativa, df_ranking, figuras_dict):
    """Compila narrativa, tabla y gráficos en un PDF."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- PÁGINA 1: TÍTULO Y NARRATIVA ---
    pdf.add_page()
    pdf.set_font("helvetica", "B", 18)
    pdf.set_text_color(31, 73, 125) # Azul institucional
    pdf.cell(0, 15, "Reporte Ejecutivo de Costos Bancarios", ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "1. Resumen y Análisis de Tendencia:", ln=True)
    pdf.set_font("helvetica", "", 10)
    
    # Limpiar y escribir narrativa
    texto_limpio = texto_narrativa.replace("**", "").replace("### 📌 ", "")
    pdf.multi_cell(0, 6, texto_limpio)
    pdf.ln(10)

    # --- PÁGINA 2: GRÁFICOS PRINCIPALES ---
    pdf.add_page()
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "2. Visualización de Datos:", ln=True)
    
    # Iterar sobre los gráficos y agregarlos al PDF
    for titulo, fig in figuras_dict.items():
        # Convertir gráfico de Plotly a imagen PNG en memoria
        img_bytes = fig.to_image(format="png", width=800, height=450, scale=2)
        img_buffer = io.BytesIO(img_bytes)
        
        pdf.set_font("helvetica", "I", 10)
        pdf.cell(0, 8, f"Gráfico: {titulo}", ln=True)
        # Insertar imagen (ajustando ancho a 180mm para que quepa en A4)
        pdf.image(img_buffer, x=15, w=180)
        pdf.ln(5)

    # --- TABLA DE DATOS AL FINAL ---
    pdf.ln(10)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "3. Consolidado Neto por Entidad:", ln=True)
    
    pdf.set_font("helvetica", "B", 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(100, 8, "Entidad Bancaria", border=1, fill=True)
    pdf.cell(50, 8, "Costo Neto Total", border=1, ln=True, align="R", fill=True)
    
    pdf.set_font("helvetica", "", 10)
    for _, fila in df_ranking.iterrows():
        pdf.cell(100, 8, str(fila['Banco']), border=1)
        pdf.cell(50, 8, f"$ {fila['Costo']:,.2f}", border=1, ln=True, align="R")
        
    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer
