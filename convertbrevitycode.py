#!/usr/bin/python2
import os
import sys
import argparse
import pickle


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('code', help='Word or 4-character Auth code')
    parser.add_argument('codebook', help="Auth table pickle file to use")
    args = parser.parse_args()
    
    with open(args.codebook, 'rb') as f:
        codebook = pickle.load(f)
        bc = {}
        for i in codebook:
            bc[codebook[i]] = i
        if args.code.lower() in codebook.keys():
            print codebook[args.code.lower()]
        elif args.code in bc.keys():
            print bc[args.code]
        else:
            print 'Code not found'
        
