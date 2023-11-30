from macros import *
import numpy as np
from gworld import *
from tkinter import *

#### CONSTANTS ####

FRAME_HEIGHT = 600
FRAME_WIDTH = 600
FRAME_MARGIN = 10
CELL_MARGIN = 5
COLORS = ['red', 'green', 'blue']

class Visualize:
    def __init__(self, world_data):
        """
        Inicializa la visualización del mundo.

        Parameters:
        - world_data: Objeto GridWorld que contiene la información del mundo.
        """
        self.frame = Tk()
        self.canvas = Canvas(self.frame, width=FRAME_WIDTH, height=FRAME_HEIGHT)
        self.canvas.grid()
        self.world = world_data
        world_data.visualize = self
        self.cell_h, self.cell_w = self.get_cell_size()
        self.agent_h, self.agent_w = self.get_agent_size()
        self.vis_cells = np.zeros_like(self.world.cells, dtype=int)
        self.aindx_obj = dict()

    

    def draw_world(self):
        """
        Dibuja la cuadrícula del mundo en la interfaz gráfica.
        """
        nrows, ncols = self.world.get_size()
        for row in range(nrows):
            for col in range(ncols):
                if (row, col) in self.world.goal_pos:
                    fill_color = 'lightgrey'  # Color gris claro para las casillas GOAL
                else:
                    fill_color = 'white'
                self.vis_cells[row][col] = self.canvas.create_rectangle(FRAME_MARGIN + self.cell_w * col,
                                                                        FRAME_MARGIN + self.cell_h * row,
                                                                        FRAME_MARGIN + self.cell_w * (col + 1),
                                                                        FRAME_MARGIN + self.cell_h * (row + 1))
                self.canvas.itemconfig(self.vis_cells[row][col], fill=fill_color, outline='black')

    def get_pos_in_cell(self, crow, ccol):
        """
        Obtiene las coordenadas de posición en píxeles de una celda en la interfaz gráfica.

        Parameters:
        - crow (int): Índice de fila de la celda.
        - ccol (int): Índice de columna de la celda.

        Returns:
        - tuple: Tupla (y1, x1, y2, x2) que representa las coordenadas en píxeles de la celda.
        """
        agent_h = self.agent_h
        agent_w = self.agent_w
        agent_y1 = FRAME_MARGIN + (crow * self.cell_h) + CELL_MARGIN
        agent_y2 = agent_y1 + agent_h
        agent_x1 = FRAME_MARGIN + (ccol * self.cell_w) + CELL_MARGIN
        agent_x2 = agent_x1 + agent_w
        return (agent_y1, agent_x1, agent_y2, agent_x2)

    def draw_agents(self):
        """
        Dibuja los agentes en la interfaz gráfica en función de sus posiciones en la cuadrícula.
        """
        for crow in range(self.world.h):
            for ccol in range(self.world.w):
                cell = self.world.cells[crow][ccol]
                if cell != UNOCCUPIED:
                    y1, x1, y2, x2 = self.get_pos_in_cell(crow, ccol)
                    color_indx = 0
                    self.aindx_obj[cell] = self.canvas.create_oval(x1, y1, x2, y2, fill=COLORS[color_indx],
                                                                    outline=COLORS[color_indx])

    def update_agent_vis(self, aindx):
        """
        Actualiza la posición visual de un agente en la interfaz gráfica.

        Parameters:
        - aindx (int): Índice del agente cuya posición visual se va a actualizar.
        """
        cy, cx = self.world.aindx_cpos[aindx]
        y1, x1, y2, x2 = self.get_pos_in_cell(cy, cx)

        # Cambia el color a rojo si el agente ha alcanzado una posición objetivo
        color = 'green' if (cy, cx) in self.world.goal_pos else 'red'
        
        self.canvas.coords(self.aindx_obj[aindx], x1, y1, x2, y2)
        self.canvas.itemconfig(self.aindx_obj[aindx], fill=color)

        

    def get_cell_size(self):
        """
        Calcula el tamaño de las celdas en función del tamaño de la cuadrícula y el tamaño de la interfaz gráfica.

        Returns:
        - tuple: Tupla (altura de celda, ancho de celda) en píxeles.
        """
        avail_h = FRAME_HEIGHT - 2 * FRAME_MARGIN
        avail_w = FRAME_WIDTH - 2 * FRAME_MARGIN
        nrows, ncols = self.world.get_size()
        cell_h = avail_h / nrows
        cell_w = avail_w / ncols
        return (cell_h, cell_w)

    def get_agent_size(self):
        """
        Calcula el tamaño de los agentes en función del tamaño de las celdas.

        Returns:
        - tuple: Tupla (altura de agente, ancho de agente) en píxeles.
        """
        agent_h = self.cell_h - 2 * CELL_MARGIN
        agent_w = self.cell_w - 2 * CELL_MARGIN
        return (agent_h, agent_w)