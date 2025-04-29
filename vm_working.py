#!/usr/bin/python3
import os
import sys
import glob

ARITH_BINARY = {'add':'A=A-1, M=D+M,','sub':'A=A-1, M=M-D,','and':'A=A-1, M=D&M,','or':'A=A-1, M=D|M,'}
ARITH_UNARY = {'neg':'@SP, A=M-1, M=-M,','not':'@SP, A=M-1, M=!M,'}
ARITH_TEST  = {'gt':'JGT','lt':'JLT','eq':'JEQ'}
SEGLABEL = {'argument':'ARG','local':'LCL','this':'THIS','that':'THAT'}

LABEL_NUMBER = 0

def pointerSeg(push,seg,index):
    # The following puts the segment's pointer + index in the D
    # register
    instr = '@%s, D=M, @%d, D=D+A,'%(SEGLABEL[seg],int(index))
    if push == 'push':
        return instr + ('A=D, D=M,'+getPushD())
    elif push == 'pop':
        return (instr+'@R15, M=D,' + getPopD() + '@R15, A=M, M=D,')
    else:
        print("Yikes, pointer segment, bet seg not found.")

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
    an input arguement if the top entry of the stack is
    true.
    """
    return "\n".join([
    getPopD(),
    f"@{label}",  # Load the destination label
    "D;JNE", # Jump if D != 0 (i.e., if the value was true)
    ","
    ])

def getGoto(label):
    """
    Return Hack ML string that will unconditionally
    jumpt to the input label.
    """
    return f"@{label},0;JMP,,"

def getLabel(label):
    """
    Returns Hack ML for a label, eg (label)
    """
    return f"({label}),"
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

    outString = f" // call {function} {nargs},"
    l = uniqueLabel()

    outString += _getPushLabel(l)

    # for item in segs:
    #     outString += _getPushMem(item)
    #push the LCL pointer
    outString += _getPushMem('LCL')
    #push the ARG pointer
    outString += _getPushMem('ARG')
    #push the THIS pointer
    outString += _getPushMem('THIS')
    #push the THAT pointer
    outString += _getPushMem('THAT')

    #reposition ARG
    outString += "// ARG = SP - nArgs - 5,@SP, D=M, @" + str(int(nargs) + 5) + ", D=D-A, @ARG, M=D,"
    #reposition LCL
    outString += ",// LCL = SP,"
    outString += _getMoveMem("SP", "LCL")

    #jump to function
    outString += ",// goto Fn,@" + function + ", 0;JMP,(@" + function + ")// (return address),"

    return outString


def getFunction(function,nlocal):
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
    output_string = f" // function {function} {nlocal},"
    output_string += f"({function}),"

    #clear locals
    for i in range(int(nlocal)):
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

    output_string = " // return,"

    output_string += " // FRAME = LCL,"
    #save endframe = LCL
    output_string += _getMoveMem("LCL","R13") + ","
    #save return address
    output_string = "@5, A=D-A, D=M, @R14, M=D,"

    #pop return value
    output_string += " // *ARG = pop(),"
    output_string += _getPopMem("ARG")

    #reposition SP
    output_string += "// SP = ARG + 1,@ARG, D=M+1, @SP, M=D,"


    #restore THAT THIS ARG LCL
    output_string += "// Restore THAT = FRAME - 1, @R13, AM=M-1, D=M, @THAT, M=D," #THAT = *(endFrame - 1)
    output_string += "// Restore THIS = FRAME - 2,@R13, AM=M-1, D=M, @THIS, M=D," #THIS = *(endFrame - 2)
    output_string += "// Restore ARG = FRAME - 3,@R13, AM=M-1, D=M, @ARG, M=D," #ARG = *(endFrame - 3)
    output_string += "// Restore LCL = FRAME - 4,@R13, AM=M-1, D=M, @LCL, M=D," #LCL = *(endFrame - 4)

    #goto retAddr
    output_string += "// goto RET,@R14, A=M, 0;JMP,"

    return output_string

# More jank, this time to define the function pointers for flow control.
PROG_FLOW  = {'if-goto':getIf_goto,'goto':getGoto,'label':getLabel,'call':getCall,'function':getFunction,'return':getReturn}

def getPopD():
    return f"@SP,AM=M-1,D=M"

def getPushD():
    return f"@SP,A=M,M=D,@SP,M=M+1"

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

def line2Command(line):
    """ This just returns a cleaned up line, removing unneeded spaces and comments"""
    line = line.split("//")[0].strip()
    return line if line else None

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
    outString = ""
    for line in f:
        command = line2Command(line)
        if command:
            args = [x.strip() for x in command.split()] # Break command into list of arguments, no return characters
            if args[0] in ARITH_BINARY.keys():
                outString += getPopD()
                outString += ARITH_BINARY[args[0]]

            elif args[0] in ARITH_UNARY.keys():
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

            elif args[1] in SEGMENTS.keys():
                outString += SEGMENTS[args[1]](args[0],args[1],args[2])

            else:
                print("Unknown command!")
                print(args)
                sys.exit(-1)

    return outString

def getInit(sysinit = True):
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

source = sys.argv[1].strip()

out_string = ""

if os.path.isdir(source):
    filelist = glob.glob(source+"*.vm")
    out_string += getInit()
    for filename in filelist:
        f = open(filename)
        out_string += ParseFile(f)
        f.close()
else:
    filename = source
    f = open(source)
    out_string += getInit(sysinit=False)
    out_string += ParseFile(f)
    f.close()

print(out_string.replace(" ","").replace(',','\n'))

#project 7
# SimpleAdd.vm -- works
# BasicTest.vm -- works
# PointerTest.vm -- works
# StackTest.vm -- works
# StaticTest.vm --

#project 8
# BasicTest.vm -- works
# FibonacciElement.vm -- works
# FibonacciSeries.vm -- works
# NestedCall.vm -- (just disable the init) works  ... -5 i think
# SimpleFunction.vm -- works
# StaticTest.vm -- maybe a init issue not sure