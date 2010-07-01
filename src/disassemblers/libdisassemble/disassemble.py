#! /usr/bin/env python


# Immunity libdisassemble
#
# Most of the functions are ported from the great libdisassm since we
#  we are using their opcode map. 

# TODO:
#    - Fix the getSize(), doesn't work well with all the opcodes
#    - Enhance the metadata info with more information on opcode.
#      i.e. we need a way to know if an address is an immediate, a relative offset, etc
#    - Fix the jmp (SIB) opcode in at&t that it has different output that the others. 
#    - support all the PREFIX*

# NOTE: This is less than a week work, so it might be full of bugs (we love bugs!)
#
# Any question, comments, hate mail: dave@immunitysec.com


# 
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#                                                                                
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#                                                                                
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# This code largely copyright Immunity, Inc (2004), parts
# copyright mammon and used under the LGPL by permission

import disassemblers.libdisassemble.opcode86 as opcode86
import struct
from sys import *

table86=opcode86.tables86
OP_PERM_MASK =  0x0000007  
OP_TYPE_MASK =  0x0000F00  
OP_MOD_MASK  =  0x00FF000  
OP_SEG_MASK  =  0x00F0000  
OP_SIZE_MASK = 0x0F000000  


class Mode:
    def __init__(self, type, mode=32):
        self.type = type #type & 0x700
        #self.flag = type & 0x7
        self.flag  = type & OP_PERM_MASK
        self.length = 0
        self.mode = mode
        
    # format "AT&T" or "INTEL"
    def printOpcode(self, format, eip=0):
        return "Not available"

    def getType(self):
        return self.type

    def getSize(self):
        return self.length
    
    def getFlag(self):
        return self.flag

    def getSFlag(self):
        return ("R", "W", "X")[self.flag/2]
    
    def getOpSize(self):
        return (self.type & OP_SIZE_MASK)

    def getAddrMeth(self):
        return (self.type & opcode86.ADDRMETH_MASK)
    
class Register(Mode):
    def __init__(self, regndx, type=opcode86.OP_REG):
        Mode.__init__(self, type)
        #print regndx
        (self.name, self.detail, self.length)=opcode86.regs[regndx]

    def printOpcode(self, format="INTEL", eip=0):
        if format == "INTEL":
            return self.name
        else:
            return "%%%s" % self.name

    def getName(self):
        return self.name
    
