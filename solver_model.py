import numpy as np
import random
import gworld as world
from visualize import Visualize
from macros import *

#### CONSTANTS ####

WORLD_WIDTH = 11
WORLD_HEIGHT = 11
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
                self.move_agent(agent)
            else:
                self.move_agent_within_goal(agent)
        self.check_goal_completion()

        self.update_visualization()

    def move_agent(self, agent):
        """
        Mueve un agente aleatoriamente dentro de la forma definida.

        Parameters:
        - agent: Índice del agente a mover.
        """
        current_pos = self.world.aindx_cpos[agent]
        valid_moves = self.get_valid_moves(current_pos)
        
        if valid_moves:
            new_pos = random.choice(valid_moves)
            self.update_agent_position(agent, current_pos, new_pos)

    def move_agent_within_goal(self, agent):
        """
        Mueve un agente aleatoriamente dentro de una casilla GOAL.

        Parameters:
        - agent: Índice del agente a mover.
        """
        current_pos = self.world.aindx_cpos[agent]
        valid_moves = self.get_valid_moves_within_goal(current_pos)
        
        if valid_moves:
            new_pos = random.choice(valid_moves)
            self.update_agent_position(agent, current_pos, new_pos)

    def get_valid_moves(self, current_pos):
        """
        Obtiene las posiciones vecinas válidas dentro de la forma definida.

        Parameters:
        - current_pos: Tupla que representa la posición actual.

        Returns:
        - list: Lista de posiciones vecinas válidas.
        """
        possible_moves = [
            (current_pos[0] - 1, current_pos[1]),  # Movimiento hacia arriba
            (current_pos[0] + 1, current_pos[1]),  # Movimiento hacia abajo
            (current_pos[0], current_pos[1] - 1),  # Movimiento hacia la izquierda
            (current_pos[0], current_pos[1] + 1)   # Movimiento hacia la derecha
        ]

        possible_moves = [(x % self.world.h, y % self.world.w) for x, y in possible_moves]

        valid_moves = [move for move in possible_moves if self.world.passable(move)]
        
        return valid_moves

    def get_valid_moves_within_goal(self, current_pos):
        """
        Obtiene las posiciones vecinas válidas dentro de una casilla GOAL.

        Parameters:
        - current_pos: Tupla que representa la posición actual.

        Returns:
        - list: Lista de posiciones vecinas válidas.
        """
        possible_moves = [
            (current_pos[0] - 1, current_pos[1]),  # Movimiento hacia arriba
            (current_pos[0] + 1, current_pos[1]),  # Movimiento hacia abajo
            (current_pos[0], current_pos[1] - 1),  # Movimiento hacia la izquierda
            (current_pos[0], current_pos[1] + 1)   # Movimiento hacia la derecha
        ]

        possible_moves = [(x % self.world.h, y % self.world.w) for x, y in possible_moves]

        valid_moves = [move for move in possible_moves if move in self.goal_pos]
        
        return valid_moves
    
    def update_agent_position(self, agent, current_pos, new_pos):
        """
        Actualiza la posición de un agente en el mundo.

        Parameters:
        - agent: Índice del agente a actualizar.
        - current_pos: Tupla que representa la posición actual.
        - new_pos: Tupla que representa la nueva posición.
        """
        if self.world.cells[new_pos[0]][new_pos[1]] == UNOCCUPIED:
            # La casilla está desocupada, permite que el agente se mueva
            self.world.cells[current_pos[0]][current_pos[1]] = UNOCCUPIED
            self.world.cells[new_pos[0]][new_pos[1]] = agent
            self.world.aindx_cpos[agent] = new_pos

            # Actualiza aindx_goalreached si el agente alcanza una posición objetivo
            if new_pos in self.goal_pos:
                self.world.aindx_goalreached[agent] = True
        else:
            # La casilla está ocupada, no permite que el agente se mueva
            print(f"No se puede mover el agente {agent} a la casilla ocupada {new_pos}")

    def check_goal_completion(self):
        """
        Verifica si todos los agentes han alcanzado una posición objetivo.
        Si es así, imprime un mensaje, cierra la ventana de visualización y termina la ejecución del programa.
        """
        if all(self.world.aindx_goalreached[agent] for agent in self.world.get_agents()):
            print("¡Todos los agentes han alcanzado una posición objetivo!")
            self.vis.frame.destroy()
            exit()

    def update_visualization(self):
        """
        Actualiza la visualización después de realizar los movimientos aleatorios.
        """
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
