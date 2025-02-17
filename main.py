import pygame
import sys
from constants import *
from the_network import TheNetwork

pygame.init()
pygame.display.set_caption("Da Star")
clock = pygame.time.Clock()
FPS = 200

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
the_network = TheNetwork(screen)


def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        screen.fill(BLACK)
        the_network.update()
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
