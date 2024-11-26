import numpy as np
from queue import PriorityQueue
"""
# Define the grid
map_grid = np.array([
    [0, 1, 0, 1, 0, 0, 1],
    [1, 1, 0, 1, 1, 1, 1],
    [0, 1, 1, 1, 0, 1, 0],
    [0, 0, 0, 1, 1, 1, 1],
    [0, 1, 0, 1, 0, 0, 0],
    [1, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0]
])
"""

# A* algorithm
def heuristic(a, b):
    """Manhattan distance on a square grid"""
    return abs(b[0] - a[0]) + abs(b[1] - a[1])

def a_star_search(start, goal, grid):
    frontier = PriorityQueue()
    frontier.put((0, start))
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0
    
    while not frontier.empty():
        current = frontier.get()[1]
        
        if current == goal:
            break
        
        for direction in [(1, 0), (-1, 0), (0, 1), (0, -1)]: # Down, Up, Right, Left
            next = (current[0] + direction[0], current[1] + direction[1])
            if 0 <= next[0] < grid.shape[0] and 0 <= next[1] < grid.shape[1]:
                if grid[next[0], next[1]] != 0:
                    new_cost = cost_so_far[current] + 1
                    if next not in cost_so_far or new_cost < cost_so_far[next]:
                        cost_so_far[next] = new_cost
                        priority = new_cost + heuristic(goal, next)
                        frontier.put((priority, next))
                        came_from[next] = current
    
    return came_from, cost_so_far

# Reconstruct path from start to goal
def reconstruct_path(came_from, start, goal):
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start) # optional
    path.reverse() # optional
    return path

"""
start = (0, 1)
goal = (0, 6)
came_from, cost_so_far = a_star_search(start, goal, map_grid)
path = reconstruct_path(came_from, start, goal)
print(path)

# output: [(0, 1), (1, 1), (2, 1), (2, 2), (2, 3), (1, 3), (1, 4), (1, 5), (1, 6), (0, 6)]
"""