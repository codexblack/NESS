# import necessary libraries
import numpy as np
from functools import partial

# Little endian CPU, lower bytes will have lower address in memory
class CPU6502:

    def __init__(self, ram):
        self.f = open('log.txt', 'w')
        self.counter = 0
        # lord forgive me for what I am about to do
        # contains the required clock cycles for ALL operations :))))
        # extra clock cycles will be added in the respective methods
        # Internal ram of size 2kiB, from $0000 to $07FF, and is mirrored
        self.memory = ram
        self.cycles_counter = 27664  # Number of clock cycles per frame @60.10 FPS
        self.cycles = {
            0x00: 7, 0x01: 6, 0x05: 3, 0x06: 5, 0x08: 3, 0x09: 2, 0x0A: 2, 0x0D: 4, 0x0E: 6, 0x10: 2, 0x11: 5, 0x15: 4, 0x16: 6, 0x18: 2, 0x19: 4, 0x1D: 4, 0x1E: 7, 0x20: 6, 0x21: 6, 0x24: 3, 0x25: 3, 0x26: 5, 0x28: 4, 0x29: 2,
            0x2A: 2, 0x2C: 4, 0x2D: 4, 0x2E: 6, 0x30: 2, 0x31: 5, 0x35: 4, 0x36: 6, 0x38: 2, 0x39: 4, 0x3D: 4, 0x3E: 7, 0x40: 6, 0x41: 6, 0x45: 3, 0x46: 5, 0x48: 3, 0x49: 2, 0x4A: 2, 0x4C: 3, 0x4D: 4, 0x4E: 6, 0x50: 2, 0x51: 5,
            0x55: 4, 0x56: 6, 0x58: 2, 0x59: 4, 0x5D: 4, 0x5E: 7, 0x60: 6, 0x61: 6, 0x65: 3, 0x66: 5, 0x68: 4, 0x69: 2, 0x6A: 2, 0x6C: 5, 0x6D: 4, 0x6E: 6, 0x70: 2, 0x71: 5, 0x75: 4, 0x76: 6, 0x78: 2, 0x79: 4, 0x7D: 4, 0x7E: 7,
            0x81: 6, 0x84: 3, 0x85: 3, 0x86: 3, 0x88: 2, 0x8A: 2, 0x8C: 4, 0x8D: 4, 0x8E: 4, 0x90: 2, 0x91: 6, 0x94: 4, 0x95: 4, 0x96: 4, 0x98: 2, 0x99: 5, 0x9A: 2, 0x9D: 5, 0xA0: 2, 0xA1: 6, 0xA2: 2, 0xA4: 3, 0xA5: 3, 0xA6: 3, 0xA8: 2,
            0xA9: 2, 0xAA: 2, 0xAC: 4, 0xAD: 4, 0xAE: 4, 0xB0: 2, 0xB1: 5, 0xB4: 4, 0xB5: 4, 0xB6: 4, 0xB8: 2, 0xB9: 4, 0xBA: 2, 0xBC: 4, 0xBD: 4, 0xBE: 4, 0xC0: 2, 0xC1: 6, 0xC4: 3, 0xC5: 3, 0xC6: 5, 0xC8: 2, 0xC9: 2, 0xCA: 2,
            0xCC: 4, 0xCD: 4, 0xCE: 6, 0xD0: 2, 0xD1: 5, 0xD5: 4, 0xD6: 6, 0xD8: 2, 0xD9: 4, 0xDD: 4, 0xDE: 7, 0xE0: 2, 0xE1: 6, 0xE4: 3, 0xE5: 3, 0xE6: 5, 0xE8: 2, 0xE9: 2, 0xEA: 2, 0xEC: 4, 0xED: 4, 0xEE: 6, 0xF0: 2, 0xF1: 5,
            0xF5: 4, 0xF6: 6, 0xF8: 2, 0xF9: 4, 0xFD: 4, 0xFE: 7
        }
        # dict to store all our lovely instructions 
        self.switch = {
                0x00: self.BRK, 0x01: partial(self.ORA, self.IZX), 0x05: partial(self.ORA, self.ZPO),
                0x06: partial(self.ASL, self.ZPO), 0x08: self.PHP, 0x09: partial(self.ORA, self.IMM),
                0x0A: partial(self.ASL, self.ACC), 0x0D: partial(self.ORA, self.ABS), 0x0E: partial(self.ASL, self.ABS),
                0x10: partial(self.BPL, self.REL), 0x11: partial(self.ORA, self.IZY), 0x15: partial(self.ORA, self.ZPX),
                0x16: partial(self.ASL, self.ZPX), 0x18: self.CLC, 0x19: partial(self.ORA, self.ABY), 0x1D: partial(self.ORA, self.ABX),
                0x1E: partial(self.ASL, self.ABX), 0x20: partial(self.JSR, self.ABS), 0x21: partial(self.AND, self.IZX),
                0x24: partial(self.BIT, self.ZPO), 0x25: partial(self.AND, self.ZPO), 0x26: partial(self.ROL, self.ZPO),
                0x28: self.PLP, 0x29: partial(self.AND, self.IMM),
                0x2A: partial(self.ROL, self.ACC), 0x2C: partial(self.BIT, self.ABS), 0x2D: partial(self.AND, self.ABS),
                0x2E: partial(self.ROL, self.ABS), 0x30: partial(self.BMI, self.REL),
                0x31: partial(self.AND, self.IZY), 0x35: partial(self.AND, self.ZPX), 0x36: partial(self.ROL, self.ZPX),
                0x38: self.SEC,
                0x39: partial(self.AND, self.ABY), 0x3D: partial(self.AND, self.ABX), 0x3E: partial(self.ROL, self.ABX),
                0x40: self.RTI, 0x41: partial(self.EOR, self.IZX), 0x45: partial(self.EOR, self.ZPO),
                0x46: partial(self.LSR, self.ZPO),
                0x48: self.PHA, 0x49: partial(self.EOR, self.IMM), 0x4A: partial(self.LSR, self.ACC), 0x4C: partial(self.JMP, self.ABS),
                0x4D: partial(self.EOR, self.ABS), 0x4E: partial(self.LSR, self.ABS), 0x50: partial(self.BVC, self.REL),
                0x51: partial(self.EOR, self.IZY),
                0x55: partial(self.EOR, self.ZPX), 0x56: partial(self.LSR, self.ZPX), 0x58: self.CLI, 0x59: partial(self.EOR, self.ABY),
                0x5D: partial(self.EOR, self.ABX), 0x5E: partial(self.LSR, self.ABX), 0x60: self.RTS, 0x61: partial(self.ADC, self.IZX),
                0x65: partial(self.ADC, self.ZPO), 0x66: partial(self.ROR, self.ZPO), 0x68: self.PLA, 0x69: partial(self.ADC, self.IMM),
                0x6A: partial(self.ROR, self.ACC), 0x6C: partial(self.JMP, self.IND), 0x6D: partial(self.ADC, self.ABS),
                0x6E: partial(self.ROR, self.ABS),
                0x70: partial(self.BVS, self.REL), 0x71: partial(self.ADC, self.IZY), 0x75: partial(self.ADC, self.ZPX),
                0x76: partial(self.ROR, self.ZPX),
                0x78: self.SEI, 0x79: partial(self.ADC, self.ABY), 0x7D: partial(self.ADC, self.ABX), 0x7E: partial(self.ROR, self.ABX),
                0x81: partial(self.STA, self.IZX), 0x84: partial(self.STY, self.ZPO), 0x85: partial(self.STA, self.ZPO),
                0x86: partial(self.STX, self.ZPO),
                0x88: self.DEY, 0x8A: self.TXA, 0x8C: partial(self.STY, self.ABS), 0x8D: partial(self.STA, self.ABS), 0x8E: partial(self.STX, self.ABS),
                0x90: partial(self.BCC, self.REL), 0x91: partial(self.STA, self.IZY), 0x94: partial(self.STY, self.ZPX), 
                0x95: partial(self.STA, self.ZPX),
                0x96: partial(self.STX, self.ZPY), 0x98: self.TYA, 0x99: partial(self.STA, self.ABY), 0x9A: self.TXS,
                0x9D: partial(self.STA, self.ABX), 0xA0: partial(self.LDY, self.IMM), 0xA1: partial(self.LDA, self.IZX), 
                0xA2: partial(self.LDX, self.IMM),
                0xA4: partial(self.LDY, self.ZPO), 0xA5: partial(self.LDA, self.ZPO), 0xA6: partial(self.LDX, self.ZPO), 0xA8: self.TAY,
                0xA9: partial(self.LDA, self.IMM), 0xAA: self.TAX, 0xAC: partial(self.LDY, self.ABS), 0xAD: partial(self.LDA, self.ABS),
                0xAE: partial(self.LDX, self.ABS), 0xB0: partial(self.BCS, self.REL), 0xB1: partial(self.LDA, self.IZY), 
                0xB4: partial(self.LDY, self.ZPX),
                0xB5: partial(self.LDA, self.ZPX), 0xB6: partial(self.LDX, self.ZPY), 0xB8: self.CLV, 0xB9: partial(self.LDA, self.ABY),
                0xBA: self.TSX, 0xBC: partial(self.LDY, self.ABX), 0xBD: partial(self.LDA, self.ABX), 0xBE: partial(self.LDX, self.ABY),
                0xC0: partial(self.CPY, self.IMM), 0xC1: partial(self.CMP, self.IZX), 0xC4: partial(self.CPY, self.ZPO), 
                0xC5: partial(self.CMP, self.ZPO),
                0xC6: partial(self.DEC, self.ZPO), 0xC8: self.INY, 0xC9: partial(self.CMP, self.IMM), 0xCA: self.DEX,
                0xCC: partial(self.CPY, self.ABS), 0xCD: partial(self.CMP, self.ABS), 0xCE: partial(self.DEC, self.ABS), 
                0xD0: partial(self.BNE, self.REL),
                0xD1: partial(self.CMP, self.IZY), 0xD5: partial(self.CMP, self.ZPX), 0xD6: partial(self.DEC, self.ZPX), 0xD8: self.CLD,
                0xD9: partial(self.CMP, self.ABY), 0xDD: partial(self.CMP, self.ABX), 0xDE: partial(self.DEC, self.ABX), 
                0xE0: partial(self.CPX, self.IMM),
                0xE1: partial(self.SBC, self.IZX), 0xE4: partial(self.CPX, self.ZPO), 0xE5: partial(self.SBC, self.ZPO), 
                0xE6: partial(self.INC, self.ZPO),
                0xE8: self.INX, 0xE9: partial(self.SBC, self.IMM), 0xEA: self.NOP, 0xEC: partial(self.CPX, self.ABS),
                0xED: partial(self.SBC, self.ABS), 0xEE: partial(self.INC, self.ABS), 0xF0: partial(self.BEQ, self.REL), 
                0xF1: partial(self.SBC, self.IZY),
                0xF5: partial(self.SBC, self.ZPX), 0xF6: partial(self.INC, self.ZPX), 0xF8: self.SED, 0xF9: partial(self.SBC, self.ABY),
                0xFD: partial(self.SBC, self.ABX), 0xFE: partial(self.INC, self.ABX)
            }  
        # 16-bit program counter
        self.pc = 0xC000  # programs are loaded into memory starting 0x0600
        # stack pointer (grows downward) $01FF to $0100
        self.sp = 0xFD
        # 8-bit staus code
        # 0 -> Carry                            C
        # 1 -> Zero                             Z
        # 2 -> Interrupt Disable                I
        # 3 -> Decimal Mode (Unused in NES)     D
        # 4 -> Break                            B
        # 5 -> Unused                           -
        # 6 -> Overflow                         V
        # 7 -> Negative                         N
        self.status_code = 0x24  # Unused bit is set to 1 by default, and I is set to 1 on startup
        # We have 3 8-bit registers
        # 8-bit register X
        self.X = 0x00
        # 8-bit register Y
        self.Y = 0x00
        # 8-bit accumulator
        self.A = 0x00
        # Set to True when an operation needs an extra clock cycle to execute
        self.extra_cycle: np.short = 0

    def execute(self):
        while(self.cycles_counter >= 0):
            # reset some variables
            self.counter += 1
            self.extra_cycle = 0x00
            #---------------------
            # nestest
            #self.f.write('--------{}--------- \n'.format(self.counter))
            # self.f.write('2h: {}  3h: {} \n'.format(hex(self.read_memory(0x02)), hex(self.read_memory(0x03))))
            #self.f.write('A:{} X:{} Y:{} \n'.format(hex(self.A), hex(self.X), hex(self.Y)))
            #self.f.write('PC:{} SP:{} P:{} \n'.format(hex(self.pc), hex(self.sp), hex(self.status_code)))
            #---------------------
            op_code = self.read_memory(self.pc)
            self.set_status_bit(5, 1)
            self.pc += 1
            # Actual execution
            self.switch.get(op_code, self.UNK)()
            self.cycles_counter -= (self.cycles[op_code] + self.extra_cycle)
            self.set_status_bit(5, 1)
        self.cycles_counter += 27664

    # Resets
    def reset(self):
        # Set pc address
        self.pc = np.uint16((self.read_memory(0xFFFC) << 8) | self.read_memory(0xFFFD))
        # Reset all registers
        self.A = 0x00
        self.X = 0x00
        self.Y = 0x00
        self.sp = 0xFD
        self.status_code = 0x24
        # Add 8 cycles needed for reset
        self.cycles_counter -= 8

    def irq(self):
        if ((self.status_code >> 2) & 0x01):
            # Push PC onto the stack
            self.stack_push(np.uint8(self.pc >> 8))
            self.stack_push(np.uint8(self.pc & 0xFF))
            # Push status codes to the stack
            self.set_status_bit(4, 0)
            self.set_status_bit(5, 1)
            self.set_status_bit(2, 1)
            self.stack_push(self.status_code)
            # Get the new PC
            self.pc = np.uint16((self.memory_read(0xFFFE) << 8) | self.memory_read(0xFFFF))
            # Add number of cycles needed
            self.cycles_counter -=8

    def nmi(self):
        # Push PC onto the stack
        self.stack_push(np.uint8(self.pc >> 8))
        self.stack_push(np.uint8(self.pc & 0xFF))
        # Push status codes to the stack
        self.set_status_bit(4, 0)
        self.set_status_bit(5, 1)
        self.set_status_bit(2, 1)
        self.stack_push(self.status_code)
        # Get the new PC
        self.pc = np.uint16((self.memory_read(0xFFFA) << 8) | self.memory_read(0xFFFB))
        # Add number of cycles needed
        self.cycles_counter -=8

    # Helper functions
    def set_status_bit(self, bit, condition):
        mask = 1 << bit
        self.status_code &= ~mask
        if condition:
            self.status_code |= mask

    def clear_status_bit(self, bit, condition):
        self.status_code &= ~(condition << bit)

    def stack_push(self, value):
        self.write_memory(((1 << 8) | self.sp), value)
        self.sp = np.uint8(self.sp - 1)

    def stack_pop(self):
        self.sp = np.uint8(self.sp + 1)
        return self.read_memory(((1 << 8) | self.sp))

    # &'ing address with 0x07FF helps us account for mirroring of the RAM
    # which is only 2KiB in size, from range $0800 to $1FFF
    # The PPU registers are also mirrored every 8 bytes originally 
    # ranging from $2000 to $2007, mirrored till $3FFF
    def read_memory(self, address):
        return self.memory.read(address)

    def write_memory(self, address, value):
        self.memory.write(address, value)
    # Addressing modes
    def ACC(self):
        # Accumulator is set as target for operation
        return self.A

    def IMM(self):
        # gets the value of the next byte after the opcode
        # here, this byte will be a value as opposed to being an address
        self.pc += 1
        return self.pc - 1

    def ZPO(self):
        # Access the lower 256 bytes of memory
        # AKA all offsets of page zero of the CPU memory
        addr = self.read_memory(self.pc)
        self.pc += 1
        return addr & 0x00FF

    def ZPX(self):
        # Offsets the zero page address by what is stored in register X
        addr = self.read_memory(self.pc) + self.X
        self.pc += 1
        return addr & 0x00FF

    def ZPY(self):
        # Offsets the zero page address by what is stored in register Y
        addr = self.read_memory(self.pc) + self.Y
        self.pc += 1
        return addr & 0x00FF

    def REL(self):
        # Used for branching
        # New address is current PC + branch offset (signed)
        branch_offset = self.read_memory(self.pc)
        self.pc += 1
        # check if signed number
        if branch_offset & 0x80:
            branch_offset |= 0xFF00
        return branch_offset

    def ABS(self):
        # Gets full 16-bit address from the next two bytes after the opcode
        page = self.read_memory(self.pc + 1) << 8
        offset = self.read_memory(self.pc)
        self.pc += 2
        return (page | offset)

    def ABX(self):
        # Offsets absolute address by what is in register X
        page = self.read_memory(self.pc + 1) << 8
        offset = self.read_memory(self.pc)
        self.pc += 2
        full_addy = (page | offset) + self.X
        # Adjust for extra clock cycle
        self.extra_cycle = ((full_addy & 0xFF00) == (page))
        return full_addy

    def ABY(self):
        # Offsets absolute address by what is in register Y
        page = self.read_memory(self.pc + 1) << 8
        offset = self.read_memory(self.pc)
        self.pc += 2
        full_addy = (page | offset) + self.Y
        # Adjust for extra clock cycle
        self.extra_cycle = ((full_addy & 0xFF00) == (page))
        return np.uint16(full_addy)

    def IND(self):
        # 2nd and 3rd bytes of the instruction point to a location in memory
        # the PC will be set to the address stored in those memory locations
        page = self.read_memory(self.pc + 1) << 8
        offset = self.read_memory(self.pc)
        full_addy = np.uint16(page | offset)
        # There is a bug here in the original 6502
        # if the low byte is FF, MSB fetches from address XX00 instead of XX+1
        pc_lo = self.read_memory(full_addy)
        pc_hi = (offset == 0x00FF and (self.read_memory(full_addy & 0xFF00) << 8) or
                 (self.read_memory(full_addy + 1) << 8))
        return np.uint16(pc_hi | pc_lo)

    def IZX(self):
        # IND but with zero page and X offset
        zero_page = self.read_memory(self.pc)
        self.pc += 1
        lsb = self.read_memory((zero_page + self.X) & 0x00FF)
        msb = self.read_memory((zero_page + 1 + self.X) & 0x00FF) << 8
        address = (msb | lsb)
        # Adjust for extra clock cycle
        self.extra_cycle = (address & 0xFF00) == (msb)
        return address

    def IZY(self):
        # IND but with zero page and Y offset
        zero_page = self.read_memory(self.pc)
        self.pc += 1
        lsb = self.read_memory((zero_page) & 0x00FF)
        msb = self.read_memory((zero_page + 1) & 0x00FF) << 8
        address = (msb | lsb) + self.Y
        # Adjust for extra clock cycle
        self.extra_cycle = (address & 0xFF00) == (msb)
        return np.uint16(address)

    # OpCodes... all typed by hand :,)

    def ADC(self, ad_mode):
        address = ad_mode()
        operand = self.read_memory(address)
        total = self.A + (self.status_code & 0x01) + operand
        self.set_status_bit(0, total > 0x00FF)  # set Carry bit
        # Set overflow bit
        self.set_status_bit(6, (~(self.A ^ operand) & (self.A ^ np.uint8(total)) & 0x0080))
        self.A = np.uint8(total)
        self.set_status_bit(1, self.A == 0)  # set zero bit
        self.set_status_bit(7, self.A >> 7)  # set Negative bit

    def AND(self, ad_mode):
        address = ad_mode()
        self.A &= self.read_memory(address)
        self.set_status_bit(1, self.A == 0)  # set Zero Bit
        self.set_status_bit(7, self.A >> 7)  # set Negative bit

    def ASL(self, ad_mode):
        operand = ad_mode
        operand_address = operand()
        operand = ad_mode == self.ACC and self.A or self.read_memory(operand_address)
        self.set_status_bit(0, operand >> 7)  # set carry flag
        output = np.uint8(operand << 1)
        if ad_mode == self.ACC:
            self.A = np.uint8(output)
            self.set_status_bit(1, self.A == 0)  # set zero flag
        else:
            self.write_memory(operand_address, output)
        self.set_status_bit(7, output >> 7)  # set negative flag
        

    def BCC(self, ad_mode):
        address_fetched = ad_mode()
        if (self.status_code & 0x01) == 0:
            self.extra_cycle += 0x01
            address_new = np.uint16(address_fetched + self.pc)
            if (address_new & 0xFF00) != (self.pc & 0xFF00):
                self.extra_cycle += 0x01
            self.pc = np.uint16(address_new)

    def BCS(self, ad_mode):
        address_fetched = ad_mode()
        if (self.status_code & 0x01) == 1:
            self.extra_cycle += 0x01
            address_new = address_fetched + self.pc
            if (address_new & 0xFF00) != (self.pc & 0xFF00):
                self.extra_cycle += 0x01
            self.pc = np.uint16(address_new)

    def BEQ(self, ad_mode):
        address_fetched = ad_mode()
        if (self.status_code >> 1) & (0x01):
            self.extra_cycle += 0x01
            address_new = np.uint16(address_fetched + self.pc)
            if (address_new & 0xFF00) != (self.pc & 0xFF00):
                self.extra_cycle += 0x01
            self.pc = np.uint16(address_new)

    def BIT(self, ad_mode):
        address_fetched = ad_mode()
        target = self.read_memory(address_fetched)
        temp = self.A & target
        self.set_status_bit(1, temp == 0)
        self.set_status_bit(6, (target >> 6 & 0x01))
        self.set_status_bit(7, (target >> 7 & 0x01))

    def BMI(self, ad_mode):
        address_fetched = ad_mode()
        if ((self.status_code >> 7) == 1):
            self.extra_cycle += 0x01
            address_new = np.uint16(address_fetched + self.pc)
            if (address_new & 0xFF00) != (self.pc & 0xFF00):
                self.extra_cycle += 0x01
            self.pc = np.uint16(address_new)

    def BNE(self, ad_mode):
        address_fetched = ad_mode()
        if not (((self.status_code >> 1) & (0x01))):
            self.extra_cycle += 0x01
            address_new = np.uint16(address_fetched + self.pc)
            if (address_new & 0xFF00) != (self.pc & 0xFF00):
                self.extra_cycle += 0x01
            self.pc = np.uint16(address_new)

    def BPL(self, ad_mode):
        address_fetched = ad_mode()
        if not (((self.status_code >> 7) & (0x01))):
            self.extra_cycle += 0x01
            address_new = np.uint16(address_fetched + self.pc)
            if (address_new & 0xFF00) != (self.pc & 0xFF00):
                self.extra_cycle += 0x01
            self.pc = np.uint16(address_new)

    def BRK(self):
        self.pc += 1
        self.stack_push((self.pc >> 8) & 0xFF)
        self.stack_push((self.pc) & 0xFF)
        self.set_status_bit(2, True)
        self.set_status_bit(5, True)
        self.set_status_bit(4, True)
        self.stack_push(self.status_code)
        self.pc = np.uint16(self.read_memory(0xFFFE)) | (np.uint16(self.read_memory(0xFFFF) << 8))
        self.set_status_bit(4, False)
        self.set_status_bit(5, True)

    def BVC(self, ad_mode):
        address_fetched = ad_mode()
        if not (((self.status_code >> 6) & (0x01))):
            self.extra_cycle += 0x01
            address_new = address_fetched + self.pc
            if (address_new & 0xFF00) != (self.pc & 0xFF00):
                self.extra_cycle += 0x01
            self.pc = np.uint16(address_new)

    def BVS(self, ad_mode):
        address_fetched = ad_mode()
        if ((self.status_code >> 6) & (0x01)):
            self.extra_cycle += 0x01
            address_new = address_fetched + self.pc
            if (address_new & 0xFF00) != (self.pc & 0xFF00):
                self.extra_cycle += 0x01
            self.pc = address_new

    def CLC(self):
        self.clear_status_bit(0, True)  # Clears the carry bit

    def CLD(self):
        self.set_status_bit(3, False)  # NES does not use this

    def CLI(self):
        self.clear_status_bit(2, True)  # Clears the interrupt bit

    def CLV(self):
        self.clear_status_bit(6, True)  # Clears the overflow bit

    def CMP(self, ad_mode):
        address_fetched = ad_mode()
        target = self.read_memory(address_fetched)
        temp = np.uint16(self.A) - np.uint16(target)
        self.set_status_bit(0, self.A >= target)
        self.set_status_bit(1, self.A == target & 0xFF)
        self.set_status_bit(7, (temp & 0x0080))

    def CPX(self, ad_mode):
        address_fetched = ad_mode()
        target = self.read_memory(address_fetched)
        temp = np.uint16(self.X) - np.uint16(target)
        self.set_status_bit(0, self.X >= target)
        self.set_status_bit(1, self.X == target & 0xFF)
        self.set_status_bit(7, (temp & 0x0080))

    def CPY(self, ad_mode):
        address_fetched = ad_mode()
        target = self.read_memory(address_fetched)
        temp = np.uint16(self.Y) - np.uint16(target)
        self.set_status_bit(0, (self.Y >= target))
        self.set_status_bit(1, (self.Y == target))
        self.set_status_bit(7, (temp & 0x0080))

    def DEC(self, ad_mode):
        address_fetched = ad_mode()
        value = np.uint8(self.read_memory(address_fetched) - 1)
        self.write_memory(address_fetched, value)
        self.set_status_bit(1, value == 0)
        self.set_status_bit(7, value >> 7)

    def DEX(self):
        self.X = np.uint8(self.X - 1)
        self.set_status_bit(1, self.X == 0)
        self.set_status_bit(7, self.X >> 7 & 0x01)

    def DEY(self):
        self.Y = np.uint8(self.Y -1)
        self.set_status_bit(1, self.Y == 0)
        self.set_status_bit(7, self.Y >> 7 & 0x01)

    def EOR(self, ad_mode):
        address_fetched = ad_mode()
        operand = self.read_memory(address_fetched)
        self.A ^= operand
        self.set_status_bit(1, self.A == 0)
        self.set_status_bit(7, self.A >> 7 & 0x01)

    def INC(self, ad_mode):
        address_fetched = ad_mode()
        value = np.uint8(self.read_memory(address_fetched) + 1)
        self.write_memory(address_fetched, value)
        self.set_status_bit(1, value == 0)
        self.set_status_bit(7, value >> 7 & 0x01)

    def INX(self):
        self.X = np.uint8(self.X + 1)
        self.set_status_bit(1, self.X == 0)
        self.set_status_bit(7, self.X >> 7 & 0x01)

    def INY(self):
        self.Y = np.uint8(self.Y + 1)
        self.set_status_bit(1, self.Y == 0)
        self.set_status_bit(7, self.Y >> 7 & 0x01)

    def JMP(self, ad_mode):
        address_fetched = ad_mode()
        self.pc = np.uint16(address_fetched)

    def JSR(self, ad_mode):
        address_fetched = ad_mode()
        self.pc = np.uint16(self.pc - 1)
        self.stack_push((self.pc >> 8) & 0x00FF)
        self.stack_push((self.pc) & 0x00FF)
        self.pc = np.uint16(address_fetched)

    def LDA(self, ad_mode):
        address_fetched = ad_mode()
        self.A = self.read_memory(address_fetched)
        self.set_status_bit(1, self.A == 0)
        self.set_status_bit(7, self.A >> 7)

    def LDX(self, ad_mode):
        address_fetched = ad_mode()
        self.X = self.read_memory(address_fetched)
        self.set_status_bit(1, self.X == 0)
        self.set_status_bit(7, self.X >> 7)

    def LDY(self, ad_mode):
        address_fetched = ad_mode()
        self.Y = self.read_memory(address_fetched)
        self.set_status_bit(1, self.Y == 0)
        self.set_status_bit(7, self.Y >> 7)

    def LSR(self, ad_mode):
        address_fetched = ad_mode()
        value_fetched = ad_mode == self.ACC and self.A or self.read_memory(address_fetched)
        target = value_fetched >> 1
        self.set_status_bit(0, value_fetched & 0x01)
        self.set_status_bit(1, target == 0)
        self.set_status_bit(7, target >> 7 & 0x01)
        if ad_mode == self.ACC:
            self.A = target & 0x00FF
        else:
            self.write_memory(address_fetched, target & 0x00FF)

    def NOP(self):
        return None

    def ORA(self, ad_mode):
        # Inclusive bitwise OR operation on the accumulator
        address_fetched = ad_mode()
        self.A |= self.read_memory(address_fetched)
        # update relevant status code bits
        self.set_status_bit(1, self.A == 0)  # set zero bit if needed
        # set negative flag if needed
        self.set_status_bit(7, self.A >> 7)

    def PHA(self): 
        self.stack_push(self.A)

    def PHP(self):
        self.set_status_bit(5, True)
        self.set_status_bit(4, True)
        self.stack_push(self.status_code)
        self.set_status_bit(4, False)

    def PLA(self):
        self.A = np.uint8(self.stack_pop())
        self.set_status_bit(1, self.A == 0)
        self.set_status_bit(7, self.A >> 7)

    def PLP(self):
        self.status_code = self.stack_pop()
        self.set_status_bit(4, False)
        self.set_status_bit(5, True)

    def ROL(self, ad_mode):
        address_fetched = ad_mode()
        value_fetched = ad_mode == self.ACC and self.A or self.read_memory(address_fetched)
        value = np.uint8(np.uint16(value_fetched << 1) | (self.status_code & 0x01))
        self.set_status_bit(0, (value_fetched >> 7) & 0x01)
        self.set_status_bit(7, value >> 7)
        if ad_mode == self.ACC:
            self.A = value
        else:
            self.write_memory(address_fetched, value)
        self.set_status_bit(1, value == 0)

    def ROR(self, ad_mode):
        address_fetched = ad_mode()
        value_fetched = ad_mode == self.ACC and self.A or self.read_memory(address_fetched)
        value = ((value_fetched >> 1) | np.uint16(((self.status_code & 0x01) << 7)))
        self.set_status_bit(0, value_fetched & 0x01)
        self.set_status_bit(7, value >> 7)
        if ad_mode == self.ACC:
            self.A = value
        else:
            self.write_memory(address_fetched, value)
        self.set_status_bit(1, value == 0)

    def RTI(self):
        self.status_code = self.stack_pop()
        self.set_status_bit(5, False)
        self.set_status_bit(4, False)
        pc = np.uint16(self.stack_pop())
        pc |= np.uint16(self.stack_pop() << 8)

    def RTS(self):
        lo = self.stack_pop()
        hi = self.stack_pop() << 8
        self.pc = hi | lo
        self.pc = np.uint16(self.pc + 1)

    def SBC(self, ad_mode):
        address_fetched = ad_mode()
        operand = self.read_memory(address_fetched)
        operand ^= 0x00FF
        total = self.A + (self.status_code & 0x01) + operand
        self.set_status_bit(0, total > 0x00FF)  # set Carry bit
        # Set overflow bit
        self.set_status_bit(6, (~(self.A ^ operand) & (self.A ^ np.uint8(total)) & 0x0080))
        self.A = np.uint8(total)
        self.set_status_bit(1, self.A == 0)  # set zero bit
        self.set_status_bit(7, self.A >> 7)  # set Negative bit

    def SEC(self):
        self.set_status_bit(0, True)

    def SED(self):
        self.set_status_bit(3, True)  # unused in the NES

    def SEI(self):
        self.set_status_bit(2, True)

    def STA(self, ad_mode):
        address_fetched = ad_mode()
        self.write_memory(address_fetched, self.A)

    def STX(self, ad_mode):
        address_fetched = ad_mode()
        self.write_memory(address_fetched, self.X)

    def STY(self, ad_mode):
        address_fetched = ad_mode()
        self.write_memory(address_fetched, self.Y)

    def TAX(self):
        self.X = self.A
        self.set_status_bit(1, self.X == 0)
        self.set_status_bit(7, self.X >> 7)

    def TAY(self):
        self.Y = self.A
        self.set_status_bit(1, self.Y == 0)
        self.set_status_bit(7, self.Y >> 7)

    def TSX(self):
        self.X = np.uint8(self.sp)
        self.set_status_bit(1, self.X == 0)
        self.set_status_bit(7, self.X >> 7)

    def TXA(self):
        self.A = self.X
        self.set_status_bit(1, self.A == 0)
        self.set_status_bit(7, self.A >> 7)

    def TXS(self):
        self.sp = self.X

    def TYA(self):
        self.A = self.Y
        self.set_status_bit(1, self.A == 0)
        self.set_status_bit(7, self.A >> 7)

    def UNK(self):
        return None
