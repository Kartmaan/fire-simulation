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
    Represents a single cell in the fire simulation grid.

    Each cell holds a material and its physical properties, such as temperature, fuel level, and oxygen rate.
    It also manages the cell's state (burning or burned) and its visual representation.

    Attributes:
        row (int): The row index of the cell within the grid.
        col (int): The column index of the cell within the grid.
        material (Material): The type of material present in the cell.
        fuel_level (float): The current amount of fuel in the cell (0.0 to 100.0).
        temperature (float): The current temperature of the cell in degrees Celsius.
        oxygen_rate (float): The current oxygen level in the cell, as a percentage (0.0 to 100.0).
        wind_force (float): Not used.
        wind_direction (int): Not used.
        is_burning (bool): True if the cell is currently on fire, False otherwise.
        burned (bool): True if the cell has already been consumed by fire, False otherwise.
        manually ignited.
        flame_oscillation (float): A random factor that controls the oscillation rate of the cell's flame.
        color (tuple): The RGB color of the cell.
    """
    def __init__(self, row, col):
        # Position sur la grille
        self.row = row
        self.col = col

        # Physical attributes
        self.material: Material = self.__get_material()
        self.fuel_level = 100.0
        self.temperature = 20.0 # °C
        self.oxygen_rate = 21.0 # %

        self.wind_force = 40 # Not used
        self.wind_direction = -1 # Not used

        # Physical states
        self.is_burning = False
        self.burned = False

        # Visual attributes
        self.flame_oscillation = np.random.uniform(0.1, 0.3)
        self.color = self.material.value.color

    @staticmethod
    def __get_material():
        """
        Returns a Material according to its probability of occurrence.

        Returns :
            Material : Material object.
        """
        probabilities = {
            Material.GRASS : 0.40,
            Material.WOOD : 0.35,
            Material.WATER : 0.15,
            Material.GASOLINE : 0.10,
        }

        rand_num = np.random.random()

        # Cumulative probability test.
        # The random number between 0 and 1 is compared with these cumulative thresholds:
        # - 1st pass of the 'cumulative_proba' loop = 0.5.
        # - 2nd pass run 'cumulative_proba' = 0.95.
        # - 3rd pass of the 'cumulative_proba' loop = 1.
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
        color = self.color

        # Convert grid coordinates to pixel coordinates.
        x_pos = (MARGIN + CELL_WIDTH) * self.col + MARGIN
        y_pos = (MARGIN + CELL_HEIGHT) * self.row + MARGIN

        # --- Flame Color Gradient Based on Temperature and Oscillation ---
        if self.is_burning:
            if SHOW_GRADIENT_ANIMATION:
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
