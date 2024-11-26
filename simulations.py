import os
from logic import update_grid as up
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
import pandas as pd
from tqdm import tqdm
from multiprocessing import Pool    

def weighted_mean_subtract_min(counts):
    weighted_sum = sum(key * weight for key, weight in counts.items())
    total_weight = sum(weight for weight in counts.values())
    weighted_mean = weighted_sum / total_weight
    min_key = min(counts.keys())
    
    return weighted_mean - min_key

def create_file(file_name, collum_names, x, y):
    df = pd.DataFrame({
        collum_names[0]: x,
        collum_names[1]: y
        })
    df.to_csv(file_name, index=False)

def simulate(j, i, grid, special_grid, CAR_COUNT, SPEED, DEPARTURE, REACTION_TIME, LIGHT_SWITCH, bar_format):
    simulation_time = 0
    arrival_time_time = []
    arrival_time_arrival = []
    arrival_times_list = []
    flow_rate = []
    frame_density = []
    car_grid = []
    in_round_about = []
    density_grid, map_grid, road_list, all_paths, reaction_values, round_about_entrances, round_about = up.initialise(grid, special_grid, REACTION_TIME)
    car_count = CAR_COUNT
    timer = 0
    car_pos = {}
    while not car_grid == [] or car_count > 0:
        if simulation_time % LIGHT_SWITCH == 0:
            map_grid[map_grid == 2] = -1
            map_grid[map_grid == 3] = 2
            map_grid[map_grid == -1] = 3

        timer, car_count, car_grid, car_pos = up.spawn_cars(all_paths, map_grid, car_grid, DEPARTURE[i], SPEED, timer, car_count, car_pos)
        car_grid, death_list, flow, density, car_pos, density_grid, in_round_about = up.update_car_grid(car_grid, SPEED, density_grid, map_grid, road_list, reaction_values, car_pos, round_about_entrances, round_about, in_round_about)
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

    # Count the frequency of each integer forn the bar plot
    counts = Counter(arrival_times_list)
    values, frequencies = zip(*counts.items())

    create_file(rf'crossroad, departure, speed = 7\departure = {DEPARTURE[i][0]}\data\Travel times\travel times {j+1}.csv', ['Travel time (frames)', 'Count'], values, frequencies)

    create_file(rf'crossroad, departure, speed = 7\departure = {DEPARTURE[i][0]}\data\Average arrival time against time of arrival\arrival time {j+1}.csv', ['Simulation time (frames)', 'Average arrival time (frames)'], arrival_time_time, arrival_time_arrival)

    x_values, y_values = zip(*flow_rate)
    create_file(rf'crossroad, departure, speed = 7\departure = {DEPARTURE[i][0]}\data\Flow rate\flow rate {j+1}.csv', ['Simulation time (frames)', 'Average velocity (cells/frames)'], x_values, y_values)

    x_values, y_values = zip(*frame_density)
    create_file(rf'crossroad, departure, speed = 7\departure = {DEPARTURE[i][0]}\data\Car density over time\car density {j+1}.csv', ['Simulation time (frames)', 'Car density (cars/cells)'], x_values, y_values)

    # saving mean traffic time
    mean_traffic_time = weighted_mean_subtract_min(counts)
    with open(rf'crossroad, departure, speed = 7\departure = {DEPARTURE[i][0]}\data\time in traffic.csv', 'a') as file:
        file.write(f"{mean_traffic_time}\n")

