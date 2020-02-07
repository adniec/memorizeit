import pygame
import gui


def main():
    pygame.init()
    pygame.display.set_caption('MemorizeIT')
    try:
        pygame.display.set_icon(pygame.image.load('images/brain.png'))
    except pygame.error:
        pass
    gui.Menu()


if __name__ == '__main__': main()
