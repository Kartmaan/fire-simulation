# 🔥 Fire Propagation Simulation
**A realistic simulation of fire propagation** using thermodynamic and combustion principles, developed in Python with Pygame and NumPy.

<iframe width="560" height="315" src="https://www.youtube.com/embed/OmK2kF2qTYU?si=78ztKPB9kArCnjM0" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

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