                                                                                                                                                                                                         stmtList                                                                                                                                                                                                               
                                  __________________________________________________________________________________________________________________________________________________________________________|___________________________________________________________________________________________________________________________________________________________________________                                        
                                  |                                                                                                         |                                                                                                                                           |                            |                                                                 |                                        
                               funcDec                                                                                                   funcDec                                                                                                                                     varDec                    functionCall                                                        forBlock                                     
 _________________________________|_________________________________                                   _____________________________________|_____________________________________                                                                                               _______|_______               ______|______                    _______________________________________|_______________________________________ 
 |     |            |                                              |                                   |       |              |                                                  |                                                                                               |             |               |           |                    |            |                                  |                             | 
int   gcd      defParamList                                    stmtList                               int   coPrime      defParamList                                        stmtList                                                                                           int         idList           print   parameterList           varDec          lt                             stmtList                         sp 
               _____|______            ____________________________|____________________________                         _____|______             _______________________________|_______________________________                                                                        ______|______                     |                ____|____      __|___                               |                             | 
               |          |            |                      |                                |                         |          |             |                                                             |                                                                        |           |                functionCall          |       |      |    |                            forBlock                         i 
            defParam   defParam     varDec               whileBlock                         return                    defParam   defParam       varDec                                                       ifBlock                                                                  assign      assign              _____|______         int   idList    i   10        _______________________|________________________       
             __|___     __|___     ____|____       ___________|___________                     |                       __|___     __|___     _____|______                        _______________________________|________________________________                                     ___|___     ___|___             |          |                  |                    |            |               |                 |       
             |    |     |    |     |       |       |                     |                     a                       |    |     |    |     |          |                        |                    |                                         |                                     |     |     |     |            gcd   parameterList          assign              varDec          lt          stmtList             sp       
            int   a    int   b    int   idList    ne                 stmtList                                         int   a    int   b    int      idList                      ne               stmtList                                  stmtList                                  a   73872   b   5728                     __|__              __|__              ____|____      __|___            |                 |       
                                           |     __|__        ___________|___________                                                                   |                      __|___                 |                                         |                                                                              |   |              |   |              |       |      |    |       functionCall           j       
                                         temp    |   |        |           |         |                                                                 assign                   |    |           functionCall                               functionCall                                                                        a   b              i   5             int   idList    j   10      ______|_______                  
                                                 b   0      assign      assign   assign                                                            _____|______               val   1     ____________|____________                     ________|_________                                                                                                                   |                  |            |                  
                                                           ___|____     __|__    ___|___                                                           |          |                           |                       |                     |                |                                                                                                                 assign            coPrime   parameterList            
                                                           |      |     |   |    |     |                                                          val    functionCall                   print               parameterList             print        parameterList                                                                                                           __|__                           __|__                
                                                         temp    mod    a   b    b   temp                                                                _____|______                              _______________|_______________            ___________|____________                                                                                                     |   |                           |   |                
                                                                __|__                                                                                    |          |                              |     |     |    |     |      |            |     |     |          |                                                                                                     j   5                           i   j                
                                                                |   |                                                                                   gcd   parameterList                     "gcd("   a   ", "   b   ") ="   val           a   "and"   b   "are co-prime!"                                                                                                                                                   
                                                                a   b                                                                                             __|__                                                                                                                                                                                                                                                         
                                                                                                                                                                  |   |                                                                                                                                                                                                                                                         
                                                                                                                                                                  a   b                                                                                                                                                                                                                                                         
extern _printf
global _main

section .data
    __t_0: dd 0
    __t_4: dd 1
    __t_6: dd "gcd(", 0
    __t_7: dd ", ", 0
    __t_8: dd ") =", 0
    __t_9: db "%s %d %s %d %s %d", 0Ah, 0
    __t_10: dd "and", 0
    __t_11: dd "are co-prime!", 0
    __t_12: db "%d %s %d %s", 0Ah, 0
    __t_13: dd 73872
    __t_14: dd 5728
    __t_16: db "%d", 0Ah, 0
    __t_17: dd 5
    __t_18: dd 10
    __t_20: dd 5
    __t_21: dd 10

section .bss
    __v_1_0_a: resd 1
    __v_1_0_b: resd 1
    __v_1_0_temp: resd 1
    __t_1: resd 1
    __t_2: resd 1
    __v_1_1_a: resd 1
    __v_1_1_b: resd 1
    __v_1_1_val: resd 1
    __t_3: resd 1
    __t_5: resd 1
    __v_0_0_a: resd 1
    __v_0_0_b: resd 1
    __t_15: resd 1
    __v_0_0_i: resd 1
    __t_19: resd 1
    __v_1_2_j: resd 1
    __t_22: resd 1
    __t_23: resd 1

