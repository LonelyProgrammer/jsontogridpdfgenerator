# -*- coding:utf-8 -*-
import os
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import pdfencrypt, colors
from reportlab.platypus import *
from reportlab.platypus import Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import *
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import enum


class Margins(int, enum.Enum):
    left = 72
    right = 72
    top = 72
    bottom = 18

class FontStyle(str, enum.Enum):
    Normal = ''
    Bold = '-Bold'
    Italic = '-italic'    
    Bold_Italic = Bold+Italic
        

class text2Pdf():
    """docstring for text2Pdf"""

    def __init__(self, filename):
        pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
        self.fileName = filename
        self.point = 1
        self.font = "Arial"
        self.fontSize = 10  
        self.styles = None
        self.createStyle()
        self.elements = []

    def readFonts(self,path):
        return os.listdir(path)
    
    def setFont(self, fontname):
        fontList = self.readFonts(os.path.abspath('/app/Fonts/'))
        for aFont in fontList:
            if aFont == fontname+'.ttf':
                pdfmetrics.registerFont(TTFont(fontname, os.path.abspath('/app/Fonts/') + '/' + aFont, subfontIndex=0))
            if aFont == fontname+' Bold'+'.ttf':
                pdfmetrics.registerFont(TTFont(fontname+FontStyle.Bold, os.path.abspath('/app/Fonts/') + '/'+ aFont, subfontIndex=0))    
            if aFont == fontname+' Italic'+'.ttf':
                pdfmetrics.registerFont(TTFont(fontname+FontStyle.Italic,  os.path.abspath('/app/Fonts/') + '/'+ aFont, subfontIndex=0))
            if aFont == fontname+' Bold Italic'+'.ttf':
                pdfmetrics.registerFont(TTFont(fontname+FontStyle.Bold_Italic, os.path.abspath('/app/Fonts/') + '/'+ aFont, subfontIndex=0))

        self.font = fontname

    def createStyle(self):
        del self.styles
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name='Justify',fontName=self.font,fontSize=self.fontSize, leading=12, alignment=TA_JUSTIFY, spaceBefore=10))
        self.styles.add(ParagraphStyle(name='Table_unicode',fontName="Arial",fontSize=self.fontSize, alignment=TA_JUSTIFY))

    def addStyle(self, stylename = None, fontname = None, fontsize = None, fontstyle=FontStyle.Normal, rightindent = 0, leftindent=0, firstlineindent=0):
        fontname = self.font
        fontsize = self.fontSize
        self.styles.add(ParagraphStyle(name=stylename,fontName=fontname + fontstyle,fontSize=fontsize, leading=12, alignment=TA_JUSTIFY, spaceBefore=10, rightIndent = rightindent, leftIndent= leftindent, firstLineIndent= firstlineindent))

    def addImage(self,imagePath, width=None, height=None, hAlign='LEFT'):
        im = Image(imagePath, width=width, height=height, hAlign=hAlign)
        self.elements.append(im)


    def addTable(self, table, cols):
        newTable = []
        for item in table:
            tempTable = []
            for i in xrange(0,cols):
                tempTable.append(Paragraph(item[i], self.styles["Table_unicode"], encoding="utf-8"))
            newTable.append(tempTable)

        _w,_h = A4
        _w -= ((Margins.left+Margins.right)+13)
        _w = (_w / cols)
        t=Table(newTable,_w, len(table)*[0.25*inch])
        t.setStyle(TableStyle([('ALIGN',(1,1),(-2,-2),'LEFT'),
                    ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                    ('BOX', (0,0), (-1,-1), 0.25, colors.black)]))
        self.elements.append(t)
        
    def addContent(self, content, style):
        self.elements.append(Paragraph(content, self.styles[style], encoding="utf-8"))
            

    def make_pdf_file_with_password(self, password):
        doc = BaseDocTemplate(self.fileName, pagesize = A4, rightMargin=Margins.right,leftMargin=Margins.left,topMargin=Margins.top,bottomMargin=Margins.bottom, encrypt=password)
        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='docFrame')
        doc.addPageTemplates([PageTemplate(id='doc', frames=frame)])
        doc.build(self.elements)
