import pygame
from game_objects import Defense
from projectiles import Projectile
from config import RED, GREEN, YELLOW

class LaserTurret(Defense):
    def __init__(self, position, orbital_radius, cost=150, damage=25, fire_rate=1.5):
        super().__init__(position, orbital_radius, cost, damage, fire_rate)
        self.range = 200
        self.rotation_speed = 0.1
        self.charge_time = 0.5
        self.color = RED
        
    def _fire_at_target(self, target):
        aim_angle = self.calculate_aim(target)
        projectile = Projectile(self.position, aim_angle, self.damage, speed=10, color=self.color)
        return projectile
        
    def charge_laser(self):
        pass
        
    def render(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.position[0]), int(self.position[1])), self.size)

class ResourceCollector(Defense):
    def __init__(self, position, orbital_radius, cost=100):
        super().__init__(position, orbital_radius, cost, 0, 0)
        self.collection_rate = 10
        self.storage_capacity = 100
        self.current_storage = 0
        self.color = GREEN
        
    def collect_resources(self, dt):
        amount = self.collection_rate * dt / 1000
        collected = min(amount, self.storage_capacity - self.current_storage)
        self.current_storage += collected
        return collected
        
    def transfer_resources(self):
        resources = self.current_storage
        self.current_storage = 0
        return resources
        
    def upgrade_capacity(self):
        self.storage_capacity *= 1.5
        self.collection_rate *= 1.2
        
    def render(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.position[0]), int(self.position[1])), self.size)
        fill_percent = self.current_storage / self.storage_capacity
        fill_radius = int(self.size * fill_percent)
        if fill_radius > 0:
            pygame.draw.circle(surface, YELLOW, (int(self.position[0]), int(self.position[1])), fill_radius)