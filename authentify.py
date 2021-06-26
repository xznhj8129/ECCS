#!/usr/bin/python2
import os
import sys
import argparse
import pickle


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('code', help='Grid coords in Letter-Number format or 4-character Auth code')
    parser.add_argument('authtable', help="Auth table pickle file to use")
    args = parser.parse_args()
    
    with open(args.authtable, 'rb') as f:
        padbook = pickle.load(f)
        
    if len(args.code)==3:
        print padbook[args.code]
        
    elif len(args.code)==4:
        if args.code in padbook.values():
            print padbook.keys()[padbook.values().index(args.code)]
        else:
            print 'Code not found'
        