if __name__ == "__main__":

    # setup bar type
    bar_format = "{l_bar}%s{bar}%s{r_bar}" % ('\x1b[32m', '\x1b[0m')

    CAR_COUNT = 2500
    SPEED = [7, 0.2, 0]
    DEPARTURE = [[1, 0.2, 0], [2, 0.2, 0], [3, 0.2, 0], [4, 0.2, 0], [5, 0.2, 0], [6, 0.2, 0], [7, 0.2, 0], [8, 0.2, 0], [9, 0.2, 0], [10, 0.2, 0], 
                 [11, 0.2, 0], [12, 0.2, 0], [13, 0.2, 0], [14, 0.2, 0], [15, 0.2, 0], [16, 0.2, 0], [17, 0.2, 0], [18, 0.2, 0], [19, 0.2, 0], [20, 0.2, 0]]
    REACTION_TIME = [20, 0.2, 0]
    LIGHT_SWITCH = 90
    
    grid = [[(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (2, 270), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], 
            [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (3, 90), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], 
            [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (3, 90), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], 
            [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (3, 90), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], 
            [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (3, 90), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], 
            [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (3, 90), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], 
            [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (3, 90), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], 
            [(2, 0), (3, 0), (3, 0), (3, 0), (3, 0), (3, 0), (3, 0), (6, 0), (3, 0), (3, 0), (3, 0), (3, 0), (3, 0), (3, 0), (2, 180)], 
            [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (3, 90), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], 
            [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (3, 90), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], 
            [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (3, 90), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], 
            [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (3, 90), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], 
            [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (3, 90), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], 
            [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (3, 90), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], 
            [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (2, 90), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]]

    special_grid = [[0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0], 
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]]

    os.makedirs('crossroad, departure, speed', exist_ok=True)

    for i in tqdm(range(len(DEPARTURE)), desc='Total progress', bar_format=bar_format):
        if os.path.exists(rf'crossroad, departure, speed = 7\departure = {DEPARTURE[i][0]}'):
            continue
        os.makedirs(rf'crossroad, departure, speed = 7\departure = {DEPARTURE[i][0]}', exist_ok=True)
        os.makedirs(rf'crossroad, departure, speed = 7\departure = {DEPARTURE[i][0]}\graphs', exist_ok=True)
        os.makedirs(rf'crossroad, departure, speed = 7\departure = {DEPARTURE[i][0]}\data', exist_ok=True)
        os.makedirs(rf'crossroad, departure, speed = 7\departure = {DEPARTURE[i][0]}\data\Travel times', exist_ok=True)
        os.makedirs(rf'crossroad, departure, speed = 7\departure = {DEPARTURE[i][0]}\data\Average arrival time against time of arrival', exist_ok=True)
        os.makedirs(rf'crossroad, departure, speed = 7\departure = {DEPARTURE[i][0]}\data\Flow rate', exist_ok=True)
        os.makedirs(rf'crossroad, departure, speed = 7\departure = {DEPARTURE[i][0]}\data\Car density over time', exist_ok=True)

        average_time_in_traffic = []

        with Pool(5) as p:
            p.starmap(simulate, [(j, i, grid, special_grid, CAR_COUNT, SPEED, DEPARTURE, REACTION_TIME, LIGHT_SWITCH, bar_format) for j in range(5)])

        average_time_in_traffic = pd.read_csv(rf'crossroad, departure, speed = 7\departure = {DEPARTURE[i][0]}\data\time in traffic.csv', header=None)

        with open(rf'crossroad, departure, speed = 7\departure = {DEPARTURE[i][0]}\average traffic.csv', 'a') as file:
            file.write(f"{np.mean(average_time_in_traffic[0])},{np.std(average_time_in_traffic[0])}\n")
    
    departure = []
    avg_arrival_time = []
    uncertainty = []
    for i in range(len(DEPARTURE)):
        data = pd.read_csv(rf'crossroad, departure, speed = 7\departure = {DEPARTURE[i][0]}\average traffic.csv', header=None)
        departure.append(DEPARTURE[i][0])
        avg_arrival_time.append(data.iloc[0, 0])
        uncertainty.append(data.iloc[0, 1])
    
    df = pd.DataFrame({
        'Departure (frames)': departure,
        'average arrival time (frames)': avg_arrival_time,
        'Uncertainty': uncertainty
        })
    df.to_csv(rf'crossroad, departure, speed = 7\combined average traffic.csv', index=False)

    for i in tqdm(range(len(DEPARTURE)), desc='Creating graphs', bar_format=bar_format):
        os.makedirs(rf'crossroad, departure, speed = 7\departure = {DEPARTURE[i][0]}\graphs', exist_ok=True)
        for j in range(5):
            plt.figure(figsize=(15, 10))

            # Create subplot 1 for the bar plot
            data1 = pd.read_csv(rf'crossroad, departure, speed = 7\departure = {DEPARTURE[i][0]}\data\Travel times\travel times {j+1}.csv')
            plt.subplot(2, 2, 1)  # 1 row, 2 columns, subplot 1
            plt.bar(data1['Travel time (frames)'], data1['Count'])
            plt.xlabel('Travel time (frames)')
            plt.ylabel('Count')
            plt.title('Travel times')

            # Create subplot 2 for the line plot
            data2 = pd.read_csv(rf'crossroad, departure, speed = 7\departure = {DEPARTURE[i][0]}\data\Average arrival time against time of arrival\arrival time {j+1}.csv')
            plt.subplot(2, 2, 2)  # 1 row, 2 columns, subplot 2
            plt.plot(data2['Simulation time (frames)'], data2['Average arrival time (frames)'] , marker='.', linestyle='None')
            plt.xlabel('Simulation time (frames)')
            plt.ylabel('Average arrival time (frames)')
            plt.title('Average arrival time against time of arrival')

            # Create subplot 2 for the line plot
            data3 = pd.read_csv(rf'crossroad, departure, speed = 7\departure = {DEPARTURE[i][0]}\data\Flow rate\flow rate {j+1}.csv')
            plt.subplot(2, 2, 3)  # 1 row, 2 columns, subplot 2
            plt.plot(data3['Simulation time (frames)'], data3['Average velocity (cells/frames)'], marker='.', linestyle='None')
            plt.xlabel('Simulation time (frames)')
            plt.ylabel('Averge velocity (cells/frames)')
            plt.title('Flow rate')

            # Create subplot 2 for the line plot
            data4 = pd.read_csv(rf'crossroad, departure, speed = 7\departure = {DEPARTURE[i][0]}\data\Car density over time\car density {j+1}.csv')
            plt.subplot(2, 2, 4)  # 1 row, 2 columns, subplot 2
            plt.plot(data4['Simulation time (frames)'], data4['Car density (cars/cells)'], marker='.', linestyle='None')
            plt.xlabel('Simulation time (frames)')
            plt.ylabel('Car density (cars/cells)')
            plt.title('Car density over time')

            #adjust plot
            plt.subplots_adjust(wspace=0.2, hspace=0.2)  
            plt.tight_layout()

            plt.savefig(rf'crossroad, departure, speed = 7\departure = {DEPARTURE[i][0]}\graphs\graph {j+1}', dpi=300)
            
            # Hide plots
            plt.close()


    print('Simulation completed')