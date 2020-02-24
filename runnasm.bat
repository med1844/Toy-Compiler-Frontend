@echo off
nasm -f win32 _test.asm && gcc _test.obj -o _test.exe && _test