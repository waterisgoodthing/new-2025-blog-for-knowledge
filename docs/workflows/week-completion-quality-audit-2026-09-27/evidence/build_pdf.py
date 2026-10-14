from pathlib import Path
import re,html,json
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor,white
from reportlab.lib.pagesizes import A4,landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=Path(__file__).resolve().parents[4]
SRC=ROOT/'Personal_Learning_System_Week_Completion_Quality_Audit.md'
OUT=ROOT/'Personal_Learning_System_Week_Completion_Quality_Audit.pdf'
pdfmetrics.registerFont(TTFont('Audit','/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
W,H=landscape(A4); margin=36; width=W-2*margin
styles={
 'body':ParagraphStyle('body',fontName='Audit',fontSize=9.5,leading=14.6,spaceAfter=7,wordWrap='CJK',textColor=HexColor('#223147')),
 'cell':ParagraphStyle('cell',fontName='Audit',fontSize=8.3,leading=12,wordWrap='CJK',textColor=HexColor('#223147')),
 'headcell':ParagraphStyle('headcell',fontName='Audit',fontSize=8.5,leading=12,wordWrap='CJK',textColor=white),
 'title':ParagraphStyle('title',fontName='Audit',fontSize=24,leading=34,spaceAfter=18,textColor=HexColor('#122f4e'),wordWrap='CJK'),
 'h2':ParagraphStyle('h2',fontName='Audit',fontSize=15,leading=22,spaceBefore=16,spaceAfter=10,keepWithNext=True,textColor=HexColor('#126677'),wordWrap='CJK'),
 'h3':ParagraphStyle('h3',fontName='Audit',fontSize=11.5,leading=17,spaceBefore=10,spaceAfter=7,keepWithNext=True,textColor=HexColor('#254a67'),wordWrap='CJK'),
 'code':ParagraphStyle('code',fontName='Audit',fontSize=8.5,leading=13,spaceAfter=5,wordWrap='CJK',backColor=HexColor('#eef4f6')),
}
def clean(s):
 s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'\1',s)
 s=s.replace('**','').replace('`','')
 return html.escape(s).replace('→',' → ').replace('←',' ← ')
def para(s,style='body'):return Paragraph(clean(s),styles[style])
lines=SRC.read_text().splitlines();story=[];i=0;in_code=False;table_count=0
while i<len(lines):
 l=lines[i]
 if not l.strip():i+=1;continue
 if l.startswith('```'):
  i+=1;code=[]
  while i<len(lines) and not lines[i].startswith('```'):
   code.append(lines[i]);i+=1
  story.append(Paragraph('<br/>'.join(html.escape(x).replace(' ','&nbsp;') for x in code),styles['code']));i+=1;continue
 if l.startswith('|'):
  rows=[]
  while i<len(lines) and lines[i].startswith('|'):
   row=[x.strip() for x in lines[i].strip().strip('|').split('|')]
   if not all(re.fullmatch(r':?-+:?',x) for x in row):rows.append(row)
   i+=1
  n=max(map(len,rows)); rows=[r+['']*(n-len(r)) for r in rows]
  # ID/task columns stay compact; allocate room to implementation and evidence.
  if n==7:ratios=[.065,.145,.22,.23,.17,.105,.065]
  elif n==6:ratios=[.07,.20,.285,.225,.135,.085]
  elif n==5:ratios=[.12,.26,.19,.29,.14]
  elif n==4:ratios=[.17,.30,.19,.34]
  elif n==3:ratios=[.20,.36,.44]
  else:ratios=[1/n]*n
  if n==7 and 'Debt' in rows[0][1]:ratios=[.055,.20,.11,.085,.16,.19,.20]
  if n==6 and rows[0][0].startswith('Layer'):ratios=[.12,.12,.235,.13,.255,.14]
  if n==5 and rows[0][0].startswith('路线/'):ratios=[.14,.20,.25,.19,.22]
  if rows[0][0]=='ID' and n>=10:ratios=[.055,.105,.045,.085,.1,.16,.045,.12,.09,.105][:n]
  total=sum(ratios);cw=[width*r/total for r in ratios]
  data=[[para(x,'headcell' if ri==0 else 'cell') for x in row] for ri,row in enumerate(rows)]
  t=Table(data,colWidths=cw,repeatRows=1,hAlign='LEFT')
  t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#184d66')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('ROWBACKGROUNDS',(0,1),(-1,-1),[white,HexColor('#f1f5f7')]),('LINEBELOW',(0,0),(-1,0),.5,HexColor('#184d66')),('LINEBELOW',(0,1),(-1,-1),.3,HexColor('#d2dce1'))]))
  story.extend([t,Spacer(1,9)]);table_count+=1;continue
 if l.startswith('# '):story.append(para(l[2:],'title'))
 elif l.startswith('## '):story.append(para(l[3:],'h2'))
 elif l.startswith('### '):story.append(para(l[4:],'h3'))
 else:story.append(para(l))
 i+=1
def page(c,doc):
 c.saveState();c.setStrokeColor(HexColor('#bed0da'));c.line(margin,H-25,W-margin,H-25)
 c.setFont('Audit',7);c.setFillColor(HexColor('#52677c'));c.drawString(margin,H-19,'个人学习系统  |  全 Week 完成质量审计  |  2026-09-27')
 c.drawString(margin,18,'证据驱动审计 · 本地验证不等于生产验收 · 未修改业务代码');c.drawRightString(W-margin,18,str(doc.page));c.restoreState()
doc=SimpleDocTemplate(str(OUT),pagesize=(W,H),rightMargin=margin,leftMargin=margin,topMargin=37,bottomMargin=34,title='个人学习系统全 Week 完成质量技术审计',author='Technical Audit')
doc.build(story,onFirstPage=page,onLaterPages=page)
print(json.dumps({'pdf':str(OUT),'source_chars':len(SRC.read_text()),'tables':table_count},ensure_ascii=False))
