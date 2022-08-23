#!/usr/bin/python3

from Crypto.Random import random
import binascii
import os
import sys
import argparse
import pickle

def randnumber():
    return random.choice(range(0,9))

class checkerboard():
    def __init__(self, boardtype, pad):
        self.brevity = False
        if boardtype == 'ct46':
            
            self.asciiimage ="""
-----------------------------------------------------
|  A    E    I    N    O    R    |      CT-46       |
|  1    2    3    4    5    6    |                  |
|---------------------------------------------------|
|  B    C    D    F    G    H    J    K    L    M   |
|  70   71   72   73   74   75   76   77   78   79  |
|---------------------------------------------------|
|  P    Q    S    T    U    V    W    X    Y    Z   |
|  80   81   82   83   84   85   86   87   88   89  |
|---------------------------------------------------|
|  SPC  .    ,    :    ?    /    (    )    "   CODE |
|  90   91   92   93   94   95   96   97   98   99  |
|---------------------------------------------------|
|  0    1    2    3    4    5    6    7    8    9   |
|  00   01   02   03   04   05   06   07   08   09  |
-----------------------------------------------------"""
            self.checkerboard = {'a':'1','e':'2','i':'3','n':'4','o':'5','r':'6','b': '70','c': '71','d': '72','f': '73','g': '74','h': '75','j': '76','k': '77','l': '78','m': '79','p': '80','q': '81','s': '82','t': '83','u': '84','v': '85','w': '86','x': '87','y': '88','z': '89',' ': '90','.': '91',',': '92',':': '93','?': '94','/': '95',')': '96','(': '97','"': '98','CODE': '99','0': '00','1': '01','2': '02','3': '03','4': '04','5': '05','6': '06','7': '07','8': '08','9': '09'}
            self.reverse = {'88': 'x', '89': 'z', '82': 's', '83': 't', '80': 'p', '81': 'q', '86': 'w', '87': 'y', '84': 'u', '85': 'v', '02': '2', '03': '3', '00': '0', '01': '1', '06': '6', '07': '7', '04': '4', '05': '5', '79': 'm', '08': '8', '09': '9', '1': 'a', '3': 'i', '2': 'e', '5': 'o', '4': 'n', '6': 'r', '96': ')', '99': 'CODE', '76': 'j', '75': 'h', '74': 'g', '73': 'f', '72': 'd', '71': 'c', '70': 'b', '91': '.', '90': ' ', '93': ':', '92': ',', '95': '/', '94': '?', '97': '(', '78': 'l', '77': 'k', '98': '"'}
        else:
            raise(Exception('Error: invalid checkerboard type '+boardtype))
        
        self.boardtype = boardtype
        self.pad = pad
        self.usedno = None



    def encrypt(self,plaintext,no):
        msgno=str(no)
        while len(msgno)<5:
            msgno='0'+msgno
        self.usedno = msgno
        pt = plaintext.lower()

        if self.brevity:
            for i in self.reversecodebook:
                if i in pt:
                    print(i,self.reversecodebook[i])
                    pt = pt.replace(i,'\x99'+self.reversecodebook[i])
        
        converted=''
        brevconv = False
        for i in pt:
            if i == '\x99':
                converted=converted+'99'
                brevconv = True
            elif i=='\n':
                pass
            else:
                if i not in self.checkerboard.keys():
                    raise Exception('Character "{}" not found in checkerboard {}'.format(i,self.boardtype))
                if brevconv and i in '0123456789':
                    converted=converted+i
                elif brevconv:
                    brevconv = False
                
                if not brevconv: converted=converted+str(self.checkerboard[i])
                
        if len(converted)>len(self.pad):
            raise Exception('Message longer than self.pad! Msg: {} chars Pad: {} chars'.format(len(converted),len(self.pad)))
            
        while len(converted)%5!=0:
            converted=converted+'91'
        
        con=[]
        for i in converted: con.append(int(i))
        
        otp=[]
        ourpad=[]
        for i in self.pad:
            ourpad.append(i)
        idc=0
        
        padid=''
        while len(otp)<len(con):
            if idc<5:
                padid= padid+str(ourpad.pop(0))
                idc+=1
            else:
                otp.append(ourpad.pop(0))
        
        #print 'message no:',msgno
        #print 'pad id:', padid
        
        ciphertext = msgno+ padid
        
        for i in range(len(con)):
            res= (int(con[i]) - int(otp[i])) % 10
            ciphertext=ciphertext+str(res)
            
        return ciphertext

    def decrypt(self,ctext):
        idc=0
        ourpad=[]
        otp=[]
        msgno=ctext[:5]
        msgid=ctext[5:10]
        self.usedno = msgno
        ciphertext=ctext[5:]
        no=int(msgno)
        
        bc = {}
        if self.brevity:
            for i in self.reversecodebook:
                x = ''
                for j in i:
                    x=x+str(self.checkerboard[j])
                bc[self.reversecodebook[i]] = x
        
        for i in self.pad:
            ourpad.append(i)
        
        padid=''
        while len(otp)<len(ciphertext):
            if idc<5:
                padid = padid+str(ourpad.pop(0))
                idc+=1
            else:
                otp.append(ourpad.pop(0))
                
        goodpad = (padid == msgid)
        #print 'message no:',msgno
        #print 'pad id:',padid
        
        if goodpad:
            print('Decryption successful')
        else:
            return (False, "Decryption error")

        decrypted=''
        enc=ciphertext[5:]
        #print [enc]
        for i in range(len(enc)):
            res = (int(enc[i]) + int(otp[i])) % 10
            decrypted=decrypted+str(res)

        text=''
        a=decrypted
        cleartext=''
        while len(a)>0:
            if self.brevity and a.startswith('99'):
                s = a[:6]
                code = s[2:]
                a = a.replace(s, bc[code])
            for i in self.reverse:
                if a.startswith(i):
                    cleartext=cleartext+self.reverse[i]
                    a=a[len(i):]
                    
        return (goodpad, cleartext)
    
    def purgepad(self, padfile):
            
        with open(padfile, 'rb') as f:
            padbook = pickle.load(f)
        padlen = len(padbook[self.usedno])
        owr = ''
        for i in range(padlen):
            owr+= '0'
        padbook[self.usedno] = owr
        with open(padfile, 'wb') as f:
            pickle.dump(padbook, f, pickle.HIGHEST_PROTOCOL)
        del padbook[self.usedno]
        with open(padfile, 'wb') as f:
            pickle.dump(padbook, f, pickle.HIGHEST_PROTOCOL)
        


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('message', help='Message, filename or OTP len in blocks of 5',nargs="?")
    parser.add_argument('--pad', help="One time pad file to use")
    parser.add_argument('-e', help='Encrypt',required=False,action="store_true")
    parser.add_argument('-d', help='Decrypt',required=False,action="store_true")
    parser.add_argument('--keeppad', help="Do not purge pad (dangerous)",required=False,action="store_true")
    parser.add_argument('--board', help='Checkerboard type',required=False,default='ct46')
    parser.add_argument('--brevity', help='Use brevity codes',required=False)
    args = parser.parse_args()
    
    firstavail = None
    if not args.message:
        if not sys.stdin.isatty():
            args.message = sys.stdin.read()
        else:
            parser.print_help()
            parser.exit()

    if not (args.e ^ args.d):
        print('Error: unknown action')
        exit(1)

    if args.e or args.d:
        with open(args.pad, 'rb') as f:
            padbook = pickle.load(f)
        for i in range(0,1000):
            msgno=str(i+1)
            while len(msgno)<5:
                msgno='0'+msgno
            if msgno in padbook:
                firstavail = msgno
                break
    
    #inmsg = ''
    #for i in args.message:
    #    try:
    #        int(i)
    #        inmsg+=i
    #    except:
    #        pass
    inmsg = args.message
    
    padid = args.pad.split('/')
    padid = padid[len(padid)-1].split('_')[1]
            
    cipher = checkerboard(args.board.lower(),padbook[msgno])
    if args.brevity:
        cipher.brevity = True
        with open(args.brevity, 'rb') as f:
            cipher.codebook = pickle.load(f)
        cipher.reversecodebook = {}
        for i in cipher.codebook:
            cipher.reversecodebook[cipher.codebook[i].lower()] = i
            
    if args.e:
        encrypted = cipher.encrypt(inmsg,firstavail)
        if not args.keeppad: cipher.purgepad(args.pad)
        print(padid+encrypted, len(padid+encrypted))

    elif args.d:
        padid = inmsg[6:]
        msgno = inmsg[6:11]
        decrypted = cipher.decrypt(inmsg[6:])
        goodpad, message = decrypted
        if not args.keeppad and goodpad: cipher.purgepad(args.pad)
        print(message)

