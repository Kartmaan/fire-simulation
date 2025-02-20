import pygame
import numpy as np

from src.scaling_option import screen, MARGIN, CELL_WIDTH, CELL_HEIGHT
from src.material import Material
from src.colors import Colors

colors = Colors()

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
            color = colors.white

        # Conversion des coordonnées de grille en coordonnées de pixel.
        x_pos = (MARGIN + CELL_WIDTH) * self.col + MARGIN
        y_pos = (MARGIN + CELL_HEIGHT) * self.row + MARGIN

        if 20.0 <= self.temperature < 20.5:
            pygame.draw.rect(screen, color, [x_pos, y_pos, CELL_WIDTH, CELL_HEIGHT])
        elif 20.5 <= self.temperature < self.material.value.ignition_temp:
            pygame.draw.rect(screen, colors.orange, [x_pos, y_pos, CELL_WIDTH, CELL_HEIGHT])
        else:
            pygame.draw.rect(screen, colors.red, [x_pos, y_pos, CELL_WIDTH, CELL_HEIGHT])