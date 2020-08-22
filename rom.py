import numpy as np
from mappers.mapper_0 import Mapper0

class ROM:

    def __init__(self, memory):
        rom_file = open('mario.nes', 'rb')
        # Header format as follows
        # 0-3 -> Constant NES followed by EOF
        # 4 -> PRG ROM size in 16kiB units
        # 5 -> CHR ROM size in 8kiB units
        # 6 -> Flags 6 - Mapper, mirroring, battery, trainer
        # 7 -> Flags 7 - Mapper, VS/Playchoice, NES 2.0
        # 8 -> Flags 8 - PRG-RAM size (rarely used extension)
        # 9 -> Flags 9 - TV system (rarely used extension)
        # 10 -> Flags 10 - TV system, PRG-RAM presence (unofficial, rarely used extension)
        # 11-15 -> Unused padding (should be filled with zero, but some rippers put their name across bytes 7-15)
        header = list(rom_file.read(16))
        # skip trainer data if it exists
        if header[:4] != [78, 69, 83, 26]:
            print("Invalid NES ROM")
        if (header[6] & 0x04):
            rom_file.seek(512, 1)  # skip trainer data
        self.mapper_id = ((header[7] >> 4) << 4) | (header[6] >> 4)  # determine mapper id
        prg_size = header[4] * 16384
        chr_size = header[5] * 8192
        prg_memory = np.array(list(rom_file.read(prg_size)), dtype=np.uint8)
        chr_memory = np.array(list(rom_file.read(chr_size)), dtype=np.uint8)
        self.mirror_type = (header[6] & 1) | (((header[6] >> 3) & 1) << 1)
        self.mapper = Mapper0(header[4], header[5], prg_memory, chr_memory)  # Mapper 0 by default for now..
        memory.mapper = self.mapper
     

