#!/usr/bin/python3
import math
import easygui
import datetime
import subprocess
import traceback
import traceback
from aescrypt import *
from gencodes import *
from authentify import *
from rsaaes import *
from otp import *

class gen_args():
    def __init__(self):
        self.codes = easygui.multchoicebox(msg='Select codes to generate',title='Select', choices=['All','OTP','AES','Auth','Brevity'])
        if self.codes:
            self.formats = easygui.multchoicebox(msg='Select formats to generate',title='Select', choices=['All','PDF','pickle','txt'])
        if self.codes and self.formats:
            self.all = 'All' in self.codes
            self.allcodes = 'All' in self.codes
            self.allformats = 'All' in self.formats
            self.brevity = 'Brevity' in self.codes
            self.aes = 'AES' in self.codes
            self.otp = 'OTP' in self.codes
            self.auth = 'Auth' in self.codes
            self.pdf = 'PDF' in self.formats
            self.txt = 'txt' in self.formats
            self.pickle = 'pickle' in self.formats

v = str( 1.2 )
titlebar = 'ECCS GUI'+v

args_keeppad = True # change to False for production

try:
    with open('.usecodes','r') as file:
        codes_set = file.read()
    codebook_aes = 'codebooks'+os.sep+codes_set+'_aespad.pickle'
    codebook_auth = 'codebooks'+os.sep+codes_set+'_auth.pickle'
    codebook_brevity = 'codebooks'+os.sep+codes_set+'_brevitycodes.pickle'
    codebook_otp = 'codebooks'+os.sep+codes_set+'_otp.pickle'
    keyfileid = codes_set.split('_')[1]
except:
    codes_set = None
    codebook_aes = None
    codebook_otp = None
    codebook_auth = None
    codebook_brevity = None
    keyfileid = None
    
try:
    with open('.usedkey','r') as file:
        keyname = file.read()
    rsa_key = RSA_key()
    rsa_key.import_key_file('rsakeys'+os.sep+keyname, args.p)
    
except:
    rsa_key = None

