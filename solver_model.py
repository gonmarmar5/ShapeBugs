import numpy as np
import random
import gworld as world
from visualize import Visualize
from macros import *

#### CONSTANTS ####

WORLD_WIDTH = 10
WORLD_HEIGHT = 10
NUM_AGENTS = 10    # square of square_size - e

# Tamaño del cuadrado
square_size = 4

# Coordenadas del cuadrado centrado
square_center_x = WORLD_WIDTH // 2
square_center_y = WORLD_WIDTH // 2

# Calcular las esquinas del cuadrado
half_size = square_size // 2

square_top_left = (square_center_x - half_size, square_center_y - half_size)
square_top_right = (square_center_x + half_size, square_center_y - half_size)
square_bottom_left = (square_center_x - half_size, square_center_y + half_size)
square_bottom_right = (square_center_x + half_size, square_center_y + half_size)

# Crea un cuadrado de tamaño square_size centrado en el centro del mundo
GOAL = [
    (x, y) for x in range(square_center_x - half_size, square_center_x + half_size + 1)
    for y in range(square_center_y - half_size, square_center_y + half_size + 1)
]

class SolverModel:
    def __init__(self, world, visualize=None):
        self.world = world
        self.goal_pos = world.goal_pos
        self.vis = visualize
    
    def solve_step(self):
        """
        Realiza un paso en el proceso de solución.
        Implementa la lógica de movimiento aleatorio de los agentes con envolvimiento.
        Actualiza aindx_goalreached si un agente se encuentra dentro de una posición objetivo.
        """
        for agent in self.world.get_agents():
            if not self.world.aindx_goalreached[agent]:
                # Obtiene la posición actual del agente
                current_pos = self.world.aindx_cpos[agent]

                # Obtiene las posiciones vecinas posibles
                possible_moves = [
                    (current_pos[0] - 1, current_pos[1]),  # Movimiento hacia arriba
                    (current_pos[0] + 1, current_pos[1]),  # Movimiento hacia abajo
                    (current_pos[0], current_pos[1] - 1),  # Movimiento hacia la izquierda
                    (current_pos[0], current_pos[1] + 1)   # Movimiento hacia la derecha
                ]

                # Aplica envolvimiento horizontal y vertical
                possible_moves = [(x % self.world.h, y % self.world.w) for x, y in possible_moves]

                # Filtra las posiciones vecinas posibles para obtener solo las posiciones transitables
                valid_moves = [move for move in possible_moves if self.world.passable(move)]

                if valid_moves:
                    # Elije aleatoriamente una posición vecina válida y actualiza la posición del agente
                    new_pos = random.choice(valid_moves)
                    self.world.cells[current_pos[0]][current_pos[1]] = UNOCCUPIED
                    self.world.cells[new_pos[0]][new_pos[1]] = agent
                    self.world.aindx_cpos[agent] = new_pos

                    # Actualiza aindx_goalreached si el agente alcanza una posición objetivo
                    if new_pos in self.goal_pos:
                        self.world.aindx_goalreached[agent] = True

        # Verifica si todos los agentes han alcanzado una posición objetivo
        if all(self.world.aindx_goalreached[agent] for agent in self.world.get_agents()):
            print("¡Todos los agentes han alcanzado una posición objetivo!")
            self.vis.frame.destroy()  
            exit()  

        # Actualiza la visualización después de realizar los movimientos aleatorios
        if self.vis:
            for agent in self.world.get_agents():
                self.vis.update_agent_vis(agent)

if __name__ == "__main__":
    
    world_grid = world.GridWorld(WORLD_WIDTH, WORLD_HEIGHT)
    world_grid.add_agents_rand(NUM_AGENTS)
    world_grid.add_goal_pos(GOAL)

    vis = Visualize(world_grid)

    vis.draw_world()
    vis.draw_agents()

    vis.canvas.pack()
    vis.canvas.update()
    vis.canvas.after(100)

    solver = SolverModel(world_grid, vis)

    iter_val = 0

    while (True):
        solver.solve_step()
        finished = True
        agents_inside = 0
        
        for agent in world_grid.get_agents():
            if (world_grid.aindx_goalreached[agent]):
                agents_inside += 1

        print('- Iteración ', iter_val, '- Numero de agentes dentro de la forma: ', agents_inside)
        vis.canvas.update()
        vis.canvas.after(500)

        iter_val += 1
