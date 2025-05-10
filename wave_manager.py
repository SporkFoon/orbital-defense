import random
import math
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from enemies import BasicEnemy, FastEnemy

class WaveManager:
    def __init__(self):
        self.current_wave = 0
        self.difficulty_level = 1.0
        self.enemy_types = [BasicEnemy, FastEnemy]
        self.spawn_rate = 1.0
        self.enemies_in_wave = 0
        self.enemies_spawned = 0
        self.last_spawn_time = 0
        self.wave_active = False
        self.wave_outcomes = []
        
    def start_wave(self):
        self.current_wave += 1
        self.enemies_in_wave = self._calculate_wave_size()
        self.enemies_spawned = 0
        self.wave_active = True
        self.last_spawn_time = pygame.time.get_ticks()
        return self.current_wave
        
    def spawn_enemies(self, current_time):
        if not self.wave_active or self.enemies_spawned >= self.enemies_in_wave:
            return None
            
        if current_time - self.last_spawn_time >= 1000 / self.spawn_rate:
            angle = random.uniform(0, 2 * math.pi)
            radius = max(SCREEN_WIDTH, SCREEN_HEIGHT)
            x = SCREEN_WIDTH // 2 + math.cos(angle) * radius
            y = SCREEN_HEIGHT // 2 + math.sin(angle) * radius
            
            enemy_type = self._choose_enemy_type()
            enemy = enemy_type([x, y])
            
            self.enemies_spawned += 1
            self.last_spawn_time = current_time
            
            if self.enemies_spawned >= self.enemies_in_wave:
                self.wave_active = False
                
            return enemy
        return None
        
    def _calculate_wave_size(self):
        return int(5 + self.current_wave * 1.5)
        
    def _choose_enemy_type(self):
        if self.current_wave < 3:
            return BasicEnemy
        else:
            weights = [100 - min(80, self.current_wave * 10), min(80, self.current_wave * 10)]
            return random.choices(self.enemy_types, weights=weights, k=1)[0]
            
    def increase_difficulty(self):
        self.difficulty_level += 0.1
        self.spawn_rate = min(5.0, self.spawn_rate * 1.1)
        
    def wave_completed(self, success):
        self.wave_outcomes.append((self.current_wave, success))
        if success:
            self.increase_difficulty()