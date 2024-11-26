from logic import update_grid as up
import numpy as np

def fast_math(car_grid, map_grid, density_grid, special_grid, SPEED, REACTION_TIME, DEPARTURE, LIGHT_SWITCH, arrival_times_list, arrival_time_time, arrival_time_arrival, simulation_time, frame_count, timer, car_count, simulation_running, draw_plots, house_coord, road_list, flow_rate, frame_density):
    while np.all(car_grid['time_alive'] != 0) or car_count > 0:
        if frame_count % LIGHT_SWITCH == 0:
            map_grid[map_grid == 2] = -1
            map_grid[map_grid == 3] = 2
            map_grid[map_grid == -1] = 3

        timer, car_count, car_grid = up.spawn_cars(house_coord, map_grid, car_grid, DEPARTURE, SPEED, timer, car_count)
        car_grid, death_list, flow, density = up.update_car_grid(car_grid, SPEED, density_grid, REACTION_TIME, map_grid, road_list)
        arrival_times_list.extend(death_list)
        death_list = np.array(death_list)
        avg = np.mean(death_list) if death_list.size > 0 else 0
        if avg != 0:
            arrival_time_time.append(simulation_time)
            arrival_time_arrival.append(avg)
        
        flow = np.array(flow)
        avg = np.mean(flow) if flow.size > 0 else 0
        flow_rate.append((simulation_time, avg))
        frame_density.append((simulation_time, density))
        simulation_time += 1
        frame_count += 1
    simulation_running = False
    draw_plots = True
    return simulation_running, draw_plots, arrival_times_list, arrival_time_time, arrival_time_arrival, flow_rate, frame_density