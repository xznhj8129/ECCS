#!/usr/bin/python2
# -*- coding: utf-8 -*-
from fpdf import FPDF
import pickle

with open('brevitycodes','r') as file:
    codes = file.read()
codes = codes[:len(codes)-1]
codes = codes.upper().split('\n')
codes.sort()

codebook = {}
wordlen = len(codes)

padid = '00001'
date = '1-1-1'

pdf = FPDF()
pdf.add_page()
pdf.set_font("Courier", size=24,style='B')

pdf.cell(0, 20, txt="TOP SECRET", ln=1, align="C")
pdf.cell(0, 5, txt="BREVITY CODES", ln=1, align="C")
pdf.cell(0, 5, txt='', ln=1, align="C")
pdf.set_font("Courier", size=12)
pdf.cell(0, 5, txt=date, ln=1, align="C")
pdf.cell(0, 5, txt='PAD ID: '+padid, ln=1, align="C")
pdf.set_font("Courier", size=12, style='B')
pdf.cell(0, 10, txt='DESTROY BY BURNING WHEN IN RISK OF CAPTURE', ln=1, align="C")
pdf.cell(0, 5, txt='', ln=1, align="C")
txt='TOP SECRET\nBREVITY CODES\n{}\nPAD ID: {}\n'.format(date,padid)
txt=txt+'SECURELY WIPE WHEN IN RISK OF CAPTURE\n\n'
    
pdf.set_font("Courier", size=11)
if wordlen < 100:
    with open('codenumbers100','r') as file:
        use = file.read().split('\n')
elif wordlen < 220:
    with open('codenumbers220','r') as file:
        use = file.read().split('\n')
elif wordlen < 807:
    with open('codenumbers807','r') as file:
        use = file.read().split('\n')

x = []
for i in range(len(codes)):
    #print use[i],codes[i]
    codebook[use[i]] = codes[i]
    x.append((use[i], codes[i]))
    txt+= '{}    {}\n'.format(use[i],codes[i])

pages = []
lines = []
linelen = 52
columns=1
cc = 0
n = 0

while 1:
    
    if cc >= (linelen):
        columns += 1
        
    if columns > 2:
        cc = 0
        pages.append(lines)
        lines = []
        columns = 1
    
    if len(pages)>0:
        linelen = 65

    for i in range(linelen):
        
        try:
            l = x.pop(0)
        except IndexError:
            l = ('   ','    ')
            
        #print n, i, columns, cc, len(pages), l[1],linelen
        
        len1 = 28 - (4+len(l[1]))
        spc1 = ''
        for k in range(len1):
            spc1+=' '
            
        if columns == 1:
            lines.append('{}  {}{}'.format( l[0], l[1], spc1 ))
        else:
            lines[i] = lines[i]+'{}  {}{}'.format( l[0], l[1], spc1 )
   
        n += 1
        cc += 1
    
    cc = 0
    columns += 1
    if len(x) == 0:
        pages.append(lines)
        break

while len(pages)>0:
    page = pages.pop(0)
    for i in page:
        pdf.cell(0, 4, txt=''+i, ln=1, align="C")
    if len(pages)>0:
        pdf.add_page()

pdf.output("{}_{}_codes.pdf".format(date,padid))
with open('{}_{}_codes.pickle'.format(date,padid), 'wb') as f:
    pickle.dump(codebook, f, pickle.HIGHEST_PROTOCOL)
with open('{}_{}_codes.txt'.format(date,padid), "w") as file:
    file.write(txt)

