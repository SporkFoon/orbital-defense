import pygame

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
PURPLE = (255, 0, 255)

# Game config
FPS = 60
PLANET_RADIUS = 50
MAX_ORBITAL_RADIUS = 350
RESOURCE_START = 500
BACKGROUND_COLOR = (10, 10, 40)

# Initialize pygame and screen
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Orbital Defense")
clock = pygame.time.Clock()