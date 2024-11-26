import pygame
import pygame.locals as pl
import numpy as np

class Button(pygame.sprite.Sprite):
    def __init__(self, screen, text, scale_x, scale_y, scale_width, scale_height, 
                 inactive_color=(100, 100, 100), pressed_color=(50, 50, 50), 
                 font_scale=0.4, on_click=None, base_screen_width=800, base_screen_height=600):
        super().__init__()
        self.screen = screen
        self.text = text
        self.base_screen_width = base_screen_width
        self.base_screen_height = base_screen_height
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.scale_width = scale_width
        self.scale_height = scale_height
        self.font_scale = font_scale
        self.inactive_color = inactive_color
        self.pressed_color = pressed_color
        self.on_click = on_click
        self.font = pygame.font.SysFont(None, int(self.base_screen_height * self.font_scale))
        self.last_click_result = None
        self.update_position()  # Initially set position based on scaling factors

    def update_position(self):
        # Calculate new positions and sizes based on the current screen size
        screen_width, screen_height = self.screen.get_size()
        self.x = int(screen_width * self.scale_x)
        self.y = int(screen_height * self.scale_y)
        self.width = int(screen_height * self.scale_width)
        self.height = int(screen_height * self.scale_height)
        self.font_size = int(screen_height * self.font_scale)
        self.font = pygame.font.SysFont(None, self.font_size)
        self.create_image()  # Update button image with new positions

    def create_image(self, color=None):
        if color is None:
            color = self.inactive_color
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(color)
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        text_x = (self.width - text_surface.get_width()) // 2
        text_y = (self.height - text_surface.get_height()) // 2
        self.image.blit(text_surface, (text_x, text_y))

    def draw(self):
        self.screen.blit(self.image, (self.x, self.y))

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_hover():
            self.is_pressed = True
            self.create_image(self.pressed_color)  # Use pressed color
        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_pressed = False
            self.create_image()  # Use default (inactive) color
            if self.is_hover():
                if self.on_click:
                    self.last_click_result = self.on_click()  # Call the click event function

    def is_hover(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        return (mouse_x >= self.x and mouse_x <= self.x + self.width and
                mouse_y >= self.y and mouse_y <= self.y + self.height)

class GradientRect(pygame.sprite.Sprite):
    def __init__(self, screen, scale_x, scale_y, scale_width, scale_height, 
                 start_color, end_color, base_screen_width=800, base_screen_height=600):
        super().__init__()
        self.screen = screen
        self.base_screen_width = base_screen_width
        self.base_screen_height = base_screen_height
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.scale_width = scale_width
        self.scale_height = scale_height
        self.start_color = np.array(start_color)
        self.end_color = np.array(end_color)
        self.update_position()  # Initially set position based on scaling factors

    def update_position(self):
        # Calculate new positions and sizes based on the current screen size
        screen_width, screen_height = self.screen.get_size()
        self.x = int(screen_width * self.scale_x)
        self.y = int(screen_height * self.scale_y)
        self.width = int(screen_width * self.scale_width)
        self.height = int(screen_height * self.scale_height)
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    def draw_gradient(self):
        for i, x in enumerate(range(self.x, self.x + self.width)):
            factor = i / self.width
            color = tuple((self.start_color + (self.end_color - self.start_color) * factor).astype(int))
            pygame.draw.line(self.screen, color, (x, self.y), (x, self.y + self.height))

    def draw(self):
        self.draw_gradient()