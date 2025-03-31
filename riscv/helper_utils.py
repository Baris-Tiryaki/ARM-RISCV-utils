#!/usr/bin/env python3

# https://msyksphinz-self.github.io/riscv-isadoc/html/rvi.html

"""       1       2       3
"R":    [6:0], [14:12], [31:25]     rd,rs1,rs2
"I":    [6:0], [14:12]              rd,rs1,imm
"I2":   [6:0], [14:12], [31:25]     rd,rs1,shamt
"S":    [6:0], [14:12]              rs2,offset(rs1)
"B":    [6:0], [14:12]              rs1,rs2,offset
"U":    [6:0]                       rd,imm
"J":    [6:0]                       rd,offset
"""

class Opcodes:
    OP_IMM= 0b00_100_11
    OP=     0b01_100_11
    LOAD=   0b00_000_11
    STORE=  0b01_000_11
    BRANCH= 0b11_000_11
    JAL=    0b11_011_11
    JALR=   0b11_001_11
    AUIPC=  0b00_101_11
    LUI=    0b01_101_11
    XORID=  0b0001011
    HALT=   0b0000000


InstructionDatabase = {
    "HALT": ["U", Opcodes.HALT],
    
    "ADDI": ["I", Opcodes.OP_IMM, 0b000],
    "SLTI": ["I", Opcodes.OP_IMM, 0b010],
    "SLTIU":["I", Opcodes.OP_IMM, 0b011],
    "ANDI": ["I", Opcodes.OP_IMM, 0b111],
    "ORI":  ["I", Opcodes.OP_IMM, 0b110],
    "XORI": ["I", Opcodes.OP_IMM, 0b100],
    "XORID": ["I", Opcodes.XORID, 0b100],
    
    "SLLI": ["I2", Opcodes.OP_IMM, 0b001, 0b000_0000],
    "SRLI": ["I2", Opcodes.OP_IMM, 0b101, 0b000_0000],
    "SRAI": ["I2", Opcodes.OP_IMM, 0b101, 0b010_0000],
    
    "LUI":  ["U", Opcodes.LUI],
    "AUIPC":["U", Opcodes.AUIPC],
    
    "ADD":  ["R", Opcodes.OP, 0b000, 0b000_0000],
    "SLT":  ["R", Opcodes.OP, 0b010, 0b000_0000],
    "SLTU": ["R", Opcodes.OP, 0b011, 0b000_0000],
    "AND":  ["R", Opcodes.OP, 0b111, 0b000_0000],
    "OR":   ["R", Opcodes.OP, 0b110, 0b000_0000],
    "XOR":  ["R", Opcodes.OP, 0b100, 0b000_0000],
    "SLL":  ["R", Opcodes.OP, 0b001, 0b000_0000],
    "SRL":  ["R", Opcodes.OP, 0b101, 0b000_0000],
    "SUB":  ["R", Opcodes.OP, 0b000, 0b010_0000],
    "SRA":  ["R", Opcodes.OP, 0b101, 0b010_0000],
    
    "JAL":  ["J", Opcodes.JAL],
    "JALR": ["I", Opcodes.JALR, 0b000],
    
    "BEQ":  ["B", Opcodes.BRANCH, 0b000],
    "BNE":  ["B", Opcodes.BRANCH, 0b001],
    "BLT":  ["B", Opcodes.BRANCH, 0b100],
    "BLTU": ["B", Opcodes.BRANCH, 0b110],
    "BGE":  ["B", Opcodes.BRANCH, 0b101],
    "BGEU": ["B", Opcodes.BRANCH, 0b111],
    
    "LB":   ["I", Opcodes.LOAD, 0b000],
    "LH":   ["I", Opcodes.LOAD, 0b001],
    "LW":   ["I", Opcodes.LOAD, 0b010],
    "LBU":  ["I", Opcodes.LOAD, 0b100],
    "LHU":  ["I", Opcodes.LOAD, 0b101],
    
    "SB":   ["S", Opcodes.STORE, 0b000],
    "SH":   ["S", Opcodes.STORE, 0b001],
    "SW":   ["S", Opcodes.STORE, 0b010],
}


PseudoInstructions = { # https://github.com/riscv-non-isa/riscv-asm-manual/blob/main/riscv-asm.md
    "NOP", "MV", "NOT", "NEG", "BLTE", "BLTEU", "BGT", "BGTU", "J", "BranchZ", "LI"
}


RegisterMap = {
    "x0" : 0,
    "x1" : 1,
    "x2" : 2,
    "x3" : 3,
    "x4" : 4,
    "x5" : 5,
    "x6" : 6,
    "x7" : 7,
    "x8" : 8,
    "x9" : 9,
    "x10" : 10,
    "x11" : 11,
    "x12" : 12,
    "x13" : 13,
    "x14" : 14,
    "x15" : 15,
    "x16" : 16,
    "x17" : 17,
    "x18" : 18,
    "x19" : 19,
    "x20" : 20,
    "x21" : 21,
    "x22" : 22,
    "x23" : 23,
    "x24" : 24,
    "x25" : 25,
    "x26" : 26,
    "x27" : 27,
    "x28" : 28,
    "x29" : 29,
    "x30" : 30,
    "x31" : 31,
    
    "zero" : 0,
    "ra" : 1,
    "sp" : 2,
    "gp" : 3,
    "tp" : 4,
    "t0" : 5,
    "t1" : 6,
    "t2" : 7,
    "fp" : 8,
    "s0" : 8,
    "s1" : 9,
    "a0" : 10,
    "a1" : 11,
    "a2" : 12,
    "a3" : 13,
    "a4" : 14,
    "a5" : 15,
    "a6" : 16,
    "a7" : 17,
    "s2" : 18,
    "s3" : 19,
    "s4" : 20,
    "s5" : 21,
    "s6" : 22,
    "s7" : 23,
    "s8" : 24,
    "s9" : 25,
    "s10" : 26,
    "s11" : 27,
    "t3" : 28,
    "t4" : 29,
    "t5" : 30,
    "t6" : 31,
}



def parseReg(regString):
    return RegisterMap[regString.lower().strip()]

def parseImm(immString, hiBit=32, loBit=0, signed=True):
    value = int(immString, 0)
    if(not signed and value<0):
        raise ValueError('Immediate value error: It should not be negative')
    if( (value & ((1<<loBit)-1)) != 0):
        raise ValueError(f'Immediate value error: Last {loBit} bits must be 0')
    if(not signed and value>=(1<<hiBit) ):
        raise ValueError(f"Immediate value error: Unsigned value doesn't fit to {hiBit} bits")
    if(signed and (value>=(1<<(hiBit-1)) or (value<-(1<<(hiBit-1)) ) ) ):
        raise ValueError(f"Immediate value error: Signed value doesn't fit to {hiBit} bits")
    #if(signed and value<0):
    #    value += 1<<hiBit
    return value

def num2str(num):
    if(num<1000 and num>-1000):
        return str(num)
    else:
        if(num<0):
            return f"-0x{-num:X}"
        else:
            return f"0x{num:X}"
    
def signed(value, bitlen=32):
    if( (value>>(bitlen-1)) > 0 ):
        value -= 1<<(bitlen)
    return value

def unsigned(value, bitlen=32):
    return value % (1<<bitlen)

def getBits(num, high, low):
    num = num & ( ( 1<<(high+1) )-1 )
    return num>>low

def num2Hex(num):
    hex_str=f"{num:08x}"
    #hex_str = hex_str[::-1]
    hex_str = hex_str[0:4] + "_" + hex_str[4:8]
    return "0x"+hex_str



