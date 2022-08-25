#!/bin/bash
echo 'Wiping codes'
shred -zv -n 1 *_otp.*
shred -zv -n 1 *_aespad.*
shred -zv -n 1 *_auth.*
shred -zv -n 1 *_brevitycodes.*
shred -zv -n 1 *.asc
shred -zv -n 1 */*_otp.*
shred -zv -n 1 */*_aespad.*
shred -zv -n 1 */*_auth.*
shred -zv -n 1 */*_brevitycodes.*
shred -zv -n 1 */*.asc
rm *_otp.*
rm *_aespad.*
rm *_auth.*
rm *_brevitycodes.*
rm *.asc
rm */*_otp.*
rm */*_aespad.*
rm */*_auth.*
rm */*_brevitycodes.*
rm */*.asc
echo 'Codes and keys wiped'
