#!/usr/bin/python3

import math
from Crypto.Random import random
import Crypto.Random as Random
import binascii
import os
import sys
import argparse

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', help='Encrypt',action='store_true')
    parser.add_argument('-d', help='Decrypt',action='store_true')
    parser.add_argument('-o', help="Output file",nargs="?")
    parser.add_argument('--keyfile', help='Random data key file to use',nargs="?")
    parser.add_argument('--file', help="File to XOR",nargs="?")
    parser.add_argument('--genrandom',help="Generate Random Data file, number of blocks of 10kb",required=False)
    parser.add_argument('--keepblocks',help="Keep decryption blocks (UNSAFE)",required=False,action='store_true')
    args = parser.parse_args()
    
    if args.genrandom:
        if not args.keyfile:
            print('Error: please specify a keyblock filename')
            exit(1)
        kb = 10
        n_blocks = int(args.genrandom)
        f = b''
        print('Generating {} blocks of {} kilobytes of random data'.format(n_blocks,kb))

        for i in range(n_blocks):
            bits = int(kb)*1000
            rand = binascii.b2a_hex(Random.new().read(bits))
            if i == n_blocks-1:
                f+=rand
            else:
                f += rand + b'\n'
                        
        with open(args.keyfile, "wb") as file:
            file.write(f)
        print('Done')

    else:
        if not (args.e ^ args.d):
            print('Error: unknown action')
            exit(1)
            
        filename = args.file
        encrypt = args.e == True
        deleteblocks = args.keepblocks

        kb = (10 *1000)

        randfile = bytearray(open(args.keyfile, 'rb').read())
        keyblocks = randfile.split(b'\n')
        n_blocks = len(keyblocks)
        
        print('Blocks:', n_blocks)
        for i in range(len(keyblocks)):
            if not keyblocks[i].startswith(b'X'):
                startblock = i
                break
        
        print('Start block:',startblock)
        randsizeavail = kb * n_blocks - startblock
        blocksavail = n_blocks - startblock
        print('Blocks available:',n_blocks - startblock)

        inputfile = bytearray(open(filename, 'rb').read())
        if encrypt:
            size = len(filename)+len(inputfile)+1
        else:
            inputfile = inputfile[inputfile.find(b'\n')+1:]
            size = len(inputfile)


        blocksneeded = math.ceil(size / kb)
        print('Blocks needed:',blocksneeded)
        if blocksneeded > blocksavail: 
            print('Error: not enough blocks')
            exit(1)

        key = b''
        n = 0
        for i in keyblocks:
            if not i.startswith(b'X'):
                key += binascii.a2b_hex(i)
                if not args.keepblocks: 
                    keyblocks[startblock+n] = b'X' + binascii.b2a_hex(Random.new().read(kb))[1:]
                n+=1
                if n==blocksneeded: break
                
        xord_byte_array = bytearray(size)

        if encrypt:
            inputfile = bytes(filename,'utf-8')+b'\n' + inputfile

        # XOR between the files
        for i in range(size):
            xord_byte_array[i] = inputfile[i] ^ key[i]

        if encrypt:
            xord_byte_array.insert(0,ord('\n'))
            sb = str(startblock)
            for i in range(len(sb)):
                xord_byte_array.insert(0,ord(sb[len(sb)-1-i]))

        if not encrypt:
            new_filename = b''
            for i in range(xord_byte_array.index(10)):
                new_filename+=bytes(chr(xord_byte_array.pop(0)),'utf-8')
            new_filename = new_filename.decode("utf-8") 
            xord_byte_array = xord_byte_array[1:]
            print(new_filename)

            filename = new_filename
        else:
            filename = ''.join(random.choice('ABCDEF1234567890') for _ in range(8))+'.enc'
 
        if not args.keepblocks:
            f = b''
            nn = 0
            for i in keyblocks:
                if nn == len(keyblocks)-1:
                    f += i
                else:
                    f += i + b'\n'
                nn+=1
            with open(args.keyfile, "wb") as file:
                file.write(f)
 
        open(filename, 'wb').write(xord_byte_array)
        print('Done, output:',filename)
