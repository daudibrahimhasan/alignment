from pathlib import Path
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from xml.sax.saxutils import escape
import re,fitz
pdfmetrics.registerFont(TTFont('TNR',r'C:\Windows\Fonts\times.ttf'));pdfmetrics.registerFont(TTFont('TNR-Bold',r'C:\Windows\Fonts\timesbd.ttf'))
st=getSampleStyleSheet()
for x in st.byName.values():x.fontName='TNR';x.fontSize=10.5;x.leading=14
for k in ['Title','Heading1','Heading2']:st[k].fontName='TNR-Bold'
small=ParagraphStyle('cell',fontName='TNR',fontSize=8.5,leading=11)
def text_html(val):
 val=escape(val.replace('**',''))
 return re.sub(r'\[([^]]+)\]\((https?://[^)]+)\)',r'<link href="\2" color="blue">\1</link>',val)
story=[]
for name in ['STUDY_REPORT.md','FOLDER_REPORT.md']:
 if story:story.append(PageBreak())
 lines=Path(name).read_text(encoding='utf8').splitlines();i=0
 while i<len(lines):
  line=lines[i];i+=1
  if not line.strip() or line.startswith('!['):continue
  if line.startswith('|'):
   rows=[line]
   while i<len(lines) and lines[i].startswith('|'):rows.append(lines[i]);i+=1
   cells=[[Paragraph(text_html(c.strip()),small) for c in r.strip('|').split('|')] for r in rows if not r.startswith('| ---')]
   table=Table(cells,colWidths=[499/len(cells[0])]*len(cells[0]),repeatRows=1,hAlign='LEFT')
   table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eeeeee')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,0),.5,colors.grey)]));story.extend([table,Spacer(1,9)]);continue
  style=st['Title'] if line.startswith('# ') else st['Heading1'] if line.startswith('## ') else st['Heading2'] if line.startswith('### ') else st['BodyText']
  story.extend([Paragraph(text_html(line.lstrip('# ')),style),Spacer(1,5)])
SimpleDocTemplate('STUDY_REPORT.pdf',rightMargin=48,leftMargin=48,topMargin=44,bottomMargin=44).build(story)
pdf=fitz.open('STUDY_REPORT.pdf');Path('previews').mkdir(exist_ok=True)
for i in range(len(pdf)):pdf[i].get_pixmap(matrix=fitz.Matrix(.75,.75)).save(f'previews/report-{i+1}.png')
print('Rendered',len(pdf),'pages in Times New Roman')
