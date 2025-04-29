#!/usr/bin/python3
import os
import sys
import glob

ARITH_BINARY = {'add':'A=A-1, M=D+M,','sub':'A=A-1, M=M-D,','and':'A=A-1, M=M&D,','or':'A=A-1, M=M|D,'}
ARITH_UNARY = {'neg':'@SP, A=M-1, M=-M,','not':'@SP, A=M-1, M=!M,'}
ARITH_TEST  = {'gt':'JGT','lt':'JLT','eq':'JEQ'}
SEGLABEL = {'argument':'ARG','local':'LCL','this':'THIS','that':'THAT'}

LABEL_NUMBER = 0

# def pointerSeg(push,seg,index):
#     # The following puts the segment's pointer + index in the D
#     # register
#     instr = '@%s, D=M, @%d, D=D+A,'%(SEGLABEL[seg],int(index))
#     if push == 'push':
#         return instr + ('A=D, D=M,'+getPushD())
#     elif push == 'pop':
#         return (instr+'@R15, M=D,' + getPopD() + '@R15, A=M, M=D,')
#     else:
#         print("Yikes, pointer segment, bet seg not found.")
def pointerSeg(pushpop, seg, index):
    """
    Generate Hack assembly code for push/pop operations on pointer-based segments.


    INPUTS:
        pushpop = a text string 'pop' means pop to memory location, 'push' 
                  is push memory location onto stack
        seg     = the name of the segment that will be be the base address
                  in the form of a text string
        index   = an integer that specifies the offset from the base 
                  address specified by seg

    RETURN: 
        The memory address is speficied by segment's pointer (SEGLABEL[seg]) + index (index))
        if pushpop is 'push', push the address contents to the stack
        if pushpop is 'pop' then pop the stack to the memory address.
        The string returned accomplishes this. ML commands are seperated by commas (,).

    NOTE: This function will only be called if the seg is one of:
    "local", "argument", "this", "that"

    """
    output_str = ""
    
    base_address = SEGLABEL[seg]
    if pushpop == "push":
        # output_str = ",".join([
        #     f"@{index}",
        #     f"D=A",
        #     f"@{base_address}",
        #     "A=M",
        #     f"A=D+A",
        #     "D=M",
        #     getPushD()
        # ])
        output_str = ",".join([
            f"@{base_address}",
            "D=M",
            f"@{index}",
            f"A=D+A",
            "D=M",
            getPushD()
        ])


    else:
        output_str = ",".join([
            f"@{index}",
            "D=A",
            f"@{base_address}",
            "D=D+M",
            "@R13",
            "M=D",
            getPopD(),
            "@R13",
            "A=M",
            "M=D",
        ])

    return output_str + ",,"

def fixedSeg(push,seg,index):
    if push == 'push':
        if seg == 'pointer':
            return ('@%d, D=M,'%(3 + int(index)) + getPushD())
        elif seg == 'temp':
            return ('@%d, D=M,'%(5 + int(index)) + getPushD())
    elif push == 'pop':
        if seg == 'pointer':
            return (getPopD() + '@%d, M=D,'%(3 + int(index)))
        elif seg == 'temp':
            return (getPopD() + '@%d, M=D,'%(5 + int(index)))
    else:
        print("Yikes, fixed segment, but seg not found.")

def constantSeg(push,seg,index):
    global filename
    fn_ = filename.split('/')
    fn_ = fn_[-1]
    fn_ = fn_.split('.')
    fn_ = fn_[0]
    if seg == 'constant':
        return '@%d,    D=A,'%(int(index)) + getPushD()
    elif seg == 'static' and push == 'push':
        return '@%s.%d, D=M,'%(fn_,int(index)) + getPushD()
    elif seg == 'static' and push == 'pop':
        return getPopD() + '@%s.%d, M=D,'%(fn_,int(index))

# Yeah this is akward, but needed so that the function handles are known.
SEGMENTS = {'constant':constantSeg,'static':constantSeg,'pointer':fixedSeg,'temp':fixedSeg,\
            'local':pointerSeg,'argument':pointerSeg,'this':pointerSeg,'that':pointerSeg}


def getIf_goto(label):
    """
    Returns Hack ML to goto the label specified as
    an input argument if the top entry of the stack is
    true.
    """
    return getPopD() + '@%s, D;JNE,' % label

def getGoto(label):
    """
    Return Hack ML string that will unconditionally 
    jump to the input label.
    """
    return '@%s, 0;JMP,' % label

def getLabel(label):
    """
    Returns Hack ML for a label, e.g., (label)
    """
    return '(%s),' % label

