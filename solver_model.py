import time
import numpy as np
import random
import gworld as world
from visualize import Visualize
from macros import *

#### CONSTANTS ####

WORLD_WIDTH = 21
WORLD_HEIGHT = 21
NUM_AGENTS = 120    # square of square_size - e
NUM_ITERATIONS = 100
TIME_RESET = 100

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
        Move an agent using a simplified heuristic to bias towards the goal.

        Parameters:
        - agent: Index of the agent to move.
        """
        current_pos = self.world.aindx_cpos[agent]
        goal_pos = self.goal_pos

        new_pos = self.bias_towards_goal(current_pos, goal_pos)
        self.update_agent_position(agent, current_pos, new_pos)

    def bias_towards_goal(self, current_pos, goal_pos, probability=0.8):
        """
        Move towards the goal with a certain probability, otherwise move randomly.

        Parameters:
        - current_pos: Current position.
        - goal_pos: List of goal positions.
        - probability: Probability of moving towards the goal (default is 0.8).

        Returns:
        - tuple: New position.
        """
        if random.random() < probability:
            # Move towards a random goal position
            chosen_goal = random.choice(goal_pos)
            dx = chosen_goal[0] - current_pos[0]
            dy = chosen_goal[1] - current_pos[1]

            new_pos = (
                current_pos[0] + int(dx / abs(dx)) if dx != 0 else current_pos[0],
                current_pos[1] + int(dy / abs(dy)) if dy != 0 else current_pos[1]
            )
        else:
            # Move randomly
            valid_moves = self.get_valid_moves(current_pos)
            new_pos = random.choice(valid_moves) if valid_moves else current_pos

        return new_pos

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
        if current_pos in self.goal_pos:
                self.world.aindx_goalreached[agent] = True
        else:
            self.world.aindx_goalreached[agent] = False
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
            else:
                self.world.aindx_goalreached[agent] = False
        # else:
            # La casilla está ocupada, no permite que el agente se mueva
            # print(f"No se puede mover el agente {agent} a la casilla ocupada {new_pos}")

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
                vis.remove_agent_vis(agent) 

    def check_goal_completion():
        """
        Verifica si todos los agentes han alcanzado una posición objetivo.
        Si es así, imprime un mensaje, cierra la ventana de visualización y termina la ejecución del programa.
        """
        if all(world_grid.aindx_goalreached[agent] for agent in world_grid.get_agents()):
            print("¡Todos los agentes han alcanzado una posición objetivo!")
            vis.frame.destroy()
            exit()

    def remove_agents_outside_shape():
        ''' 
        Remove agents outside the shape
        '''
        print("Se alcanzaron ", NUM_ITERATIONS, " iteraciones. Eliminando agentes fuera de la figura.")
        agents_outside = []
        for agent in world_grid.get_agents():
            if not world_grid.aindx_goalreached[agent]:
                agents_outside.append(agent)
        
        for agent in agents_outside:
            world_grid.remove_agent(agent)
            vis.remove_agent_vis(agent) 
        vis.canvas.update()
        vis.canvas.after(TIME_RESET)

    def move_goal_pos_left(num_iter):
        iter_val = 0
        while iter_val != num_iter:
            # If any cell of new_goal_positions is the border of the grid, then stop
            if not any(x == 0 or x == WORLD_WIDTH - 1 or y == 0 or y == WORLD_WIDTH - 1 for x, y in world_grid.goal_pos):

                new_goal_positions = [(gy, gx - 1) for (gy, gx) in world_grid.goal_pos]

                world_grid.update_goal_pos(new_goal_positions)
                vis.draw_world()
                vis.draw_agents()

                vis.canvas.update()
            
            solver = SolverModel(world_grid, vis)
            solver.solve_step()

            agents_inside = 0

            for agent in world_grid.get_agents():
                if world_grid.aindx_goalreached[agent]:
                    agents_inside += 1

            print('- Iteración ', iter_val, '- Numero de agentes dentro de la forma: ', agents_inside)
            vis.canvas.update()
            vis.canvas.after(TIME_RESET)
            iter_val += 1

    def move_goal_pos_up(num_iter):
        iter_val = 0
        while iter_val != num_iter:
            # If any cell of new_goal_positions is the border of the grid, then stop
            if not any(x == 0 or x == WORLD_WIDTH - 1 or y == 0 or y == WORLD_WIDTH - 1 for x, y in world_grid.goal_pos):

                new_goal_positions = [(gy - 1, gx) for (gy, gx) in world_grid.goal_pos]
                world_grid.update_goal_pos(new_goal_positions)
                vis.draw_world()
                vis.draw_agents()

                vis.canvas.update()
            solver = SolverModel(world_grid, vis)
            solver.solve_step()

            agents_inside = 0

            for agent in world_grid.get_agents():
                if world_grid.aindx_goalreached[agent]:
                    agents_inside += 1

            print('- Iteración ', iter_val, '- Numero de agentes dentro de la forma: ', agents_inside)
            vis.canvas.update()
            vis.canvas.after(TIME_RESET)
            iter_val += 1

    def move_goal_pos_right(num_iter):
        iter_val = 0
        while iter_val != num_iter:
            # If any cell of new_goal_positions is the border of the grid, then stop
            if not any(x == 0 or x == WORLD_WIDTH - 1 or y == 0 or y == WORLD_WIDTH - 1 for x, y in world_grid.goal_pos):

                new_goal_positions = [(gy, gx + 1) for (gy, gx) in world_grid.goal_pos]

                world_grid.update_goal_pos(new_goal_positions)
                vis.draw_world()
                vis.draw_agents()

                vis.canvas.update()
            
            solver = SolverModel(world_grid, vis)
            solver.solve_step()

            agents_inside = 0

            for agent in world_grid.get_agents():
                if world_grid.aindx_goalreached[agent]:
                    agents_inside += 1

            print('- Iteración ', iter_val, '- Numero de agentes dentro de la forma: ', agents_inside)
            vis.canvas.update()
            vis.canvas.after(TIME_RESET)
            iter_val += 1
    
    def move_goal_pos_down(num_iter):
        iter_val = 0
        while iter_val != num_iter:
            # If any cell of new_goal_positions is the border of the grid, then stop
            if not any(x == 0 or x == WORLD_WIDTH - 1 or y == 0 or y == WORLD_WIDTH - 1 for x, y in world_grid.goal_pos):

                new_goal_positions = [(gy + 1, gx) for (gy, gx) in world_grid.goal_pos]
                world_grid.update_goal_pos(new_goal_positions)
                vis.draw_world()
                vis.draw_agents()

                vis.canvas.update()
            solver = SolverModel(world_grid, vis)
            solver.solve_step()

            agents_inside = 0

            for agent in world_grid.get_agents():
                if world_grid.aindx_goalreached[agent]:
                    agents_inside += 1

            print('- Iteración ', iter_val, '- Numero de agentes dentro de la forma: ', agents_inside)
            vis.canvas.update()
            vis.canvas.after(TIME_RESET)
            iter_val += 1

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

    while (iter_val != NUM_ITERATIONS):
        '''
        First iterations to form the shape
        '''
        solver.solve_step()

        agents_inside = 0
        
        for agent in world_grid.get_agents():
            if (world_grid.aindx_goalreached[agent]):
                agents_inside += 1
        
        # Funciones que modifican el comportamiento de los agentes, descomentar para probar
        agents_translation()
        #agents_death()
        
        print('- Iteración ', iter_val, '- Numero de agentes dentro de la forma: ', agents_inside)
        vis.canvas.update()
        if iter_val == 25:
            time.sleep(2)
        vis.canvas.after(TIME_RESET)

        iter_val += 1
    
    print("Se terminó el movimiento de los agentes. Han terminado: ", agents_inside , "agentes dentro de la figura de ", NUM_AGENTS, " agentes iniciales.")

    # Eliminamos todos los agentes fuera de la figura 
    remove_agents_outside_shape()
    print("Se han eliminado", NUM_AGENTS - len(world_grid.get_agents()) ,"agentes que estaban fuera de la figura.")
    
    # Movemos la figura alrededor del mapa
    move_goal_pos_left(WORLD_WIDTH//4 - 1)
    print("Se alcanzaron ", WORLD_WIDTH//4 - 1, " iteraciones. Moviendo la figura hacia arriba.")
    time.sleep(0.1)
    move_goal_pos_up(WORLD_HEIGHT//4 - 1)
    print("Se alcanzaron ", WORLD_WIDTH//2 - 2, " iteraciones. Moviendo la figura hacia la derecha.")
    time.sleep(0.1)
    move_goal_pos_right(WORLD_WIDTH//2 - 2)
    print("Se alcanzaron ", WORLD_WIDTH//2 - 2, " iteraciones. Moviendo la figura hacia abajo.")
    time.sleep(0.1)
    move_goal_pos_down(WORLD_HEIGHT//2 - 2)
    print("Se alcanzaron ", WORLD_HEIGHT//2 - 2, " iteraciones. Moviendo la figura hacia la izquierda.")
    time.sleep(0.1)
    move_goal_pos_left(WORLD_WIDTH//4 - 1)
    print("Se alcanzaron ", WORLD_WIDTH//4 - 1, " iteraciones. Moviendo la figura hacia arriba.")
    time.sleep(0.1)
    move_goal_pos_up(WORLD_HEIGHT//4 - 1)
    
    agents_inside = 0
    for agent in world_grid.get_agents():
        if (world_grid.aindx_goalreached[agent]):
            agents_inside += 1
    print("Se terminó el movimiento de la figura. Han terminado: ", agents_inside , "agentes dentro de la figura de ", NUM_AGENTS, " agentes iniciales. (", round(agents_inside/NUM_AGENTS*100,2), "%")
    time.sleep(5)