while 1:
    try:
        mainmsg = 'Encrypted Covert Communication System\n\nUsing codes: {}'.format(codes_set)
        if args_keeppad: mainmsg+='\n\nWARNING: TEST MODE ON, CODES WILL NOT BE CLEARED AFTER USE'
        else: mainmsg+='\n\nWARNING: Live mode on, codes WILL be cleared after use'
        
        ch = easygui.choicebox(msg=mainmsg,
                               title=titlebar,
                               choices=["AES Encrypt",
                                        "AES Decrypt",
                                        "AES File Encrypt",
                                        "AES File Decrypt",
                                        "One Time Pad Encrypt",
                                        "One Time Pad Decrypt",
                                        "Authentify",
                                        "RSA-AES Encrypt",
                                        "RSA-AES Decrypt",
                                        "RSA-AES File Encrypt",
                                        "RSA-AES File Decrypt",
                                        "Generate RSA Key",
                                        #"Steghide Embed File",
                                        #"Steghide Extract File",
                                        #"File XOR-OTP Encrypt"
                                        #"File XOR-OTP Decrypt"
                                        #"Generate XOR-OTP Key file"
                                        "Select codebooks",
                                        "Generate codebooks",
                                        "Securely wipe file",
                                        "DESTROY CODEBOOKS",
                                        "TEST MODE TOGGLE",
                                        "Exit"])
        
        if ch=='Exit' or ch==None: break

        elif ch == 'Select codebooks':
            date = datetime.datetime.utcnow().strftime("%Y-%m-%d")
            dat = easygui.multenterbox(msg='Enter key values\nMake sure keys are in codebooks folder and not renamed', title=titlebar, fields=['Codepads Date','Codepads ID'], values=[date,'00000'])
            if not dat:
                continue
            codes_set = dat[0]+'_'+dat[1]
            keyfileid = dat[1]
            with open('.usecodes','w') as file:
                file.write(codes_set)
            codebook_aes = 'codebooks'+os.sep+codes_set+'_aespad.pickle'
            codebook_auth = 'codebooks'+os.sep+codes_set+'_auth.pickle'
            codebook_brevity = 'codebooks'+os.sep+codes_set+'_brevitycodes.pickle'
            codebook_otp = 'codebooks'+os.sep+codes_set+'_otp.pickle'

            files = True
            if not os.path.isfile(codebook_aes): files = False
            if not os.path.isfile(codebook_auth): files = False
            if not os.path.isfile(codebook_brevity): files = False
            if not os.path.isfile(codebook_otp): files = False

            if not files:
                easygui.msgbox("Error: no such files",titlebar)
                codes_set = None
                codebook_aes = None
                codebook_otp = None
                codebook_auth = None
                codebook_brevity = None

        elif ch in ["AES Encrypt","AES Decrypt","AES File Encrypt","AES File Decrypt"]:
            
            args_e = ch in ["AES Encrypt","AES File Encrypt"]
            args_d = ch in ["AES Decrypt","AES File Decrypt"]
            args_key1 = None
            args_key2 = None
            args_iv = None
            args_b64 = True
            args_rawkey = False
            
            if args_e:
                keymode = easygui.indexbox(msg='Choose key mode', title=titlebar, choices=('Plain key', 'Pickle keys','Generate one'), default_choice='Plain key')
            else:
                keymode = easygui.indexbox(msg='Choose key mode', title=titlebar, choices=('Plain key', 'Pickle keys'), default_choice='Plain key')
            if keymode == 1:
                
                if not codebook_aes:
                    keyfile = easygui.fileopenbox(msg="Select Pickle file", title=titlebar, default='*_aespad.pickle', filetypes=["*.pickle"], multiple=False)
                else:
                    keyfile = codebook_aes
            else:
                keyfile = None
            
            args_keyfile = keyfile

            if keymode == 2:
                args_key1 = Random.new().read(16)
                args_key2 = Random.new().read(16)
                args_iv = Random.new().read(AES.block_size)
                
                keymsg = 'Key 1/2: '+binascii.b2a_hex(args_key1).decode() + '\nKey 2/2: ' + binascii.b2a_hex(args_key2).decode() + '\nIV: '+binascii.b2a_hex(args_iv).decode()
                easygui.textbox(msg="Encryption keys and IV below. Use Control+C to copy.",title=titlebar,text=keymsg)
            else:
                enterkeys = easygui.multenterbox(msg='Enter Key halves and IV', title=titlebar, fields=['Key 1','Key 2','Initialization Vector'], values=[])
                if not enterkeys:
                    continue
                args_key1, args_key2, args_iv = enterkeys
            
            
            if args_keyfile:
                with open(args_keyfile, 'rb') as f:
                    codebook = pickle.load(f)
                
                try:
                    key1 = binascii.a2b_hex(codebook[args_key1.upper()])
                    key2 = binascii.a2b_hex(codebook[args_key2.upper()])
                    binkey = key1+key2
                    biniv = binascii.a2b_hex(codebook[args_iv.upper()])
                except:
                    easygui.msgbox("Error: Key indexes not found, maybe they have been deleted after being used",titlebar)
                    continue
                    
            else:
                binkey = args_key1+args_key2
                biniv = args_iv
                
            if ch in ["AES File Encrypt","AES File Decrypt"]:
                args_file = easygui.fileopenbox(msg="Select file to encrypt/decrypt", title=titlebar, default='*', multiple=False)
                if not args_file: continue
            else:
                args_file = None

            if args_file:
                if args_e:
                    filename = args_file
                    with open(filename,'rb') as file:
                        filecontent = file.read()
                    encfile = AESencrypt(filecontent, binkey, biniv)
                    encfile = binascii.b2a_hex(encfile)
                    with open(filename+'.enc','wb') as file:
                        file.write(encfile)
                    easygui.msgbox("File encrypted\nNew file name:{}".format(filename+'.enc'),titlebar)
                    
                elif args_d:
                    filename = args_file
                    with open(filename,'rb') as file:
                        filecontent = file.read()
                    newfilename = filename[:filename.find('.enc')]
                    filecontent = binascii.a2b_hex(filecontent)
                    decfile = AESdecrypt(filecontent, binkey, biniv,True)
                    with open(newfilename,'wb') as file:
                        file.write(decfile)
                    easygui.msgbox("File decrypted\nNew file name:{}".format(newfilename),titlebar)
                
            else:
                args_message = easygui.textbox(msg="Enter the message below",text='',title=titlebar)
                if not args_message: 
                    continue
            
                if args_e:
                    a = AESencrypt(args_message, binkey, biniv)
                    if args_keyfile:
                        message = PEM.encode(a,'AES MESSAGE {} {}'.format(keyfileid, args_key1.upper()+args_key2.upper()+args_iv.upper()))
                    else:
                        message = PEM.encode(a,'AES MESSAGE')
                    easygui.textbox(msg="Encrypted message below. Use Control+C to copy.",title=titlebar,text=message)
                    
                elif args_d:
                    #print(str([args_message]))
                    a = PEM.decode(args_message)[0]
                    message = str(AESdecrypt(a, binkey, biniv,False),'utf-8')
                    easygui.textbox(msg="Decrypted message below. Use Control+C to copy.",title=titlebar,text=message)
                    
            if args_keyfile and not args_keeppad:
                overwrite = '00000000000000000000000000000000'
                codebook[args_key1.upper()] = overwrite
                codebook[args_key2.upper()] = overwrite
                codebook[args_iv.upper()] = overwrite
                
                with open(args_keyfile, 'wb') as f:
                    pickle.dump(codebook, f, pickle.HIGHEST_PROTOCOL)
                    
                with open(args_keyfile, 'rb') as f:
                    codebook = pickle.load(f)
                    
                del codebook[args_key1.upper()]
                del codebook[args_key2.upper()]
                del codebook[args_iv.upper()]
                with open(args_keyfile, 'wb') as f:
                    pickle.dump(codebook, f, pickle.HIGHEST_PROTOCOL)
                        
                
        elif ch in ["One Time Pad Encrypt","One Time Pad Decrypt"]:
            try:
                args_e = ch == "One Time Pad Encrypt"
                args_d = ch == "One Time Pad Decrypt"
                args_board = 'ct46'
                args_brevity = True
                if not codebook_otp:
                    args_pad = easygui.fileopenbox(msg="Select Pickle file", title=titlebar, default='*_otp.pickle', filetypes=["*.pickle"], multiple=False)
                else:
                    args_pad = codebook_otp
                padid = args_pad.split('/')
                padid = padid[len(padid)-1].split('_')[1]
                firstavail = None
        
                args_message = easygui.textbox(msg="Enter the message below",text='',title=titlebar)
                if args_message == None: 
                    continue
            
                if args_e or args_d:
                    with open(args_pad, 'rb') as f:
                        padbook = pickle.load(f)
                    for i in range(0,1000):
                        msgno=str(i+1)
                        while len(msgno)<5:
                            msgno='0'+msgno
                        if msgno in padbook:
                            firstavail = msgno
                            break

                cipher = checkerboard(args_board.lower(),padbook[msgno])
                if args_brevity:
                    if not codebook_brevity:
                         codebook_brevity = easygui.fileopenbox(msg="Select Brevity Codes Pickle file", title=titlebar, default='*_brevitycodes.pickle', filetypes=["*.pickle"], multiple=False)
                    cipher.brevity = True
                    with open(codebook_brevity, 'rb') as f:
                        cipher.codebook = pickle.load(f)
                    cipher.reversecodebook = {}
                    for i in cipher.codebook:
                        cipher.reversecodebook[cipher.codebook[i].lower()] = i
                        
                if args_e:
                    try:
                        encrypted = padid+cipher.encrypt(args_message,firstavail)
                    except Exception as e:
                        easygui.msgbox("Error!\n"+str(e)+'\n'+str(type(e)),titlebar)
                        continue
                    if not args_keeppad: cipher.purgepad(args_pad)
                    easygui.textbox(msg="Encrypted message below. Use Control+C to copy.",title=titlebar,text=encrypted)

                elif args_d:
                    padid = args_message[:6]
                    msgno = args_message[6:11]
                    decrypted = cipher.decrypt(args_message[6:])
                    goodpad, message = decrypted
                    if not args_keeppad and goodpad: cipher.purgepad(args_pad)
                    easygui.textbox(msg="Decrypted message below. Use Control+C to copy.",title=titlebar,text=message)
                        
            except Exception as e:
                easygui.msgbox("Error!\n"+traceback.format_exc(),titlebar)

        elif ch == 'Generate codebooks':
            
            args = gen_args()
            
            if args.codes != None and args.formats != None:
                
                if not (args.aes or args.otp or args.auth or args.all or args.allcodes):
                    raise argparse.ArgumentTypeError('Error: pick one type of code book') 
                if not (args.pdf or args.txt or args.pickle or args.all or args.allformats):
                    raise argparse.ArgumentTypeError('Error: pick one format') 

                date = datetime.datetime.utcnow().strftime("%Y-%m-%d")
                padid = ''.join(random.choice('1234567890') for _ in range(5))
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
                easygui.msgbox('Crypto pads {} {} generated'.format(padid,date),titlebar)
                
        elif ch == 'Authentify':
            if not codebook_auth:
                authtable = easygui.fileopenbox(msg="Select Pickle file", title=titlebar, default='*_auth.pickle', filetypes=["*.pickle"], multiple=False)
            else:
                authtable = codebook_auth
            code = easygui.enterbox(msg="Enter code\nGrid coords in Letter-Number format or 4-character Auth code", title=titlebar)
            
            with open(authtable, 'rb') as f:
                padbook = pickle.load(f)
                
            if len(code)==3:
                easygui.msgbox('Code: '+padbook[code.upper()],titlebar)
                
            elif len(code)==5:
                if code in padbook.values():
                    easygui.msgbox('Code: '+padbook.keys()[padbook.values().index(code.upper())],titlebar)
                else:
                    easygui.msgbox( 'Auth failed, code not found',titlebar)
            else:
                easygui.msgbox('Invalid code',titlebar)
                
        elif ch == 'Securely wipe file':
            args_file = easygui.fileopenbox(msg="Select file to encrypt/decrypt", title=titlebar, default='*.*',filetypes='*', multiple=True)
            print(args_file)
            if args_file is not None:
                confirm = easygui.ynbox(msg='ARE YOU SURE?\nWiping this file will destroy it forever.',title=titlebar)
                if confirm:

                    if type(args_file) == str:
                        files2wipe = [args_file]
                    elif type(args_file) == list:
                        files2wipe = []
                        for fn in args_file:
                            files2wipe.append(fn)
                    
                    commands=[]
                    for fn in files2wipe:
                        commands.append('shred -zuv -n 3 "{}"'.format(fn))
                    
                    for cmde in commands:
                        execproc = subprocess.Popen(cmde, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                        cmdoutput = execproc.stdout.read() + execproc.stderr.read()
                        #print(cmdoutput)
                    
                    easygui.msgbox('File wiped',titlebar)
                    
        elif ch == 'Generate RSA Key':
            if not os.path.exists('rsakeys'):
                os.mkdir('rsakeys')
                
            enterkeys = easygui.multpasswordbox(msg='Enter Key name, size (2048, 3084, 4096) and encryption passphrase', title=titlebar, fields=['Filename','Size','Passphrase'], values=[])
            if not enterkeys:
                continue
            args_name, args_size, args_key = enterkeys
                
            Alice = RSA_key()
            Alice.gen_key(int(args_size))
            pubfn = '{}_{}_public.asc'.format(args_name,args_size)
            sfn = '{}_{}.asc'.format(args_name,args_size)
            with open('rsakeys{}{}'.format(os.sep,pubfn), "w",encoding='utf-8') as file:
                file.write(Alice.export_public_key())
            with open('rsakeys{}{}'.format(os.sep,sfn), "w",encoding='utf-8') as file:
                file.write(Alice.export_private_key(args_key))
            print('Exported secret key', sfn)
            print('Exported public key',pubfn)
            easygui.msgbox("Keys generated\nSecret key: {}\nPublic key: {}".format(sfn,pubfn),titlebar)

        elif ch in ["RSA-AES Encrypt","RSA-AES Decrypt","RSA-AES File Encrypt","RSA-AES File Decrypt"]:

            args_e = ch in ["RSA-AES Encrypt","RSA-AES File Encrypt"]
            args_d = ch in ["RSA-AES Decrypt","RSA-AES File Decrypt"]
            args_file = ch in ["RSA-AES File Encrypt","RSA-AES File Decrypt"]
        
            MyKey = RSA_key()
            HisKey = RSA_key()
            fn1 = easygui.fileopenbox(msg="Select secret sender keyfile", title=titlebar, default='rsakeys'+os.sep+'*.asc', multiple=False)
            if not fn1: continue
            fn1p = easygui.passwordbox("Enter passphrase to unlock key",title=titlebar)
            fn2 = easygui.fileopenbox(msg="Select public receiver keyfile", title=titlebar, default='rsakeys'+os.sep+'*.asc', multiple=False)
            if not fn2: continue
            print(fn1,fn1p,fn2)
            MyKey.import_key_file(fn1,fn1p)
            HisKey.import_key_file(fn2)

            if args_file:
                args_message = easygui.fileopenbox(msg="Select file", title=titlebar, default='*', multiple=False)
                isfile = True
                
                if args_e:
                    filename = args_message
                    with open(filename,'rb') as file:
                        filecontent = file.read()
                    hash = SHA512.new()
                    hash.update(filecontent)
                    encfile = rsaaes_encrypt(MyKey, HisKey, filecontent,True)
                    with open(filename+'.enc','wb') as file:
                        file.write(encfile)
                    easygui.msgbox('File encrypted at {}\nSHA512: {}'.format(filename+'.enc',hash.hexdigest()),titlebar)
                    
                    
                elif args_d:
                    filename = args_message
                    with open(filename,'rb') as file:
                        filecontent = file.read()
                    newfilename = filename[:filename.find('.enc')]
                    decfile = rsaaes_decrypt(MyKey, HisKey, filecontent, True)
                    
                    #print('Signature verifies:',decfile['verify'],decfile['hash'])
                    
                    with open(newfilename,'wb') as file:
                        file.write(decfile['msg'])
                        
                    easygui.msgbox('File decrypted at {}\nSignature verifies: {}\nSHA512: {}'.format(newfilename,decfile['verify'],decfile['hash']),titlebar)
                    
            else:
                args_message = easygui.textbox(msg="Enter the message below",text='',title=titlebar)
                if not args_message: 
                    continue
                if args_e:
                    enc = rsaaes_encrypt(MyKey, HisKey, args_message).decode()
                    easygui.textbox(msg="Encrypted message",title=titlebar,text=str(enc))
                    
                elif args_d:
                    dec = rsaaes_decrypt(MyKey, HisKey, args_message)
                    if dec['verify']:
                        verify = 'VERIFIED'
                    else:
                        verify = 'FAILED VERIFICATION'
                    easygui.textbox(msg="Decrypted message\nMessage signature: "+verify,title=titlebar,text=dec['msg'])

        elif ch == 'DESTROY CODEBOOKS':
            
            confirm = easygui.ynbox(msg='ARE YOU SURE?',title=titlebar)
            if confirm:
                commands = ['shred -zv -n 1 *_otp.*',
                            'shred -zv -n 1 *_aespad.*',
                            'shred -zv -n 1 *_auth.*',
                            'shred -zv -n 1 *_brevitycodes.*',
                            'shred -zv -n 1 */*_otp.*',
                            'shred -zv -n 1 */*_aespad.*',
                            'shred -zv -n 1 */*_auth.*',
                            'shred -zv -n 1 */*_brevitycodes.*',
                            'rm *_otp.*',
                            'rm *_aespad.*',
                            'rm *_auth.*',
                            'rm *_brevitycodes.*',
                            'rm */*_otp.*',
                            'rm */*_aespad.*',
                            'rm */*_auth.*',
                            'rm */*_brevitycodes.*']
                for cmde in commands:
                    execproc = subprocess.Popen(cmde, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                    cmdoutput = execproc.stdout.read() + execproc.stderr.read()
                    #print(cmdoutput)
                easygui.msgbox('Codebooks wiped',titlebar)
                
        elif ch == 'TEST MODE TOGGLE':
            if not args_keeppad:
                confirm = easygui.ynbox(msg='ARE YOU SURE?\nTurning off Live mode will prevent ECCS from clearing used keys, making it easy to crack messages if they are reused in a real environment.',title=titlebar)
            else:
                confirm = True
            if confirm:
                args_keeppad = not args_keeppad
    
    except Exception:
        error = traceback.format_exc()
        easygui.msgbox(msg="An error has occured\n"+error,title=titlebar)
        print(error)
        
