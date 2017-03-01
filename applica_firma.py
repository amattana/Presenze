from pyPdf import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from StringIO import StringIO
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle, Image


def applica_firma(file_firma, pdf_file):

    # Using ReportLab to insert image into PDF
    imgTemp = StringIO()
    imgDoc = canvas.Canvas(imgTemp)

    buff= 50

    # Draw image on Canvas and save PDF in buffer
    imgPath = file_firma
    imgDoc.drawImage(imgPath, 200, 190-buff, 200, 75)    ## at (399,760) with size 160x160

    p=imgDoc.beginPath()
    p.moveTo(200,210-buff)
    p.lineTo(400,210-buff)

    imgDoc.drawPath(p, stroke=1, fill=1)
    imgDoc.setFont("Helvetica", 8)
    imgDoc.drawString(260, 195-buff, "(Firma del Richiedente)")
    imgDoc.save()

    # Use PyPDF to merge the image-PDF into the template
    page = PdfFileReader(file(pdf_file,"rb")).getPage(0)
    overlay = PdfFileReader(StringIO(imgTemp.getvalue())).getPage(0)
    page.mergePage(overlay)

    #Save the result
    output = PdfFileWriter()
    output.addPage(page)
    output.write(file(pdf_file,"w"))