def getCall(function,nargs):
    """
    This function returns the Hack ML code to 
    invoke the `call function nargs` type command in 
    the Hack virtual machine (VM) language.

    In order for this to work, review slides
    46-58 in the Project 8 presentation available 
    on the nand2tetris.org website.
    """
    #handling call
    #we have to:
    #   save caller's segment pointers
    #   reposition ARG
    #   reposition LCL
    #   Go to execute the callee's code

    #no helper function to set working stack of caller and nArgs

    #---------bot stack----------
    #working stack of caller
    #nArgs
    #saved frame
    #nVars

    #implementation
    #push the return address
    returnLabel = uniqueLabel()
    code = f"// call {function} {nargs},"
    label_saved = _getPushLabel(returnLabel)

    #push the LCL pointer
    code += _getPushMem('LCL')
    #push the ARG pointer
    code += _getPushMem('ARG')
    #push the THIS pointer
    code += _getPushMem('THIS')
    #push the THAT pointer
    code += _getPushMem('THAT')

    #reposition ARG
    code += "// ARG = SP - nArgs - 5,@SP, D=M, @" + str(int(nargs) + 5) + ", D=D-A, @ARG, M=D,"
    #reposition LCL
    code += ",// LCL = SP,"
    code += _getMoveMem("SP", "LCL")
    
    #jump to function
    code += ",// goto Fn,@" + function + ", 0;JMP,(" + label_saved + ")// (return address),"

    code += getLabel(returnLabel)
    return code

def _getMoveMem(src,dest):
    """
    Helper function to move the contents of src to memory location dest.
    """
    ans = "@" + str(src) + ",D=M," + "@" + str(dest) + ",M=D,"
    return ans

def getFunction(function,nargs):
    """
    Return the Hack ML code to represent a function which sets a label
    and initializes local variables to zero.
    See slides 59-63 in the nand2tetris book.
    """
    #We have to:
    #   Inject an entry point label into the code
    #   Initialize the local segment of the callee    
    #
    #---------bot stack----------
    #working stack of caller
    #nArgs
    #saved frame
    #nVars
    #...
    #SP
    #global stack

    #implementation
    #goto label
    output_string += f"({function}),"

    #clear locals
    for i in range(int(nargs)):
        output_string += ",".join([
            SEGMENTS["constant"]("push","constant",0),
        ])

    return output_string

def getReturn():
    """
    Returns Hack ML code to perform a return, one
    of the more complex operations in this unit.
    The code restores all the memory segments to the
    calling function. It also has to restore the 
    instruction pointer (IP) and reset the stack 
    pointer. See slides 64-76 of nand2tetris.org
    project 8.
    """
    #overall idea
    # // The code below creates and uses two temporary variables:
    # // endFrame and retAddr;
    # // The pointer notation *addr is used to denote: RAM[addr].
    # endFrame = LCL            // gets the address at the frame’s end
    # retAddr = *(endFrame – 5) // gets the return address
    # *ARG = pop()              // puts the return value for the caller
    # SP = ARG + 1              // repositions SP
    # THAT = *(endFrame – 1)    // restores THAT
    # THIS = *(endFrame – 2)    // restores THIS
    # ARG = *(endFrame – 3)     // restores ARG
    # LCL = *(endFrame – 4)     // restores LCL\
    # goto retAddr              // jumps to the return address
    code = "// return,"

    #save endframe = LCL
    code = "// FRAME = LCL,@LCL, D=M,@R14, M=D," #save to R14
    #save return address
    code += "// RET = *(FRAME - 5),@5, A=D-A, D=M, @R15, M=D," #save to R15

    #pop return value
    code += "// *ARG = pop()," + _getPopMem("ARG")

    #reposition SP
    code += "// SP = ARG + 1,@ARG, D=M+1, @SP, M=D," #SP = ARG + 1

    #restore THAT
    code += "// Restore THAT = FRAME - 1, @R14, AM=M-1, D=M, @THAT, M=D," #THAT = *(endFrame - 1)
    code += "// Restore THIS = FRAME - 2,@R14, AM=M-1, D=M, @THIS, M=D," #THIS = *(endFrame - 2)
    code += "// Restore ARG = FRAME - 3,@R14, AM=M-1, D=M, @ARG, M=D," #ARG = *(endFrame - 3)
    code += "// Restore LCL = FRAME - 4,@R14, AM=M-1, D=M, @LCL, M=D," #LCL = *(endFrame - 4)

    #goto retAddr
    code += "// goto RET,@R15, A=M, 0;JMP," #goto retAddr

    return code



    


# More jank, this time to define the function pointers for flow control.
PROG_FLOW  = {'if-goto':getIf_goto,'goto':getGoto,'label':getLabel,'call':getCall,'function':getFunction,'return':getReturn}

def _getPushMem(src):
    """
    Helper function to push memory to location src to stack
    """
    ans = "@" + str(src) + ",D=M," + getPushD()
    return ans

