import random
import math
import pygame
from person import Person
from constants import *
from utility import handle_color_gene, handle_alpha_for_weight
from hover_manager import HoverManager


class TheNetwork:
    def __init__(self, screen):
        self.current_start = None
        self.current = None
        self.path_stack = None
        self.visited_nodes = None
        self.search_initialized = None
        self.screen = screen
        self.phase = "growth"
        self.all_people = {}
        self.can_grow_people = []
        self.scored_nodes = []
        self.hover_manager = HoverManager(screen)
        self.current_top_right_text = None

        # Spatial hash grid
        self.agent_size = 5
        self.cell_size = self.agent_size * 2
        self.max_growth_len = self.agent_size * 2
        self.min_growth_len = self.agent_size * 6

        self.grid_width = WINDOW_WIDTH // self.cell_size
        self.grid_height = WINDOW_HEIGHT // self.cell_size
        self.spatial_grid = {}  # Dictionary for occupied cells
        self.operations = 0
        self.max_people = 1000

        # Create Adam
        adam = Person(pos_x=WINDOW_WIDTH // 2, pos_y=WINDOW_HEIGHT // 2, color=RED, id=0, linked_to=None,
                      size=15, gene_marker="r")

        adam.bias_flags = [random.choice([True, False]) for _ in range(10)]

        self.all_people[0] = adam
        self.can_grow_people.append(adam)

        # Mark Adam's cell as occupied
        cell_x = int(adam.pos_x // self.cell_size)
        cell_y = int(adam.pos_y // self.cell_size)
        self.spatial_grid[(cell_x, cell_y)] = True

        self.growth_timer = 0
        self.find_timer = 0
        self.finding_route = False
        self.current_route = []

    def update(self):
        if self.phase == "growth":
            self.growth_timer += 1
            if self.growth_timer >= 1:
                self.growth_timer = 0
                self.new_person()

            if len(self.all_people) >= self.max_people:
                self.phase = "communication"
            if len(self.can_grow_people) <= 0:
                self.phase = "communication"
        if self.phase == "communication":
            self.draw_top_right_text()
            self.find_timer += 1
            self.communication()

        self.hover_manager.update(self.all_people)

        self.draw_people()
        self.draw_operations()

        self.hover_manager.draw()

    def new_person(self):
        if not self.can_grow_people:
            self.phase = "communication"
            return

        parent = random.choice(self.can_grow_people)
        self.can_grow_people.remove(parent)
        parent.can_grow = False

        num_children = random.randint(1, 10)

        for _ in range(num_children):
            self.operations += 1
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(self.min_growth_len, self.max_growth_len)

            new_x = parent.pos_x + math.cos(angle) * distance
            new_y = parent.pos_y + math.sin(angle) * distance

            # Check boundaries
            if not (0 <= new_x <= WINDOW_WIDTH and 0 <= new_y <= WINDOW_HEIGHT):
                continue

            cell_x = int(new_x // self.cell_size)
            cell_y = int(new_y // self.cell_size)

            if self.is_position_free(new_x, new_y):
                self.operations += 1
                new_id = len(self.all_people)

                color, new_gene_marker = handle_color_gene(parent)

                new_person = Person(
                    pos_x=new_x,
                    pos_y=new_y,
                    color=color,
                    parent_id=parent.id,
                    id=new_id,
                    linked_to=parent.id,
                    size=self.agent_size,
                    gene_marker=new_gene_marker
                )

                parent.linked_to.add(new_id)
                self.all_people[new_id] = new_person
                self.can_grow_people.append(new_person)
                self.spatial_grid[(cell_x, cell_y)] = True

            else:
                existing_person = None
                for person in self.all_people.values():
                    if (abs(person.pos_x - new_x) < self.cell_size and
                            abs(person.pos_y - new_y) < self.cell_size):
                        existing_person = person
                        break

                if existing_person:
                    parent.linked_to.add(existing_person.id)
                    existing_person.linked_to.add(parent.id)

    def is_position_free(self, x, y):
        self.operations += 1  # Grid lookup is an operation
        cell_x = int(x // self.cell_size)
        cell_y = int(y // self.cell_size)

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if (cell_x + dx, cell_y + dy) in self.spatial_grid:
                    return False
        return True

    def search_pulse(self, target):
        if not self.queue:
            return "failed"

        current_node, pulse_strength = self.queue.pop(0)

        if current_node.id in self.visited:
            return None

        self.visited.add(current_node.id)

        weight_increase = random.uniform(0.05, 0.15)
        current_node.weight = min(1.0, current_node.weight + weight_increase)
        r, g, b, a = current_node.color
        current_node.color = (r, g, b, handle_alpha_for_weight(current_node.weight))

        # Check if we reached target during forward pulse
        if current_node.id == target.id and not self.is_returning:
            # Reconstruct the path to follow back
            path = []
            node_id = current_node.id
            while node_id is not None:
                path.append(node_id)
                node_id = self.came_from.get(node_id)

            path.reverse()  # Now path goes from start to target

            # Initialize return journey
            self.queue = [(target, 10.0)]
            self.visited = set()
            self.is_returning = True
            self.pulse_edges = []
            self.return_path = path  # Store the path for the return journey
            self.current_path_index = 0
            return None

        # Handle return pulse differently
        if self.is_returning:
            # Check if we're back at start
            if current_node.id == self.current_start.id:
                return "complete"

            # During return, only follow the pre-calculated path
            current_index = self.return_path.index(current_node.id)
            if current_index > 0:  # If we're not at the start of the path
                # Get the previous node in the path (we're going backwards)
                prev_node_id = self.return_path[current_index - 1]
                prev_node = self.all_people[prev_node_id]

                # Add the edge to visualization
                self.pulse_edges.append((
                    (current_node.pos_x, current_node.pos_y),
                    (prev_node.pos_x, prev_node.pos_y)
                ))

                # Add the next node to the queue
                self.queue.append((prev_node, pulse_strength))
                return None

        # Forward pulse logic remains the same
        dampened_strength = pulse_strength * current_node.weight

        if dampened_strength < 0.1:
            return None

        if not hasattr(self, 'pulse_edges'):
            self.pulse_edges = []

        WEIGHT_THRESHOLD = 0.3
        possible_paths = []
        low_weight_paths = []

        for linked_id in current_node.linked_to:
            if linked_id not in self.visited:
                linked_node = self.all_people[linked_id]
                if linked_node.weight >= WEIGHT_THRESHOLD:
                    possible_paths.append((linked_node, linked_node.weight))
                else:
                    low_weight_paths.append((linked_node, linked_node.weight))

        if not possible_paths and low_weight_paths:
            possible_paths = low_weight_paths

        if possible_paths:
            # Sort paths by weight, highest first
            possible_paths.sort(key=lambda x: x[1], reverse=True)

            # Always take the strongest path
            strongest_node = possible_paths[0][0]
            self.queue.append((strongest_node, dampened_strength))

            if strongest_node.id not in self.came_from:
                self.came_from[strongest_node.id] = current_node.id
                self.pulse_edges.append((
                    (current_node.pos_x, current_node.pos_y),
                    (strongest_node.pos_x, strongest_node.pos_y)
                ))

            # 60% chance to send a pulse to a random other node
            if len(possible_paths) > 1 and random.random() < 0.7:
                other_paths = possible_paths[1:]
                random_node = random.choice(other_paths)[0]

                weaker_strength = dampened_strength * 0.5
                self.queue.append((random_node, weaker_strength))

                if random_node.id not in self.came_from:
                    self.came_from[random_node.id] = current_node.id
                    self.pulse_edges.append((
                        (current_node.pos_x, current_node.pos_y),
                        (random_node.pos_x, random_node.pos_y)
                    ))

        return None
    def communication(self):
        # Initialize weights and pulsing state if not done
        if not hasattr(self, 'is_pulsing'):
            self.is_pulsing = False
            self.is_returning = False
            # Initialize all nodes with visible weights
            for person in self.all_people.values():
                person.weight = .5
                r, g, b, _ = person.color
                person.color = (r, g, b, handle_alpha_for_weight(person.weight))
            self.pulse_edges = []

        # Only start new pulse search if we're not currently pulsing
        if not self.is_pulsing:
            # Decay all node weights and update their alphas
            for node in self.all_people.values():
                node.weight = max(0.1, node.weight * 0.98)
                r, g, b, _ = node.color
                node.color = (r, g, b, handle_alpha_for_weight(node.weight))

            # Reset previous pair if they exist
            if hasattr(self, 'current_start') and hasattr(self, 'current_target'):
                r, g, b, _ = self.start_original_color
                self.current_start.color = (r, g, b, handle_alpha_for_weight(self.current_start.weight))
                r, g, b, _ = self.target_original_color
                self.current_target.color = (r, g, b, handle_alpha_for_weight(self.current_target.weight))
                self.current_start.size = self.agent_size
                self.current_target.size = self.agent_size

            # Clear previous pulse visualization
            self.pulse_edges = []
            self.current_route = []

            # Weighted random selection of nodes with amplified weights
            nodes = list(self.all_people.values())
            if not nodes:
                return

            # Amplify the differences between weights using exponential
            AMPLIFICATION = 2  # Increase this to make selection more biased towards higher weights
            weights = [node.weight ** AMPLIFICATION for node in nodes]

            if not weights:
                return

            # Normalize weights to ensure they sum to 1
            total_weight = sum(weights)
            if total_weight == 0:
                normalized_weights = [1 / len(weights)] * len(weights)
            else:
                normalized_weights = [w / total_weight for w in weights]

            # Select start node using weighted random choice
            self.current_start = random.choices(nodes, weights=normalized_weights, k=1)[0]

            # Select target node with same weighting scheme
            target_nodes = [n for n in nodes if n.id != self.current_start.id]
            if not target_nodes:
                return

            target_weights = [n.weight ** AMPLIFICATION for n in target_nodes]
            total_target_weight = sum(target_weights)
            if total_target_weight == 0:
                normalized_target_weights = [1 / len(target_weights)] * len(target_weights)
            else:
                normalized_target_weights = [w / total_target_weight for w in target_weights]

            self.current_target = random.choices(target_nodes, weights=normalized_target_weights, k=1)[0]

            # Store their original colors before changing them
            self.start_original_color = self.current_start.color
            self.target_original_color = self.current_target.color

            # Set their appearance for the search
            self.current_start.color = WHITE
            self.current_start.size = 15
            self.current_target.color = WHITE
            self.current_target.size = 15

            # Initialize search
            self.is_pulsing = True
            self.is_returning = False
            self.queue = [(self.current_start, 1000.0)]
            self.visited = set()
            self.came_from = {self.current_start.id: None}

        # Continue existing pulse search
        if self.is_pulsing:
            result = self.search_pulse(self.current_target)
            if result == "complete" or result == "failed":
                self.is_pulsing = False
                self.is_returning = False

    def draw_people(self):
        # Draw links first
        for person in self.all_people.values():
            for linked_id in person.linked_to:
                linked_person = self.all_people[linked_id]
                pygame.draw.line(
                    self.screen,
                    (128, 128, 128),
                    (int(person.pos_x), int(person.pos_y)),
                    (int(linked_person.pos_x), int(linked_person.pos_y)),
                    1
                )

        # Draw active pulse edges
        if hasattr(self, 'pulse_edges'):
            for start_pos, end_pos in self.pulse_edges:
                pygame.draw.line(
                    self.screen,
                    YELLOW,
                    (int(start_pos[0]), int(start_pos[1])),
                    (int(end_pos[0]), int(end_pos[1])),
                    3
                )

        # Draw final route if exists
        if hasattr(self, 'current_route') and self.current_route:
            for i in range(len(self.current_route) - 1):
                pygame.draw.line(
                    self.screen,
                    YELLOW,
                    self.current_route[i],
                    self.current_route[i + 1],
                    3
                )

        # Draw nodes with alpha support
        for person in self.all_people.values():
            # Create a surface for the circle with per-pixel alpha
            surface = pygame.Surface((person.size * 2, person.size * 2), pygame.SRCALPHA)

            # Draw the circle on the surface
            pygame.draw.circle(
                surface,
                person.color,  # This should be (r,g,b,a)
                (person.size, person.size),  # Center of the surface
                person.size
            )

            # Blit the surface onto the screen
            self.screen.blit(
                surface,
                (int(person.pos_x - person.size), int(person.pos_y - person.size))
            )

    def draw_operations(self):
        font = pygame.font.SysFont('arial', 24)
        text = font.render(f'Operations: {self.operations}, phase: {self.phase}, total agents:{len(self.all_people)}',
                           True, RED)
        self.screen.blit(text, (10, 10))

    def draw_top_right_text(self):
        font = pygame.font.SysFont('arial', 24)
        text_surface = font.render(self.current_top_right_text, True, (255, 255, 255))  # White text

        # Position in top right with some padding
        padding = 10
        text_x = WINDOW_WIDTH - text_surface.get_width() - padding
        text_y = padding

        # Draw background box
        padding_box = 5
        bg_rect = (
            text_x - padding_box,
            text_y - padding_box,
            text_surface.get_width() + (2 * padding_box),
            text_surface.get_height() + (2 * padding_box)
        )

        # Semi-transparent black background
        s = pygame.Surface((bg_rect[2], bg_rect[3]))
        s.set_alpha(200)
        s.fill((0, 0, 0))
        self.screen.blit(s, (bg_rect[0], bg_rect[1]))

        # Draw text
        self.screen.blit(text_surface, (text_x, text_y))
