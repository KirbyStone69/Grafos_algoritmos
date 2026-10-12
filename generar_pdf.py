"""Generador de documento PDF a partir de las capturas en orden numérico.

Uso:
    python generar_pdf.py
    python generar_pdf.py --algoritmo dijkstra
    python generar_pdf.py --salida "Resolucion_Algoritmos.pdf"
"""
import argparse
import sys
from pathlib import Path
from PIL import Image
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

CARPETA_CAPTURAS = Path("capturas_pasos")
PDF_SALIDA_DEFAULT = Path("Resolucion_Grafos_Algoritmos.pdf")


def crear_pdf(carpeta_base=CARPETA_CAPTURAS, ruta_pdf=PDF_SALIDA_DEFAULT, algoritmo_filtro=None):
    carpeta_base = Path(carpeta_base)
    ruta_pdf = Path(ruta_pdf)

    if not carpeta_base.exists():
        print(f"Error: La carpeta {carpeta_base} no existe. Ejecuta primero 'python capturar_pasos.py'.")
        return False

    subcarpetas = sorted([d for d in carpeta_base.iterdir() if d.is_dir()])
    if algoritmo_filtro and algoritmo_filtro != "todos":
        subcarpetas = [d for d in subcarpetas if d.name == algoritmo_filtro]

    if not subcarpetas:
        print(f"No se encontraron capturas para procesar en {carpeta_base}.")
        return False

    print(f"\n==========================================")
    print(f"Generando PDF: {ruta_pdf.resolve()}")
    print(f"==========================================")

    # Documento horizontal (landscape letter: 792 x 612 pt)
    ancho_pag, alto_pag = landscape(letter)
    margen = 25
    doc = SimpleDocTemplate(
        str(ruta_pdf),
        pagesize=landscape(letter),
        leftMargin=margen,
        rightMargin=margen,
        topMargin=margen,
        bottomMargin=margen
    )

    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        'TituloPrincipal',
        parent=estilos['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#20452f'),
        alignment=1, # Centrado
        spaceAfter=10
    )
    estilo_subtitulo = ParagraphStyle(
        'SubtituloPrincipal',
        parent=estilos['Normal'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#48c878'),
        alignment=1,
        spaceAfter=15
    )
    estilo_pie = ParagraphStyle(
        'PieFoto',
        parent=estilos['Italic'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#333333'),
        alignment=1
    )

    elementos = []

    # Portada del reporte
    elementos.append(Spacer(1, 100))
    elementos.append(Paragraph("RESOLUCIÓN PASO A PASO DE ALGORITMOS EN GRAFOS", estilo_titulo))
    elementos.append(Paragraph("Dijkstra · Bellman–Ford · Floyd–Warshall · A*", estilo_subtitulo))
    elementos.append(Spacer(1, 40))

    info_portada = [
        ["Materia:", "Fundamentos de la Inteligencia Artificial"],
        ["Unidad:", "Unidad 1 - Grafos y Algoritmos de Búsqueda"],
        ["Reporte:", "Trazado y Visualización Secuencial de Pasos"],
    ]
    tabla_info = Table(info_portada, colWidths=[120, 300])
    tabla_info.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#20452f')),
        ('TEXTCOLOR', (1,0), (1,-1), colors.HexColor('#333333')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    elementos.append(tabla_info)
    elementos.append(PageBreak())

    ancho_disponible = ancho_pag - (2 * margen)
    alto_disponible = alto_pag - (2 * margen) - 50 # espacio para texto

    total_imagenes_agregadas = 0

    for subcarpeta in subcarpetas:
        nombre_algo = subcarpeta.name.replace("_", " ").title()
        # Buscar imágenes ordenadas numéricamente
        archivos_imgs = sorted(list(subcarpeta.glob("*.png")))
        if not archivos_imgs:
            continue

        print(f"Añadiendo {len(archivos_imgs)} capturas de '{nombre_algo}'...")

        for idx, ruta_img in enumerate(archivos_imgs, start=1):
            # Obtener dimensiones originales con PIL
            with Image.open(ruta_img) as im:
                ancho_orig, alto_orig = im.size

            ratio = min(ancho_disponible / ancho_orig, alto_disponible / alto_orig)
            w_final = ancho_orig * ratio
            h_final = alto_orig * ratio

            elementos.append(Paragraph(f"<b>{nombre_algo.upper()}</b> — Captura {idx} de {len(archivos_imgs)} ({ruta_img.name})", estilo_subtitulo))
            elementos.append(RLImage(str(ruta_img), width=w_final, height=h_final))
            elementos.append(Spacer(1, 6))
            elementos.append(Paragraph(f"Secuencia: {ruta_img.stem}", estilo_pie))
            elementos.append(PageBreak())
            total_imagenes_agregadas += 1

    doc.build(elementos)
    print(f"\n[OK] PDF generado con exito: {ruta_pdf.resolve()}")
    print(f"[OK] Total de paginas/capturas incluidas: {total_imagenes_agregadas}")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compila las capturas ordenadas en un archivo PDF.")
    parser.add_argument("--carpeta", default=str(CARPETA_CAPTURAS), help="Carpeta que contiene las capturas.")
    parser.add_argument("--salida", default=str(PDF_SALIDA_DEFAULT), help="Nombre del archivo PDF resultante.")
    parser.add_argument("--algoritmo", default="todos", help="Algoritmo específico a compilar (opcional).")
    args = parser.parse_args()

    crear_pdf(args.carpeta, args.salida, args.algoritmo)
