#!/usr/bin/python3
import os
import sys
import argparse
import getpass
from cryptomodule import *

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('message', help='Message',nargs='?')
    parser.add_argument('-e', help='Encrypt',action='store_true')
    parser.add_argument('-d', help='Decrypt',action='store_true')
    parser.add_argument('--file',help='Encrypt/decrypt File',required=False,action='store_true')
    parser.add_argument('--mykey', help='My RSA key')
    parser.add_argument('--hiskey', help='Recipient RSA key')
    parser.add_argument('--genkey', help='Generate RSA key',action='store_true')
    parser.add_argument('-s',help='Key size for generation (2048, 3084, 4096)',required=False)
    parser.add_argument('-n',help='Key filename for generation',required=False)
    parser.add_argument('-p',help='Key passphrase',required=False)
    args = parser.parse_args()
            
    if not args.message:
        if args.genkey:
            pass
        elif not sys.stdin.isatty():
            args.message = sys.stdin.read()
        else:
            parser.print_help()
            parser.exit()

    if not (args.e ^ args.d ^ args.genkey):
        print('Error: unknown action')
        exit(1)
        
    if ((args.e | args.d | args.genkey) and args.p==None):
        print('Enter key passphrase')
        args.p = getpass.getpass()
        #print('Error: key passphrase not provided')
        #exit(1)
        
    if (not args.mykey or not args.hiskey) and not args.genkey:
        print('Error: missing key(s)')
        exit(1)
    
    if args.genkey:
        newkey = RSA_key()
        newkey.gen_key(int(args.s))
        pubfn = '{}_{}_public.asc'.format(args.n,args.s)
        sfn = '{}_{}.asc'.format(args.n,args.s)
        with open(pubfn, "w",encoding='utf-8') as file:
            file.write(newkey.export_public_key())
        with open(sfn, "w",encoding='utf-8') as file:
            file.write(newkey.export_private_key(args.p))
        print('Exported secret key', sfn)
        print('Exported public key',pubfn)
        
    else:
        MyKey = RSA_key()
        HisKey = RSA_key()
        MyKey.import_key_file(args.mykey,args.p)
        HisKey.import_key_file(args.hiskey)
        
        if args.file:
            isfile = True
            if args.e:
                filename = args.message
                with open(filename,'rb') as file:
                    filecontent = file.read()
                hash = SHA512.new()
                hash.update(filecontent)
                encfile = rsaaes_encrypt(MyKey, HisKey, filecontent,True)
                with open(filename+'.enc','wb') as file:
                    file.write(encfile)
                print('File encrypted at '+filename+'.enc')
                print('SHA512: '+hash.hexdigest())
                
            elif args.d:
                filename = args.message
                with open(filename,'rb') as file:
                    filecontent = file.read()
                newfilename = filename[:filename.find('.enc')]
                decfile = rsaaes_decrypt(MyKey, HisKey, filecontent, True)
                print('File decrypted at',newfilename)
                print('Signature verifies:',decfile['verify'])
                print('SHA512:',decfile['hash'])
                with open(newfilename,'wb') as file:
                    file.write(decfile['msg'])
        
        else:
            if args.e:
                enc = rsaaes_encrypt(MyKey, HisKey, args.message).decode()
                print(enc)
                
            elif args.d:
                dec = rsaaes_decrypt(MyKey, HisKey, args.message)
                print(dec)
