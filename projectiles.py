import math
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, RED

class Projectile:
    def __init__(self, position, angle, damage, speed=5, color=RED):
        self.position = list(position)
        self.angle = angle
        self.damage = damage
        self.speed = speed
        self.color = color
        self.destroyed = False
        self.radius = 5
        
    def update(self):
        self.position[0] += math.cos(self.angle) * self.speed
        self.position[1] += math.sin(self.angle) * self.speed
        
        if (self.position[0] < 0 or self.position[0] > SCREEN_WIDTH or 
            self.position[1] < 0 or self.position[1] > SCREEN_HEIGHT):
            self.destroyed = True
            
    def check_collision(self, enemies):
        for enemy in enemies:
            dx = enemy.position[0] - self.position[0]
            dy = enemy.position[1] - self.position[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < enemy.radius + self.radius:
                enemy.take_damage(self.damage)
                self.destroyed = True
                return enemy
        return None
        
    def render(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.position[0]), int(self.position[1])), self.radius)