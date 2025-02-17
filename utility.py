import random


def handle_alpha_for_weight(weight):
    weight = max(0, min(1, weight))
    a = int(weight * 255)
    return a


def handle_color_gene(parent):
    r, g, b, a = parent.color

    parent_gene = parent.gene_marker
    gene_preference_strength = 10
    drift = 30

    mutation_chance_r = 1 - (r / 255)
    mutation_chance_g = 1 - (g / 255)
    mutation_chance_b = 1 - (b / 255)
    red_mutated = False
    green_mutated = False
    blue_mutated = False

    mutation = random.uniform(0, 1)

    if parent_gene == "r" and mutation < mutation_chance_r:
        r += gene_preference_strength
        red_mutated = True
    if parent_gene == "g" and mutation < mutation_chance_g:
        g += gene_preference_strength
        green_mutated = True
    if parent_gene == "b" and mutation < mutation_chance_b:
        b += gene_preference_strength
        blue_mutated = True
    if parent_gene == "white":
        r += 2
        g += 2
        b += 2

    if not red_mutated:
        r += int(random.uniform(-drift, drift))
    if not green_mutated:
        g += int(random.uniform(-drift, drift))
    if not blue_mutated:
        b += int(random.uniform(-drift, drift))

    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))

    balance_threshold = 15
    if (abs(r - g) < balance_threshold and
            abs(g - b) < balance_threshold and
            abs(r - b) < balance_threshold):
        gene_preference = "white"
    else:
        # Determine strongest color and assign gene preference
        if r >= g and r >= b:
            gene_preference = "r"
        elif g >= r and g >= b:
            gene_preference = "g"
        else:
            gene_preference = "b"

    color = (r, g, b, a)

    return color, gene_preference
