import pygame
import random
import math


class Person:
    def __init__(self, pos_x, pos_y, color, id, gene_marker=None, linked_to=None, size=None, parent_id=None):
        # Existing attributes
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.size = size
        self.color = color
        self.id = id
        self.linked_to = set()
        self.parent_id = parent_id
        self.can_grow = True
        self.gene_marker = gene_marker
        self.weight = .1
