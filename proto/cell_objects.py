from enum import Enum
from dataclasses import dataclass

import numpy as np
import pygame

pygame.init()

# Récupération des dimensions de l'écran
user_screen_info = pygame.display.Info()
USER_SCREEN_WIDTH = user_screen_info.current_w
USER_SCREEN_HEIGHT = user_screen_info.current_h
scale = 1.5

# Dimensionnement de la fenêtre
WIN_WIDTH = USER_SCREEN_WIDTH // scale  # 1280
WIN_HEIGHT = USER_SCREEN_HEIGHT // scale  # 720

# Taille initiale des cellules
# Ces tailles seront, au besoin, ajustées de manière à ce qu'un nombre entier de cellules puisse être contenu dans
# les dimensions de la surface
CELL_WIDTH_INIT = 8
CELL_HEIGHT_INIT = 8

# Marge entre deux cellules (px)
MARGIN = 2

run = True
fps = 60

# Couleurs (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 180, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
BLUE = (0, 0, 255)
PINK = (210, 0, 210)
MAROON = (153, 76, 0)

# Calcul du nombre entier de cellules pouvant être contenu dans la surface selon les paramètres initiaux
cells_in_row_init = int(WIN_WIDTH // (CELL_WIDTH_INIT + MARGIN))
cells_in_col_init = int(WIN_HEIGHT // (CELL_HEIGHT_INIT + MARGIN))

# Calcul de la taille totale de la grille selon les paramètres initiaux
grid_width_init = (cells_in_row_init * (CELL_WIDTH_INIT + MARGIN)) + MARGIN
grid_height_init = (cells_in_col_init * (CELL_HEIGHT_INIT + MARGIN)) + MARGIN

CELL_WIDTH = CELL_WIDTH_INIT
CELL_HEIGHT = CELL_HEIGHT_INIT

# Vérifie si la taille de la grille ne dépasse pas celle de la surface souhaitée
if grid_width_init > WIN_WIDTH or grid_height_init > WIN_HEIGHT:
    width_ratio = WIN_WIDTH / grid_width_init if grid_width_init > WIN_WIDTH else 1.0
    height_ratio = WIN_HEIGHT / grid_height_init if grid_height_init > WIN_HEIGHT else 1.0
    scale_ratio = min(width_ratio, height_ratio)

    CELL_WIDTH = int(CELL_WIDTH_INIT * scale_ratio)
    CELL_HEIGHT = int(CELL_HEIGHT_INIT * scale_ratio)

    if CELL_WIDTH < 1:  # Ensure cell width is at least 1px
        CELL_WIDTH = 1

    if CELL_HEIGHT < 1:  # Ensure cell height is at least 1px
        CELL_HEIGHT = 1

    print(f"Cell size adjusted from {CELL_WIDTH_INIT}x{CELL_HEIGHT_INIT} to {CELL_WIDTH}x{CELL_HEIGHT}")

# Ajustement du nombre de cellules par ligne/colonne
cells_in_row = int(WIN_WIDTH // (CELL_WIDTH + MARGIN))
cells_in_col = int(WIN_HEIGHT // (CELL_HEIGHT + MARGIN))
print(f"Cells : {cells_in_row}x{cells_in_col} = {cells_in_row*cells_in_col}")

# Application des dimensions de la fenêtre
WINDOW_SIZE = [WIN_WIDTH, WIN_HEIGHT]
screen = pygame.display.set_mode(WINDOW_SIZE)

pygame.display.set_caption("Space Grid")

clock = pygame.time.Clock()

# Rayon de propagation autour de la cellule cliquée.
NEIGHBORHOOD_RADIUS = 10

# Une dataclass est une classe spécialement conçue pour contenir des données.
# Le décorateur se charge de générer automatiquement les méthodes spéciales telles que __init__, __repr__, etc.
# Une dataclass met donc l'accent sur les données et la concision.
@dataclass
class MaterialProperties:
    """
    Propriétés des matériaux.

    ignition_temp : Température à laquelle le matériau commence à brûler.
    combustion_heat : Énergie libérée par unité de masse lors de la combustion.
    burn_rate : Vitesse à laquelle le matériau brûle une fois enflammé (masse perdue par unité de temps).
    thermal_conductivity : Capacité du matériau à conduire la chaleur.
    thermal_capacity : Quantité de chaleur nécessaire pour augmenter la température du matériau.
    density : Masse par unité de volume, qui influence la quantité de combustible disponible.
    humidity : Quantité d'eau dans le matériau, qui peut retarder l'ignition et la combustion.
    emissivity : Capacité du matériau à émettre de l'énergie thermique par rayonnement.
    """
    ignition_temp: float # °C
    combustion_heat: float # MJ/kg
    burn_rate: float # kg/m²/s
    thermal_conductivity: float # W(m.K)
    thermal_capacity: float # (KJ/(kg.K))
    density: float # kg/m3
    humidity: float # %
    emissivity: float # [0,1]
    color: tuple

class Material(Enum):
    """
    Enumération des matériaux et de leurs propriétés.
    """
    WOOD = MaterialProperties(ignition_temp=300.0,
                              combustion_heat=18.0,
                              burn_rate=0.35,
                              thermal_conductivity=0.2,
                              thermal_capacity=1.8,
                              density=650.0,
                              humidity=10.0,
                              emissivity=0.8,
                              color=MAROON)

    GRASS = MaterialProperties(ignition_temp=300.0,
                              combustion_heat=18.0,
                              burn_rate=0.5,
                              thermal_conductivity=0.2,
                              thermal_capacity=2.0,
                              density=80.0,
                              humidity=25.0,
                              emissivity=0.8,
                              color=GREEN)

    FUEL = MaterialProperties(ignition_temp=100.0,
                              combustion_heat=40.0,
                              burn_rate=0.8,
                              thermal_conductivity=0.3,
                              thermal_capacity=1.8,
                              density=750.0,
                              humidity=2.0,
                              emissivity=0.8,
                              color=PINK)

# -------- CELL CLASS DEFINITION --------
class Cell:
    def __init__(self, row, col):
        # Position sur la grille
        self.row = row
        self.col = col

        # Attributs physiques
        self.material: Material = self.get_material()
        self.fuel_level: 100.0
        self.temperature = 20.0
        self.oxygen_rate = 21.0
        self.humidity_rate = 20.0
        self.heat_absorbed = 0
        self.heat_radiated = 0
        self.wind_force = 40
        self.wind_direction = -1

        # États physiques.
        self.is_burning = False
        self.burned = False

        # Attributs logiques
        self.state = 0  # 0: WHITE, 1: RED, 2: ORANGE

    def get_neighbors(self, grid: list[list], radius: int) -> list:
        """
        Renvoie la liste des cellules voisines dans un rayon déterminé.

        :param grid: La liste de toutes les cellules.
        :param radius: Rayon du voisinage (en nombre de cellules).

        :return: La liste des cellules voisines.
        """
        neighbors = []
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0

        for offset_row in range(-radius, radius + 1):
            for offset_col in range(-radius, radius + 1):
                if offset_row == 0 and offset_col == 0:  # Ne pas prendre en compte la cellule cliquée.
                    continue

                neighbor_row = self.row + offset_row
                neighbor_col = self.col + offset_col

                # S'assurer que les coordonnées ne sont pas hors surface.
                if 0 <= neighbor_row < rows and 0 <= neighbor_col < cols:
                    neighbors.append(grid[neighbor_row][neighbor_col])

        return neighbors

    @staticmethod
    def get_material():
        """
        Retourne un Material selon sa probabilité d'apparition.

        :return: Material.
        """
        probabilities = {
            Material.GRASS : 0.50,
            Material.WOOD : 0.45,
            Material.FUEL : 0.05
        }

        rand_num = np.random.random()

        # Test de probabilité cumulative.
        # Le nombre aléatoire est comparé avec ces seuils cumulatifs :
        # 1er passage de la boucle 'cumulative_proba' = 0.5.
        # 2ᵉ passage de la boucle 'cumulative_proba' = 0.95.
        # 3ᵉ passage de la boucle 'cumulative_proba' = 1.
        # À chacun de ces passages, on vérifie si 'rand_num' est inférieur ou égal à 'cumulative_proba', si c'est le
        # cas, la fonction renvoie le matériau associé à la valeur de probabilité.
        cumulative_proba = 0
        for material, proba in probabilities.items():
            cumulative_proba += proba

            if rand_num < cumulative_proba:
                return material

    def draw(self):
        """
        Dessine la cellule sur la surface principale.
        """
        color = WHITE
        if self.material == Material.GRASS:
            color = Material.GRASS.value.color
        elif self.material == Material.WOOD:
            color = Material.WOOD.value.color
        elif self.material == Material.FUEL:
            color = Material.FUEL.value.color
        else:
            color = WHITE

        x_pos = (MARGIN + CELL_WIDTH) * self.col + MARGIN
        y_pos = (MARGIN + CELL_HEIGHT) * self.row + MARGIN

        pygame.draw.rect(screen, color, [x_pos, y_pos, CELL_WIDTH, CELL_HEIGHT])

# -------- END CELL CLASS DEFINITION --------

# Création d'une liste de Cell objects.
grid: list[list[Cell]] = [[Cell(row, col) for col in range(cells_in_row)] for row in range(cells_in_col)]

# -------- MAIN LOOP -----------
while run:
    for event in pygame.event.get():  # All user events
        if event.type == pygame.QUIT:  # Closing window
            run = False  # Exit from main loop
            break

        if event.type == pygame.MOUSEBUTTONDOWN:  # Mouse click
            if pygame.mouse.get_pressed()[0]:  # Left click
                pos = pygame.mouse.get_pos()  # Get cursor coordinates

                # Les coordonnées du curseur sont converties en coordonnées de grille.
                column = pos[0] // (CELL_WIDTH + MARGIN)
                row = pos[1] // (CELL_HEIGHT + MARGIN)
                print("[Column : {} - Row : {}]".format(column, row))

                clicked_cell = grid[row][column]  # Récupération de l'objet Cell cliqué.

                # Parcours de la grille pour réinitialiser les états.
                for r in range(cells_in_col):
                    for c in range(cells_in_row):
                        if grid[r][c].state == 1 or grid[r][c].state == 2:
                            grid[r][c].state = 0

                # Changement de couleur de la cellule cliquée via l'attribut 'state' de l'objet Cell.
                if clicked_cell.state == 0:
                    clicked_cell.state = 1  # Red cell (clicked)
                else:
                    clicked_cell.state = 0  # White cell

                # Récupération du voisinage via la méthode 'get_neighbors' de l'objet Cell cliqué.
                neighbors = clicked_cell.get_neighbors(grid, NEIGHBORHOOD_RADIUS)
                for neighbor_cell in neighbors:
                    neighbor_cell.state = 2  # Orange cell (neighbor)

    # Arrière-plan
    screen.fill((50, 50, 50))

    # Dessin de la grille
    for row in range(cells_in_col):  # Itération sur ligne (y-axis, cells_in_col)
        for column in range(cells_in_row):  # Itération sur colonne (x-axis, cells_in_row)
            cell = grid[row][column]  # Récupération de l'objet Cell pour chaque position.
            cell.draw()

    # Set the FPS
    clock.tick(fps)

    # Update display
    pygame.display.flip()

pygame.quit()