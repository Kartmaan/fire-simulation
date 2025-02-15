import pygame
import random

# Paramètres de la grille
GRID_SIZE = 80  # Nombre de cellules en largeur et hauteur
CELL_SIZE = 5  # Taille de chaque cellule (pixels)
MARGIN = 2  # Espace entre les cellules

# Définition des couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
GRAY = (169, 169, 169)

# Initialisation de Pygame
pygame.init()
screen = pygame.display.set_mode((GRID_SIZE * (CELL_SIZE + MARGIN), GRID_SIZE * (CELL_SIZE + MARGIN)))
pygame.display.set_caption("Simulation de Propagation du Feu")


class Cell:
    """Représente une cellule de la grille avec ses attributs physiques."""

    def __init__(self, x: int, y: int, material: str = "empty"):
        self.x = x
        self.y = y
        self.temperature = 20.0  # Température initiale (°C)
        self.oxygen = 21.0  # Pourcentage d'oxygène
        self.material = material  # Matériau : "wood", "fabric", "stone", etc.
        self.in_fire = False  # La cellule est-elle en feu ?
        self.burned = False  # La cellule a-t-elle déjà brûlé ?

    def ignite(self):
        """Enflamme la cellule si elle est inflammable."""
        if self.material in ["wood", "fabric"] and not self.burned:
            self.in_fire = True

    def update(self, grid):
        """Met à jour l'état de la cellule."""
        if self.in_fire:
            self.temperature += 5  # Augmentation de température
            self.oxygen -= 1  # Réduction d'oxygène

            # Si l'oxygène tombe à zéro ou la température dépasse 600°C, le feu s'arrête
            if self.oxygen <= 0 or self.temperature >= 600:
                self.in_fire = False
                self.burned = True

            # Propagation du feu aux cellules voisines
            self.spread_fire(grid)

    def spread_fire(self, grid):
        """Propage le feu aux cellules voisines."""
        neighbors = self.get_neighbors(grid)
        for cell in neighbors:
            if not cell.in_fire and not cell.burned:
                ignition_chance = random.random()
                if ignition_chance < 0.3:  # Probabilité de propagation
                    cell.ignite()

    def get_neighbors(self, grid):
        """Retourne la liste des cellules voisines."""
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Gauche, Droite, Haut, Bas
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                neighbors.append(grid[ny][nx])
        return neighbors

def create_grid():
    """Crée une grille de cellules avec des matériaux aléatoires."""
    grid = []
    for y in range(GRID_SIZE):
        row = []
        for x in range(GRID_SIZE):
            material = random.choice(["empty", "wood", "fabric", "stone"])
            row.append(Cell(x, y, material))
        grid.append(row)
    return grid

def draw_grid(grid):
    """Dessine la grille à l'écran."""
    screen.fill(WHITE)
    for row in grid:
        for cell in row:
            color = GRAY if cell.material == "stone" else WHITE
            if cell.material == "wood":
                color = (139, 69, 19)  # Marron foncé
            elif cell.material == "fabric":
                color = (255, 223, 186)  # Beige clair
            if cell.in_fire:
                color = RED
            elif cell.burned:
                color = BLACK

            pygame.draw.rect(screen, color,
                             [(MARGIN + CELL_SIZE) * cell.x + MARGIN,
                              (MARGIN + CELL_SIZE) * cell.y + MARGIN,
                              CELL_SIZE, CELL_SIZE])


# Initialisation de la grille
grid = create_grid()

# Démarre un feu sur une cellule aléatoire
start_x, start_y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
grid[start_y][start_x].ignite()

# Boucle principale
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Mise à jour de la simulation
    for row in grid:
        for cell in row:
            cell.update(grid)

    # Affichage
    draw_grid(grid)
    pygame.display.flip()
    clock.tick(10)  # Limite la vitesse d'exécution à 10 FPS

pygame.quit()