#!/usr/bin/env python3

from riscv_helper_utils import *

import subprocess

XORED_STUDENT_IDS = 123 ^ 456

class Computer:
    def __init__(self):
        self.PC = 0x00000000  # Program Counter
        self.RF = [0] * 32  # Register File (Registers are always stored unsigned)
        self.DMem = [0] * (2**16)  # Data Memory        (each element is 8-bits)
        self.IMem = [0] * (2**14)  # Instruction Memory (each element is 32-bits)
        
    def load_program_from_hex(self, program_hex):
        lines = [line.strip() for line in program_hex.split("\n") if line.strip() != ""]
        im_ptr = 0 #Instruction Memory Pointer
        for line in lines:
            line = line.replace(" ","")
            line = line[6:8]+line[4:6]+line[2:4]+line[0:2] # Reverse byte order
            inst_hex = int(line,16)
            self.IMem[im_ptr//4] = inst_hex
            im_ptr += 4
    
    def compile_from_assembly(self, program_assembly):
        program_hex = riscv_assemble(program_assembly)
        self.load_program_from_hex(program_hex)
        
    def run(self):
        self.PC=0
        instruction = RiscvInstruction()
        while(True):
            inst_hex = self.IMem[self.PC//4]
            if(inst_hex==0x00000000): break
            instruction.fromHex(inst_hex)
            print(f"_{self.PC:02X}: ", end='')
            print(f"{instruction.s:30}", end='')
            instruction.run(self)
            print()
    
    def readData(self, adr, numBytes=4):
        memSize = len(self.DMem)
        readval=0
        for i in range(numBytes):
            readval |= self.DMem[(adr+i)%memSize]<<(8*i)
        return readval
    
    def writeData(self, adr, data, numBytes=4):
        data_str = f"{data:08X}"
        print(f"DataMemory[{adr+numBytes-1}:{adr}] <= 0x{data_str[-2*numBytes:]}", end='')
        memSize = len(self.DMem)
        for i in range(numBytes):
            self.DMem[(adr+i)%memSize] = data & 0xFF
            data = data>>8

    def writeToRF(self, reg, data):
        if(reg==0):
            return
        data=unsigned(data)
        self.RF[reg]=data
        print(f"x{reg} <= 0x{data:08X} = {data}  ", end='')
        if( data & 0x80000000 ): #Number may be signed
            print(f" = {data-(1<<32)} ", end='')



class RiscvInstruction:
    def __init__(self):
        self.h = 0x00000000       #These are meant to be readonly
        self.s = "NOP;"           #These are meant to be readonly
        self.parsed = ["NOP"]       #These are meant to be readonly
    
    def fromHex(self, h):
        self.parsed = RiscvInstruction._parseFromHex(h)
        self.s = RiscvInstruction._generateStr(self.parsed)
        self.h = h
    
    def fromStr(self, s):
        self.parsed = RiscvInstruction._parseFromStr(s)
        self.h = RiscvInstruction._generateHex(self.parsed)
        self.s = s
    
    def run(self, computer):
        RF = computer.RF
        DM = computer.DMem
        mnem = self.parsed["mnem"]
        info = InstructionDatabase[mnem]
        type = info[0]
        if( type in ["B","J"] or mnem=="JALR" ):
            condition=False
            next_PC = 0
            if(mnem == "JAL"):
                computer.writeToRF(self.parsed["rd"], computer.PC+4)
                next_PC = computer.PC + self.parsed["imm"]
                condition=True
            elif(mnem == "JALR"):
                computer.writeToRF(self.parsed["rd"], computer.PC+4)
                next_PC = RF[self.parsed["rs1"]] + self.parsed["imm"]
                condition=True
            else: # Branch
                opr1=RF[self.parsed["rs1"]]
                opr2=RF[self.parsed["rs2"]]
                if(mnem=="BEQ"):   condition=(opr1==opr2)
                elif(mnem=="BNE"): condition=(opr1!=opr2)
                elif(mnem=="BLT"): condition=(signed(opr1)<signed(opr2))
                elif(mnem=="BGE"): condition=(signed(opr1)>=signed(opr2))
                elif(mnem=="BLTU"): condition=(opr1<opr2)
                elif(mnem=="BGEU"): condition=(opr1>=opr2)
                next_PC = computer.PC + self.parsed["imm"]
            if(condition):
                print(f"PC <= 0x{next_PC:08X}", end='')
                computer.PC = next_PC
            else:
                computer.PC += 4
                
        else:
            if( type in ["R","I","I2"] ):
                opr1=RF[self.parsed["rs1"]]
                if(type=="R"):
                    opr2=RF[self.parsed["rs2"]]
                else:
                    opr2=unsigned(self.parsed["imm"])
                if( mnem in ["ADD","ADDI","JALR"] ):result= opr1+opr2
                elif( mnem=="SUB" ):                result= opr1-opr2
                elif( mnem in ["AND","ANDI"] ):     result= opr1&opr2
                elif( mnem in ["OR","ORI"] ):       result= opr1|opr2
                elif( mnem in ["XOR","XORI"] ):     result= opr1^opr2
                elif( mnem in ["SLT","SLTI"] ):     result= int(signed(opr1)<signed(opr2))
                elif( mnem in ["SLTU","SLTIU"] ):   result= int(opr1<opr2)
                elif( mnem in ["SLL","SLLI"] ):     result= opr1<< (opr2 & 0x1F)
                elif( mnem in ["SRL","SRLI"] ):     result= opr1>> (opr2 & 0x1F)
                elif( mnem in ["SRA","SRAI"] ):     result= signed(opr1)>> (opr2 & 0x1F)
                elif( mnem == "LBU" ):              result= computer.readData(opr1+signed(opr2),1)
                elif( mnem == "LHU" ):              result= computer.readData(opr1+signed(opr2),2)
                elif( mnem == "LW" ):               result= computer.readData(opr1+signed(opr2),4)
                elif( mnem == "LB" ):               result= signed(computer.readData(opr1+signed(opr2),1) ,8)
                elif( mnem == "LH" ):               result= signed(computer.readData(opr1+signed(opr2),2) ,16)
                elif( mnem == "XORID" ):            result= opr1^XORED_STUDENT_IDS
                computer.writeToRF(self.parsed["rd"], result)
            
            elif( type == "U" ):
                imm = self.parsed["imm"]
                if( mnem == "LUI" ):     result=imm
                elif( mnem == "AUIPC" ): result=computer.PC+imm
                computer.writeToRF(self.parsed["rd"], result)
            
            elif( type == "S" ):
                opr2 = RF[self.parsed["rs2"]]
                imm = self.parsed["imm"]
                opr1 = RF[self.parsed["rs1"]]
                if( mnem == "SB" ):      computer.writeData(opr1+imm,opr2,1)
                elif( mnem == "SH" ):    computer.writeData(opr1+imm,opr2,2)
                elif( mnem == "SW" ):    computer.writeData(opr1+imm,opr2,4)
                
            computer.PC += 4
    
    
    # Static functions
    def _parseFromHex(h):
        parsed={}
        opcode = getBits(h,6,0)
        funct3 = getBits(h,14,12)
        funct7 = getBits(h,31,25)
        rd = getBits(h,11,7)
        rs1 = getBits(h,19,15)
        rs2 = getBits(h,24,20)
        possibleInstructions = {key:value for key,value in InstructionDatabase.items() if value[1]==opcode}
        matches=[]
        for mnem,value in possibleInstructions.items():
            type = value[0]
            if(type in ["R","I2"]):
                if(value[2]==funct3 and value[3]==funct7):
                    matches.append(mnem)
            elif(type in ["I","S","B"]):
                if(value[2]==funct3):
                    matches.append(mnem)
            elif(type in ["U","J"]):
                matches.append(mnem)
        if(len(matches) != 1):
            raise ValueError(f"Instruction had not 1 match! ({len(matches)} matches)  opcode={opcode} funct3={funct3} funct7={funct7}")
        mnem = matches[0]
        type = possibleInstructions[mnem][0]
        if(type == "R"):
            parsed = {"mnem": mnem, "rd":rd, "rs1":rs1, "rs2":rs2}
        elif(type == "I"):
            imm = getBits(h,31,20)
            parsed = {"mnem": mnem, "rd":rd, "rs1":rs1, "imm":signed(imm,12)}
        elif(type == "I2"):
            imm = getBits(h,24,20)
            parsed = {"mnem": mnem, "rd":rd, "rs1":rs1, "imm":imm}
        elif(type == "S"):
            imm = (getBits(h,31,25)<<5) | \
                   getBits(h,11,7)
            parsed = {"mnem": mnem, "rs1":rs1, "rs2":rs2, "imm":signed(imm,12)}
        elif(type == "B"):
            imm = (getBits(h,31,31)<<12) | \
                   (getBits(h,30,25)<<5) | \
                   (getBits(h,11,8)<<1) | \
                   (getBits(h,7,7)<<11)
            parsed = {"mnem": mnem, "rs1":rs1, "rs2":rs2, "imm":signed(imm,13)}
        elif(type == "U"):
            imm = getBits(h,31,12)<<12
            parsed = {"mnem": mnem, "rd":rd, "imm":imm}
        elif(type == "J"):
            imm = (getBits(h,31,31)<<20) | \
                   (getBits(h,30,21)<<1) | \
                   (getBits(h,20,20)<<11) | \
                   (getBits(h,19,12)<<12)
            parsed = {"mnem": mnem, "rd":rd, "imm":signed(imm,21)}
        return parsed
    
    def _parseFromStr(s):
        s = s.split(";")[0] #Ignore comments after ;
        s = s.split("#")[0] #Ignore comments after #
        s = s.split("//")[0] #Ignore comments after //
        s = s.strip()
        parts = s.split(" ")
        mnemonic = parts[0].upper()
        args = " ".join(parts[1:])
        parsed = []
        if( mnemonic not in InstructionDatabase ):
            return;
        instructionInfo = InstructionDatabase[mnemonic]
        instructionType = instructionInfo[0]
        if(instructionType == "R"):
            rd, rs1, rs2 = args.split(",")
            parsed = {"mnem": mnemonic,  "rd": parseReg(rd), "rs1": parseReg(rs1), "rs2": parseReg(rs2)}
        elif(instructionType in ["I","I2"] ):
            if( mnemonic in ["LB","LH","LW","LBU","LHU","JALR"]): # mnem rd,offset(rs1)
                rd, imm_rs1 = args.split(",")
                imm,rs1 = imm_rs1.split("(")
                rs1 = rs1.replace(")", "")
            else:
                rd, rs1, imm = args.split(",")
            if(instructionType == "I"):
                imm = parseImm(imm,12,0);
            else: # "I2"
                imm = parseImm(imm,5,0,False); # shamt
            parsed = {"mnem": mnemonic, "rd": parseReg(rd), "rs1": parseReg(rs1), "imm": imm}
        elif(instructionType == "S" ):
            rs2, imm_rs1 = args.split(",")
            imm,rs1 = imm_rs1.split("(")
            rs1 = rs1.replace(")", "")
            parsed = {"mnem": mnemonic, "rs1": parseReg(rs1), "rs2": parseReg(rs2), "imm": parseImm(imm,12,0)}
        elif(instructionType == "B" ):
            rs1, rs2, imm = args.split(",")
            parsed = {"mnem": mnemonic, "rs1": parseReg(rs1), "rs2": parseReg(rs2), "imm": parseImm(imm,13,1)}
        elif(instructionType == "U" ):
            rd, imm = args.split(",")
            parsed = {"mnem": mnemonic, "rd": parseReg(rd), "imm": parseImm(imm,20,0, False)<<12} # Imm parsing is modified to be consistent with general consensus
        elif(instructionType == "J" ):
            rd, imm = args.split(",")
            parsed = {"mnem": mnemonic, "rd": parseReg(rd), "imm": parseImm(imm,21,1)}
        
        return parsed
            
    
    def _generateHex(parsed):
        mnem = parsed["mnem"]
        info = InstructionDatabase[mnem]
        type = info[0]
        binary = 0x00000000
        
        if("rd" in parsed):
            binary |= parsed["rd"]<<7
        if("rs1" in parsed):
            binary |= parsed["rs1"]<<15
        if("rs2" in parsed):
            binary |= parsed["rs2"]<<20
        if(len(info)>1):
            binary |= info[1] #opcode
        if(len(info)>2):
            binary |= info[2]<<12  #funct3
        if(len(info)>3):
            binary |= info[3]<<25  #funct7
            
        # Only immediates are left
        if("imm" in parsed):
            imm = parsed["imm"]
            if(type in ["I","I2"]):
                imm=imm%(1<<12)  # To fix negatives
                binary |= imm<<20
            elif(type == "S"):
                imm=imm%(1<<12)  # To fix negatives
                binary |= getBits(imm,11,5)<<25
                binary |= getBits(imm,4,0)<<7
            elif(type == "B"):
                imm=imm%(1<<13)  # To fix negatives
                binary |= getBits(imm,12,12)<<31
                binary |= getBits(imm,10,5)<<25
                binary |= getBits(imm,4,1)<<8
                binary |= getBits(imm,11,11)<<7
            elif(type == "U"):
                imm=imm%(1<<32)  # To fix negatives
                binary |= getBits(imm,31,12)<<12
            elif(type == "J"):
                imm=imm%(1<<32)  # To fix negatives
                binary |= getBits(imm,20,20)<<31
                binary |= getBits(imm,10,1)<<21
                binary |= getBits(imm,11,11)<<20
                binary |= getBits(imm,19,12)<<12
                
        
        return binary
    
    def _generateStr(parsed):
        mnem = parsed["mnem"]
        info = InstructionDatabase[mnem]
        type = info[0]
        instruction_str=mnem.lower() + (" "*(8-len(mnem)))
        if(type=="R"):
            instruction_str += f"x{parsed['rd']}, x{parsed['rs1']}, x{parsed['rs2']}"
        elif(type=="I"):
            if( mnem in ["LB","LH","LW","LBU","LHU","JALR"]): 
                instruction_str += f"x{parsed['rd']}, {num2str(parsed['imm'])}(x{parsed['rs1']})"
            else:
                instruction_str += f"x{parsed['rd']}, x{parsed['rs1']}, {num2str(parsed['imm'])}"
            
        elif(type=="I2"):
            instruction_str += f"x{parsed['rd']}, x{parsed['rs1']}, {parsed['imm']}"
        elif(type=="S"):
            instruction_str += f"x{parsed['rs2']}, {num2str(parsed['imm'])}(x{parsed['rs1']})"
        elif(type=="B"):
            instruction_str += f"x{parsed['rs1']}, x{parsed['rs2']}, {num2str(parsed['imm'])}"
        elif(type=="U"):
            instruction_str += f"x{parsed['rd']}, {num2str(parsed['imm']>>12)}"   # Imm parsing is modified to be consistent with general consensus
        elif(type=="J"):
            instruction_str += f"x{parsed['rd']}, {num2str(parsed['imm'])}"
        return instruction_str




def riscv_assemble(assembly_str):
    lines = assembly_str.split("\n")
    response_str=""
    r = RiscvInstruction()
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

def riscv_disassemble(hex_str):
    lines = hex_str.split("\n")
    response_str=""
    r = RiscvInstruction()
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







"""
Use riscv64-linux-gnu-gcc and riscv64-linux-gnu-ld to compile and dissassemble the code

def run_make():
    result = subprocess.run(['make'], capture_output=True, text=True)
    if result.returncode == 0:
        print("Make command executed successfully!")
        print("Output:\n", result.stdout)
        return True
    else:
        print("Error in make command:")
        print(result.stderr)
        return False

def riscv_assemble(assembly_str):
    with open("sample.s", 'w') as file:
        file.write(assembly_str)
    if(not run_make()):
        return "An eror occured"
    with open("dissassembly.txt", 'r') as file:
        content = file.read()
    before, after = content.split("Disassembly of section .text:\n")
    return after

"""
