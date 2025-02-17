# hover_manager.py
import pygame
import math
from constants import *


class HoverManager:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont('arial', 16)
        self.hovered_person = None

    def is_mouse_over_person(self, mouse_pos, person):
        """Check if mouse is hovering over a person node"""
        dx = mouse_pos[0] - person.pos_x
        dy = mouse_pos[1] - person.pos_y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance <= person.size

    def update(self, people):
        """Update hovered person based on mouse position"""
        mouse_pos = pygame.mouse.get_pos()
        self.hovered_person = None

        for person in people.values():
            if self.is_mouse_over_person(mouse_pos, person):
                self.hovered_person = person
                break

    def draw(self):
        """Draw RGB values if hovering over a person"""
        if self.hovered_person:
            # Create text with color values and gene marker
            color = self.hovered_person.color
            color_text = f"RGB{color}"
            marker_text = f"Marker({self.hovered_person.gene_marker})"
            weight_text = f"Weights({self.hovered_person.weight})"

            color_surface = self.font.render(color_text, True, WHITE)
            marker_surface = self.font.render(marker_text, True, WHITE)
            weight_surface = self.font.render(weight_text,True, WHITE)

            # Position text above the node
            text_x = int(self.hovered_person.pos_x - color_surface.get_width() // 2)
            text_y = int(self.hovered_person.pos_y - self.hovered_person.size - 40)


            # Calculate background rectangle to fit both lines
            padding = 5
            bg_width = max(color_surface.get_width(), marker_surface.get_width()) + (2 * padding)
            bg_height = color_surface.get_height() + marker_surface.get_height() + (2 * padding)

            bg_rect = (
                text_x - padding,
                text_y - padding,
                bg_width,
                bg_height
            )

            # Draw background with semi-transparency
            s = pygame.Surface((bg_rect[2], bg_rect[3]))
            s.set_alpha(200)
            s.fill((0, 0, 0))
            self.screen.blit(s, (bg_rect[0], bg_rect[1]))

            # Draw both lines of text
            self.screen.blit(color_surface, (text_x, text_y))
            self.screen.blit(marker_surface, (text_x, text_y + color_surface.get_height()))
            self.screen.blit(weight_surface, (text_x, text_y + color_surface.get_height() * 2))
