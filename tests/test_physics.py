import unittest

import numpy as np

from src.material import Material
from src.physics import heat_conduction, update_ignition, update_combustion
from src.physics import (MIN_TEMP, MAX_TEMP, MEGAJOULES_TO_JOULES, KILOJOULES_TO_JOULES, OXYGEN_CONSUMPTION_FACTOR,
                         MIN_OXYGEN_RATE)

class TestHeatConduction(unittest.TestCase):
    def test_heat_conduction_no_transfer(self):
        """
        Test that heat conduction does not occur when all cells have the same temperature.
        """
        temp_grid = np.full((3, 3), 50.0)  # All cells at 50°C
        conductivity_grid = np.full((3, 3), 0.5)
        capacity_grid = np.full((3, 3), 1.0)
        delta_time = 0.1

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

        # Check if the temperature of the hottest cell decreased.
        self.assertLess(float(updated_grid[0, 0]), float(original_temp_grid[0, 0]))

        # Check if the temperature of its right neighbor increased.
        self.assertGreater(float(updated_grid[0, 1]), float(original_temp_grid[0, 1]))

        # Check if the temperature of its bottom neighbor increased.
        self.assertGreater(float(updated_grid[1, 0]), float(original_temp_grid[1, 0]))

    def test_heat_conduction_min_temp(self):
        """
        Test that no cell goes below the minimum temperature (MIN_TEMP) after heat conduction.
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
        Test that no cell exceeds the maximum temperature (MAX_TEMP) after heat conduction.
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

class TestUpdateIgnition(unittest.TestCase):
    def test_ignition_no_humidity(self):
        """
        Test that ignition occurs at the base ignition temperature when humidity is zero.
        """
        # Setup:
        # Create a 3x3 grid where the cell in the center is at the exact ignition temperature.
        # The humidity_grid is all zeros (no humidity).
        ignition_temp = 300.0
        temperature_grid = np.full((3, 3), ignition_temp - 10)
        temperature_grid[1, 1] = ignition_temp
        ignition_temp_grid = np.full((3, 3), ignition_temp)
        humidity_grid = np.zeros((3, 3))
        burned_grid = np.zeros((3, 3), dtype=bool)

        # Call the function:
        is_burning_grid = update_ignition(temperature_grid.copy(), ignition_temp_grid, humidity_grid, burned_grid)

        # Assertions:
        # The cell in the center should be burning (True).
        self.assertTrue(is_burning_grid[1, 1])
        # All other cells should not be burning (False).
        for i in range(3):
            for j in range(3):
                if i != 1 or j != 1:
                    self.assertFalse(is_burning_grid[i, j])

    def test_ignition_with_humidity(self):
        """
        Test that ignition is delayed (occurs at a higher temperature) when humidity is present.
        """
        # Setup:
        # Create a 3x3 grid where the cell in the center is at the base ignition temperature.
        # The humidity_grid has a value of 50.0 for all cells.
        ignition_temp = 300.0
        temperature_grid = np.full((3, 3), ignition_temp)
        ignition_temp_grid = np.full((3, 3), ignition_temp)
        humidity_grid = np.full((3, 3), 50.0)
        burned_grid = np.zeros((3, 3), dtype=bool)

        # Call the function:
        is_burning_grid = update_ignition(temperature_grid.copy(), ignition_temp_grid, humidity_grid, burned_grid)

        # Assertions:
        # No cells should be burning because of the humidity.
        # The temperatures of all cells are equal to the ignition temperature, if all cells had a humidity value of
        # zero, they would be on fire, but their humidity value (set to 50) delays combustion, so no cell should be
        # on fire here.
        for row in is_burning_grid:
            for cell_burning in row:
                self.assertFalse(cell_burning)

        # Setup 2:
        # Add a temperature of 100° to the center cell.
        # We greatly increase the temperature of the central cell to force ignition. Despite its humidity value, the
        # cell should be on fire.
        temperature_grid[1, 1] += 500.0
        # Call the function:
        is_burning_grid = update_ignition(temperature_grid.copy(), ignition_temp_grid, humidity_grid, burned_grid)

        # Assertions:
        # The cell in the center should be burning now.
        self.assertTrue(is_burning_grid[1, 1])
        # All other cells should not be burning.
        for i in range(3):
            for j in range(3):
                if i != 1 or j != 1:
                    self.assertFalse(is_burning_grid[i, j])

    def test_no_reignition_after_burning(self):
        """
        Verify that a cell that has already burned does not re-ignite even if conditions are met.
        """
        # Setup:
        # Create a 3x3 grid with a cell that has already burned.
        ignition_temp = 300.0
        temperature_grid = np.full((3, 3), ignition_temp)
        ignition_temp_grid = np.full((3, 3), ignition_temp)
        humidity_grid = np.zeros((3, 3))
        burned_grid = np.zeros((3, 3), dtype=bool)
        burned_grid[1, 1] = True # The central cell is burned

        # Call the function:
        is_burning_grid = update_ignition(temperature_grid.copy(), ignition_temp_grid, humidity_grid, burned_grid)

        # Assertions:
        # The cell in the center should not ignite because it is burned.
        self.assertFalse(is_burning_grid[1, 1])

       # The other cells should be on fire
        for i in range(3):
            for j in range(3):
                if i != 1 or j != 1:
                    self.assertTrue(is_burning_grid[i, j])

class TestUpdateCombustion(unittest.TestCase):
    def setUp(self):
        self.cells_number = (3, 3)
        self.delta_time = 0.1
        self.fuel_start = 100.0
        self.oxygen_start = 21.0
        self.oxygen_consumption_factor = OXYGEN_CONSUMPTION_FACTOR
        self.temp = 400.0

        # Material property values
        self.test_material = Material.WOOD
        self.burn_rate = self.test_material.value.burn_rate
        self.combustion_heat = self.test_material.value.combustion_heat
        self.density = self.test_material.value.density
        self.thermal_capacity = self.test_material.value.thermal_capacity

        # Material property grids
        self.fuel_grid = np.full(self.cells_number, self.fuel_start)
        self.oxygen_grid = np.full(self.cells_number, 21.0)
        self.temperature_grid = np.full(self.cells_number, self.temp)
        self.burn_rate_grid = np.full(self.cells_number, self.burn_rate)
        self.combustion_heat_grid = np.full(self.cells_number, self.combustion_heat)
        self.density_grid = np.full(self.cells_number, self.density)
        self.thermal_capacity_grid = np.full(self.cells_number, self.thermal_capacity)

    def test_fuel_consumption(self):
        """Test that burning cells consume fuel correctly."""
        is_burning_grid = np.array([
            [False, False, False],
            [False, True, False],
            [False, False, False]
        ])

        # Expected fuel consumption
        fuel_consumed_expected = self.burn_rate * self.delta_time

        # Execution
        _, updated_fuel_grid, _, _, _ = update_combustion(self.temperature_grid.copy(), self.fuel_grid.copy(),
                                                          self.oxygen_grid.copy(), is_burning_grid.copy(),
                                                          self.burn_rate_grid, self.combustion_heat_grid,
                                                          self.density_grid, self.thermal_capacity_grid,
                                                          self.delta_time)

        # Assertions
        # Check fuel consumption in burning cell.
        self.assertAlmostEqual(updated_fuel_grid[1, 1], self.fuel_start - fuel_consumed_expected)

        # Check fuel consumption in non-burning cells.
        self.assertEqual(updated_fuel_grid[0, 0], self.fuel_start)

        # Check that no cell has negative fuel
        for row in updated_fuel_grid:
            for fuel in row:
                self.assertGreaterEqual(fuel, 0.0)

    def test_heat_generation(self):
        """Test that burning cells generate heat correctly."""
        cell_volume = 1.0

        is_burning_grid = np.array([
            [False, False, False],
            [False, True, False],
            [False, False, False]
        ])

        # Expected fuel consumption
        fuel_consumed_expected = self.burn_rate * self.delta_time
        cell_mass = cell_volume * self.density
        # Expected heat generated
        heat_generated_expected = fuel_consumed_expected * self.combustion_heat * MEGAJOULES_TO_JOULES
        # Expected temperature delta
        delta_temp_expected = heat_generated_expected / (cell_mass * self.thermal_capacity * KILOJOULES_TO_JOULES)

        # Execution
        updated_temperature_grid, _, _, _, _ = update_combustion(self.temperature_grid.copy(), self.fuel_grid.copy(),
                                                                 self.oxygen_grid.copy(), is_burning_grid.copy(),
                                                                 self.burn_rate_grid, self.combustion_heat_grid,
                                                                 self.density_grid, self.thermal_capacity_grid,
                                                                 self.delta_time)

        # Assertions
        # Check temperature increase in burning cell
        self.assertAlmostEqual(updated_temperature_grid[1, 1], self.temp + delta_temp_expected)

        # Check temperature in non-burning cells
        self.assertEqual(updated_temperature_grid[0, 0], self.temp)

        # Check that no cell exceed MAX_TEMP
        for row in updated_temperature_grid:
            for temp in row:
                self.assertLessEqual(temp, MAX_TEMP)

    def test_oxygen_consumption(self):
        """Test that burning cells consume oxygen correctly."""
        is_burning_grid = np.array([
            [False, False, False],
            [False, True, False],
            [False, False, False]
        ])

        # Expected fuel consumption
        fuel_consumed_expected = self.burn_rate * self.delta_time
        # Expected oxygen consumption
        oxygen_consumed_expected = fuel_consumed_expected * self.oxygen_consumption_factor * self.delta_time

        # Execution
        _, _, updated_oxygen_grid, _, _ = update_combustion(self.temperature_grid.copy(), self.fuel_grid.copy(),
                                                            self.oxygen_grid.copy(), is_burning_grid.copy(),
                                                            self.burn_rate_grid, self.combustion_heat_grid,
                                                            self.density_grid, self.thermal_capacity_grid,
                                                            self.delta_time)

        # Assertions
        # Check oxygen consumption in burning cell
        self.assertAlmostEqual(updated_oxygen_grid[1, 1], self.oxygen_start - oxygen_consumed_expected)

        # Check oxygen in non-burning cells
        self.assertEqual(updated_oxygen_grid[0, 0], self.oxygen_start)

        # Check that no cell has negative oxygen
        for row in updated_oxygen_grid:
            for oxygen in row:
                self.assertGreaterEqual(oxygen, 0.0)

    def test_stop_burning_no_fuel(self):
        """Test that a cell stop burning when it does not have fuel anymore."""
        fuel_grid = np.array([
            [100.0, 100.0, 100.0],
            [100.0, 0.0, 100.0],
            [100.0, 100.0, 100.0]
        ])

        is_burning_grid = np.array([
            [True, True, True],
            [True, True, True],
            [True, True, True]
        ])

        # Execution
        _, _, _, updated_is_burning_grid, _ = update_combustion(self.temperature_grid.copy(), fuel_grid.copy(),
                                                                self.oxygen_grid.copy(), is_burning_grid.copy(),
                                                                self.burn_rate_grid, self.combustion_heat_grid,
                                                                self.density_grid, self.thermal_capacity_grid,
                                                                self.delta_time)

        # Assertions
        # Check that the central cell is no more burning because he does not have fuel anymore.
        self.assertFalse(updated_is_burning_grid[1, 1])

        # Check that cells that have fuel are still burning
        self.assertTrue(updated_is_burning_grid[0, 0])

    def test_stop_burning_no_oxygen(self):
        """Test that a cell stop burning when it does not have enough oxygen anymore."""
        oxygen_limit = MIN_OXYGEN_RATE - 1.0

        oxygen_grid = np.array([
            [21.0, 21.0, 21.0],
            [21.0, oxygen_limit, 21.0],
            [21.0, 21.0, 21.0]
        ])

        is_burning_grid = np.array([
            [True, True, True],
            [True, True, True],
            [True, True, True]
        ])

        # Execution
        _, _, _, updated_is_burning_grid, _ = update_combustion(self.temperature_grid.copy(), self.fuel_grid.copy(),
                                                                oxygen_grid.copy(), is_burning_grid.copy(),
                                                                self.burn_rate_grid, self.combustion_heat_grid,
                                                                self.density_grid, self.thermal_capacity_grid,
                                                                self.delta_time)

        # Assertions
        # Check that the central cell is no more burning because it doesn't have enough oxygen anymore.
        self.assertFalse(updated_is_burning_grid[1, 1])

        # Check that cells that have enough oxygen are still burning
        self.assertTrue(updated_is_burning_grid[0, 0])

if __name__ == '__main__':
    unittest.main()