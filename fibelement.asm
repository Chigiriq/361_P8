@256
D=A
@SP
M=D
A=A+1
M=-1
A=A+1
M=-1
A=A+1
M=-1
A=A+1
M=-1
//callSys.init0
@UL_1
D=A
@SP
A=M
M=D
@SP
M=M+1


@LCL
D=M
@SP
A=M
M=D
@SP
M=M+1


@ARG
D=M
@SP
A=M
M=D
@SP
M=M+1


@THIS
D=M
@SP
A=M
M=D
@SP
M=M+1


@THAT
D=M
@SP
A=M
M=D
@SP
M=M+1


//ARG=SP-nArgs-5
@SP
D=M
@5
D=D-A
@ARG
M=D

//LCL=SP
@SP
D=M
@LCL
M=D

//gotoFn
@Sys.init
0;JMP
(UL_1)

@UL_2
(UL_2)
0;JMP
//functionMain.fibonacci0
(Main.fibonacci)
@ARG
D=M
@0
D=D+A
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1
@2
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
A=A-1
M=M-D
@SP
AM=M-1
D=M
@UL_3
D;JLT
@UL_4
D=0;JMP
(UL_3)
D=-1
(UL_4)
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M

@N_LT_2
D;JNE

@N_GE_2
0;JMP

(N_LT_2)
@ARG
D=M
@0
D=D+A
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1
//return
//FRAME=LCL
@LCL
D=M
@R13
M=D
@5
A=D-A
D=M
@R14
M=D

//*ARG=pop()
@SP
AM=M-1
D=M

@ARG
A=M
M=D

//SP=ARG+1
@ARG
D=M+1
@SP
M=D

//RestoreTHAT=*(FRAME-1)
@R13
AM=M-1
D=M
@THAT
M=D

//RestoreTHIS=*(FRAME-2)
@R13
AM=M-1
D=M
@THIS
M=D

//RestoreARG=*(FRAME-3)
@R13
AM=M-1
D=M
@ARG
M=D

//RestoreLCL=*(FRAME-4)
@R13
AM=M-1
D=M
@LCL
M=D

//gotoRET
@R14
A=M
0;JMP

(N_GE_2)
@ARG
D=M
@0
D=D+A
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1
@2
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
A=A-1
M=M-D
//callMain.fibonacci1
@UL_5
D=A
@SP
A=M
M=D
@SP
M=M+1


@LCL
D=M
@SP
A=M
M=D
@SP
M=M+1


@ARG
D=M
@SP
A=M
M=D
@SP
M=M+1


@THIS
D=M
@SP
A=M
M=D
@SP
M=M+1


@THAT
D=M
@SP
A=M
M=D
@SP
M=M+1


//ARG=SP-nArgs-5
@SP
D=M
@6
D=D-A
@ARG
M=D

//LCL=SP
@SP
D=M
@LCL
M=D

//gotoFn
@Main.fibonacci
0;JMP
(UL_5)

@ARG
D=M
@0
D=D+A
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
A=A-1
M=M-D
//callMain.fibonacci1
@UL_6
D=A
@SP
A=M
M=D
@SP
M=M+1


@LCL
D=M
@SP
A=M
M=D
@SP
M=M+1


@ARG
D=M
@SP
A=M
M=D
@SP
M=M+1


@THIS
D=M
@SP
A=M
M=D
@SP
M=M+1


@THAT
D=M
@SP
A=M
M=D
@SP
M=M+1


//ARG=SP-nArgs-5
@SP
D=M
@6
D=D-A
@ARG
M=D

//LCL=SP
@SP
D=M
@LCL
M=D

//gotoFn
@Main.fibonacci
0;JMP
(UL_6)

@SP
AM=M-1
D=M
A=A-1
M=D+M
//return
//FRAME=LCL
@LCL
D=M
@R13
M=D
@5
A=D-A
D=M
@R14
M=D

//*ARG=pop()
@SP
AM=M-1
D=M

@ARG
A=M
M=D

//SP=ARG+1
@ARG
D=M+1
@SP
M=D

//RestoreTHAT=*(FRAME-1)
@R13
AM=M-1
D=M
@THAT
M=D

//RestoreTHIS=*(FRAME-2)
@R13
AM=M-1
D=M
@THIS
M=D

//RestoreARG=*(FRAME-3)
@R13
AM=M-1
D=M
@ARG
M=D

//RestoreLCL=*(FRAME-4)
@R13
AM=M-1
D=M
@LCL
M=D

//gotoRET
@R14
A=M
0;JMP

//functionSys.init0
(Sys.init)
@4
D=A
@SP
A=M
M=D
@SP
M=M+1
//callMain.fibonacci1
@UL_7
D=A
@SP
A=M
M=D
@SP
M=M+1


@LCL
D=M
@SP
A=M
M=D
@SP
M=M+1


@ARG
D=M
@SP
A=M
M=D
@SP
M=M+1


@THIS
D=M
@SP
A=M
M=D
@SP
M=M+1


@THAT
D=M
@SP
A=M
M=D
@SP
M=M+1


//ARG=SP-nArgs-5
@SP
D=M
@6
D=D-A
@ARG
M=D

//LCL=SP
@SP
D=M
@LCL
M=D

//gotoFn
@Main.fibonacci
0;JMP
(UL_7)

(END)
@END
0;JMP


