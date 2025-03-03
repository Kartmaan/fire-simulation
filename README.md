# 🔥 Fire Propagation Simulation
**A realistic simulation of fire propagation** using thermodynamic and combustion principles, developed in Python with Pygame and NumPy.

[![Watch the video](/assets/readme/thumbnail.png)](https://youtu.be/OmK2kF2qTYU?si=1zg0MunhyuBElVxR)

## 📜 Description
This project models the propagation of a fire in a 2D environment composed of different materials. It integrates physical mechanisms such as:
- **Thermal conduction** between neighboring cells.
- **Self-sustained combustion** with fuel and oxygen consumption.
- The impact of **humidity** and material properties on ignition.

The simulation takes the form of a grid made up of a number of cells, each of which acts as a unit of space with a number of physical attributes, such as temperature or oxygen rate. Each cell also contains a material with intrinsic physical properties. 

![Cell](/assets/readme/cell.png)

The simulation supports 4 different materials:
- **Wood**
- **Grass**
- **Water** (_non-combustible_)
- **Gasoline**

These materials are randomly distributed on the grid according to the probability of appearance of each material.