from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet


def generar_pdf(figuras, titulo, nombre_pdf):

    doc = SimpleDocTemplate(nombre_pdf)

    styles = getSampleStyleSheet()

    elementos = []

    elementos.append(
        Paragraph(titulo, styles['Title'])
    )

    elementos.append(Spacer(1, 20))

    for i, fig in enumerate(figuras):

        img = f"grafico_{i}.png"

        fig.write_image(img)

        elementos.append(
            Image(img, width=450, height=250)
        )

        elementos.append(Spacer(1, 10))

    doc.build(elementos)

    return nombre_pdf