class Address(Mode):
    def __init__(self, data, length, type=opcode86.ADDEXP_DISP_OFFSET, signed=1, relative = None):
        Mode.__init__(self, type)
        
        self.signed=signed
        self.length  = length
        #print "'%s' %d %x, %s"%(data, length, type, relative)
        fmt = "<"
        if self.signed:
            fmt += ("b", "h", "l")[length//2]
        else:
            fmt += ("B", "H", "L")[length//2]
        
        if (self.getAddrMeth() ==  opcode86.ADDRMETH_A):
            fmt += "H"
            length += 2
            self.value, self.segment = struct.unpack(fmt, data[:length])
        else:
            self.value, = struct.unpack(fmt, data[:length])
            self.segment = None
        
        self.relative = relative

        
    def printOpcode(self, format="INTEL", eip=0, exp=0):
        value = self.value
        segment = self.segment
        
        if (self.relative):
            value += eip
            
        if format == "INTEL":
            tmp=""
            if (segment):
                tmp += "0x%04x:"%(segment)
            if self.signed:
                if value < 0:
                    return "%s-0x%x" % (tmp, value * -1)
                return "%s0x%x" % (tmp,self.value)
            else:
            #if self.length == 4 or not self.signed:
                return "%s0x%x" % (tmp,self.value)
            #else:
                
        else:
            pre=""
            #if self.getAddrMeth() == opcode86.ADDRMETH_E and not exp:
            if (self.getAddrMeth() == opcode86.ADDRMETH_I or self.getAddrMeth() == opcode86.ADDRMETH_A or self.type & opcode86.OP_IMM) and not exp:
                pre+="$"
            if segment:
                pre = "$0x%04x:%s"%(segment,pre)
            if (value < 0):
                if (self.signed):
                    return "%s0x%0x" % (pre, ((1<<self.length*8) + value))
                else:
                    return "%s-0x%0x" % (pre, (-value))
            else:
                return "%s0x%0x" % (pre, (value))

class Expression(Mode):
    def __init__(self, disp, base, type):
        Mode.__init__(self, type)		
        self.disp  = disp
        self.base  = base
        self.psize = 4

    def setPsize(self, size):
        self.psize= size

    def getPsize(self):
        return self.psize

    def getType(self):
        return EXPRESSION

    def printOpcode(self, format="INTEL", eip=0):
        tmp=""
        if format == "INTEL":
            if self.base:
                tmp += self.base.printOpcode(format, eip)
            if self.disp:
                if self.disp.value:
                    if self.disp.value > 0 and tmp:
                        tmp+="+"
                    tmp += self.disp.printOpcode(format, eip, 1)
            pre=""
            optype=self.getOpSize()
        
            addr_meth=self.getAddrMeth()
            if addr_meth == opcode86.ADDRMETH_E:
                if optype  == opcode86.OPTYPE_b:
                    pre="BYTE PTR"
                elif optype== opcode86.OPTYPE_w:
                    pre="WORD PTR"
                else :
                    pre="DWORD PTR"
            tmp="%s [%s]" % (pre, tmp)
        else:
            if self.base:
                tmp+="(%s)" % self.base.printOpcode(format, eip)
            if self.disp:
                tmp= "%s%s" % (self.disp.printOpcode(format, eip, 1), tmp)				
            #tmp="Not available"
        return tmp
class SIB(Mode):
    def __init__(self, scale, base, index):
        self.scale = scale
        self.base  = base
        self.index = index
    def printOpcode(self, format="INTEL", eip=0):
        tmp=""
        if format == "INTEL":
            if self.base:
                tmp+="%s" % self.base.printOpcode(format, eip)
            if self.scale > 1:
                tmp+= "*%d" % self.scale
            if self.index:
                if tmp:
                    tmp+="+"
                tmp+="%s" % self.index.printOpcode(format, eip)
        else:
            if self.base:
                tmp+="%s" % self.base.printOpcode(format, eip)
            if self.index:
                #if tmp:
                    #tmp+=","
                tmp += ", %s" % self.index.printOpcode(format, eip)
            if self.scale:
                if (self.scale > 1 or self.index):
                    tmp+=", %d" % self.scale

            return tmp
        return tmp 	
        
class Prefix:
    def __init__(self, ndx, ptr):
        self.ptr = ptr
        self.type = opcode86.prefix_table[ndx]
    
    def getType(self):
        return self.type

    def getName(self):
        if self.ptr[6]:
            return self.ptr[6]
        else:
            return ""
    
class Opcode:
    def __init__(self, data, mode=32):
        self.length = 0
        self.mode = mode
        if mode == 64:
            self.addr_size = 4
        else:
            self.addr_size = mode/8     # 32-bit mode = 4 bytes.  16-bit mode = 2 bytes
        self.data = data
        self.off  = 0
        self.source = ""
        self.dest   = ""
        self.aux    = ""
        self.prefix = []
        self.parse(table86[0], self.off)
    
    def getOpcodetype(self):
        return self.opcodetype
        
    def parse(self, table, off):
        """
        Opcode.parse() is the core logic of libdisassemble.  It recurses through the supplied bytes digesting prefixes and opcodes, and then handles operands.
        """
        try:    ## Crash Gracefully with a "invalid" opcode
            self.addr_size = 4
            ndx = self.data[off]
            
            ### This next line slices and dices the opcode to make it fit correctly into the current lookup table.
            #
            #      byte  min          shift       mask
            #   (tbl_0F, 0, 0xff, 0, 0xff),
            #   (tbl_80, 3, 0x07, 0, 0xff),
            #
            #           simple subtraction
            #           shift bits right        (eg.  >> 4 makes each line in the table valid for 16 numbers... ie 0xc0-0xcf are all one entry in the table)
            #           mask part of the byte   (eg.  & 0x7 only makes use of the 00000111 bits...)
            if (ndx > table[4]):
                table = table86[table[5]]               # if the opcode byte falls outside the bounds of accepted values, use the table pointed to as table[5]
            ndx = ( (ndx - table[3]) >> table[1]) & table[2]
            ptr = table[0][ndx] # index from table
            
            if ptr[1] == opcode86.INSTR_PREFIX or (ptr[1] & opcode86.INSTR_PREFIX64 and self.mode == 64):
                # You can have more than one prefix (!?)
                if ptr[0] != 0 and len(self.data) > off and self.data[off+1] == 0x0F:
                    self.parse(table86[ptr[0]],  off+2)         # eg. 660Fxx, F20Fxx, F30Fxx, etc...
                else:
                    self.prefix.append( Prefix(ndx, ptr) )
                    self.parse(table, off+1) # parse next instruction
                
                return
            if ptr[0] != 0:
                # > 1 byte length opcode
                self.parse(table86[ptr[0]],  off+1)
                return 
            
            ### End Recursion, we hit a leaf node.
            
            self.opcode     = ptr[6]
            self.opcodetype = ptr[1]
            self.cpu        = ptr[5]
            self.off        = off + 1 # This instruction
            
            if table[2] != 0xff:        # Is this byte split between opcode and operand?  If so, let's not skip over this byte quite yet...
                self.off-=1
            #print >>stderr,("   opcode = %s\n   opcodetype = %x\n   cpu = %x\n   off = %d"%(ptr[6], ptr[1], ptr[5], off+1))
            
            bytes=0
            #       src dst aux
            values=['', '', '' ]		
            r = [False]*3
            w = [False]*3
            #print self.off
            
            for a in range(2, 5):
                ret = (0, None)
                
                tmp =ptr[a]
                addr_meth = tmp & opcode86.ADDRMETH_MASK;
                if addr_meth == opcode86.OP_REG:
                    # what do i supposed to do?
                    pass
                
                operand_size = self.get_operand_size(tmp)
                #print operand_size
                if operand_size == 1:
                    genreg = opcode86.REG_BYTE_OFFSET
                elif operand_size == 2:
                    genreg = opcode86.REG_WORD_OFFSET
                else:
                    genreg= opcode86.REG_DWORD_OFFSET
    
                # Begin hashing on the ADDRMETH for this operand.  This should determine the number of bytes to advance in the data.
                if addr_meth == opcode86.ADDRMETH_E:
                    ret=self.get_modrm(self.data[self.off:], opcode86.MODRM_EA, genreg, self.addr_size, tmp)  
                    
                elif addr_meth == opcode86.ADDRMETH_M:
                    ret=self.get_modrm(self.data[self.off:], opcode86.MODRM_EA, genreg, self.addr_size, tmp)  
    
                elif addr_meth == opcode86.ADDRMETH_N:
                    ret=self.get_modrm(self.data[self.off:], opcode86.MODRM_EA, opcode86.REG_MMX_OFFSET, self.addr_size, tmp)  
    
                elif addr_meth == opcode86.ADDRMETH_Q:
                    ret=self.get_modrm(self.data[self.off:], opcode86.MODRM_EA, opcode86.REG_MMX_OFFSET, self.addr_size, tmp)  
                    
                elif addr_meth == opcode86.ADDRMETH_R:
                    ret=self.get_modrm(self.data[self.off:], opcode86.MODRM_EA, genreg, self.addr_size, tmp)  
    
                elif addr_meth == opcode86.ADDRMETH_W:
                    ret=self.get_modrm(self.data[self.off:], opcode86.MODRM_EA, opcode86.REG_SIMD_OFFSET, self.addr_size, tmp)  
    
                elif addr_meth == opcode86.ADDRMETH_C:
                    ret=self.get_modrm(self.data[self.off:], opcode86.MODRM_reg, opcode86.REG_CTRL_OFFSET, self.addr_size, tmp)  
    
                elif addr_meth == opcode86.ADDRMETH_D:
                    ret=self.get_modrm(self.data[self.off:], opcode86.MODRM_reg, opcode86.REG_DEBUG_OFFSET, self.addr_size, tmp)  
    
                elif addr_meth == opcode86.ADDRMETH_G:
                    ret=self.get_modrm(self.data[self.off:], opcode86.MODRM_reg, genreg, self.addr_size, tmp)  
    
                elif addr_meth == opcode86.ADDRMETH_P:
                    ret=self.get_modrm(self.data[self.off:], opcode86.MODRM_reg, opcode86.REG_MMX_OFFSET, self.addr_size, tmp)  
    
                elif addr_meth == opcode86.ADDRMETH_S:
                    ret=self.get_modrm(self.data[self.off:], opcode86.MODRM_reg, opcode86.REG_SEG_OFFSET, self.addr_size, tmp)  
    
                #elif addr_meth == opcode86.ADDRMETH_T:      #TEST REGISTERS?:
                    #ret=self.get_modrm(self.data[self.off:], opcode86.MODRM_EA, opcode86.REG_TEST_OFFSET, self.addr_size, tmp)  
                
                elif addr_meth == opcode86.ADDRMETH_U:
                    ret=self.get_modrm(self.data[self.off:], opcode86.MODRM_EA, opcode86.REG_SIMD_OFFSET, self.addr_size, tmp)  
                
                elif addr_meth == opcode86.ADDRMETH_V:
                    ret=self.get_modrm(self.data[self.off:], opcode86.MODRM_reg, opcode86.REG_SIMD_OFFSET, self.addr_size, tmp)  
    
                elif addr_meth == opcode86.ADDRMETH_A:
                    ret= (self.addr_size, Address(self.data[self.off:], self.addr_size, tmp, signed=0))  
    
                elif addr_meth == opcode86.ADDRMETH_F:
                    # eflags, so what?
                    pass
    
                elif addr_meth == opcode86.ADDRMETH_I:
                    if tmp & opcode86.OP_SIGNED:
                        ret = (operand_size, Address( self.data[self.off+bytes:], operand_size, tmp))
                        #ret = (self.addr_size, Address( self.data[self.off+bytes:], operand_size, tmp))
                    else:
                        ret = (operand_size, Address( self.data[self.off+bytes:], operand_size,tmp,  signed=0))
                        #ret = (self.addr_size, Address( self.data[self.off+bytes:], operand_size,tmp,  signed=0))
    
                elif addr_meth == opcode86.ADDRMETH_J:
                    ret = (operand_size, Address( self.data[self.off+bytes:], operand_size, tmp, signed=1, relative=True))
                    #ret = (self.addr_size, Address( self.data[self.off+bytes:], operand_size, tmp, signed=1, relative=True))
    
                elif addr_meth == opcode86.ADDRMETH_O:
                    ret = (self.addr_size, Address( self.data[self.off:], self.addr_size, tmp, signed=0))
                
                elif addr_meth == opcode86.ADDRMETH_X:
                    ret = (0, Register(6+opcode86.REG_DWORD_OFFSET, tmp))
                    
                elif addr_meth == opcode86.ADDRMETH_Y:
                    ret = (0, Register(7+opcode86.REG_DWORD_OFFSET, tmp))
    
                else:
                    if tmp & opcode86.OP_REG:
                        regoff = 0
                        if self.mode == 64 and self.opcodetype in [opcode86.INS_PUSH, opcode86.INS_POP]:
                            regoff = opcode86.REG_QWORD_OFFSET - opcode86.REG_DWORD_OFFSET
                        if self.rex('w'):
                            regoff -= 16
                        if self.rex('b'):
                            regoff += 8
                        ret = (0, Register(ptr[5+a]+regoff, tmp))
                    elif tmp & opcode86.OP_IMM:
                        print("a")
                        ret = (0, Address("%c"%ptr[5+a], 1, signed=0))
                    else:
                        ret= (0, None)
                if ret[1]: 
                    if isinstance(ret[1], Expression):
                        ret[1].setPsize(operand_size)				
                values[a-2]=ret[1]
                r[a-2] = (tmp & opcode86.OP_R) != 0
                w[a-2] = (tmp & opcode86.OP_W) != 0
                bytes += ret[0]
                
            self.source = values[0]
            self.dest   = values[1]
            self.aux    = values[2]
            self.r = r
            self.w = w
    
            self.off += bytes
            #self.data = self.data[:self.off]
        except IndexError:
            output = ""
            for i in range(len(self.data)):
                output += "%02x"%self.data[i]

            print (("Error Parsing Opcode - Data: %s\t Offset: 0x%x"%(output,self.off)), file=stderr)
            
            x,y,z = exc_info()
            excepthook(x,y,z)

    def getSize(self):
        return self.off
    
    def get_operand_size(self, opflag):      
        """
        get_operand_size() gets the operand size, not the address-size or the size of the opcode itself.  
        But it's also bastardized, because it manipulates self.addr_size at the top
        """
        size=self.mode / 8      #initial setting (4 for 32-bit mode)
        if self.mode == 64:
            size = 4
        
        flag = opflag & opcode86.OPTYPE_MASK
        
        #print "flag=%x   mode=%d"%(flag,self.mode)
        if (flag in opcode86.OPERSIZE.keys()):                  # lookup the value in the table
            size = opcode86.OPERSIZE[flag][size >> 2]
            
            
        for a in self.prefix:
            if a.getType() & opcode86.PREFIX_OP_SIZE  and size > 2:
                size = 2
            if a.getType() & opcode86.PREFIX_ADDR_SIZE:   
               # this simply swaps between 16- to 32-bit (default is determined on a "system-wide" level.  This will require changing for 64-bit mode
                if (self.addr_size == 2):
                    self.addr_size = 4 
                else:
                    self.addr_size = 2
                    
        return size
        
        """
        ### THIS IS THE OLD LIBDISASSEMBLE CODE...
        #print flag
        if flag == opcode86.OPTYPE_c:
            size = (1,2)[size==4]
        elif (flag == opcode86.OPTYPE_a) or (flag == opcode86.OPTYPE_v) or (flag == opcode86.OPTYPE_z):
            size = (2,4)[size==4]			
        elif flag == opcode86.OPTYPE_p:
            size = (4,6)[size==4]			
        elif flag == opcode86.OPTYPE_b:
            size = 1
        elif flag == opcode86.OPTYPE_w:
            size = 2
        elif flag == opcode86.OPTYPE_d:
            size = 4		
        elif flag & opcode86.OPTYPE_s:
            size = 6		
        elif flag & opcode86.OPTYPE_q:
            size = 8		
        # - a lot more to add
        """
    
    def get_reg(self, regtable, num):
        return regtable[num]	

    def get_sib(self, data, mod):
        count = 1
        sib     = data[0]
        s=None
        #print "SIB: %s" %  hex(ord(data[0]))
        
        scale    = (sib >> 6) & 0x3   #  XX
        index    = (sib & 56) >>3     #    XXX
        base     = sib & 0x7          #       XXX

        base2 = None
        index2= None
        #print base, index, scale
        # Especial case
        if base == 5 and not mod:
            base2   = Address(data[1:], 4)
            count += 4
        else:
            if self.rex('b'):
                base += 8
            base2 = Register(base + 16)

        index2=None
        # Yeah, i know, this is really ugly
        if index != 4: # ESP
            if self.rex('x'):
                index += 8
            index2=Register( index + 16)
        else:
            scale = 0
        s= SIB( 1<<scale, base2, index2)
        return (count, s)

    def get_modrm(self, data, flags, reg_type, size, type_flag):
        """
        returns a tuple:  (bytecount, Object)
        * bytecount is the number of bytes to advance through data
        """
        modrm=  data[0]
        count = 1
        mod  = (modrm >> 6) & 0x3   #  XX
        reg  = (modrm >> 3) & 0x7   #    XXX
        rm   = modrm & 0x7          #       XXX

        result = None
        disp   = None
        base   = None

        rmoff = 0
        regoff = 0
        if self.rex('w'):
            rmoff -= 16
            regoff -= 16
        if self.rex('b'):
            rmoff += 8
        if self.rex('r'):
            regoff += 8 

        if flags == opcode86.MODRM_EA:
            if   mod == 3:  # 11
                result=Register(rm+reg_type+rmoff, type_flag)
            elif mod == 0:  #  0
                if rm == 5:
                    disp= Address(data[count:], self.addr_size, type_flag)
                    count+= self.addr_size
                elif rm == 4:
                    (tmpcount, base) =self.get_sib(data[count:], mod)
                    count+=tmpcount
                else:
                    #print ("mod:%d\t reg:%d\t rm:%d"%(mod,reg,rm))
                    base=Register(rm+reg_type+rmoff, type_flag)
            else:
                
                if rm ==4:
                    disp_base = 2
                    (tmpcount, base) =self.get_sib(data[count:], mod)
                    count+=tmpcount
                else:
                    disp_base = 1
                    base=Register(rm+reg_type+rmoff, type_flag)
                #print ">BASE: %s" % base.printOpcode()
                if mod == 1:
                    disp= Address(data[disp_base:], 1, type_flag)
                    count+=1
                else:
                    disp= Address(data[disp_base:], self.addr_size, type_flag)
                    count+= self.addr_size
            if disp or base:
                result=Expression(disp, base, type_flag)
        else:
            result=Register(reg+reg_type+regoff, type_flag)
            count=0
           
        return (count, result)
    # FIX:
    #   
    def getOpcode(self, FORMAT, eip = 0):
        opcode=[]
        if not self.opcode:
            return [0]
        if FORMAT == "INTEL":
            opcode.append("%s" % self.opcode)
            #tmp="%-06s %s" % (self.opcode, " " * space)
            if self.source:
                opcode.append(self.source.printOpcode(FORMAT, eip))
                #tmp+=" %s" % self.source.printOpcode(FORMAT, eip)
            if self.dest:
                opcode.append(self.dest.printOpcode(FORMAT, eip))
                #tmp+=", %s" % self.dest.printOpcode(FORMAT, eip)
            if self.aux:
                opcode.append(self.aux.printOpcode(FORMAT, eip))

        else:
            mnemonic = self.opcode
            post=[]
            if self.source and self.dest:
                addr_meth = self.source.getAddrMeth()
                optype = self.source.getOpSize()
                mnemonic = self.opcode
                
                if addr_meth == opcode86.ADDRMETH_E and\
                  not (isinstance(self.source, Register) or\
                       isinstance(self.dest, Register)): 
                    if optype  == opcode86.OPTYPE_b:
                        mnemonic+="b"
                    elif optype== opcode86.OPTYPE_w:
                        mnemonic+=""
                    else :
                        mnemonic+="l"

                ##first="%-06s %s" %  (mnemonic, " " * space)
                post= [self.dest.printOpcode(FORMAT, eip),  self.source.printOpcode(FORMAT, eip)]
                if self.aux:
                    post.append(self.aux.printOpcode(FORMAT, eip))
                #post = "%s, %s" % (self.dest.printOpcode(FORMAT,eip),  self.source.printOpcode(FORMAT, eip))
            elif self.source:
                #second="%-06s %s" %  (mnemonic, " " * space)
                opt = self.getOpcodetype() 
                tmp=""
                if (opt== opcode86.INS_CALL or\
                    opt== opcode86.INS_BRANCH)\
                   and self.source.getAddrMeth() == opcode86.ADDRMETH_E:
                    
                    tmp = "*"
                post=[tmp + self.source.printOpcode(FORMAT, eip)]
                #post += "%s" % self.source.printOpcode(FORMAT, eip)				
            opcode = [mnemonic] + post
            
        return (opcode, self.r, self.w)
    
    def printOpcode(self, FORMAT, eip = 0, space=6):
        opcode=self.getOpcode(FORMAT, eip + self.getSize())
        prefix=self.getPrefix();
        if opcode[0]==0:
            return "invalid"
        if len(opcode) ==2:	
            return "%-08s%s%s" % (prefix+opcode[0], " " * space, opcode[1])
            #return "%-08s%s%s" % (prefix+opcode[0], " " * 6, opcode[1])
        elif len(opcode) ==3:	
            return "%-08s%s%s, %s" % (prefix+opcode[0], " " * space, opcode[1], opcode[2])
            #return "%-08s%s%s, %s" % (prefix+ opcode[0], " " * 6, opcode[1], opcode[2])
        elif len(opcode) ==4:   
            return "%-08s%s%s, %s, %s" % (prefix+opcode[0], " " * space, opcode[3], opcode[1], opcode[2])
        else:
            return "%-08s" % (prefix+opcode[0])		
        return tmp
    def rex(self, f):
        if self.mode != 64:
            return False
        b, w, x, r = False, False, False, False
        for a in self.prefix:
            type = a.getType()
            if type & opcode86.PREFIX_REX:
                if type & opcode86.PREFIX_REXB:
                    b = True
                if type & opcode86.PREFIX_REXW:
                    w = True
                if type & opcode86.PREFIX_REXX:
                    x = True
                if type & opcode86.PREFIX_REXR:
                    r = True

        if f == 'w':
            return w
        if f == 'x':
            return x
        if f == 'b':
            return b
        if f == 'r':
            return r

        return False
            
    def getPrefix(self):
        prefix=""
        for a in self.prefix:
            type = a.getType()
            if type in [opcode86.PREFIX_LOCK, opcode86.PREFIX_REPNZ, opcode86.PREFIX_REP]:
                prefix+= a.getName() + " "
            if self.mode == 64:
                if (type & opcode86.PREFIX_REX):
                    rex = ''
                    if type & opcode86.PREFIX_REXB:
                        rex += 'b'
                    if type & opcode86.PREFIX_REXW:
                        rex += 'w'
                    if type & opcode86.PREFIX_REXX:
                        rex += 'x'
                    if type & opcode86.PREFIX_REXR:
                        rex += 'r'
                    if rex:
                        prefix += 'REX.'+rex+' '
                    else:
                        prefix += 'REX '
        return prefix
if __name__=="__main__":
    # To get this information, just
    import sys
    if len(sys.argv) != 4:
        print ("usage: {} <file> <offset> <size>".format(sys.argv[0]))
        print ("\t file:\t file to disassemble")
        print ("\t offset:\t offset to beggining of code(hexa)")
        print ("\t size:\t amount of bytes to dissasemble (hexa)\n")


        sys.exit(0)
    f=open(sys.argv[1])
    offset= int(sys.argv[2], 16)
    f.seek( offset )
    buf=f.read(int(sys.argv[3], 16) )
    off=0
    FORMAT="AT&T"
    print("Disassembling file %s at offset: 0x%x" % (sys.argv[1], offset))
    while 1:
        try:
                        p=Opcode(buf[off:])
                                                                                
                        print(" %08X:   %s" % (off+offset, p.printOpcode(FORMAT)))
                        off+=p.getSize()
        except ValueError:
             break
