#!/usr/bin/python3

from Crypto import Random
from Crypto.Random import random
import string
import hashlib
import binascii
import os
import sys
import pickle
import argparse
from fpdf import FPDF
import datetime

def randcode():
    return ''.join(random.choice('ABCDEFGHJKLMNPRSTUVWXYZ1234567890') for _ in range(4))

def randnumber():
    return random.choice(range(0,9))

def gen_otp(padlen,date,padid, args):
    
    block_h = 16
    block_w = 10
    raw = ''
    rawseg = ''
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", size=24,style='B')
    pdf.cell(0, 20, txt="TOP SECRET", ln=1, align="C")
    pdf.set_font("Courier", size=20, style='B')
    pdf.cell(0, 5, txt="ONE TIME PAD CODEBOOK", ln=1, align="C")
    pdf.set_font("Courier", size=12)
    pdf.cell(0, 5, txt='', ln=1, align="C")
    pdf.cell(0, 5, txt=date, ln=1, align="C")
    pdf.cell(0, 5, txt='PAD ID: '+padid, ln=1, align="C")
    pdf.set_font("Courier", size=12, style='B')
    pdf.cell(0, 10, txt='DESTROY BY BURNING WHEN FULLY USED OR IN RISK OF CAPTURE', ln=1, align="C")
    pdf.cell(0, 5, txt='CUT OUT AND DESTROY BLOCK AFTER USE', ln=1, align="C")
    pdf.cell(0, 5, txt='', ln=1, align="C")
    
    otp = ''
    for i in range(int(padlen)*(block_w*block_h*5)):
        otp+=str(randnumber())
        
    no=1
    spacer='--------------------------------------------------------------------'
    pdf.set_font("Courier", size=11)
    pdf.cell(0, 10, txt=spacer, ln=1, align="C")
    
    txt='\n\n\t\t   ONE TIME PAD CODEBOOK '+date+'\n\n'
    txt=txt+'   DESTROY BY BURNING WHEN FULLY USED OR IN RISK OF CAPTURE\nOVERWRITE BLOCKS AFTER USE\n\n'
    txt=txt+spacer+'\n\n\t\t\t\t\t\t    00001\n\n'
    c=0
    cl=0
    cp=0
    block = ''
    blocks = []
    rows = []
    segments = []
    for i in otp:
        block += i
        if len(block)==5:
            blocks.append(block)
            block = ''
            
            if len(blocks)==block_w:
                rows.append(blocks)
                blocks = []
                
                if len(rows)==block_h:
                    segments.append(rows)
                    rows = []
    
    pdf.cell(0, 4, txt='00001', ln=1, align="C")
    pdf.cell(0, 4, txt='', ln=1, align="C")
    nn = 0
    nnn = 0
    pickledict = {}
    
    nos=str(no)
    while len(nos)<5:
        nos='0'+nos
            
    for n in range(len(segments)):
        i = segments.pop(0)
        
        for j in i:
            ptxt = ''
            for k in j:
                txt += k + '  '
                ptxt += k + '  '
            while txt.endswith('\t'):
                txt=txt[:len(txt)-1]
            while ptxt.endswith(' '):
                ptxt=ptxt[:len(ptxt)-1]
            txt+= '\n'
            pdf.cell(0, 4, txt=ptxt, ln=1, align="C")
        
        rawseg = nos+':'
        pkf = ''
        for j in i:
            for k in j:
                rawseg+=k
                pkf += k
        raw+=rawseg+'\n'
        pickledict[nos] = pkf
        
        no+=1
        nos=str(no)
        while len(nos)<5:
            nos='0'+nos
        
        if len(segments)>0:
            nn+=1
            nnn += 1
            if nnn ==2:
                pdf.add_page()
                #pdf.Rect(0, 0, 210, 100, 'D')
                nn = 0
            elif nn == 3:
                pdf.add_page()
                #pdf.Rect(0, 0, 210, 100, 'D')
                nn = 0
            
            txt += '\n\n'+spacer+'\n\n\t\t\t\t\t\t    '+nos+'\n\n'
            pdf.cell(0, 4, txt='', ln=1, align="C")
            pdf.cell(0, 4, txt=spacer, ln=1, align="C")
            pdf.cell(0, 4, txt='', ln=1, align="C")
            pdf.cell(0, 4, txt=nos, ln=1, align="C")
            pdf.cell(0, 4, txt='', ln=1, align="C")

    print('Generated OTP Length: {} numbers'.format(len(otp)))
    pdf.add_page()
    pdf.image('CT46.png',w=190,y=100)
    #pdf.cell(0, 4, txt='', ln=1, align="C")
    pdf.add_page()
    pdf.image('CT46-2.png',w=190,y=100)

    if args.pdf or args.all or args.allformats:
        pdf.output("codebooks{}{}_{}_otp.pdf".format(os.sep,date,padid))
    if args.txt or args.all or args.allformats:
        with open('codebooks{}{}_{}_otp.txt'.format(os.sep,date,padid), "w") as file:
            file.write(txt)
    if args.pickle or args.all or args.allformats:
        with open('codebooks{}{}_{}_otp.pickle'.format(os.sep,date,padid), 'wb') as f:
            pickle.dump(pickledict, f, pickle.HIGHEST_PROTOCOL)


