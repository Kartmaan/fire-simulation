from enum import Enum
from dataclasses import dataclass

import numpy as np
import pygame
from pygame.math import Vector2

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
CELL_WIDTH_INIT = 10
CELL_HEIGHT_INIT = 10

# Marge entre deux cellules (px)
MARGIN = 2

run = True
fps = 30

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

pygame.display.set_caption("Fire propagation")

clock = pygame.time.Clock()

# Une dataclass est une classe spécialement conçue pour contenir des données.
# Le décorateur se charge de générer automatiquement les méthodes spéciales telles que __init__, __repr__, etc.
# Une dataclass met donc l'accent sur les données et la concision.
@dataclass
class MaterialProperties:
    """
    Propriétés physiques communes à tous les matériaux.

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
    Enumération des matériaux et de leurs propriétés physiques intrinsèques.
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

class Cell:
    """
    Cellule d'espace qui contient le matériau.

    La cellule possède des attributs physiques tels que la température, le taux d'humidité et d'oxygène qui sont
    susceptibles d'influencer l'état du matériau durant sa combustion.
    """
    def __init__(self, row, col):
        # Position sur la grille
        self.row = row
        self.col = col

        # Attributs physiques
        self.material: Material = self.__get_material()
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
        self.timers = {}

    def timer(self, timer_name: str, duration: float) -> bool:
        """Checks if a timer has expired.

        Args:
            timer_name (str): Timer name.
            duration (float): Desired duration in seconds.

        Returns:
            bool: True if time is up, False otherwise.
        """
        now = pygame.time.get_ticks() // 1000

        if timer_name not in self.timers:
            self.timers[timer_name] = now
            return False

        elapsed_time = now - self.timers[timer_name]
        if elapsed_time >= duration:
            self.timers[timer_name] = now
            return True

        return False

    def get_neighbors(self, cell_grid: list[list['Cell']], radius: int) -> list['Cell']:
        """
        Renvoie la liste des cellules voisines dans un rayon déterminé.

        Args :
            grid (list) : La liste de toutes les cellules.
            radius (int) : Rayon du voisinage (en nombre de cellules).

        Returns :
            La liste des cellules voisines.
        """
        neighbors: list[Cell] = []
        rows = len(cell_grid)
        cols = len(cell_grid[0]) if rows > 0 else 0

        for offset_row in range(-radius, radius + 1):
            for offset_col in range(-radius, radius + 1):
                if offset_row == 0 and offset_col == 0:  # Ne pas prendre en compte la cellule cliquée.
                    continue

                neighbor_row = self.row + offset_row
                neighbor_col = self.col + offset_col

                # S'assurer que les coordonnées ne sont pas hors surface.
                if 0 <= neighbor_row < rows and 0 <= neighbor_col < cols:
                    neighbors.append(cell_grid[neighbor_row][neighbor_col])

        return neighbors

    def heat_conduction(self, cell_grid: list[list['Cell']], delta_time: float):
        """
        Transfère la chaleur par conduction aux cellules voisines.

        Args:
            cell_grid (list[list[Cell]]) : Grille des cellules
            delta_time (float) : Intervalle de temps pour le transfert de chaleur.
        """
        neighbors = self.get_neighbors(cell_grid, radius=1) # Conduction vers les voisins immédiats.

        # Parcours des cellules voisines.
        # À chaque passage de cette boucle les propriétés thermiques de la cellule source (self) sont comparées à celle
        # de la cellule voisine.
        for neighbor_cell in neighbors:
            # Transfert de chaleur uniquement du chaud vers le froid
            if neighbor_cell.temperature < self.temperature:
                # Conductivité thermique de la cellule source
                k_source = self.material.value.thermal_conductivity

                # Conductivité thermique de la cellule voisine
                k_target = neighbor_cell.material.value.thermal_conductivity

                # Simplification : on prend la moyenne des conductivités thermiques pour l'interface.
                k_interface = (k_source + k_target) / 2.0

                # Différence de température entre la cellule source et voisine.
                delta_temp = self.temperature - neighbor_cell.temperature

                # Aire de contact approximative
                contact_area = CELL_WIDTH * CELL_HEIGHT

                # Distance approximative entre les centres des cellules.
                distance = (CELL_WIDTH + CELL_HEIGHT) / 2.0
                #distance = np.sqrt(CELL_WIDTH ** 2 + CELL_HEIGHT ** 2)

                # Calcul de la quantité de chaleur transférée par conduction.
                heat_transfert = k_interface * delta_temp * contact_area / distance * delta_time

                # On applique maintenant la chaleur à la cellule voisine (augmentation de température) tout en la
                # retirant de la cellule source (diminution de la température).

                # Augmentation de température dans la cellule voisine
                neighbor_cell.temperature += heat_transfert / neighbor_cell.material.value.thermal_capacity

                # Diminution de la température dans la cellule source.
                self.temperature -= heat_transfert / self.material.value.thermal_capacity

                # Fixation d'une température minimale = température ambiante
                neighbor_cell.temperature = max(neighbor_cell.temperature, 20.0)
                self.temperature = max(self.temperature, 20.0)

    @staticmethod
    def __get_material():
        """
        Retourne un Material selon sa probabilité d'apparition.

        Returns :
            Material : Material object.
        """
        probabilities = {
            Material.GRASS : 0.50,
            Material.WOOD : 0.45,
            Material.FUEL : 0.05
        }

        rand_num = np.random.random()

        # Test de probabilité cumulative.
        # Le nombre aléatoire entre 0 et 1 est comparé avec ces seuils cumulatifs :
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
        if self.material == Material.GRASS:
            color = Material.GRASS.value.color
        elif self.material == Material.WOOD:
            color = Material.WOOD.value.color
        elif self.material == Material.FUEL:
            color = Material.FUEL.value.color
        else:
            color = WHITE

        # Conversion des coordonnées de grille en coordonnées de pixel.
        x_pos = (MARGIN + CELL_WIDTH) * self.col + MARGIN
        y_pos = (MARGIN + CELL_HEIGHT) * self.row + MARGIN

        if 20.0 <= self.temperature < 20.5:
            pygame.draw.rect(screen, color, [x_pos, y_pos, CELL_WIDTH, CELL_HEIGHT])
        elif 20.5 <= self.temperature < self.material.value.ignition_temp:
            pygame.draw.rect(screen, ORANGE, [x_pos, y_pos, CELL_WIDTH, CELL_HEIGHT])
        else:
            pygame.draw.rect(screen, RED, [x_pos, y_pos, CELL_WIDTH, CELL_HEIGHT])

# Création d'une liste de Cell objects.
grid: list[list[Cell]] = [[Cell(row, col) for col in range(cells_in_row)] for row in range(cells_in_col)]

# -------- MAIN LOOP -----------
while run:
    for event in pygame.event.get():  # All user events
        if event.type == pygame.QUIT:  # Closing window
            run = False  # Exit from main loop
            break

        # Clic souris
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos() # Coordonnées du curseur.

            # Les coordonnées pixel du curseur sont converties en coordonnées de grille.
            column = pos[0] // (CELL_WIDTH + MARGIN)
            row = pos[1] // (CELL_HEIGHT + MARGIN)

            clicked_cell: Cell = grid[row][column] # Récupération de l'objet Cell cliqué.

            # Clic gauche
            # Monte la température de la cellule au-delà du point d'ignition du matériau qu'il contient.
            if pygame.mouse.get_pressed()[0]:
                if clicked_cell.temperature < clicked_cell.material.value.ignition_temp:
                    excess_temp = 500
                    clicked_cell.temperature = clicked_cell.material.value.ignition_temp + excess_temp

                    #clicked_cell.heat_conduction(grid, delta_time=0.1)

                    print(f"({clicked_cell.row}x{clicked_cell.col}) Ignition temperature exceeded "
                          f"({clicked_cell.material.name}) : {clicked_cell.temperature}/"
                          f"{clicked_cell.material.value.ignition_temp}")

            # Clic droit
            # Affiche la température de la cellule
            if pygame.mouse.get_pressed()[2]:
                print(f"({clicked_cell.row}x{clicked_cell.col}) Temperature ({clicked_cell.material.name}) : "
                      f"{clicked_cell.temperature}")

    delta_time = 0.08
    for row in range(cells_in_col):
        for column in range(cells_in_row):
            cell = grid[row][column]
            if cell.timer("delta_time", delta_time):
                cell.heat_conduction(grid, delta_time)

    # Arrière-plan
    screen.fill((50, 50, 50))

    # Dessin de la grille
    for row in range(cells_in_col):  # Itération sur ligne (y-axis, cells_in_col)
        for column in range(cells_in_row):  # Itération sur colonne (x-axis, cells_in_row)
            cell = grid[row][column]  # Récupération de l'objet Cell pour chaque position.
            cell.draw()

    # Affichage de la flamme à proximité du curseur.
    flame_radius = 5
    cursor_pos = Vector2(pygame.mouse.get_pos())
    flame_pos = Vector2(cursor_pos.x + 12, cursor_pos.y - 2)
    pygame.draw.circle(screen, BLACK, flame_pos, flame_radius + 2) # Contour
    pygame.draw.circle(screen, RED, flame_pos, flame_radius)

    # Set the FPS
    clock.tick(fps)

    # Update display
    pygame.display.flip()

pygame.quit()