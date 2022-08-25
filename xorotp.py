#!/usr/bin/python3

import math
import Crypto.Random as Random
import binascii
import os
import sys
import argparse
import random
import pickle

class XORcrypter():
    
    def __init__(self):
        self.kb = 10
    
    def genkeyfile(self, size, filename):
        
        n_blocks = int(size)
        blocks = []

        for i in range(n_blocks):
            bits = int(self.kb)*1000
            rand = Random.new().read(bits)
            blocks.append(rand)

        with open(filename+'_xorotp.pickle', 'wb') as f:
            pickle.dump(blocks, f, pickle.HIGHEST_PROTOCOL)


    def xorfile(self, mode, keyfile, filename, keepblocks, verbose=False):

        encrypt = mode == 'e'
        deleteblocks = keepblocks

        bits = self.kb * 1000
        nullblock = b''
        for i in range(bits):
            nullblock += b'\0'

        with open(keyfile, 'rb') as f:
            keyblocks = pickle.load(f)

        n_blocks = len(keyblocks)
        
        if verbose: print('Blocks:', n_blocks)
        for i in range(len(keyblocks)):
            if keyblocks[i]!=nullblock:
                startblock = i
                break
        
        if verbose: print('Start block:',startblock)
        randsizeavail = bits * n_blocks - startblock
        blocksavail = n_blocks - startblock
        if verbose: print('Blocks available:',n_blocks - startblock)

        inputfile = bytearray(open(filename, 'rb').read())
        if encrypt:
            size = len(filename)+len(inputfile)+1
        else:
            inputfile = inputfile[inputfile.find(b'\n')+1:]
            size = len(inputfile)

        blocksneeded = math.ceil(size / bits)
        if verbose: print('Blocks needed:',blocksneeded)
        if blocksneeded > blocksavail: 
            print('Error: not enough blocks')
            exit(1)

        key = b''
        n = 0
        
        for i in range(blocksneeded):
            j = i+startblock
            if keyblocks[j] != nullblock:
                key += keyblocks[j]
                if not keepblocks:
                    keyblocks[j] = nullblock

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
 
        if not keepblocks:
            with open(keyfile, 'wb') as f:
                pickle.dump(keyblocks, f, pickle.HIGHEST_PROTOCOL)
 
        open(filename, 'wb').write(xord_byte_array)
        return filename
        

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', help='Encrypt',action='store_true')
    parser.add_argument('-d', help='Decrypt',action='store_true')
    parser.add_argument('-o', help="Output file",nargs="?")
    parser.add_argument('--keyfile', help='Random data key file to use',nargs="?")
    parser.add_argument('--file', help="File to XOR",nargs="?")
    parser.add_argument('--genrandom',help="Generate Random Data file, number of blocks of 10kb",required=False)
    parser.add_argument('--keepblocks',help="Keep decryption blocks (UNSAFE)",required=False,action='store_true')
    parser.add_argument('-v',help="Verbose",required=False,action='store_true')
    args = parser.parse_args()
    
    xor = XORcrypter()
    
    if args.genrandom:
        if not args.keyfile:
            print('Error: please specify a keyblock filename')
            exit(1)
        print('Generating {} blocks of {} kilobytes of random data'.format(args.genrandom, xor.kb))
        xor.genkeyfile(args.genrandom, args.keyfile)
        print('Done')

    else:
        
        if not (args.e ^ args.d):
            print('Error: unknown action')
            exit(1)
        
        if args.e:
            mode = 'e'
        elif args.d:
            mode = 'd'
            
        filename = xor.xorfile(mode, args.keyfile, args.file, args.keepblocks, verbose=args.v)
        print(filename)
        
