        ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
        ;;                        FIRE & TEXT                         ;;
        ;;                        ~~~~~~~~~~~                         ;;
        ;;                   coded by TASeMnik 1998                   ;;
        ;;                   compiled with TASM /m9                   ;;
        ;;                    linked with TLINK /t                    ;;
        ;;                                                            ;;
        ;; DISCLAIMER-You may use this piece of code for whatever you ;;
        ;; want, but I do not accept responsibility for any effects,  ;;
        ;; adverse or otherwise, that this code may have on you, your ;;
        ;; computer, your sanity, your dog, and anything else that    ;;
        ;; you can think of. Use it at your own risk.                 ;;
        ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

.386
tsm 	segment byte public use16
        assume cs:tsm,ds:tsm,ss:tsm,es:tsm
        org 100h
beg:    mov ax,1130h                    ;startup section
        mov bh,2
        int 10h
        push es
        pop fs
        mov font,bp
        mov ax,13h
        int 10h
        xor cx,cx
        mov bx,cx
        mov dx,3c8h
        mov al,1
        out dx,al
        inc dx
        mov cl,32
ll1:    out dx,al
        xchg ax,bx
        out dx,al
        out dx,al
        xchg bx,ax
        inc ax
        inc ax
        loop ll1
        mov cl,32
        mov al,1
ll2:    xchg ax,bx
        mov al,63
        out dx,al
        mov ax,bx
        out dx,al
        xor ax,ax
        out dx,al
        xchg ax,bx
        inc ax
        inc ax
        loop ll2
        mov cl,32
        mov al,1
ll3:    xchg ax,bx
        mov al,63
        out dx,al
        out dx,al
        xchg bx,ax
        out dx,al
        inc ax
        inc ax
        loop ll3
        mov cl,96
        mov al,63
ll4:    out dx,al
        loop ll4
        mov cl,31
ll5:    xor ax,ax
        out dx,al
        mov al,cl
        shl ax,1
        out dx,al
        mov bl,62
        sub bl,cl
        mov al,bl
        out dx,al
        loop ll5
        mov cl,31
ll6:    xor ax,ax
        out dx,al
        mov bl,cl
        shl bl,1
        mov al,62
        sub al,bl
        out dx,al
        mov al,bl
        out dx,al
        loop ll6
        push dx
        mov ax,3508h
        int 21h
        mov word ptr oldint,bx
        mov word ptr oldint+2,es
        push 0a000h
        pop es
        mov dx,offset timer
        mov ax,2508h
        int 21h

        mov bp,640                      ;main section
l1:     mov cx,320
l2:     mov di,19520
        sub di,cx
l3:     movzx ax,byte ptr es:[di]
        add al,es:[di]+2
        adc ah,bh
        add al,es:[di]-2
        adc ah,bh
        add al,es:[di]+642
        adc ah,bh
        shr ax,2
        jz short l4
        dec ax
l4:     mov ah,al
        mov es:[di]-640,ax
        mov es:[di]-320,ax
        add di,bp
        jnc l3
        sub di,bp
        pop ax
        lea ax,short [eax+eax*2]        ;one opcode "RAND"
        push ax
        mov es:[di],bh
        and ah,00100000b
        jz short l5
        mov byte ptr es:[di],160
l5:     dec cx
        loop l2
        in al,60h
        cmp al,1
        jne short l1

        mov dx,word ptr oldint          ;cleanup section
        mov ds,word ptr oldint+2
        mov ax,2508h
        int 21h
        mov ax,3
        int 10h
        pop dx
        ret

timer   proc far                        ;interrupt handler
        pusha
        mov cl,intext
        cmp cl,8
        jne short xl1
        inc poradi
        mov byte ptr intext,0
xl1:    mov di,offset text
        add di,poradi
        cmp byte ptr ds:[di],0
        jne short xl2
        sub di,poradi
        mov poradi,0
xl2:    mov al,ds:[di]
        mov dl,14
        mul dl
        mov di,font
        add di,ax
        mov si,642+320*16
        mov cx,14
xl3:    push cx
        mov bx,157
xl4:    mov ax,es:[si+2]
        mov es:[si],ax
        inc si
        inc si
        dec bx
        jnz short xl4
        mov ah,fs:[di]
        inc di
        mov cl,intext
        shl ah,cl
        test ah,10000000b
        jz short xl5
        mov ax,819eh
        add ah,color
        mov es:[si-2],ax
        inc color
        cmp color,62
        jnz short xl5
        mov color,0
xl5:    add si,326
        pop cx
        loop xl3
        inc intext
        popa
        jmp oldint
timer   endp

color   db 0                            ;data section
intext  db 0
poradi  dw 0
font    dw 0
oldint  dd 0
text    db '--* Greeting from TASeMnik',39,'s_/\_/\_/=8> Manufactory *-- '
        db '                      ',0
tsm     ends
        end     beg
