#!/usr/bin/python2
import binascii
import os
import sys
import argparse

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help='Input filename')
    parser.add_argument('outfile', help='Output filename')
    parser.add_argument('-e', help='Encode',action='store_true')
    parser.add_argument('-d', help='Decode',action='store_true')
    args = parser.parse_args()
    
    with open(args.infile, "r") as file:
        data = file.read()
        
    if args.e:
        data = binascii.b2a_hex(data)
        
    if args.d:
        data = binascii.a2b_hex(data)
        
    with open(args.outfile, "w+") as file:
        file.write(data)
