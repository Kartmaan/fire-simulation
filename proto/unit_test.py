import unittest
from cell_objects import Cell, Material, MaterialProperties

class TestHeatConduction(unittest.TestCase):
    def setUp(self):
        self.cell1 = Cell(0, 0)
        self.cell2 = Cell(0, 1)

        self.cell1.material = Material.WOOD
        self.cell2.material = Material.GRASS

        self.grid = [[self.cell1, self.cell2]]

    def test_heat_conduction_between_cells(self):
        self.cell1.temperature = 500.0
        self.cell2.temperature = 20.0
        initial_temp_cell1 = self.cell1.temperature
        initial_temp_cell2 = self.cell2.temperature

        # Conduction de chaleur entre la cellule source et cible.
        self.cell1.heat_conduction(self.grid, delta_time=0.1)

        # La température de la cellule source doit diminuer.
        self.assertLess(self.cell1.temperature, initial_temp_cell1)

        # La température de la cellule cible doit augmenter.
        self.assertGreater(self.cell2.temperature, initial_temp_cell2)

if __name__ == '__main__':
    unittest.main()