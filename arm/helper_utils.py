#!/usr/bin/env python3


RegisterMap = {
    "r0" : 0,
    "r1" : 1,
    "r2" : 2,
    "r3" : 3,
    "r4" : 4,
    "r5" : 5,
    "r6" : 6,
    "r7" : 7,
    "r8" : 8,
    "r9" : 9,
    "r10" : 10,
    "r11" : 11,
    "r12" : 12,
    "r13" : 13,
    "r14" : 14,
    "r15" : 15,
    "sp" : 13,
    "lr" : 14,
    "pc" : 15,
}

InstructionDatabase = {
    "ADD": {"op":0b00, "cmd": 0b0100},
    "SUB": {"op":0b00, "cmd": 0b0010},
    "AND": {"op":0b00, "cmd": 0b0000},
    "ORR": {"op":0b00, "cmd": 0b1100},
    "MOV": {"op":0b00, "cmd": 0b1101},
    "CMP": {"op":0b00, "cmd": 0b1010},

    "STR": {"op":0b01},
    "LDR": {"op":0b01},

    "B":  {"op":0b10},
    "BL": {"op":0b10},
    "BX": {"op":0b10}
}

ConditionCodes = {
    "EQ": [0b0000, lambda N,Z,C,V: (Z) ],
    "NE": [0b0001, lambda N,Z,C,V: (not Z) ],
    "CS": [0b0010, lambda N,Z,C,V: (C) ],
    "CC": [0b0011, lambda N,Z,C,V: (not C) ],

    "MI": [0b0100, lambda N,Z,C,V: (N) ],
    "PL": [0b0101, lambda N,Z,C,V: (not N) ],
    "VS": [0b0110, lambda N,Z,C,V: (V) ],
    "VC": [0b0111, lambda N,Z,C,V: (not V) ],

    "HI": [0b1000, lambda N,Z,C,V: (C and (not Z)) ],
    "LS": [0b1001, lambda N,Z,C,V: ((not C) and Z) ],
    "GE": [0b1010, lambda N,Z,C,V: (N == V) ],
    "LT": [0b1011, lambda N,Z,C,V: (N != V) ],

    "GT": [0b1100, lambda N,Z,C,V: ((not Z) and (N==V)) ],
    "LE": [0b1101, lambda N,Z,C,V: (Z or (N!=V)) ],
    "AL": [0b1110, lambda N,Z,C,V: (True) ]
}
ConditionCodes[""] = ConditionCodes["AL"]

# Generate all possible instruction combinations
def generateAllVariants():
    variants0  = {a + b + c: [a, b, c] for a in InstructionDatabase if InstructionDatabase[a]["op"]==0b00 for b in ConditionCodes for c in ["","S"]}  #DP Instruction variants
    variants1  = {a + b + c: [a, b, c] for a in InstructionDatabase if InstructionDatabase[a]["op"]==0b01 for b in ConditionCodes for c in ["","S"]}  #Memory Instruction variants
    variants2  = {a + b    : [a, b   ] for a in InstructionDatabase if InstructionDatabase[a]["op"]==0b10 for b in ConditionCodes}  #Branch Instruction variants
    return {**variants0, **variants1, **variants2}

AllInstructionVariants = generateAllVariants()


def parseReg(regString):
    return RegisterMap[regString.lower().strip()]


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



