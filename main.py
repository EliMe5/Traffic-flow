import pygame
import json
from engine import gui
from engine import render
from engine import grapher
from logic import update_grid as up
from logic import fast_math
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import sys

def detect_surroundings(position, grid_info, y, x):
    position['up'] = 0 if y-1 < 0 or grid_info[y-1][x][0] == 0 else 1
    position['right'] = 0 if x+1 > GRID_SIZE - 1 or grid_info[y][x+1][0] == 0 else 1
    position['down'] = 0 if y+1 > GRID_SIZE - 1 or grid_info[y+1][x][0] == 0 else 1
    position['left'] = 0 if x-1 < 0 or grid_info[y][x-1][0] == 0 else 1
    return position


def get_tile_and_rotation(up, right, down, left):
    # Convert the surrounding tiles to a binary number
    # up, right, down, left -> bit positions
    surrounding = (up << 3) | (right << 2) | (down << 1) | left
    # Mapping from surrounding pattern to tile number and rotation
    tile_mapping = {
        0b0000: (1, 0),
        0b1000: (2, 90), 0b0100: (2, 0), 0b0010: (2, 270), 0b0001: (2, 180),
        0b1010: (3, 90), 0b0101: (3, 0),
        0b1100: (4, 180), 0b0110: (4, 90), 0b0011: (4, 0), 0b1001: (4, 270),
        0b1110: (5, 0), 0b0111: (5, 270), 0b1011: (5, 180), 0b1101: (5, 90),
        0b1111: (6, 0),
    }

    # Get the tile and rotation based on the surrounding pattern
    tile = tile_mapping.get(surrounding, (1, 0))  # Default to tile 1, rotation 0 if not found

    return tile

def playAction(grid, special_grid, REACTION_TIME):
    spawn_timer = 0
    d_grid, map_grid, house_coord, road_list, all_paths, reaction_values, round_about_entrances, round_about = up.initialise(grid, special_grid, REACTION_TIME)
    return d_grid, spawn_timer, map_grid, house_coord, road_list, all_paths, reaction_values, round_about_entrances, round_about, True

def pauseAction():
    return "pause"

def restartAction(map_grid):
    spawn_timer = 0
    car_grid = []
    return spawn_timer, car_grid, False

def load_and_scale_images(tile_size):
    return {
        'empty': pygame.Surface((tile_size, tile_size)),
        'dot': pygame.transform.scale(pygame.image.load(r'assets\dot.png').convert_alpha(), (tile_size, tile_size)),
        'dash': pygame.transform.scale(pygame.image.load(r'assets\dash.png').convert_alpha(), (tile_size, tile_size)),
        'line': pygame.transform.scale(pygame.image.load(r'assets\line.png').convert_alpha(), (tile_size, tile_size)),
        'angle': pygame.transform.scale(pygame.image.load(r'assets\angle.png').convert_alpha(), (tile_size, tile_size)),
        'tripod': pygame.transform.scale(pygame.image.load(r'assets\tripod.png').convert_alpha(), (tile_size, tile_size)),
        'cross': pygame.transform.scale(pygame.image.load(r'assets\cross.png').convert_alpha(), (tile_size, tile_size)),
        'circle': pygame.transform.scale(pygame.image.load(r'assets\circle.png').convert_alpha(), (tile_size, tile_size)),
        'house': pygame.transform.scale(pygame.image.load(r'assets\house.png').convert_alpha(), (tile_size, tile_size)),
        'bus': pygame.transform.scale(pygame.image.load(r'assets\bus.png').convert_alpha(), (tile_size, tile_size)),
    }

