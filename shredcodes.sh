#!/bin/bash
echo 'Wiping codes'
shred -zv -n 1 *_otp.*
shred -zv -n 1 *_aespad.*
shred -zv -n 1 *_auth.*
shred -zv -n 1 *_brevitycodes.*
shred -zv -n 1 */*_otp.*
shred -zv -n 1 */*_aespad.*
shred -zv -n 1 */*_auth.*
shred -zv -n 1 */*_brevitycodes.*
rm *_otp.*
rm *_aespad.*
rm *_auth.*
rm *_brevitycodes.*
rm */*_otp.*
rm */*_aespad.*
rm */*_auth.*
rm */*_brevitycodes.*
echo 'Codes wiped'
