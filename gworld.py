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