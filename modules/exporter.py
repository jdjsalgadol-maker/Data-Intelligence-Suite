import io
from fpdf import FPDF

def generar_pdf(texto_narrativa, df_ranking, figuras_dict):
    """Compila narrativa, tabla y gráficos en un PDF con diseño corporativo a color."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- PÁGINA 1: PORTADA Y NARRATIVA ---
    pdf.add_page()
    
    # 🎨 PALETA DE COLORES RGB
    AZUL_CORP = (24, 83, 160)       # Azul vibrante institucional (#1853A0)
    BLANCO = (255, 255, 255)        # Blanco puro
    GRIS_TEXTO = (60, 60, 60)       # Gris carbón para texto (facilita la lectura)
    AZUL_CLARO = (240, 245, 250)    # Azul pastel para alternar filas en tablas
    
    # 1. Franja superior de color puro (Diseño de Encabezado)
    pdf.set_fill_color(*AZUL_CORP)
    pdf.rect(0, 0, 210, 6, "F")  # Dibuja una franja de color en el borde superior (A4 = 210mm)
    
    pdf.ln(5)
    pdf.set_font("helvetica", "B", 20)
    pdf.set_text_color(*AZUL_CORP)
    pdf.cell(0, 10, "Reporte de Inteligencia Financiera", ln=True, align="C")
    
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 5, "Análisis de Costos Bancarios y Tendencias", ln=True, align="C")
    pdf.ln(10)
    
    # 2. Título de Sección: Narrativa
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(*AZUL_CORP)
    pdf.cell(0, 8, "1. Resumen Ejecutivo", ln=True)
    
    # Línea divisoria a color
    pdf.set_draw_color(*AZUL_CORP)
    pdf.set_line_width(0.5)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(5)
    
    # Texto de la narrativa
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(*GRIS_TEXTO)
    texto_limpio = texto_narrativa.replace("**", "").replace("### 📌 ", "")
    pdf.multi_cell(0, 6, texto_limpio)
    pdf.ln(10)
    
    # 3. Título de Sección: Tabla
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(*AZUL_CORP)
    pdf.cell(0, 8, "2. Consolidado Neto por Entidad", ln=True)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(5)
    
    # Encabezado de la tabla (Fondo Azul, Texto Blanco)
    pdf.set_fill_color(*AZUL_CORP)
    pdf.set_text_color(*BLANCO)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(110, 9, "  Entidad Bancaria", border=0, fill=True)
    pdf.cell(70, 9, "Costo Neto Total  ", border=0, ln=True, align="R", fill=True)
    
    # Filas de la tabla con colores alternados (Zebra Striping)
    pdf.set_font("helvetica", "", 10)
    fill = False
    
    for _, fila in df_ranking.iterrows():
        # Alternar color de fondo entre blanco y azul pastel
        if fill:
            pdf.set_fill_color(*AZUL_CLARO)
        else:
            pdf.set_fill_color(*BLANCO)
            
        pdf.set_text_color(*GRIS_TEXTO)
        pdf.set_draw_color(220, 220, 220)  # Borde inferior sutil en gris claro
        
        pdf.cell(110, 8, f"  {fila['Banco']}", border="B", fill=fill)
        pdf.cell(70, 8, f"$ {fila['Costo']:,.2f}  ", border="B", ln=True, align="R", fill=fill)
        fill = not fill  # Cambiar estado para la siguiente fila
        
    pdf.ln(10)
    
    # --- PÁGINA 2: GRÁFICOS A COLOR ---
    pdf.add_page()
    pdf.set_font("helvetica", "B", 14)
    pdf.
