import math
import random
import pygame
from game_objects import GameObject
from config import SCREEN_WIDTH, SCREEN_HEIGHT, PLANET_RADIUS, PURPLE, CYAN

class Enemy(GameObject):
    def __init__(self, position, health, speed, damage, reward):
        super().__init__(position)
        self.health = health
        self.speed = speed
        self.damage = damage
        self.reward = reward
        self.movement_pattern = "direct"
        self.radius = 15
        self.destroyed = False
        self.spawn_time = pygame.time.get_ticks()
        self.closest_approach = float('inf')
        self.color = PURPLE
        
    def move(self, planet_pos):
        dx = planet_pos[0] - self.position[0]
        dy = planet_pos[1] - self.position[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        self.closest_approach = min(self.closest_approach, distance)
        
        if distance > 0:
            self.position[0] += dx / distance * self.speed
            self.position[1] += dy / distance * self.speed
            
        return distance <= PLANET_RADIUS + self.radius
        
    def attack(self, planet):
        damage_dealt = planet.take_damage(self.damage)
        return damage_dealt
        
    def take_damage(self, amount):
        self.health -= amount
        return self.check_destroyed()
        
    def check_destroyed(self):
        self.destroyed = self.health <= 0
        return self.destroyed
        
    def render(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.position[0]), int(self.position[1])), self.radius)

class BasicEnemy(Enemy):
    def __init__(self, position):
        super().__init__(position, health=50, speed=1, damage=10, reward=25)
        self.direct_speed = 1
        self.color = PURPLE
        
    def approach_direct(self, planet_pos):
        return self.move(planet_pos)

class FastEnemy(Enemy):
    def __init__(self, position):
        super().__init__(position, health=30, speed=2.5, damage=5, reward=35)
        self.evasion_chance = 0.2
        self.color = CYAN
        
    def evade_defenses(self):
        if random.random() < self.evasion_chance:
            angle = random.uniform(-math.pi/4, math.pi/4)
            dx = self.position[0] - SCREEN_WIDTH//2
            dy = self.position[1] - SCREEN_HEIGHT//2
            current_angle = math.atan2(dy, dx)
            new_angle = current_angle + angle
            distance = math.sqrt(dx*dx + dy*dy)
            
            self.position[0] = SCREEN_WIDTH//2 + math.cos(new_angle) * distance
            self.position[1] = SCREEN_HEIGHT//2 + math.sin(new_angle) * distance
            
    def move(self, planet_pos):
        self.evade_defenses()
        return super().move(planet_pos)