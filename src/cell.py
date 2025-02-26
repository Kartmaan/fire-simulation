import pygame
import numpy as np

from src.window_option import screen, MARGIN, CELL_WIDTH, CELL_HEIGHT
from src.material import Material
from src.physics import MAX_TEMP
from src.colors import Colors

colors = Colors()

SHOW_GRADIENT_ANIMATION = True

class Cell:
    """
    Space cell containing the material.

    The cell possesses physical attributes such as temperature, humidity and oxygen rate that can influence the state
    of the material during combustion.
    """
    def __init__(self, row, col):
        # Position sur la grille
        self.row = row
        self.col = col

        # Attributs physiques
        self.material: Material = self.__get_material()
        self.fuel_level = 100.0
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
        self.neighbors: list['Cell']
        self.flame_oscillation = np.random.uniform(0.1, 0.3)

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
        Returns a list of neighboring cells within a specified radius.

        Args :
            cell_grid (list): The list of all cells.
            radius (int) : Radius of neighborhood (in number of cells).

        Returns :
            The list of neighboring cells.
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

                # Make sure the coordinates are not off the surface.
                if 0 <= neighbor_row < rows and 0 <= neighbor_col < cols:
                    neighbors.append(cell_grid[neighbor_row][neighbor_col])

        return neighbors

    @staticmethod
    def __get_material():
        """
        Returns a Material according to its probability of occurrence.

        Returns :
            Material : Material object.
        """
        probabilities = {
            Material.GRASS : 0.5, #0.50
            Material.WOOD : 0.45,
            Material.FUEL : 0.05
        }

        rand_num = np.random.random()

        # Cumulative probability test.
        # The random number between 0 and 1 is compared with these cumulative thresholds:
        # 1st pass of the 'cumulative_proba' loop = 0.5.
        # 2nd pass run 'cumulative_proba' = 0.95.
        # 3rd pass of the 'cumulative_proba' loop = 1.
        # At each of these passes, a check is made to see if 'rand_num' is less than or equal to 'cumulative_proba'.
        # If so, the function returns the material associated with the probability value.
        cumulative_proba = 0
        for material, proba in probabilities.items():
            cumulative_proba += proba

            if rand_num < cumulative_proba:
                return material

    def draw(self):
        """
        Draw the cell on the main surface.
        """
        if self.material == Material.GRASS:
            color = Material.GRASS.value.color
        elif self.material == Material.WOOD:
            color = Material.WOOD.value.color
        elif self.material == Material.FUEL:
            color = Material.FUEL.value.color
        else:
            color = colors.white

        # Convert grid coordinates to pixel coordinates.
        x_pos = (MARGIN + CELL_WIDTH) * self.col + MARGIN
        y_pos = (MARGIN + CELL_HEIGHT) * self.row + MARGIN

        if self.is_burning:
            if SHOW_GRADIENT_ANIMATION:
                # --- Flame Color Gradient Based on Temperature and Oscillation ---
                # 1. Normalize Temperature:
                #    - We want to map the temperature to a range between 0 and 1.
                #    - `self.temperature - self.material.value.ignition_temp`: We subtract the ignition temperature
                #      because we're only interested in the temperature above which the cell is burning.
                #    - `MAX_TEMP - self.material.value.ignition_temp`: This is the maximum possible range of
                #      temperatures above the ignition point.
                #    - `flame_intensity` will be 0 when `self.temperature` equals `self.material.value.ignition_temp`
                #      and it will be 1 when `self.temperature` equals `MAX_TEMP`.
                flame_intensity = (self.temperature - self.material.value.ignition_temp) / (
                        MAX_TEMP - self.material.value.ignition_temp)  # Normalize temperature

                # 2. Clamp the Intensity:
                #    - We clamp the intensity between 0 and 1 using `np.clip()`.
                #    - This ensures that `flame_intensity` never goes outside the [0, 1] range,
                #      even if the temperature goes outside the [ignition_temp, MAX_TEMP] range.
                flame_intensity = np.clip(flame_intensity, 0, 1)  # Clamp between 0 and 1

                # 3. Create an Oscillation Factor:
                #    - This part creates a value that oscillates smoothly between 0 and 1 over time.
                #    - `pygame.time.get_ticks()`: Returns the number of milliseconds since `pygame.init()` was called.
                #    - `/ 200.0`: Divides by 200 to slow down the oscillation.
                #    - `* self.flame_oscillation`: Multiplies by a random value between 0.1 and 0.3 (set in the
                #      constructor) to make each cell's flame oscillate at a slightly different rate.
                #    - `np.sin(...)`: The sine function produces a smooth wave between -1 and 1.
                #    - `* 0.5 + 0.5`: Scales the wave to the [0, 1] range.
                oscillation_factor = np.sin(
                    pygame.time.get_ticks() / 200.0 * self.flame_oscillation) * 0.5 + 0.5  # Oscillate between 0 and 1

                # 4. Combine Intensity and Oscillation:
                #    - We multiply the `flame_intensity` by the `oscillation_factor`.
                #    - This means the color will vary between the color of the flame at the given intensity and black.
                gradient_value = flame_intensity * oscillation_factor

                # 5. Create the Color Gradient:
                #    - `np.interp()` is used to interpolate between colors.
                #    - `np.interp(gradient_value, [0, 0.5, 1], [255, 255, 255])`: The gradient is computed on the red
                #       component.
                #           - When gradient_value is 0: The red color will be 255.
                #           - When gradient_value is 0.5: The red color will be 255.
                #           - When gradient_value is 1: The red color will be 255.
                #    - `np.interp(gradient_value, [0, 0.5, 1], [255, 165, 0])`: The gradient is computed on the green
                #       component.
                #           - When gradient_value is 0: The green color will be 255.
                #           - When gradient_value is 0.5: The green color will be 165.
                #           - When gradient_value is 1: The green color will be 0.
                #    - `np.interp(gradient_value, [0, 1], [0, 0])`: The gradient is computed on the blue
                #       component.
                #           - When gradient_value is 0: The blue color will be 0.
                #           - When gradient_value is 1: The blue color will be 0.
                r = int(np.interp(gradient_value, [0, 0.5, 1], [255, 255, 255]))
                g = int(np.interp(gradient_value, [0, 0.5, 1], [255, 165, 0]))  # Orange in the middle
                b = int(np.interp(gradient_value, [0, 1], [0, 0]))
                color = (r, g, b)

                # Draw the cell with the calculated color.
                pygame.draw.rect(screen, color, [x_pos, y_pos, CELL_WIDTH, CELL_HEIGHT])

            else:
                pygame.draw.rect(screen, colors.red, [x_pos, y_pos, CELL_WIDTH, CELL_HEIGHT])

        elif self.burned:
            pygame.draw.rect(screen, colors.black, [x_pos, y_pos, CELL_WIDTH, CELL_HEIGHT])

        else:
            pygame.draw.rect(screen, color, [x_pos, y_pos, CELL_WIDTH, CELL_HEIGHT])
