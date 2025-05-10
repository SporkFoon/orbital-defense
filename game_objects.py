import pygame
import math
from config import SCREEN_WIDTH, SCREEN_HEIGHT, PLANET_RADIUS, RESOURCE_START, BLUE, CYAN

class GameObject:
    def __init__(self, position):
        self.position = position
        
    def update(self):
        pass
        
    def render(self, surface):
        pass

class Planet(GameObject):
    def __init__(self, position, health=100):
        super().__init__(position)
        self.health = health
        self.resources = RESOURCE_START
        self.shield_level = 0
        self.radius = PLANET_RADIUS
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, BLUE, (self.radius, self.radius), self.radius)
        
    def take_damage(self, amount):
        damage_reduced = amount * (1 - (self.shield_level * 0.1))
        self.health -= damage_reduced
        return damage_reduced
    
    def add_resources(self, amount):
        self.resources += amount
        
    def upgrade_shield(self):
        if self.resources >= 100 and self.shield_level < 5:
            self.resources -= 100
            self.shield_level += 1
            return True
        return False
        
    def check_game_over(self):
        return self.health <= 0
        
    def render(self, surface):
        surface.blit(self.image, (self.position[0] - self.radius, self.position[1] - self.radius))
        
        if self.shield_level > 0:
            shield_radius = self.radius + 10
            shield_surface = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
            shield_color = (*CYAN[:3], 50 + self.shield_level * 25)
            pygame.draw.circle(shield_surface, shield_color, (shield_radius, shield_radius), shield_radius)
            surface.blit(shield_surface, (self.position[0] - shield_radius, self.position[1] - shield_radius))

class Defense(GameObject):
    def __init__(self, position, orbital_radius, cost, damage, fire_rate):
        super().__init__(position)
        self.orbital_radius = orbital_radius
        self.cost = cost
        self.damage = damage
        self.fire_rate = fire_rate
        self.upgrade_level = 1
        self.angle = math.atan2(position[1] - SCREEN_HEIGHT//2, position[0] - SCREEN_WIDTH//2)
        self.last_fire_time = 0
        self.size = 20
        self.shots_fired = 0
        self.shots_hit = 0
        self.total_damage_dealt = 0
        
    def fire(self, current_time, enemies):
        if current_time - self.last_fire_time >= 1000 / self.fire_rate:
            target = self.detect_enemies(enemies)
            if target:
                self.last_fire_time = current_time
                self.shots_fired += 1
                return self._fire_at_target(target)
        return None
        
    def _fire_at_target(self, target):
        pass
        
    def upgrade(self):
        self.upgrade_level += 1
        self.damage *= 1.2
        self.fire_rate *= 1.1
        
    def calculate_aim(self, target):
        dx = target.position[0] - self.position[0]
        dy = target.position[1] - self.position[1]
        return math.atan2(dy, dx)
        
    def detect_enemies(self, enemies):
        if not enemies:
            return None
        closest = None
        min_dist = float('inf')
        for enemy in enemies:
            dx = enemy.position[0] - self.position[0]
            dy = enemy.position[1] - self.position[1]
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < min_dist:
                min_dist = dist
                closest = enemy
        return closest
        
    def render(self, surface):
        pygame.draw.circle(surface, (255, 0, 0), (int(self.position[0]), int(self.position[1])), self.size)