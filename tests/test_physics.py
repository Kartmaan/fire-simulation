import unittest
import numpy as np
from src.physics import heat_conduction, MIN_TEMP, MAX_TEMP

class TestHeatConduction(unittest.TestCase):
    def test_heat_conduction_no_transfer(self):
        """
        Test that heat conduction does not occur when all cells have the same temperature.
        """
        temp_grid = np.full((3, 3), 50.0)  # All cells at 50°C
        conductivity_grid = np.full((3, 3), 0.5)
        capacity_grid = np.full((3, 3), 1.0)
        delta_time = 1.0

        expected_grid = np.full((3, 3), 50.0) # No change expected

        updated_grid = heat_conduction(temp_grid.copy(), conductivity_grid, capacity_grid, delta_time)

        np.testing.assert_array_equal(updated_grid, expected_grid)

    def test_heat_conduction_transfer_high_to_low(self):
        """
        Test that heat transfers from a hotter cell to a colder cell by checking for a
        decrease in temperature in the hotter cell and an increase in temperature in
        the neighboring cells.
        """
        temp_grid = np.array([
            [100.0, 50.0, 50.0],
            [50.0, 50.0, 50.0],
            [50.0, 50.0, 50.0]
        ])
        conductivity_grid = np.full((3, 3), 0.5)
        capacity_grid = np.full((3, 3), 1.0)
        delta_time = 0.1

        original_temp_grid = temp_grid.copy()  # Keep a copy of the original temperature for comparison
        updated_grid = heat_conduction(temp_grid.copy(), conductivity_grid, capacity_grid, delta_time)
        print(updated_grid[0, 0])

        # Check if the temperature of the hottest cell decreased.
        self.assertLess(float(updated_grid[0, 0]), float(original_temp_grid[0, 0]))

        # Check if the temperature of its right neighbor increased.
        self.assertGreater(float(updated_grid[0, 1]), float(original_temp_grid[0, 1]))

        # Check if the temperature of its bottom neighbor increased.
        self.assertGreater(float(updated_grid[1, 0]), float(original_temp_grid[1, 0]))

    def test_heat_conduction_min_temp(self):
        """
        Test that no cell goes below the minimum temperature (20.0) after heat conduction.
        """
        min_temp = MIN_TEMP
        temp_grid = np.array([
            [30.0, 10.0, 10.0],
            [10.0, 10.0, 10.0],
            [10.0, 10.0, 10.0]
        ])
        conductivity_grid = np.full((3, 3), 0.5)
        capacity_grid = np.full((3, 3), 1.0)
        delta_time = 1.0

        updated_grid = heat_conduction(temp_grid.copy(), conductivity_grid, capacity_grid, delta_time)

        # Check if any cell has a temperature below the minimum.
        for row in updated_grid:
            for temp in row:
                self.assertGreaterEqual(temp, min_temp)

    def test_heat_conduction_max_temp(self):
        """
        Test that no cell goes below the minimum temperature (20.0) after heat conduction.
        """
        max_temp = MAX_TEMP
        temp_grid = np.array([
            [100.0, 8000.0, 8000.0],
            [8000, 8000.0, 8000.0],
            [8000.0, 8000.0, 8000.0]
        ])
        conductivity_grid = np.full((3, 3), 0.5)
        capacity_grid = np.full((3, 3), 1.0)
        delta_time = 1.0

        updated_grid = heat_conduction(temp_grid.copy(), conductivity_grid, capacity_grid, delta_time)

        # Check if any cell has a temperature below the minimum.
        for row in updated_grid:
            for temp in row:
                self.assertLessEqual(temp, max_temp)


if __name__ == '__main__':
    unittest.main()