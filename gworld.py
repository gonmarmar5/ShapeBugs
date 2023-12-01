import numpy as np
from macros import *
from visualize import *
import random

class GridWorld:
    def __init__(self, h, w):
        """
        Inicializa un mundo de cuadrícula con dimensiones h x w.

        Parameters:
        - h (int): Altura de la cuadrícula.
        - w (int): Ancho de la cuadrícula.
        """
        self.h = h
        self.w = w
        self.cells = np.zeros((h, w), dtype=int)
        self.visualize = None
        self.aindx_cpos = dict()          # Diccionario que mapea índices de agentes a sus posiciones (y, x).
        self.aindx_goalreached = dict()   # Diccionario que indica si cada agente ha alcanzado su objetivo.
        self.goal_pos = []                # Lista de posiciones objetivo en la cuadrícula.
        self.goal_blocked = []            # Lista de posiciones objetivo bloqueadas por agentes.

    def get_size(self):
        """
        Obtiene las dimensiones de la cuadrícula.

        Returns:
        - tuple: Tupla (altura, ancho) de la cuadrícula.
        """
        return (self.h, self.w)

    def get_agents(self):
        """
        Obtiene los índices de los agentes en la cuadrícula.

        Returns:
        - dict_keys: Claves del diccionario que representan los índices de los agentes.
        """
        return self.aindx_cpos.keys()

    def add_goal_pos(self, goal_pos):
        """
        Añade posiciones objetivo a la cuadrícula.

        Parameters:
        - goal_pos (list): Lista de tuplas (gy, gx) que representan las posiciones objetivo.
        """
        if goal_pos:
            print('Goal pos: ', goal_pos)
            for (gy, gx) in goal_pos:
                self.goal_pos.append((gy, gx))

    def add_agents(self, agents_spos):
        """
        Añade agentes a posiciones específicas en la cuadrícula.

        Parameters:
        - agents_spos (list): Lista de tuplas (sy, sx) que representan las posiciones iniciales de los agentes.

        Returns:
        - bool: True si los agentes se agregaron correctamente, False si no.
        """
        if agents_spos:
            print('Start pos: ', agents_spos)
            for (sy, sx) in agents_spos:
                nagents = len(self.aindx_cpos.keys())
                if self.cells[sy][sx] == UNOCCUPIED:
                    self.aindx_cpos[nagents + 1] = (sy, sx)
                    self.cells[sy][sx] = nagents + 1
                    if (sy, sx) in self.goal_pos:
                        self.aindx_goalreached[nagents + 1] = True
                        self.goal_blocked.append((sy, sx))
                    else:
                        self.aindx_goalreached[nagents + 1] = False
                else:
                    raise Exception('Cell has already been occupied!')
            return True
        return False

    def add_agents_rand(self, nagents=0):
        """
        Añade agentes aleatorios a la cuadrícula.

        Parameters:
        - nagents (int): Número de agentes a agregar de manera aleatoria.
        """
        if nagents:
            maxy, maxx = self.h - 1, self.w - 1
            agent_pos = set()
            while len(agent_pos) < nagents:
                y = random.randint(0, maxy)
                x = random.randint(0, maxx)
                if self.passable((y, x)):
                    agent_pos.add((y, x))
            self.add_agents(agent_pos)

    def passable(self, cell):
        """
        Verifica si una celda en la cuadrícula es transitable (no ocupada por un agente).

        Parameters:
        - cell (tuple): Tupla (y, x) que representa la posición de la celda.

        Returns:
        - bool: True si la celda es transitable, False si está ocupada.
        """
        y, x = cell[0], cell[1]
        if self.cells[y][x] != UNOCCUPIED:
            return False
        else:
            return True

    def get_aindx_from_pos(self, pos):
        """
        Obtiene el índice de un agente en función de su posición.

        Parameters:
        - pos (tuple): Tupla (y, x) que representa la posición del agente.

        Returns:
        - int: Índice del agente en la cuadrícula.
        """
        y, x = pos[0], pos[1]
        return self.cells[y][x]
    
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

        # Aplica envolvimiento horizontal y vertical
        possible_moves = [(x % self.h, y % self.w) for x, y in possible_moves]

        # Filtra las posiciones vecinas posibles para obtener solo las posiciones transitables
        valid_moves = [move for move in possible_moves if self.passable(move)]
        
        return valid_moves

    def get_agents_in_goal(self):
            """
            Obtiene los agentes que se encuentran dentro de la figura objetivo.

            Returns:
            - list: Lista de índices de agentes dentro de la figura objetivo.
            """
            agents_in_goal = [agent for agent, pos in self.aindx_cpos.items() if pos in self.goal_pos]
            return agents_in_goal

    def move_agent_randomly(self, agent):
        """
        Desplaza aleatoriamente un agente a una posición aleatoria en el mundo.

        Parameters:
        - agent: Índice del agente a desplazar.
        """
        if agent in self.aindx_cpos:
            current_pos = self.aindx_cpos[agent]

            # Obtiene una posición aleatoria en el mundo
            new_pos = (random.randint(0, self.h - 1), random.randint(0, self.w - 1))

            # Actualiza la posición del agente
            self.cells[current_pos[0]][current_pos[1]] = UNOCCUPIED
            self.cells[new_pos[0]][new_pos[1]] = agent
            self.aindx_cpos[agent] = new_pos

    def remove_agent(self, agent):
        """
        Elimina un agente del mundo.

        Parameters:
        - agent: Índice del agente a eliminar.
        """
        if agent in self.aindx_cpos:
            current_pos = self.aindx_cpos[agent]
            self.cells[current_pos[0]][current_pos[1]] = UNOCCUPIED
            del self.aindx_cpos[agent]
            del self.aindx_goalreached[agent]

