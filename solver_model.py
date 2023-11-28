import numpy as np

import gworld as world
import cost_heur_astar as ch_astar
from visualize import *


#### CONSTANTS ####

WORLD_WIDTH = 15
WORLD_HEIGHT = 15
NUM_AGENTS = 15
GOAL = ((3,2),(4,2),(5,2),(2,3),(6,3),(2,4),(6,4), \
        (3,6),(4,6),(5,6),(6,6),(2,7),(5,7),(3,8),(4,8),(5,8),(6,8), \
        (3,10),(6,10),(2,11),(4,11),(6,11),(2,12),(5,12) \
        ) 

def get_boundwalls(world):
    h, w = world.get_size()
    bwalls = set()
    for x in range(w):
        bwalls.add( (0,x) )
        bwalls.add( (h-1,x) )
    for y in range(h):
        bwalls.add( (y,0) )
        bwalls.add( (y,w-1) )
    return tuple(bwalls)

class SolverModel:
    def __init__(self, world, visualize = None):
        self.world = world
        self.goal_pos = world.goal_pos
        self.cost_heur = dict()
        self.update_cost_heur()
        self.needs_update = False
        self.vis = visualize

    def update_cost_heur(self):
        agents, goals = self.update_goal_pos()
        start = []
        for agent in agents:
            start.append(self.world.aindx_cpos[agent])
        self.cost_heur = ch_astar.get_costmat(self.world.get_nbor_cells,
                                        goals,
                                        start,
                                        lambda cell: 1,
                                        lambda cell: cell not in self.world.goal_blocked and not self.world.is_blocked(cell[0], cell[1]),
                                        self.cost_heur )
        return self.cost_heur

    def update_goal_pos(self):
        agents = []
        goal_pos = self.goal_pos
        for agent in self.world.get_agents():
            if(self.world.aindx_goalreached[agent]):
                if( self.world.aindx_cpos[agent] in goal_pos ):
                    goal_pos.remove( self.world.aindx_cpos[agent] )
            else:
                agents.append( agent )
        self.goal_pos = goal_pos
        return agents, goal_pos

    def agent_greedy_step(self, agent):
        cpos = self.world.aindx_cpos[agent]
        nbors = self.world.get_nbor_cells(cpos)

        nbor0 = nbors[-1]
        best_nbor = nbor0
        # print self.cost_heur
        min_cost = self.cost_heur[nbor0][0]

        for nbor in nbors:
            if(self.world.passable(nbor) and nbor in self.cost_heur):
                tcost = self.cost_heur[nbor][0]
                if(tcost < min_cost):
                    min_cost = tcost
                    best_nbor = nbor

        nxt_action = self.world.pos_to_action(cpos, best_nbor)
        return best_nbor, nxt_action

    def solve_step(self):
        act_agents, goal_pos = self.update_goal_pos()
        random.shuffle(act_agents)

        for agent in act_agents:

            self.update_goal_pos()

            if (self.needs_update):
                self.update_cost_heur()
                self.needs_update = False

            best_nbor, nxt_action = self.agent_greedy_step(agent)

            self.vis.canvas.update()
            self.vis.canvas.after(100)

            self.world.agent_action(agent, nxt_action)

            if(best_nbor in self.goal_pos):
                self.world.aindx_goalreached[agent] = True
                self.world.goal_blocked.append( best_nbor )

                self.needs_update = True

if __name__ == "__main__":
    
    world_grid = world.GridWorld(WORLD_WIDTH, WORLD_HEIGHT)

    # Creation of the limits of the world
    bwalls = get_boundwalls(world_grid)
    world_grid.add_rocks( bwalls )

    # Addition of the agents    
    world_grid.add_agents_rand(NUM_AGENTS)

    # Addition of the goal positions

    world_grid.add_goal_pos(GOAL)

    vis = Visualize(world_grid)

    vis.draw_world()
    vis.draw_agents()

    vis.canvas.pack()
    vis.canvas.update()
    vis.canvas.after(200)

    solver = SolverModel(world_grid, vis)

    finished = False
    iter_val = 0

    while (True):
        solver.solve_step()
        finished = True
        agents_inside = 0
        
        for agent in world_grid.get_agents():
            # En caso de que el agente no haya llegado a su meta, se sigue iterando
            if (not world_grid.aindx_goalreached[agent]):
                finished = False
            else:
                agents_inside += 1
        print('- Iteración ', iter_val, '- Numero de agentes dentro de la forma: ', agents_inside)
        vis.canvas.update()
        vis.canvas.after(200)

        if(finished):
            break

        iter_val += 1

    vis.canvas.update()
    vis.canvas.after(2500)  

# Another possible goals:

# GOAL 2:
# a.add_rocks( ( (1,1),(3,3),(1,3),(3,1),(2,4) ) )
# # a.add_agents( ((3,2),(1,6),(7,8),(2,6),(2,8),(5,6),(4,7)) )
# a.add_agents_rand(7)
# a.add_goal_pos( ( (2,3),(6,1),(8,7),(6,2),(8,2),(6,5),(7,4) ) )

# GOAL 3:
# a.add_agents_rand(27)
# a.add_goal_pos( ( (2,2),(3,2),(4,2),(3,3),(2,4),(3,4),(4,4), \
#                   (3,6),(2,7),(3,7),(4,7),(3,8), \
#                   (2,10),(3,10),(4,10),(3,11),(2,12),(3,12),(4,12),
#                   (6,2),(6,3),(6,4), (6,6),(6,7),(6,8), (6,10),(6,11),(6,12) \
#                   ) )