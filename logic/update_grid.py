from . import path_finding as pt
from . import road_grid as rg
from scipy.stats import truncnorm
from scipy.integrate import quad
import numpy as np
import random
import math


def create_cdf_lookup(mean, std, range_val):
    # Define bounds as mean ± range_val, ensuring lower bound is not less than 0
    lower = max(mean - range_val - 0.5, 0)
    upper = mean + range_val + 0.5

    # Calculate standardized bounds for truncation
    lower_bound_z = (lower - mean) / std
    upper_bound_z = (upper - mean) / std

    # Create truncated normal distribution object
    dist = truncnorm(lower_bound_z, upper_bound_z, loc=mean, scale=std)

    # Precompute CDF for each integer within the effective range
    cdf_values = {}
    for number in range(math.floor(lower), math.ceil(upper+1)):
        cdf_value = dist.cdf(number)
        normalized_cdf = (cdf_value - dist.cdf(lower)) / (dist.cdf(upper) - dist.cdf(lower))
        cdf_values[number] = 1 - normalized_cdf

    return cdf_values

def rotate_clockwise(starting_position, coordinates, round_about_entrances, round_about):
    y, x = starting_position
    quarters = {
        'top_left': [(y-1, x-2), (y-2, x-2), (y-2, x-1), (y-2, x)],
        'top_right': [(y-2, x+1), (y-2, x+2), (y-1, x+2), (y, x+2)],
        'bottom_right': [(y+1, x+2), (y+2, x+2), (y+2, x+1), (y+2, x)],
        'bottom_left': [(y+2, x-1), (y+2, x-2), (y+1, x-2), (y, x-2)]
    }
    current_index = coordinates.index((y, x))
    new_coordinates = [coordinates[current_index-2]]

    for i in range(4):
        if new_coordinates[-1] == (y, x-2):
            new_coordinates.extend(quarters['top_left'])
        elif new_coordinates[-1] == (y-2, x):
            new_coordinates.extend(quarters['top_right'])
        elif new_coordinates[-1] == (y, x+2):
            new_coordinates.extend(quarters['bottom_right'])
        elif new_coordinates[-1] == (y+2, x):
            new_coordinates.extend(quarters['bottom_left'])
        if coordinates[current_index+2] == new_coordinates[-1]:    
            coordinates[current_index-2:current_index+3] = new_coordinates
    entrance = [(y, x-2), (y-2, x), (y, x+2), (y+2, x)]
    roundabout = [(y-1, x-2), (y-2, x-2), (y-2, x-1), (y-2, x), (y-2, x+1), (y-2, x+2), (y-1, x+2), (y, x+2), (y+1, x+2), (y+2, x+2), (y+2, x+1), (y+2, x), (y+2, x-1), (y+2, x-2), (y+1, x-2), (y, x-2)]
    if entrance not in round_about_entrances:
        round_about_entrances.append(entrance)
    if roundabout not in round_about:
        round_about.append(roundabout)

    return coordinates, round_about_entrances, round_about

def find_all_paths(coordinates, map_grid, round_about_entrances, round_about):
    all_paths = []
    for start in coordinates:
        for end in coordinates:
            if start != end:
                start_coordinate = tuple(x * 7 + 3 for x in start)
                end_coordinate = tuple(x * 7 + 3 for x in end)
                came_from, cost_so_far = pt.a_star_search(start_coordinate, end_coordinate, map_grid)
                path = pt.reconstruct_path(came_from, start_coordinate, end_coordinate)
                for coord in path:
                    if map_grid[coord[0]][coord[1]] == 4:
                        path, round_about_entrances, round_about = rotate_clockwise(coord, path, round_about_entrances, round_about)
                all_paths.append(path)
    return all_paths, round_about_entrances, round_about


def initialise(initial_grid, special_grid, reaction):
    road_grid, road_list = rg.rescale_roads(initial_grid)
    density_grid = np.zeros((len(road_grid), len(road_grid)), dtype=int)
    coordinates = [(i, j) for i, row in enumerate(special_grid) for j, val in enumerate(row) if val == 1]
    round_about_entrances = []
    round_about = []
    all_paths, round_about_entrances, round_about = find_all_paths(coordinates, road_grid, round_about_entrances, round_about)
    reaction_values = create_cdf_lookup(reaction[0], reaction[1], reaction[2])
    return density_grid, road_grid, coordinates, road_list, all_paths, reaction_values, round_about_entrances, round_about

def get_truncated_normal_value(initial_values):
    mu = initial_values[0]  # Mean
    sigma = initial_values[1]  # Standard deviation
    range_val = initial_values[2]  # Range

    # Calculate the bounds in terms of standard deviation
    lower_bound = max(mu - 0.5 - range_val, 0)
    upper_bound = mu + 0.5 + range_val
    lower_bound_std = (lower_bound - mu) / sigma
    upper_bound_std = (upper_bound - mu) / sigma

    # Generate a truncated normal distribution
    truncated_normal = truncnorm(a=lower_bound_std, b=upper_bound_std, loc=mu, scale=sigma)

    # Draw a single value from the distribution
    value = truncated_normal.rvs()

    return value

def find_car_rotation(coordinates_list):
    if 0 <= 1 < len(coordinates_list):
        difference_index = tuple(a - b for a, b in zip(coordinates_list[0], coordinates_list[1]))
    else:
        difference_index = (0,0)
    return difference_index


