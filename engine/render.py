import pygame
from engine import gui
import numpy as np

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def interpolate_color(color_start, color_end, factor):
    return tuple(int(s + (e - s) * factor) for s, e in zip(color_start, color_end))


def draw_grid(screen, grid, road_types, tile_images, special_grid, special_types, TILE_SIZE, GRID_SIZE, car_grid, running, density, SPEED, display):
    if running is False:
        start_color = hex_to_rgb('#05ECFA')
        end_color = hex_to_rgb('#ED01AB')
        non_zero_values = [val for row in density for val in row if val > 0]
        min_val = min(non_zero_values) if non_zero_values else 0
        max_val = max(non_zero_values) if non_zero_values else 0
    grid_width = grid_height = TILE_SIZE * GRID_SIZE
    screen.fill(pygame.Color('#221F2F'))
    for y, row in enumerate(grid):
        for x, tile_index in enumerate(row):
            tile_type = road_types[tile_index[0]]
            screen.blit(pygame.transform.rotate(tile_images[tile_type], grid[y][x][1]), (x * TILE_SIZE, y * TILE_SIZE))
            if special_grid[y][x] != 0:
                tile_type = special_types[special_grid[y][x]-1]
                screen.blit(tile_images[tile_type], (x * TILE_SIZE, y * TILE_SIZE))
    
    graphic = [-1] * 99

    for car in car_grid:
        factor = max((car[0]) / (SPEED[0] + 0.5 + SPEED[2]), 0) 
        color_rgb = interpolate_color((0, 255, 0), (255, 0, 0), factor)
        half_difference = tuple(map(lambda x: (x+1)/2, car[2]))
        y, x = car[1][0]
        pygame.draw.circle(screen, color_rgb, ((x+half_difference[0]) * TILE_SIZE /7 , (y-half_difference[1]+1) * TILE_SIZE /7 ), TILE_SIZE/14)

        if running is True:
            try:
                graphic[x - 3] = car[0]
            except IndexError:
                print(car)
    if running is True:
        display.append(graphic)
    
    if running is False:
        for y in range(len(density)):
            for x in range(len(density)):
                if density[y, x] != 0:
                    factor = (density[y, x] - min_val) / (max_val - min_val) if max_val - min_val > 0 else 0
                    color_rgb = interpolate_color(start_color, end_color, factor)
                    pygame.draw.rect(screen, color_rgb, (x * TILE_SIZE /7 , y * TILE_SIZE /7 , TILE_SIZE/7, TILE_SIZE/7 ))

    for x in range(0, grid_width + TILE_SIZE, TILE_SIZE):
        pygame.draw.line(screen, '#FFFFFF', (x, 0), (x, grid_height))
    for y in range(0, grid_height + TILE_SIZE, TILE_SIZE):
        pygame.draw.line(screen, '#FFFFFF', (0, y), (grid_width, y)) 
    
    return display

def draw_ui_elements(playButton, pauseButton, restartButton, gradient_rect):
    playButton.draw()
    pauseButton.draw()
    restartButton.draw()
    gradient_rect.draw()
    
def refresh_screen(FPS, frame):
    pygame.display.flip()
    pygame.time.Clock().tick(FPS)
    frame += 1
    return frame
