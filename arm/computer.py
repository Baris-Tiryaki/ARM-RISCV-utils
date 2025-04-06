#!/usr/bin/env python3

from arm.helper_utils import *

class Computer:
    def __init__(self):
        pass

class ArmInstruction:
    def __init__(self):
        self.h = 0x00000000       #Readonly value
        self.s = "NOP;"           #Readonly value
        self.parsed = ["NOP"]     #Readonly value

    def fromHex(self, h):
        self.parsed = ArmInstruction._parseFromHex(h)
        self.s = ArmInstruction._generateStr(self.parsed)
        self.h = h
    
    def fromStr(self, s):
        self.parsed = ArmInstruction._parseFromStr(s)
        self.h = ArmInstruction._generateHex(self.parsed)
        self.s = s
    
    def _parseFromStr(s):
        s = s.split(";")[0] #Ignore comments after ;
        s = s.split("//")[0] #Ignore comments after //
        s = s.strip()
        parts = s.split(" ")
        mnemonic = parts[0].upper()
        args = " ".join(parts[1:])
        parsed = []
        if( mnemonic not in AllInstructionVariants ):
            return;
        variantInfo = AllInstructionVariants[mnemonic]
        mainpart = variantInfo[0]
        cond = variantInfo[1]
        S = (len(variantInfo)>=3 and variantInfo[2]=="S")
        instructionInfo = InstructionDatabase[mainpart]
        op = instructionInfo["op"]
        if(op == 0b00):  # To be continued ...
            rd, rs1, rs2 = args.split(",")
            parsed = {"mnem": mnemonic,  "rd": parseReg(rd), "rs1": parseReg(rs1), "rs2": parseReg(rs2)}
        elif(op == 0b01 ):
            parsed = {"mnem": mnemonic, "rd": parseReg(rd), "rs1": parseReg(rs1), "imm": imm}
        elif(op == 0b10 ):

        return parsed
            


def assemble(assembly_str):
    lines = assembly_str.split("\n")
    response_str=""
    r = ArmInstruction()
    for line in lines:
        line=line.split(":")[-1]
        line=line.strip()
        if( len(line) == 0 ):
            response_str += "\n"
            continue
        try:
            r.fromStr(line)
            hex_str = f"{r.h:08X}"
            hex_str = hex_str[6:8]+" "+hex_str[4:6]+" "+hex_str[2:4]+" "+hex_str[0:2] # Reverse byte order
            response_str += f"{hex_str}\n"
        except Exception as e:
            response_str += f"ERROR\n"
            print(f"Exception occured: {e}")
    return response_str[:-1]

def disassemble(hex_str):
    lines = hex_str.split("\n")
    response_str=""
    r = ArmInstruction()
    address=0
    for line in lines:
        line=line.strip()
        line=line.replace("_","").replace(" ","")
        if( len(line) == 0 ):
            response_str += "\n"
            continue
        response_str += f"_{address:02X}: "
        address += 4
        if( len(line) != 8 ):
            response_str += "ERROR\n"
            continue
        try:
            line = line[6:8]+line[4:6]+line[2:4]+line[0:2] # Reverse byte order
            inst_hex = int(line,16)
            r.fromHex(inst_hex)
            response_str += f"{r.s}\n"
        except Exception as e:
            response_str += f"ERROR\n"
            print(f"Exception occured: {e}")
    return response_str[:-1]

if __name__ == "__main__":
    with open("session_instr.s","r") as f:
        sample_code=f.read()
    comp = Computer()
    comp.compile_from_assembly(sample_code)
    comp.run()


