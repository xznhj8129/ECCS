#!/usr/bin/python3
import binascii
import os
import sys
import argparse
import pickle
from Crypto.Random import random
from Crypto.Cipher import AES
from Crypto.IO import PEM
from Crypto.Util.Padding import pad, unpad

def AESencrypt(data, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    if type(data) is str:
        bytedata = bytes(data,'utf-8')
    else:
        bytedata = data
    padded = pad(bytedata,16)
    encrypted = cipher.encrypt(padded) #fuckup on files
    del cipher
    return encrypted

def AESdecrypt(data, key, iv, binary):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    dec = cipher.decrypt(data)
    unpadded = unpad(dec,16)
    decrypted = unpadded
    del cipher
    return decrypted

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('message', help='Message or filename',nargs='?')
    parser.add_argument('-e', help='Encrypt',action='store_true')
    parser.add_argument('-d', help='Decrypt',action='store_true')
    parser.add_argument('--key1', help='Encryption key 1/2 (32 characters)')
    parser.add_argument('--key2', help='Encryption key 2/2 (32 characters)')
    parser.add_argument('--iv', help='Initiation vector (16 characters)')
    parser.add_argument('--pem', help='PEM encoding of input/output',action="store_true")
    parser.add_argument('--rawkey',help='No base64 for keys and IV',action="store_true")
    parser.add_argument('--file', help='Encrypt/decrypt file, .enc extension',action="store_true")
    parser.add_argument('--keyfile', help='Use pickle key file',required=False)
    parser.add_argument('--keeppad', help="Do not purge pad (dangerous)",required=False,action="store_true")
    args = parser.parse_args()
            
    if not args.message:
        if not sys.stdin.isatty():
            args.message = sys.stdin.read()
        else:
            parser.print_help()
            parser.exit()

    if not (args.e ^ args.d):
        print('Error: unknown action')
        exit(1)
    if not args.key1 or not args.key2:
        print('Error: no encryption key')
        exit(1)
    if not args.iv:
        print('Error: no initiation vector')
        exit(1)
    
    if not args.rawkey and not args.keyfile:
        binkey = binascii.a2b_hex(args.key1+args.key2)
        biniv = binascii.a2b_hex(args.iv)
    elif args.keyfile:
        with open(args.keyfile, 'rb') as f:
            codebook = pickle.load(f)
        keyfileid = args.keyfile.split('_')[1]
        key1 = binascii.a2b_hex(codebook[args.key1.upper()])
        key2 = binascii.a2b_hex(codebook[args.key2.upper()])
        binkey = key1+key2
        biniv = binascii.a2b_hex(codebook[args.iv.upper()])
            
    else:
        binkey = args.key1+args.key2
        biniv = args.iv
            
    if args.file:
        if args.e:
            filename = args.message
            with open(filename,'rb') as file:
                filecontent = file.read()
            encfile = AESencrypt(filecontent, binkey, biniv)
            if args.pem: 
                encfile = bytes(PEM.encode(encfile,'FILE'),'utf-8')
            with open(filename+'.enc','wb') as file:
                file.write(encfile)
            print(filename+'.enc')
            
        elif args.d:
            filename = args.message
            with open(filename,'rb') as file:
                filecontent = file.read()
            newfilename = filename[:filename.find('.enc')]
            if args.pem: 
                filecontent = PEM.decode(str(filecontent,'utf-8'))[0]
            decfile = AESdecrypt(filecontent, binkey, biniv, True)
            with open(newfilename,'wb') as file:
                file.write(decfile)
            print(newfilename)
        
    else:
        if args.e:
            a = AESencrypt(args.message, binkey, biniv)
            if args.pem:
                if args.keyfile:
                    print(PEM.encode(a,'AES MESSAGE {} {}'.format(keyfileid,args.key1.upper()+args.key2.upper()+args.iv.upper())))
                else:
                    print(PEM.encode(a,'AES MESSAGE'))
            else:
                print(a)
            
        elif args.d:
            if args.pem:
                a = PEM.decode(args.message)[0]
                #a = binascii.a2b_hex(args.message)
            else:
                a = args.message
            print(str(AESdecrypt(a, binkey, biniv,False),'utf-8'))
            
    if args.keyfile and not args.keeppad:
        overwrite = '00000000000000000000000000000000'
        codebook[args.key1.upper()] = overwrite
        codebook[args.key2.upper()] = overwrite
        codebook[args.iv.upper()] = overwrite
        
        with open(args.keyfile, 'wb') as f:
            pickle.dump(codebook, f, pickle.HIGHEST_PROTOCOL)
            
        with open(args.keyfile, 'rb') as f:
            codebook = pickle.load(f)
            
        del codebook[args.key1.upper()]
        del codebook[args.key2.upper()]
        del codebook[args.iv.upper()]
        with open(args.keyfile, 'wb') as f:
            pickle.dump(codebook, f, pickle.HIGHEST_PROTOCOL)
        
        
        

