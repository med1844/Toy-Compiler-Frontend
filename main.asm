extern _printf
global _main

section .data
_fmt: db "%d", 0Ah, 0
_a: dd 4
_b: dd 5

section .text
_add:
    mov eax, dword [esp + 4]
    mov ebx, dword [esp + 8]
    add eax, ebx
    ret

_main:
    push 4
    push 5
    call _add
    add esp, 8
    push eax
    push _fmt
    call _printf
    add esp, 8
    ret