# Load constants
if __name__ == "__main__":
    with open('config.json', 'r') as file:
            data = json.load(file)

    # Constants for the simulation
    ASPECT_RATIO = 16/9
    HEIGHT = data['height']
    WIDTH = HEIGHT * ASPECT_RATIO

    GRID_SIZE = data['grid_size']
    TILE_SIZE = HEIGHT // GRID_SIZE

    FPS = data['fps']

    CAR_COUNT = data['car_count']
    SPEED = [data['average_speed'], data['uncertainty_speed'], data['range_speed']]
    DEPARTURE = [data['average_departure'], data['uncertainty_departure'], data['range_departure']]
    REACTION_TIME = [data['average_reaction_time'], data['uncertainty_reaction_time'], data['range_reaction_time']]
    LIGHT_SWITCH = data['light_switch_interval']
    RENDER = data['render']

    # Calculate button positions and sizes
    button_size_relative = 70 / 940 
    spacing_relative = 10 / 940

    button_size = 70 / 940 * HEIGHT
    spacing = 10 / 940 * HEIGHT
    top_left_corner_x = HEIGHT + spacing


    pygame.init()

    # Set up the display
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

    # Load images and associate them with road types

    TILE_SIZE = HEIGHT // GRID_SIZE
    tile_images = load_and_scale_images(TILE_SIZE)
    tile_images['empty'].fill(pygame.Color('#221F2F'))

    # Define road types and associate them with the loaded images
    road_types = ['empty', 'dot', 'dash', 'line', 'angle', 'tripod', 'cross', 'circle']
    special_types = ['house', 'bus']
    grid = [[(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], 
            [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], 
            [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], 
            [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], 
            [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], 
            [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], 
            [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], 
            [(2, 0), (3, 0), (3, 0), (3, 0), (3, 0), (3, 0), (3, 0), (3, 0), (3, 0), (3, 0), (6, 0), (3, 0), (3, 0), (3, 0), (2, 180)], 
            [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], 
            [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], 
            [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], 
            [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], 
            [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], 
            [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], 
            [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]]

    special_grid = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
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
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]



    # Initialize grid with indices corresponding to 'empty' tiles
    
    grid = [[(0, 0) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    special_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
    car_grid = []
    density_grid = np.zeros((GRID_SIZE * 7, GRID_SIZE * 7), dtype=int)


    # Create gui using your custom class
    playButton = gui.Button(
        screen=screen,
        text="Play",
        scale_x=(HEIGHT + spacing_relative * HEIGHT) / WIDTH,  # Convert x position to scale based on WIDTH
        scale_y=spacing_relative,  # Y position as a scale of HEIGHT
        scale_width=button_size_relative,  # Adjust button width scale based on aspect ratio
        scale_height=button_size_relative,  # Button height scale
        font_scale=0.03,  # Adjust font size scale as needed
        on_click=playAction,
        base_screen_width=WIDTH,
        base_screen_height=HEIGHT
    )

    pauseButton = gui.Button(
        screen=screen,
        text="Pause",
        scale_x=(HEIGHT + spacing_relative * HEIGHT + button_size_relative * HEIGHT * ASPECT_RATIO + spacing_relative * HEIGHT) / WIDTH,
        scale_y=spacing_relative,
        scale_width=button_size_relative,
        scale_height=button_size_relative,
        font_scale=0.03,  # Adjust font size scale as needed
        on_click=pauseAction,
        base_screen_width=WIDTH,
        base_screen_height=HEIGHT
    )

    restartButton = gui.Button(
        screen=screen,
        text="Restart",
        scale_x=(HEIGHT + 2 * spacing_relative * HEIGHT + 2 * button_size_relative * HEIGHT * ASPECT_RATIO) / WIDTH,
        scale_y=spacing_relative,
        scale_width= button_size_relative,
        scale_height=button_size_relative,
        font_scale=0.03,  # Adjust font size scale as needed
        on_click=restartAction,
        base_screen_width=WIDTH,
        base_screen_height=HEIGHT
    )

    playButton.on_click = lambda: playAction(grid, special_grid, REACTION_TIME)
    restartButton.on_click = lambda: restartAction(grid)

    gradient_rect = gui.GradientRect(
        screen=screen,
        scale_x= spacing_relative + HEIGHT / WIDTH,
        scale_y=0.5 - button_size_relative,
        scale_width=5 * button_size_relative,
        scale_height=button_size_relative,
        start_color=(5, 236, 250),  # RGB for #05ECFA
        end_color=(237, 1, 171),    # RGB for #ED01AB
        base_screen_width=WIDTH,
        base_screen_height=HEIGHT
    )

    # Main simulation loop
    running = True
    simulation_running = False
    frame_count = 0

    arrival_time_time = []
    arrival_time_arrival = []
    arrival_times_list = []
    flow_rate = []
    frame_density = []
    road_list = [(0, 0)]
    draw_plots = False
    car_pos = {}

    in_round_about = []
    display = []

    while running:
        # Handle events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Get mouse position and convert it to grid coordinates
                mx, my = pygame.mouse.get_pos()
                gx, gy = mx // TILE_SIZE, my // TILE_SIZE
                if event.button == 1 and gx <= GRID_SIZE - 1:
                    # Cycle through road types
                    Position = {'up':0, 'right':0, 'down':0, 'left':0}
                    if grid[gy][gx] == (0,0):
                        Position = detect_surroundings(Position, grid, gy, gx)
                        grid[gy][gx] = get_tile_and_rotation(Position['up'], Position['right'], Position['down'], Position['left'])
                        special_grid[gy][gx] = 0
                        neighboring_coordinates = [(1, 0), (0, -1), (-1, 0), (0, 1)]
                        for (dy, dx) in neighboring_coordinates:
                            new_y, new_x = gy + dy, gx + dx
                            if 0 <= new_y <= GRID_SIZE - 1 and 0 <= new_x <= GRID_SIZE - 1 and 0 < grid[new_y][new_x][0] < 8:
                                Position = {'up':0, 'right':0, 'down':0, 'left':0}
                                Position = detect_surroundings(Position, grid, new_y, new_x)
                                grid[new_y][new_x] = get_tile_and_rotation(Position['up'], Position['right'], Position['down'], Position['left'])
                                special_grid[new_y][new_x] = 0

                    elif 0 < grid[gy][gx][0] < 6:
                        grid[gy][gx] = (0,0)
                        special_grid[gy][gx] = 0
                        neighboring_coordinates = [(1, 0), (0, -1), (-1, 0), (0, 1)]
                        for (dy, dx) in neighboring_coordinates:
                            new_y, new_x = gy + dy, gx + dx
                            if 0 <= new_y <= GRID_SIZE - 1 and 0 <= new_x <= GRID_SIZE - 1 and 0 < grid[new_y][new_x][0] < 8:
                                Position = {'up':0, 'right':0, 'down':0, 'left':0}
                                Position = detect_surroundings(Position, grid, new_y, new_x)
                                grid[new_y][new_x] = get_tile_and_rotation(Position['up'], Position['right'], Position['down'], Position['left'])
                                special_grid[new_y][new_x] = 0


                    elif 5 < grid[gy][gx][0] < 8:
                        grid[gy][gx] = ((grid[gy][gx][0] - 5) % 2 + 6, 0)
                
                if event.button == 3 and gx <= GRID_SIZE - 1:
                    if grid[gy][gx][0] not in [0, 7]:
                        if special_grid[gy][gx] == 0:
                            special_grid[gy][gx] = 1
                        elif special_grid[gy][gx] == 1 and grid[gy][gx][0] not in [5, 6]:
                            special_grid[gy][gx] = 2
                        else:
                            special_grid[gy][gx] = 0
            
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                HEIGHT = event.h
                WIDTH = HEIGHT * ASPECT_RATIO
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                TILE_SIZE = min(WIDTH, HEIGHT) // GRID_SIZE
                tile_images = load_and_scale_images(TILE_SIZE)
                tile_images['empty'].fill(pygame.Color('#221F2F'))

                # Update playButton position and size
                playButton.update_position()
                pauseButton.update_position()
                restartButton.update_position()
                gradient_rect.update_position()

            playButton.update(event)
            pauseButton.update(event)
            restartButton.update(event)

        if playButton.last_click_result is not None:
            if simulation_running is False:
                density_grid, timer, map_grid, house_coord, road_list, all_paths, reaction_values, round_about_entrances, round_about, simulation_running = playButton.last_click_result
                all_paths.pop()
                car_count = CAR_COUNT
                simulation_time = 0
                #print(grid)
            elif simulation_running == "pause":
                simulation_running = True
            playButton.last_click_result = None
        
        if pauseButton.last_click_result is not None:
            simulation_running = pauseButton.last_click_result
            pauseButton.last_click_result = None

        if restartButton.last_click_result is not None:
            timer, car_grid, simulation_running = restartButton.last_click_result
            restartButton.last_click_result = None    

        if car_grid == [] and simulation_running is True and car_count <= 0: 
            simulation_running = False
            draw_plots = True

        if simulation_running is True:
            if RENDER is True:
                if simulation_time % LIGHT_SWITCH == 0:
                    map_grid[map_grid == 2] = -1
                    map_grid[map_grid == 3] = 2
                    map_grid[map_grid == -1] = 3
                timer, car_count, car_grid, car_pos = up.spawn_cars(all_paths, map_grid, car_grid, DEPARTURE, SPEED, timer, car_count, car_pos)
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
            else:
                simulation_running, draw_plots, arrival_times_list, arrival_time_time, arrival_time_arrival, flow_rate, frame_density = fast_math.fast_math(car_grid, map_grid, density_grid, special_grid, SPEED, REACTION_TIME, DEPARTURE, LIGHT_SWITCH, arrival_times_list, arrival_time_time, arrival_time_arrival, simulation_time, frame_count, timer, car_count, simulation_running, draw_plots, house_coord, road_list, flow_rate, frame_density)


        # Inside your game loop or where you render your game's components
        display = render.draw_grid(screen, grid, road_types, tile_images, special_grid, special_types, TILE_SIZE, GRID_SIZE, car_grid, simulation_running, density_grid, SPEED, display)
        render.draw_ui_elements(playButton, pauseButton, restartButton, gradient_rect)
        frame_count = render.refresh_screen(FPS, frame_count)

        if draw_plots:
            grapher.draw_plots(arrival_times_list, arrival_time_time, arrival_time_arrival, flow_rate, frame_density)
            draw_plots = False

            display = display[52:109]

            # Create a custom colormap with normalized positions
            cmap = mcolors.LinearSegmentedColormap.from_list(
                "custom_green_red",
                [(0, "#FFFFFF"), 
                (0.1, "#2ECF03"), 
                (0.3, "#8DE45F"), 
                (0.5, "#FEED47"), 
                (0.7, "#FF922C"), 
                (0.8, "#FD673A"), 
                (1, "#EC204F")],
                N=12
            )

            fig, ax = plt.subplots()
            # Show the matrix with the custom colormap
            cax = ax.matshow(display, cmap=cmap, vmin=-1, vmax=10)

            # Add a color bar
            colorbar = plt.colorbar(cax, ticks=range(-1, 11))
            colorbar.ax.set_ylabel('Speed (cells/frame)', fontsize=16)
            plt.title('Synchronous flow', fontsize=18)

            # Set up the axes
            ax.set_xticks(range(0, len(display[0]), 10))
            ax.set_yticks(range(0, len(display), 10))
            ax.tick_params(axis='both', which='both', labelsize=16)
            ax.set_yticklabels(range(0, len(display), 10))

            ax.set_xlabel('Distance (cells)', fontsize=16)
            ax.set_ylabel('Time (frames)', fontsize=16)

            # Invert y-axis to have 0 at the top
            ax.invert_yaxis()

            plt.tight_layout()
            plt.savefig('heatmap.png', dpi=300)
            plt.show()

    # Clean up
    pygame.quit()
    sys.exit()
