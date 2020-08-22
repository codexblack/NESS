# import necessary libraries
import pygame
from cpu import CPU6502 as CPU
from rom import ROM
from memory import Memory

def main():
    # set up everything here
    
    # Initilaise pygame
    pygame.init()
    nes_icon = pygame.image.load('icon.png')
    pygame.display.set_icon(nes_icon)
    screen = pygame.display.set_mode((256, 240))
    pygame.display.set_caption('NESS') 
    done = False
    # Emulator components initialised here
    memory = Memory()
    cpu = CPU(memory)
    rom = ROM(memory)
    while not done:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        done = True
        cpu.execute()

main()