def find_next_distance(coordinates_list, map_grid, car_grid, index, speed, car_pos, in_round_about, round_about_entrances, round_about): 
    max_speed = math.ceil(speed[0]+0.5+speed[2])
    for step in range(min(max_speed + 1, len(coordinates_list)-1)):
        coor = coordinates_list[step + 1]
        if step + 2 < len(coordinates_list):
            next_y, next_x = coordinates_list[step + 2]
        else:
            next_y, next_x = coor
        rotation = tuple(a - b for a, b in zip(coor, (next_y, next_x)))
        old_y, old_x = coordinates_list[step]
        old_rotation = tuple(a - b for a, b in zip((old_y, old_x), coor))
        for i in range(len(in_round_about)):
            if (coor[0],coor[1]) in round_about_entrances[i] and in_round_about[i] >= 14 and coordinates_list[0] not in round_about[i]:
                return step + 1, 0
                
        if (map_grid[coor[0]][coor[1]] == 2 and old_rotation[0] == 0) or (map_grid[coor[0]][coor[1]] == 3 and old_rotation[1] == 0):
            return step + 1, 0
        else:
            if coor in car_pos:
                for new_car_index in car_pos[coor]:
                    if index != new_car_index and rotation == car_grid[new_car_index][2]:
                        return step + 1, car_grid[new_car_index][0]
    return None, None

def next_speed(reaction, current_speed, distance, old_speed, velocity):
    if distance is None or distance > current_speed:
        if current_speed > old_speed:
            return math.ceil( old_speed + ((current_speed-old_speed)/3) )
        else:
            return current_speed
    if distance <= 1:
        return 0
    if distance <= current_speed:
        max_speed = distance - 1
        if distance >= next(reversed(reaction)):
            return max(min(current_speed,max_speed), 1)
        if distance <= next(iter(reaction)):
            if old_speed > velocity:
                return max(min(math.ceil(old_speed + ((velocity-old_speed)/(2 * distance)) * old_speed),max_speed), 1)
            elif old_speed  == velocity:
                return max(min(old_speed,max_speed), 1)
            else:
                return max(min(math.ceil(old_speed + ((velocity-old_speed)/(0.5 * distance)) * old_speed),max_speed), 1)
        else:
            probability = reaction[distance]
        if random.random() < probability:
            if old_speed > velocity:
                return max(min(math.ceil(old_speed + ((velocity-old_speed)/(2 * distance)) * old_speed),max_speed), 1)
            elif old_speed  == velocity:
                return max(min(old_speed,max_speed), 1)
            else:
                return max(min(math.ceil(old_speed + ((velocity-old_speed)/(0.5 * distance)) * old_speed),max_speed), 1)
        else:
            return min(current_speed, max_speed)


def spawn_cars(all_paths, map_grid, car_grid, departure, speed, timer, car_count, car_pos):
    random.shuffle(all_paths)
    timer -= 1
    if timer <= 0 and car_count > 0:
        # Finds viable start and end coordinates
        for p in all_paths:
            if p[0] not in car_pos:
                path = p
                break
        else:
            timer = 1
            return timer, car_count, car_grid, car_pos

        # find the next speed and time
        speed = abs(round(get_truncated_normal_value(speed)))
        timer = abs(round(get_truncated_normal_value(departure)))
        car_count -= 1
    
        #direction
        difference_index = tuple(a - b for a, b in zip(path[0], path[1]))
        car_grid.append((speed, path, difference_index , 1))
        
        if path[0] in car_pos:
            car_pos[path[0]].append(len(car_grid) - 1)
        else:
            car_pos[path[0]] = [len(car_grid) - 1]

        return timer, car_count, car_grid, car_pos
    return timer, car_count, car_grid, car_pos

def update_car_grid(car_grid, o_speed, density_grid, map_grid, road_list, reaction_values, car_pos, round_about_entrances, round_about, in_round_about):
    new_car_grid = []
    flow = []
    death_list = []
    car_count= 0
    new_car_pos = {}
    new_in_round_about = [0] * len(round_about)
    # structure = (speed, coordinates_list, rotation, time_alive)
    for n in range(len(car_grid)):
        old_speed, coordinates_list, rotation, time_alive = car_grid[n]
        time_alive += 1
        speed = abs(round(get_truncated_normal_value(o_speed)))
        distance, velocity = find_next_distance(coordinates_list, map_grid, car_grid, n, o_speed, car_pos, in_round_about, round_about_entrances, round_about)
        speed = next_speed(reaction_values, speed, distance, old_speed, velocity)
        density_grid[coordinates_list[0][0], coordinates_list[0][1]] += 1
        flow.append(speed)
        if 0 <= speed < len(coordinates_list):
            coordinates_list = coordinates_list[speed:]
            rotation = find_car_rotation(coordinates_list)
            new_car_grid.append((speed, coordinates_list, rotation, time_alive))
            # update carpos to RAM
            if coordinates_list[0] in new_car_pos:
                new_car_pos[coordinates_list[0]].append(n - len(death_list))
            else:
                new_car_pos[coordinates_list[0]] = [n - len(death_list)]
            
            for i in range(len(round_about)):
                if coordinates_list[0] in round_about[i]:
                    new_in_round_about[i] += 1

            car_count += 1
        else:
            death_list.append(time_alive)

    car_density = car_count / ( len(road_list) * 2)                
    return new_car_grid, death_list, flow, car_density, new_car_pos, density_grid, new_in_round_about