def _getPushLabel(src):
    """
    Helper function to push the ROM address of a label to the
    stack.
    """
    ans = "@" + str(src) + ",D=A," + getPushD()
    return ans
   

def _getPopMem(dest):
    """
    Helper function to pop the stack to the memory address dest.
    """
    ans = getPopD() + "@" + str(dest) + ",A=M,M=D,"
    return ans

def _getMoveMem(src,dest):
    """
    Helper function to move the contents of src to memory location dest.
    """
    ans = "@" + str(src) + ",D=M," + "@" + str(dest) + ",M=D,"
    return ans

def line2Command(l):
            return l[:l.find('//')].strip()

def uniqueLabel():
    global LABEL_NUMBER
    LABEL_NUMBER +=1
    return "UL_"+ str(LABEL_NUMBER)

def getPushD():
     # This method takes no arguments and returns a string with assembly language
     # that will push the contents of the D register to the stack.
     return '@SP, A=M, M=D, @SP, M=M+1,'

def getPopD():
    # This method takes no arguments and returns a string with assembly language
    # that will pop the stack to the D register.
    # SIDE EFFECT: The A register contains the SP.
     return '@SP, AM=M-1, D=M,'

def ParseFile(f):
    # outString = ""
    outString = f"// {sys.argv[0]},"
    for line in f:
        command = line2Command(line)
        if command:
            args = [x.strip() for x in command.split()] # Break command into list of arguments, no return characters
            if args[0] in ARITH_BINARY.keys():
                outString += getPopD()
                outString += f"// {args[0]},"
                outString += ARITH_BINARY[args[0]]


            elif args[0] in ARITH_UNARY.keys():
                outString += f"// {args[0]},"
                outString += ARITH_UNARY[args[0]]

            elif args[0] in PROG_FLOW.keys():
                if args[0] == 'function' or args[0] == 'call':
                    outString += PROG_FLOW[args[0]](args[1],int(args[2]))
                elif args[0] == 'return':
                    outString += PROG_FLOW[args[0]]()
                elif args[0] == 'label' or args[0] == 'goto' or args[0] == 'if-goto':
                    outString += PROG_FLOW[args[0]](args[1])


            elif args[0] in ARITH_TEST.keys():
                outString += getPopD()
                outString += ARITH_BINARY['sub']
                outString += getPopD()
                l1 = uniqueLabel()
                l2 = uniqueLabel()
                js = \
                  '@%s, D;%s, @%s, D=0;JMP, (%s),D=-1,(%s),'\
                  %(l1,ARITH_TEST[args[0]],l2,l1,l2)
                outString += js
                outString += getPushD()

            elif args[0] in PROG_FLOW.keys():
                
                if len(args) == 1:
                    outString += PROG_FLOW[args[0]]()

                elif len(args) == 2:
                    cmd, label = args[0:2]
                    outString += PROG_FLOW[cmd](label)

                elif len(args) == 3:
                    cmd, fn, n = args[0:3]
                    outString += PROG_FLOW[cmd](fn, n)

                out_string += ','

            elif args[1] in SEGMENTS.keys():
                outString += SEGMENTS[args[1]](args[0],args[1],args[2])

            else:
                print("Unknown command!")
                print(args)
                sys.exit(-1)

    return outString

# def getInit(sysinit = True):
    """
    Write the VM initialization code:
        Set the SP to 256.
        Initialize system pointers to -1.
        Call Sys.Init()
        Halt loop
    Passing sysinit = False oly sets the SP.  This allows the simpler
    VM test scripts to run correctly.
    """
    os = ""
    os += '@256,D=A,@SP,M=D,'
    if sysinit:
        os += 'A=A+1,M=-1,A=A+1,M=-1,A=A+1,M=-1,A=A+1,M=-1,'  # initialize ARG, LCL, THIS, THAT
        os += getCall('Sys.init', 0) # release control to init
        halt = uniqueLabel()
        os += '@%s, (%s), 0;JMP,' % (halt, halt)
    return os

# source = sys.argv[1].strip()
# Hardcoded path to the .vm file or directory
# source = "FunctionCalls\\SimpleFunction\\SimpleFunction.vm"
source = "361_P8\\ProgramFlow\\BasicLoop\\BasicLoop.vm"

# no idea how to run the other tests so agonnnyyyyy. 
# 1 AM MOMENT
# I AM LOOSING BRAINCELLS
# SEND HELP

#notes:
# functioncalls works

out_string = ""

if os.path.isdir(source):
    filelist = glob.glob(source+"*.vm")
    # out_string += getInit()
    for filename in filelist:
        f = open(filename)
        out_string += ParseFile(f)
        f.close()
else:
    filename = source
    f = open(source)
    # out_string += getInit(sysinit=False)
    out_string += ParseFile(f)
    f.close()

print(out_string.replace(" ","").replace(',','\n'))