def gen_aes(date,padid, args):
    txt=''
    messages = 100
    linesn = messages*3
    letters = 'ABCDEFGHJKLMNPRSTUVWXYZabcdefghijkmnopqrstuvwxyz1234567890'
    no=1

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", size=24,style='B')
    pdf.cell(0, 20, txt="TOP SECRET", ln=1, align="C")
    pdf.cell(0, 5, txt="AES B64 ENCRYPTION KEYS PAD", ln=1, align="C")
    pdf.set_font("Courier", size=12)
    pdf.cell(0, 5, txt='', ln=1, align="C")
    pdf.cell(0, 5, txt=str(messages)+' MESSAGES', ln=1, align="C")
    pdf.cell(0, 5, txt=date, ln=1, align="C")
    pdf.cell(0, 5, txt='PAD ID: '+padid, ln=1, align="C")
    pdf.set_font("Courier", size=12, style='B')
    pdf.cell(0, 10, txt='DESTROY BY BURNING WHEN FULLY USED OR IN RISK OF CAPTURE', ln=1, align="C")
    pdf.cell(0, 10, txt='CROSS OUT CODE AFTER USE', ln=1, align="C")
    pdf.cell(0, 5, txt='', ln=1, align="C")
    
    txt='TOP SECRET\nAES B64 ENCRYPTION KEYS PAD\n{} MESSAGES\n{}\nPAD ID: {}\nCOPY/PASTE 00000000000000000000000000000000 OVER CODE AFTER USE\n'.format(messages, date, padid)
    txt=txt+'SECURELY WIPE WHEN FULLY USED OR IN RISK OF CAPTURE\n\n\n'

    keys = []
    for i in range(linesn*2):
        keys.append(binascii.b2a_hex(Random.new().read(16)))

    pdf.cell(0, 5, txt='\t       A                               B', ln=1, align="C")
    pdf.cell(0, 5, txt='', ln=1, align="C")
    pdf.set_font("Courier", size=11)
    txt+='\t\t\t\t\t\tA\t\t\t\t\t\t\t\tB\n\n'
    keyfile = {}
    for i in range(linesn):
        si = str(i+1)
        a=keys.pop(0)
        b=keys.pop(0)
        keyfile['A'+si] = a
        keyfile['B'+si] = b
        pdf.cell(0, 4, txt=str(si+'    '+str(a,'utf-8')+'    '+str(b,'utf-8')), ln=1, align="C")
        pdf.cell(0, 4, txt='', ln=1, align="C")
        txt+= str(str(i+1)+'\t\t'+str(a,'utf-8')+'\t'+str(b,'utf-8'))+'\n'


    if args.pdf or args.all or args.allformats:
        pdf.output("codebooks{}{}_{}_aespad.pdf".format(os.sep,date,padid))
    if args.pickle or args.all or args.allformats:
        with open('codebooks{}{}_{}_aespad.pickle'.format(os.sep,date,padid), 'wb') as f:
            pickle.dump(keyfile, f, pickle.HIGHEST_PROTOCOL)
    if args.txt or args.all or args.allformats:
        with open('codebooks{}{}_{}_aespad.txt'.format(os.sep,date,padid), "a+") as file:
            file.write(txt)


