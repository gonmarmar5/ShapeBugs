import numpy as np
import random
import gworld as world
from visualize import Visualize
from macros import *

#### CONSTANTS ####

WORLD_WIDTH = 21
WORLD_HEIGHT = 21
NUM_AGENTS = 120    # square of square_size - e

# Tamaño del cuadrado
square_size = 10

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
                self.move_agent_within_goal_based_on_density(agent)

        self.check_goal_completion()

        self.update_visualization()

    ### Agentes fuera de la figura ####
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

    ### Agentes dentro de la figura ####

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

    def move_agent_within_goal_based_on_density(self, agent):
        """
        Mueve un agente en base a la densidad de agentes dentro de la figura.

        Parameters:
        - agent: Índice del agente a mover.
        """
        current_pos = self.world.aindx_cpos[agent]
        valid_moves = self.get_valid_moves_within_goal(current_pos)
        
        if valid_moves:
            # Divide la figura objetivo en subregiones
            subregions = self.divide_goal_into_subregions()

            # Calcula la densidad de agentes en cada subregión
            agent_density_in_subregions = [self.calculate_agent_density(subregion) for subregion in subregions]

            # Encuentra la subregión menos densa y elige una posición en esa subregión
            min_density_subregion = min(enumerate(agent_density_in_subregions), key=lambda x: x[1])[0]
            
            new_pos = self.choose_position_in_subregion(min_density_subregion, subregions)

            # Mueve el agente a la nueva posición
            self.update_agent_position(agent, current_pos, new_pos) # todo un agente no puede moverse a mas de 1 casilla

    def divide_goal_into_subregions(self, subregion_size=11):    
        """
        Divide la figura objetivo en subregiones.

        Parameters:
        - subregion_size: Tamaño de las subregiones.

        Returns:
        - list: Lista de subregiones.
        """
        subregions = []

        for i in range(0, len(self.goal_pos), subregion_size):
            subregion = self.goal_pos[i:i+subregion_size]
            subregions.append(subregion)
        return subregions

    def calculate_agent_density(self, subregion):
        """
        Calcula la densidad de agentes en una subregión.

        Parameters:
        - subregion: Subregión de la figura objetivo.

        Returns:
        - float: Densidad de agentes en la subregión.
        """
        num_agents = 0
        # Calcula el número de agentes en la subregión
        for agent in self.world.get_agents():
            if self.world.aindx_goalreached[agent]:
                if self.world.aindx_cpos[agent] in subregion:
                    num_agents += 1

        # Calcula el tamaño total de la subregión
        subregion_size = len(subregion)

        # Calcula la densidad de agentes dividiendo el número de agentes por el tamaño total de la subregión
        density = num_agents / subregion_size if subregion_size > 0 else 0.0
        return density

    def choose_position_in_subregion(self, subregion_idx, subregions):
        """
        Elige una posición dentro de una subregión considerando maximizar la densidad en el centro de GOAL.

        Parameters:
        - subregion_idx: Índice de la subregión en la que se moverá el agente.
        - subregions: Lista de subregiones.

        Returns:
        - tuple: Nueva posición en la subregión.
        """
        # Obtén la subregión correspondiente al índice
        subregion = subregions[subregion_idx]

        # Obtén las posiciones en el centro de GOAL
        center_goal_positions = [(pos[0], pos[1]) for pos in subregion if (pos[0], pos[1]) in self.goal_pos]

        if center_goal_positions:
            # Si hay casillas en el centro de GOAL, elige una posición aleatoria en el centro
            new_pos = random.choice(center_goal_positions)
        else:
            # Si no hay casillas en el centro de GOAL, elige una posición aleatoria en la subregión
            new_pos = random.choice(subregion)

        return new_pos

    ### Global functions ####    

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
        # else:
            # La casilla está ocupada, no permite que el agente se mueva
            # print(f"No se puede mover el agente {agent} a la casilla ocupada {new_pos}")

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

    def agents_translation(agents_to_move = NUM_AGENTS//4, iter = 25):
        # Mueve los agentes aleatoriamente después de 'iter' iteraciones
        if agents_inside > agents_to_move and iter_val == iter:
            agents_to_move = random.sample(world_grid.get_agents_in_goal(), agents_to_move)
            for agent in agents_to_move:
                world_grid.move_agent_randomly(agent)
                vis.update_agent_vis(agent, True)

    def agents_death(num_of_death = NUM_AGENTS//4, iter = 25):
        if iter_val == iter:
            # Eliminar algunos agentes
            agents_to_remove = random.sample(world_grid.get_agents(), num_of_death)
            for agent in agents_to_remove:
                world_grid.remove_agent(agent)
                vis.remove_agent_vis(agent)  # Asegúrate de tener una función para eliminar visualmente al agente

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
        
        #agents_translation()
        #agents_death()
        
        print('- Iteración ', iter_val, '- Numero de agentes dentro de la forma: ', agents_inside)
        vis.canvas.update()
        vis.canvas.after(500)

        iter_val += 1