section .text
__CB_2:
    mov ebx, [esp + 4]
    mov dword [__v_1_1_a], ebx
    mov ebx, [esp + 8]
    mov dword [__v_1_1_b], ebx
    push eax
    push ebx
    push dword [__v_1_1_b]
    push dword [__v_1_1_a]
    call __CB_0
    add esp, 8
    mov dword [__t_3], eax
    pop ebx
    pop eax
    mov ebx, dword [__t_3]
    mov dword [__v_1_1_val], ebx
    push eax
    xor eax, eax
    push ebx
    mov ebx, dword [__v_1_1_val]
    cmp ebx, dword [__t_4]
    lahf 
    shr eax, 14
    and eax, 1
    xor eax, 1
    mov dword [__t_5], eax
    pop ebx
    pop eax
    push ebx
    mov ebx, dword [__t_5]
    cmp ebx, 1
    pop ebx
    jz __CB_3
    jmp __CB_4
__CB_6:
    push eax
    xor eax, eax
    push ebx
    mov ebx, dword [__v_1_2_j]
    cmp ebx, dword [__t_21]
    lahf 
    shr eax, 15
    and eax, 1
    mov dword [__t_22], eax
    pop ebx
    pop eax
    push ebx
    mov ebx, dword [__t_22]
    cmp ebx, 0
    pop ebx
    jz __CB_5_SEG_1
    push eax
    push ebx
    push dword [__v_1_2_j]
    push dword [__v_0_0_i]
    call __CB_2
    add esp, 8
    mov dword [__t_23], eax
    pop ebx
    pop eax
    inc dword [__v_1_2_j]
    jmp __CB_6
__CB_0:
    mov ebx, [esp + 4]
    mov dword [__v_1_0_a], ebx
    mov ebx, [esp + 8]
    mov dword [__v_1_0_b], ebx
    jmp __CB_1
__CB_5_SEG_1:
    inc dword [__v_0_0_i]
    jmp __CB_5
__CB_1:
    push eax
    xor eax, eax
    push ebx
    mov ebx, dword [__v_1_0_b]
    cmp ebx, dword [__t_0]
    lahf 
    shr eax, 14
    and eax, 1
    xor eax, 1
    mov dword [__t_1], eax
    pop ebx
    pop eax
    push ebx
    mov ebx, dword [__t_1]
    cmp ebx, 0
    pop ebx
    jz __CB_0_SEG_1
    push eax
    push ebx
    push edx
    xor edx, edx
    mov eax, dword [__v_1_0_a]
    mov ebx, dword [__v_1_0_b]
    div ebx
    mov dword [__t_2], edx
    pop edx
    pop ebx
    pop eax
    mov ebx, dword [__t_2]
    mov dword [__v_1_0_temp], ebx
    mov ebx, dword [__v_1_0_b]
    mov dword [__v_1_0_a], ebx
    mov ebx, dword [__v_1_0_temp]
    mov dword [__v_1_0_b], ebx
    jmp __CB_1
__CB_3:
    push dword [__v_1_1_val]
    push __t_8
    push dword [__v_1_1_b]
    push __t_7
    push dword [__v_1_1_a]
    push __t_6
    push __t_9
    call _printf
    add esp, 28
    jmp _exit
    jmp _exit
__CB_5:
    push eax
    xor eax, eax
    push ebx
    mov ebx, dword [__v_0_0_i]
    cmp ebx, dword [__t_18]
    lahf 
    shr eax, 15
    and eax, 1
    mov dword [__t_19], eax
    pop ebx
    pop eax
    push ebx
    mov ebx, dword [__t_19]
    cmp ebx, 0
    pop ebx
    jz _exit
    mov ebx, dword [__t_20]
    mov dword [__v_1_2_j], ebx
    jmp __CB_6
__CB_0_SEG_1:
    mov eax, dword [__v_1_0_a]
    ret 
    jmp _exit
_exit:
    mov eax, 0
    ret 
    jmp _exit
__CB_4:
    push __t_11
    push dword [__v_1_1_b]
    push __t_10
    push dword [__v_1_1_a]
    push __t_12
    call _printf
    add esp, 20
    jmp _exit
    jmp _exit
_main:
    mov ebx, dword [__t_13]
    mov dword [__v_0_0_a], ebx
    mov ebx, dword [__t_14]
    mov dword [__v_0_0_b], ebx
    push eax
    push ebx
    push dword [__v_0_0_b]
    push dword [__v_0_0_a]
    call __CB_0
    add esp, 8
    mov dword [__t_15], eax
    pop ebx
    pop eax
    push dword [__t_15]
    push __t_16
    call _printf
    add esp, 8
    mov ebx, dword [__t_17]
    mov dword [__v_0_0_i], ebx
    jmp __CB_5