def gen_auth(date,padid, args):
    grid_w = 9
    grid_v = 48

    date=datetime.datetime.utcnow().strftime("%Y-%m-%d")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", size=24,style='B')

    pdf.cell(0, 20, txt="TOP SECRET", ln=1, align="C")
    pdf.cell(0, 5, txt="AUTHENTIFICATION TABLE", ln=1, align="C")
    pdf.cell(0, 5, txt='', ln=1, align="C")
    pdf.set_font("Courier", size=12)
    pdf.cell(0, 5, txt=date, ln=1, align="C")
    pdf.cell(0, 5, txt='PAD ID: '+padid, ln=1, align="C")
    pdf.set_font("Courier", size=12, style='B')
    pdf.cell(0, 10, txt='DESTROY BY BURNING WHEN FULLY USED OR IN RISK OF CAPTURE', ln=1, align="C")
    pdf.cell(0, 5, txt='CROSS OUT CODE AFTER USE', ln=1, align="C")
    pdf.cell(0, 5, txt='', ln=1, align="C")
    txt='TOP SECRET\nAUTHENTIFICATION TABLE\n{}\nPAD ID: {}\nCOPY/PASTE 0000 OVER CODE AFTER USE\n'.format(date,padid)
    txt=txt+'SECURELY WIPE WHEN FULLY USED OR IN RISK OF CAPTURE\n\n'

    codes = []
    for i in range(grid_w*grid_v):
        codes.append(randcode())

    pdf.set_font("Courier", size=11)
    pdf.cell(0, 10, txt='      A       B       C       D       E       F       G       H       J', ln=1, align="L")
    txt += '\tA\t\tB\t\tC\t\tD\t\tE\t\tF\t\tG\t\tH\t\tJ\n'
    pickledict = {}
    ind = {0:'A',1:'B',2:'C',3:'D',4:'E',5:'F',6:'G',7:'H',8:'J'}
    for i in range(0,grid_v):
        if i < 9:
            si = '0'+str(i+1)
        else:
            si = str(i+1)
        txt+= '{}\t'.format(si)
        
        cc = []
        for j in range(grid_w):
            code = codes.pop(0)
            cc.append(code)
            pickledict[ ind[j]+si ] = code
        
        x = ''
        for j in cc:
            x+= j+'    '
        for j in cc:
            txt+= j+'\t'
            
        pdf.cell(0, 4, txt=si+'    '+x, ln=1, align="L")
        txt+='\n'
    
    if args.pdf or args.all or args.allformats:
        pdf.output("codebooks{}{}_{}_auth.pdf".format(os.sep,date,padid))
    if args.pickle or args.all or args.allformats:
        with open('codebooks{}{}_{}_auth.pickle'.format(os.sep,date,padid), 'wb') as f:
            pickle.dump(pickledict, f, pickle.HIGHEST_PROTOCOL)
    if args.txt or args.all or args.allformats:
        with open('codebooks{}{}_{}_auth.txt'.format(os.sep,date,padid), "w") as file:
            file.write(txt)


def gen_brevity(date,padid, args):
    with open('brevitycodes','r') as file:
        codes = file.read()
    codes = codes[:len(codes)-1]
    codes = codes.upper().split('\n')
    codes.sort()

    codebook = {}
    wordlen = len(codes)

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
    with open('codenumbers','r') as file:
        use = file.read().split('\n')

    x = []
    for i in range(len(codes)):
        codebook[use[i]] = codes[i].lower()
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
                
            len1 = 28 - (4+len(l[1]))
            spc1 = ''.join(' ' for _ in range(len1))
                
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

    
    if args.pdf or args.all or args.allformats:
        pdf.output("codebooks{}{}_{}_brevitycodes.pdf".format(os.sep,date,padid))
    if args.pickle or args.all or args.allformats:
        with open('codebooks{}{}_{}_brevitycodes.pickle'.format(os.sep,date,padid), 'wb') as f:
            pickle.dump(codebook, f, pickle.HIGHEST_PROTOCOL)
    if args.txt or args.all or args.allformats:
        with open('codebooks{}{}_{}_brevitycodes.txt'.format(os.sep,date,padid), "w") as file:
            file.write(txt)



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--all', help='Generate everything',action="store_true")
    parser.add_argument('--allformats', help='Generate all formats',action="store_true")
    parser.add_argument('--pdf', help='Generate pdf documents',action="store_true")
    parser.add_argument('--txt',help='Generate text files',action="store_true")
    parser.add_argument('--pickle', help='Generate pickle files',action="store_true")
    parser.add_argument('--allcodes', help='Generate all codes',action="store_true")
    parser.add_argument('--otp', help='Generate OTP pads',required=False,action="store_true")
    parser.add_argument('--auth', help='Generate Authentification table',required=False,action="store_true")
    parser.add_argument('--aes', help='Generate AES code pads',required=False,action="store_true")
    parser.add_argument('--brevity', help='Generate brevity codes',required=False,action="store_true")
    args = parser.parse_args()
    
    if not (args.aes or args.otp or args.auth or args.all or args.allcodes):
        raise argparse.ArgumentTypeError('Error: pick one type of code book') 
    if not (args.pdf or args.txt or args.pickle or args.all or args.allformats):
        raise argparse.ArgumentTypeError('Error: pick one format') 

    date = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    padid = ''.join(random.choice('1234567890') for _ in range(6))
    padlen = 100

    if not os.path.exists('codebooks'):
        os.mkdir('codebooks')

    if args.brevity or args.all or args.allcodes:
        gen_brevity(date,padid, args)
        print('Brevity codes generated')
    if args.aes or args.all or args.allcodes:
        gen_aes(date,padid, args)
        print('AES codes generated')
    if args.auth or args.all or args.allcodes:
        gen_auth(date,padid, args)
        print('Authentifier generated')
    if args.otp or args.all or args.allcodes:
        gen_otp(padlen,date,padid, args)
        print('One Time Pad generated')
    print('Crypto pads {} {} generated'.format(padid,date))
