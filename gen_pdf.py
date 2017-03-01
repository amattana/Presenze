from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, cm,landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle, Image
from reportlab.platypus.flowables import PageBreak, Spacer
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate
from reportlab.lib.styles import ParagraphStyle
from reportlab.graphics.shapes import Line
from reportlab.graphics.shapes import Drawing
from pyPdf import PdfFileWriter, PdfFileReader
from StringIO import StringIO

import os
from web_test import go_to_records, init_feste, calcola_mese, stampa_oremin
import os.path

PATH_PDF = "/static/"

mesi={'Gennaio'   : '01', 
      'Febbraio'  : '02', 
      'Marzo'     : '03',
      'Aprile'    : '04',
      'Maggio'    : '05',
      'Giugno'    : '06',
      'Luglio'    : '07',
      'Agosto'    : '08',
      'Settembre' : '09',
      'Ottobre'   : '10',
      'Novembre'  : '11',
      'Dicembre'  : '12'
     }

def create_pdfdoc(pdfdoc, story):
    """
    Creates PDF doc from story.
    """
    MARGIN_SIZE = 25 * mm
    PAGE_SIZE = A4
    pdf_doc = BaseDocTemplate(pdfdoc, pagesize = PAGE_SIZE,
        leftMargin = MARGIN_SIZE, rightMargin = MARGIN_SIZE,
        topMargin = MARGIN_SIZE, bottomMargin = MARGIN_SIZE)
    main_frame = Frame(MARGIN_SIZE, MARGIN_SIZE,
        PAGE_SIZE[0] - 2 * MARGIN_SIZE, PAGE_SIZE[1] - 2 * MARGIN_SIZE,
        leftPadding = 0, rightPadding = 0, bottomPadding = 0,
        topPadding = 0, id = 'main_frame')
    main_template = PageTemplate(id = 'main_template', frames = [main_frame])
    pdf_doc.addPageTemplates([main_template])
    pdf_doc.build(story)

def applica_firma(file_firma, pdf_file):

    # Using ReportLab to insert image into PDF
    imgTemp = StringIO()
    imgDoc = canvas.Canvas(imgTemp)

    buff= 100

    # Draw image on Canvas and save PDF in buffer
    if os.path.isfile(file_firma):
        imgPath = file_firma
        imgDoc.drawImage(imgPath, 200, 190-buff, 200, 75)  

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
    os.rename(pdf_file, pdf_file[:-4]+"_A.pdf")
    #Save the result
    output = PdfFileWriter()
    output.addPage(page)
    output.write(file(pdf_file,"w"))


def genera_pdf(fname):
    """
    Crea il PDF dai dati elaborati del cartellino
    """
    f=open(fname,'r')
    lista=f.readlines()
    f.close() 
    pdf_name = "static/"+(lista[2][:-1].split(' ')[1]+"-"+mesi[lista[2][:-1].split(' ')[0]])+"_"+lista[1][:-1].replace(' ','_')+".pdf"

    #print lista
    n=go_to_records(lista)
    turni=lista[n:]

    tabella_turni = [['','Ingresso', 'Uscita']]
    for i in xrange(len(turni)):
        tabella_turni += [[str(i+1),turni[i][3:24].replace('E',''),turni[i].split(',')[1][1:22].replace('U','')]]
    

    feste=init_feste(int(lista[2].split(' ')[1][:-1]))
    giorno, notte, festa = calcola_mese(turni, feste)
    diurno = stampa_oremin(giorno)
    notturno = stampa_oremin(notte)
    festivo = stampa_oremin(festa)

    styleSheet = getSampleStyleSheet()
    story = []
    a=Image("inaf_logo.png", 1.6*inch, 1.6*inch)
    data=[[a, "ISTITUTO NAZIONALE DI ASTROFISICA\n\nISTITUTO DI RADIOASTRONOMIA"]]

    table = Table(data, colWidths=200, rowHeights=100)
    table.setStyle(TableStyle([
                          ('INNERGRID', (0,0), (-1,-1), 0, colors.white),
                          ('BOX', (0,0), (-1,-1), 0, colors.white),
                          ('BACKGROUND',(0,0),(-1,-1),colors.white),
                          ('ALIGN',(0,0),(-1,-1),'CENTER'),
                          ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                          ]))
    #story.append(Spacer(0, 5 * mm))
    story.append(table)
    story.append(Spacer(0, 10 * mm))
    story.append(Paragraph(lista[1][:-1]+" - "+lista[2][:-1], styleSheet['Title']))
    story.append(Spacer(0, 6 * mm))


    parstyle=ParagraphStyle(
        'title',
        fontName='Helvetica-Bold',
        fontSize=16,
        alignment=TA_CENTER,
        )
    story.append(Paragraph("Giornate in turno:", parstyle))
    story.append(Spacer(0, 10 * mm))
    table = Table(tabella_turni, colWidths=(30,150,150), rowHeights=20)
    table.setStyle(TableStyle([
                          ('INNERGRID', (0,0), (-1,-1), 0.25, colors.gray),
                          ('BOX', (0,0), (-1,-1), 0.25, colors.gray),
                          ('BACKGROUND',(0,0),(-1,-1),colors.white),
                          ('ALIGN',(0,0),(-1,-1),'CENTER'),
                          ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                          ]))
    story.append(table)

    story.append(Spacer(0, 10 * mm))

    parstyle=ParagraphStyle(
        'title',
        fontName='Helvetica-Bold',
        fontSize=16,
        alignment=TA_CENTER,
    )
    story.append(Paragraph("Riepilogativo Turni:", parstyle))

    story.append(Spacer(0, 10 * mm))
    table_style =[
                          ('INNERGRID', (0,0), (-1,-1), 0.25, colors.gray),
                          ('BOX', (0,0), (-1,-1), 0.25, colors.gray),
                          ('BACKGROUND',(0,0),(-1,-1),colors.white),
                          ('ALIGN',(0,0),(-1,-1),'LEFT'),
                          ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                          ] 

    data=[['Diurno:', diurno],
      ['Notturno:', notturno],
      ['Festivo:', festivo],
     ]
    table = Table(data, colWidths=(70,110), rowHeights=20)
    table.setStyle(table_style)
    story.append(table)

    story.append(Spacer(0, 10 * mm))
    #story.append(Spacer(0, 5 * mm))
    d = Drawing(200, 1)
    file_firma = "firme/"+lista[3][:-1]+".png"
    #if os.path.isfile(file_firma):
    #    a=Image(file_firma, 300/2, 90/2)
    #    story.append(a)
    #else:
    #    story.append(Spacer(0, 10 * mm))
    #    d.add(Line(150, 0, 300, 0))
    #    story.append(d)
    #    parstyle=ParagraphStyle(
    #        'title',
    #        fontName='Helvetica',
    #        fontSize=8,
    #        alignment=TA_CENTER,
    #    )
    #    story.append(Paragraph("(Firma del Richiedente)", parstyle))

    if os.path.isfile(fname[:-4]+".note"):
        parstyle=ParagraphStyle(
            'normal',
            fontName='Helvetica-Bold',
            fontSize=10,
            alignment=TA_CENTER,
            underlineProportion=1,
            )
        story.append(Paragraph("""<u>NOTE</u>:""", parstyle))
        story.append(Spacer(0, 4 * mm))
        n=open(fname[:-4]+".note","r")
        nota=n.readlines()
        n.close()
        parstyle=ParagraphStyle(
            'normal',
            fontName='Helvetica',
            fontSize=10,
            alignment=TA_CENTER,
            )
        for h in nota:
            story.append(Paragraph(h, parstyle))

    create_pdfdoc(pdf_name, story)

    applica_firma(file_firma, pdf_name)

    return pdf_name

if __name__ == "__main__":
    genera_pdf(sys.argv[1])


