import pygame
import sys
import math
import random
import os
import csv
import sqlite3
from datetime import datetime

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Orbital Defense")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
PURPLE = (255, 0, 255)

FPS = 60
PLANET_RADIUS = 50
MAX_ORBITAL_RADIUS = 350
RESOURCE_START = 500
BACKGROUND_COLOR = (10, 10, 40)

clock = pygame.time.Clock()

def load_image(name, size=None):
    surface = pygame.Surface(size if size else (32, 32))
    surface.fill(BLUE)
    return surface

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
        pygame.draw.circle(surface, RED, (int(self.position[0]), int(self.position[1])), self.size)

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

class GameStats:
    def __init__(self):
        self.player_score = 0
        self.waves_completed = 0
        self.resources_collected = 0
        self.enemies_defeated = 0
        self.accuracy = 0.0
        self.total_shots = 0
        self.total_hits = 0
        self.damage_sources = {}
        self.upgrade_choices = {}
        self.defense_placements = []
        self.enemy_survival_times = []
        self.resources_over_time = []
        self.session_start_time = pygame.time.get_ticks()
        
        os.makedirs('data', exist_ok=True)
        
        self.init_db()
        
    def init_db(self):
        self.conn = sqlite3.connect('data/game_stats.db')
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_sessions (
            id INTEGER PRIMARY KEY,
            date TEXT,
            duration INTEGER,
            waves_completed INTEGER,
            score INTEGER,
            resources_collected INTEGER,
            enemies_defeated INTEGER,
            accuracy REAL
        )
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS defense_placements (
            session_id INTEGER,
            defense_type TEXT,
            orbital_radius REAL,
            angle REAL,
            upgrade_level INTEGER,
            damage_dealt INTEGER,
            FOREIGN KEY (session_id) REFERENCES game_sessions(id)
        )
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS enemy_data (
            session_id INTEGER,
            enemy_type TEXT,
            survival_time INTEGER,
            damage_dealt INTEGER,
            penetration_depth REAL,
            FOREIGN KEY (session_id) REFERENCES game_sessions(id)
        )
        ''')
        
        self.conn.commit()
        
    def update_stats(self, stat_type, value=None, **kwargs):
        if stat_type == "enemy_defeated":
            self.enemies_defeated += 1
            self.player_score += value
            
            enemy = kwargs.get('enemy')
            if enemy:
                survival_time = pygame.time.get_ticks() - enemy.spawn_time
                self.enemy_survival_times.append({
                    'enemy_type': enemy.__class__.__name__,
                    'survival_time': survival_time,
                    'penetration_depth': enemy.closest_approach
                })
                
        elif stat_type == "wave_completed":
            self.waves_completed += 1
            
        elif stat_type == "resources_collected":
            self.resources_collected += value
            current_time = pygame.time.get_ticks() - self.session_start_time
            self.resources_over_time.append((current_time, value))
            
        elif stat_type == "defense_placed":
            defense = kwargs.get('defense')
            if defense:
                self.defense_placements.append({
                    'type': defense.__class__.__name__,
                    'orbital_radius': defense.orbital_radius,
                    'angle': defense.angle,
                    'position': defense.position
                })
                
        elif stat_type == "damage_taken":
            source = kwargs.get('source', 'Unknown')
            amount = value
            if source not in self.damage_sources:
                self.damage_sources[source] = 0
            self.damage_sources[source] += amount
            
        elif stat_type == "shot_fired":
            self.total_shots += 1
            
        elif stat_type == "shot_hit":
            self.total_hits += 1
            
        elif stat_type == "upgrade_choice":
            upgrade_type = kwargs.get('upgrade_type', 'Unknown')
            if upgrade_type not in self.upgrade_choices:
                self.upgrade_choices[upgrade_type] = 0
            self.upgrade_choices[upgrade_type] += 1
            
        if self.total_shots > 0:
            self.accuracy = self.total_hits / self.total_shots
            
    def save_stats(self):
        session_duration = pygame.time.get_ticks() - self.session_start_time
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        self.cursor.execute('''
        INSERT INTO game_sessions (date, duration, waves_completed, score, resources_collected, enemies_defeated, accuracy)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (date_str, session_duration, self.waves_completed, self.player_score, 
              self.resources_collected, self.enemies_defeated, self.accuracy))
        
        session_id = self.cursor.lastrowid
        
        for placement in self.defense_placements:
            self.cursor.execute('''
            INSERT INTO defense_placements (session_id, defense_type, orbital_radius, angle, upgrade_level, damage_dealt)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (session_id, placement['type'], placement['orbital_radius'], placement['angle'], 1, 0))
            
        for enemy_data in self.enemy_survival_times:
            self.cursor.execute('''
            INSERT INTO enemy_data (session_id, enemy_type, survival_time, damage_dealt, penetration_depth)
            VALUES (?, ?, ?, ?, ?)
            ''', (session_id, enemy_data['enemy_type'], enemy_data['survival_time'], 0, enemy_data['penetration_depth']))
            
        self.conn.commit()
        
        with open(f'data/game_session_{date_str.replace(":", "-").replace(" ", "_")}.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Date', date_str])
            writer.writerow(['Duration (ms)', session_duration])
            writer.writerow(['Waves Completed', self.waves_completed])
            writer.writerow(['Score', self.player_score])
            writer.writerow(['Resources Collected', self.resources_collected])
            writer.writerow(['Enemies Defeated', self.enemies_defeated])
            writer.writerow(['Accuracy', self.accuracy])
        
    def generate_report(self):
        return {
            'summary': {
                'score': self.player_score,
                'waves': self.waves_completed,
                'resources': self.resources_collected,
                'enemies': self.enemies_defeated,
                'accuracy': self.accuracy
            }
        }
        
    def export_to_csv(self, filename='game_stats_export.csv'):
        with open(f'data/{filename}', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Game Summary Stats'])
            writer.writerow(['Score', 'Waves', 'Resources', 'Enemies', 'Accuracy'])
            writer.writerow([self.player_score, self.waves_completed, self.resources_collected, 
                            self.enemies_defeated, self.accuracy])
            
            writer.writerow([])
            writer.writerow(['Enemy Survival Data'])
            writer.writerow(['Enemy Type', 'Survival Time (ms)', 'Penetration Depth'])
            for enemy_data in self.enemy_survival_times:
                writer.writerow([enemy_data['enemy_type'], enemy_data['survival_time'], enemy_data['penetration_depth']])
                
            writer.writerow([])
            writer.writerow(['Defense Placement Data'])
            writer.writerow(['Type', 'Orbital Radius', 'Angle'])
            for placement in self.defense_placements:
                writer.writerow([placement['type'], placement['orbital_radius'], placement['angle']])

class GameController:
    def __init__(self):
        self.planet = Planet([SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2])
        self.defenses = []
        self.active_enemies = []
        self.projectiles = []
        self.wave_manager = WaveManager()
        self.stats = GameStats()
        self.game_time = 0
        self.selected_defense_type = LaserTurret
        self.game_over = False
        self.placement_mode = False
        self.wave_in_progress = False
        self.ui_manager = UIManager(self)
        self.show_help = True
        
    def start_game(self):
        self.game_time = pygame.time.get_ticks()
        self.stats.session_start_time = self.game_time
        
    def process_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.end_game()
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.end_game()
                    pygame.quit()
                    sys.exit()
                    
                elif event.key == pygame.K_SPACE and not self.wave_in_progress:
                    self.wave_manager.start_wave()
                    self.wave_in_progress = True
                    
                elif event.key == pygame.K_1:
                    self.selected_defense_type = LaserTurret
                    
                elif event.key == pygame.K_2:
                    self.selected_defense_type = ResourceCollector
                    
                elif event.key == pygame.K_p:
                    self.placement_mode = not self.placement_mode

                elif event.key == pygame.K_h:
                    self.show_help = not self.show_help
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.handle_click(pygame.mouse.get_pos())
                    
    def handle_click(self, pos):
        if self.placement_mode:
            dx = pos[0] - self.planet.position[0]
            dy = pos[1] - self.planet.position[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if PLANET_RADIUS + 20 <= distance <= MAX_ORBITAL_RADIUS:
                defense_cost = self.selected_defense_type(pos, distance).cost
                if self.planet.resources >= defense_cost:
                    defense = self.selected_defense_type(pos, distance)
                    self.defenses.append(defense)
                    self.planet.resources -= defense_cost
                    self.stats.update_stats("defense_placed", defense=defense)
            
    def update_game_state(self):
        current_time = pygame.time.get_ticks()
        dt = current_time - self.game_time
        self.game_time = current_time
        
        if self.planet.check_game_over():
            self.game_over = True
            
        for defense in self.defenses:
            if isinstance(defense, ResourceCollector):
                collected = defense.collect_resources(dt)
                if defense.current_storage >= defense.storage_capacity * 0.9:
                    transferred = defense.transfer_resources()
                    self.planet.add_resources(transferred)
                    self.stats.update_stats("resources_collected", transferred)
            else:
                projectile = defense.fire(current_time, self.active_enemies)
                if projectile:
                    self.projectiles.append(projectile)
                    self.stats.update_stats("shot_fired")
        
        for projectile in self.projectiles[:]:
            projectile.update()
            hit_enemy = projectile.check_collision(self.active_enemies)
            
            if hit_enemy:
                self.stats.update_stats("shot_hit")
                
            if projectile.destroyed:
                self.projectiles.remove(projectile)
                
        for enemy in self.active_enemies[:]:
            hit_planet = enemy.move(self.planet.position)
            
            if hit_planet:
                damage = enemy.attack(self.planet)
                self.stats.update_stats("damage_taken", damage, source=enemy.__class__.__name__)
                self.active_enemies.remove(enemy)
            elif enemy.destroyed:
                self.stats.update_stats("enemy_defeated", enemy.reward, enemy=enemy)
                self.active_enemies.remove(enemy)
                self.planet.add_resources(enemy.reward // 2)
                
        if self.wave_in_progress:
            new_enemy = self.wave_manager.spawn_enemies(current_time)
            if new_enemy:
                self.active_enemies.append(new_enemy)
                
            if not self.wave_manager.wave_active and len(self.active_enemies) == 0:
                self.wave_in_progress = False
                self.wave_manager.wave_completed(True)
                self.stats.update_stats("wave_completed")
    
    def render(self):
        screen.fill(BACKGROUND_COLOR)
        
        for r in range(100, MAX_ORBITAL_RADIUS + 1, 50):
            pygame.draw.circle(screen, (*WHITE, 30), self.planet.position, r, 1)
            
        if self.placement_mode:
            mouse_pos = pygame.mouse.get_pos()
            dx = mouse_pos[0] - self.planet.position[0]
            dy = mouse_pos[1] - self.planet.position[1]
            distance = math.sqrt(dx*dx + dy*dy)
            if PLANET_RADIUS + 20 <= distance <= MAX_ORBITAL_RADIUS:
                color = GREEN if self.planet.resources >= self.selected_defense_type(mouse_pos, distance).cost else RED
                pygame.draw.circle(screen, color, mouse_pos, 20, 2)
        
        self.planet.render(screen)
        
        for defense in self.defenses:
            defense.render(screen)
            
        for enemy in self.active_enemies:
            enemy.render(screen)
            
        for projectile in self.projectiles:
            projectile.render(screen)
            
        self.ui_manager.render_ui()

        if self.show_help:
            self.ui_manager.show_controls_overlay()
        
        pygame.display.flip()
        
    def end_game(self):
        self.stats.save_stats()
        
    def main_loop(self):
        self.start_game()
        
        while not self.game_over:
            self.process_input()
            self.update_game_state()
            self.render()
            clock.tick(FPS)
            
        self.ui_manager.show_game_over()
        self.end_game()

class UIManager:
    def __init__(self, game_controller):
        self.game_controller = game_controller
        self.font_small = pygame.font.SysFont(None, 24)
        self.font_medium = pygame.font.SysFont(None, 36)
        self.font_large = pygame.font.SysFont(None, 48)
        
    def render_ui(self):
        ui_overlay = pygame.Surface((SCREEN_WIDTH, 60), pygame.SRCALPHA)
        ui_overlay.fill((5, 5, 20, 220))  # Darker blue with more opacity
        screen.blit(ui_overlay, (0, 0))
    
        stats_x = 20
        stats_y = 10
    
        health_percent = self.game_controller.planet.health / 100
        health_width = 120
        health_height = 10
    
        health_color = (0, 230, 0) if health_percent > 0.5 else (230, 230, 0) if health_percent > 0.25 else (230, 0, 0)
        health_text = self.font_small.render(f"{int(self.game_controller.planet.health)}", True, health_color)
        screen.blit(health_text, (stats_x, stats_y - 2))
    
        pygame.draw.rect(screen, (30, 30, 40), (stats_x + 30, stats_y, health_width, health_height), 0, 3)
        pygame.draw.rect(screen, health_color, (stats_x + 30, stats_y, int(health_width * health_percent), health_height), 0, 3)
        pygame.draw.rect(screen, (100, 100, 120), (stats_x + 30, stats_y, health_width, health_height), 1, 3)
    
        resource_y = stats_y + 22
        pygame.draw.circle(screen, GREEN, (stats_x + 8, resource_y + 4), 6)  # Resource icon
        resource_text = self.font_small.render(f"{int(self.game_controller.planet.resources)}", True, WHITE)
        screen.blit(resource_text, (stats_x + 20, resource_y))
    
        center_x = SCREEN_WIDTH // 2 - 40
        wave_text = self.font_small.render(f"WAVE {self.game_controller.wave_manager.current_wave}", True, WHITE)
        screen.blit(wave_text, (center_x, stats_y))
    
        enemy_icon_size = 12
        enemy_count = len(self.game_controller.active_enemies)
        enemy_total = self.game_controller.wave_manager.enemies_in_wave
        enemy_text = self.font_small.render(f"{enemy_count}/{enemy_total}", True, PURPLE)
    
        enemy_icon_x = center_x + 5
        enemy_icon_y = resource_y + 2
        pygame.draw.circle(screen, PURPLE, (enemy_icon_x, enemy_icon_y), enemy_icon_size // 2)
        screen.blit(enemy_text, (enemy_icon_x + 15, resource_y))
    
        score_x = SCREEN_WIDTH - 120
        score_text = self.font_small.render(f"SCORE: {self.game_controller.stats.player_score}", True, WHITE)
        screen.blit(score_text, (score_x, stats_y))
    
        if not self.game_controller.wave_in_progress:
            dock_height = 60
            dock_overlay = pygame.Surface((SCREEN_WIDTH, dock_height), pygame.SRCALPHA)
            dock_overlay.fill((5, 5, 20, 220))  # Match top bar color
            screen.blit(dock_overlay, (0, SCREEN_HEIGHT - dock_height))
        
            button_width = 120
            button_height = 40
            button_y = SCREEN_HEIGHT - dock_height + 10
        
            laser_button_x = SCREEN_WIDTH // 2 - button_width - 15
            laser_selected = self.game_controller.selected_defense_type == LaserTurret
        
            button_color = (60, 60, 200) if laser_selected else (30, 30, 80)
            border_color = (100, 100, 255) if laser_selected else RED
            border_width = 3 if laser_selected else 2
        
            pygame.draw.rect(screen, button_color, (laser_button_x, button_y, button_width, button_height), 0, 6)
            pygame.draw.rect(screen, border_color, (laser_button_x, button_y, button_width, button_height), border_width, 6)
        
            pygame.draw.circle(screen, RED, (laser_button_x + 20, button_y + button_height//2), 8)
            pygame.draw.line(screen, (255, 100, 100), 
                        (laser_button_x + 28, button_y + button_height//2 - 5),
                        (laser_button_x + 40, button_y + button_height//2 + 5), 2)
        
            laser_text = self.font_small.render("Laser", True, WHITE)
            screen.blit(laser_text, (laser_button_x + 45, button_y + 8))
            laser_cost = self.font_small.render(f"${150}", True, (150, 150, 255))
            screen.blit(laser_cost, (laser_button_x + 45, button_y + 23))
        
            collector_button_x = SCREEN_WIDTH // 2 + 15
            collector_selected = self.game_controller.selected_defense_type == ResourceCollector
        
            button_color = (60, 180, 60) if collector_selected else (30, 80, 30)
            border_color = (100, 255, 100) if collector_selected else GREEN
            border_width = 3 if collector_selected else 2
        
            pygame.draw.rect(screen, button_color, (collector_button_x, button_y, button_width, button_height), 0, 6)
            pygame.draw.rect(screen, border_color, (collector_button_x, button_y, button_width, button_height), border_width, 6)
        
            pygame.draw.circle(screen, GREEN, (collector_button_x + 20, button_y + button_height//2), 8)
            pygame.draw.circle(screen, YELLOW, (collector_button_x + 20, button_y + button_height//2), 4)
        
            collector_text = self.font_small.render("Collector", True, WHITE)
            screen.blit(collector_text, (collector_button_x + 45, button_y + 8))
            collector_cost = self.font_small.render(f"${100}", True, (150, 255, 150))
            screen.blit(collector_cost, (collector_button_x + 45, button_y + 23))
    
        if self.game_controller.placement_mode:
            placement_text = self.font_medium.render("PLACEMENT MODE", True, GREEN)
            text_width = placement_text.get_width()
            pygame.draw.rect(screen, (0, 0, 0, 180), 
                            (SCREEN_WIDTH // 2 - text_width // 2 - 15, 70, text_width + 30, 40), 0, 10)
            pygame.draw.rect(screen, GREEN, 
                            (SCREEN_WIDTH // 2 - text_width // 2 - 15, 70, text_width + 30, 40), 1, 10)
            screen.blit(placement_text, (SCREEN_WIDTH // 2 - text_width // 2, 75))
    
        if not self.game_controller.wave_in_progress and self.game_controller.wave_manager.current_wave > 0:
            complete_text = self.font_medium.render("Wave Complete! Press SPACE for next wave", True, WHITE)
            text_width = complete_text.get_width()
            pygame.draw.rect(screen, (0, 0, 0, 200), 
                            (SCREEN_WIDTH // 2 - text_width // 2 - 15, SCREEN_HEIGHT - 100, text_width + 30, 40), 0, 10)
            pygame.draw.rect(screen, WHITE, 
                            (SCREEN_WIDTH // 2 - text_width // 2 - 15, SCREEN_HEIGHT - 100, text_width + 30, 40), 1, 10)
            screen.blit(complete_text, (SCREEN_WIDTH // 2 - text_width // 2, SCREEN_HEIGHT - 95))
            
    def show_game_over(self):
        game_over_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            alpha = min(255, y * 0.6)
            color = (5, 5, max(5, 30 - y * 0.1))
            pygame.draw.line(game_over_bg, color, (0, y), (SCREEN_WIDTH, y))
        screen.blit(game_over_bg, (0, 0))
    
        box_width, box_height = 400, 300
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
    
        panel = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        panel.fill((10, 10, 40, 220))
        pygame.draw.rect(panel, (100, 100, 150), (0, 0, box_width, box_height), 2, 15)
        screen.blit(panel, (box_x, box_y))
    
        game_over_text = self.font_large.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, box_y + 30))
    
        score_text = self.font_medium.render(
            f"Final Score: {self.game_controller.stats.player_score}", True, WHITE)
        waves_text = self.font_medium.render(
            f"Waves Completed: {self.game_controller.stats.waves_completed}", True, WHITE)
    
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, box_y + 100))
        screen.blit(waves_text, (SCREEN_WIDTH // 2 - waves_text.get_width() // 2, box_y + 150))
    
        continue_box_width, continue_box_height = 300, 50
        continue_box_x = SCREEN_WIDTH // 2 - continue_box_width // 2
        continue_box_y = box_y + box_height - 70
    
        pygame.draw.rect(screen, (40, 40, 80), 
                        (continue_box_x, continue_box_y, continue_box_width, continue_box_height), 0, 10)
        pygame.draw.rect(screen, (100, 100, 150), 
                        (continue_box_x, continue_box_y, continue_box_width, continue_box_height), 2, 10)
    
        continue_text = self.font_small.render("Press Any Key to Continue (ESC to Quit)", True, WHITE)
        screen.blit(continue_text, 
                (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, continue_box_y + 15))
    
        pygame.display.flip()
    
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    waiting = False

    def show_controls_overlay(self):
        overlay = pygame.Surface((220, 190), pygame.SRCALPHA)
        overlay.fill((5, 5, 20, 230)) 
        pygame.draw.rect(overlay, WHITE, (0, 0, 220, 190), 1, 8) 
    
        title = self.font_medium.render("Controls", True, WHITE)
        overlay.blit(title, (10, 10))
    
        controls = [
            "1 - Laser Turret",
            "2 - Resource Collector",
            "P - Toggle Placement",
            "LMB - Place Defense",
            "Space - Start Wave",
            "H - Toggle Help",
            "Esc - Quit"
        ]
    
        for i, control in enumerate(controls):
            text = self.font_small.render(control, True, WHITE)
            overlay.blit(text, (15, 45 + i * 20))
    
        screen.blit(overlay, (SCREEN_WIDTH - 230, 70))

class StatsDisplay:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Orbital Defense - Statistics")
        self.font_small = pygame.font.SysFont(None, 24)
        self.font_medium = pygame.font.SysFont(None, 36)
        self.font_large = pygame.font.SysFont(None, 48)
        
        self.conn = sqlite3.connect('data/game_stats.db')
        self.cursor = self.conn.cursor()
        
    def load_data(self):
        self.cursor.execute("SELECT * FROM game_sessions ORDER BY date DESC LIMIT 10")
        self.sessions = self.cursor.fetchall()
        
        self.cursor.execute("""
        SELECT defense_type, orbital_radius, angle 
        FROM defense_placements 
        WHERE session_id = (SELECT id FROM game_sessions ORDER BY date DESC LIMIT 1)
        """)
        self.placements = self.cursor.fetchall()
        
        self.cursor.execute("""
        SELECT enemy_type, AVG(survival_time), COUNT(*) 
        FROM enemy_data 
        WHERE session_id = (SELECT id FROM game_sessions ORDER BY date DESC LIMIT 1)
        GROUP BY enemy_type
        """)
        self.enemy_data = self.cursor.fetchall()
        
    def generate_heatmap(self):
        heatmap = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        for defense_type, radius, angle in self.placements:
            x = SCREEN_WIDTH // 2 + radius * math.cos(angle)
            y = SCREEN_HEIGHT // 2 + radius * math.sin(angle)
            
            if defense_type == 'LaserTurret':
                color = (*RED, 100)
            elif defense_type == 'ResourceCollector':
                color = (*GREEN, 100)
            else:
                color = (*BLUE, 100)
                
            pygame.draw.circle(heatmap, color, (int(x), int(y)), 30)
            
        return heatmap
        
    def plot_resource_graph(self):
        self.cursor.execute("""
        SELECT resources_collected FROM game_sessions 
        ORDER BY date DESC LIMIT 10
        """)
        resources = self.cursor.fetchall()
        
        graph = pygame.Surface((600, 300), pygame.SRCALPHA)
        graph.fill((*BLACK, 150))
        
        pygame.draw.line(graph, WHITE, (50, 250), (550, 250))
        pygame.draw.line(graph, WHITE, (50, 250), (50, 50))
        
        if resources:
            max_value = max([r[0] for r in resources]) if resources else 1
            for i, (r,) in enumerate(resources):
                bar_height = (r / max_value) * 200 if max_value > 0 else 0
                pygame.draw.rect(graph, GREEN, (60 + i * 50, 250 - bar_height, 40, bar_height))
                
            for i, (r,) in enumerate(resources):
                text = self.font_small.render(str(r), True, WHITE)
                graph.blit(text, (60 + i * 50, 255))
                
        return graph
        
    def show_defense_effectiveness(self):
        self.cursor.execute("""
        SELECT defense_type, COUNT(*) 
        FROM defense_placements 
        GROUP BY defense_type
        """)
        defense_counts = self.cursor.fetchall()
        
        graph = pygame.Surface((600, 300), pygame.SRCALPHA)
        graph.fill((*BLACK, 150))
        
        if defense_counts:
            total = sum([count for _, count in defense_counts])
            colors = [RED, GREEN, BLUE, YELLOW, CYAN]
            
            start_angle = 0
            for i, (defense_type, count) in enumerate(defense_counts):
                angle = count / total * 360 if total > 0 else 0
                end_angle = start_angle + angle
                
                pygame.draw.arc(graph, colors[i % len(colors)], (100, 50, 200, 200), 
                               math.radians(start_angle), math.radians(end_angle), 100)
                
                label_angle = math.radians(start_angle + angle / 2)
                label_x = 200 + math.cos(label_angle) * 150
                label_y = 150 + math.sin(label_angle) * 150
                
                label = self.font_small.render(f"{defense_type}: {count}", True, WHITE)
                graph.blit(label, (label_x, label_y))
                
                start_angle = end_angle
                
        return graph
        
    def display_enemy_analysis(self):
        self.cursor.execute("""
        SELECT enemy_type, AVG(survival_time), COUNT(*) 
        FROM enemy_data 
        GROUP BY enemy_type
        """)
        enemy_stats = self.cursor.fetchall()
        
        graph = pygame.Surface((600, 300), pygame.SRCALPHA)
        graph.fill((*BLACK, 150))
        
        if enemy_stats:
            max_time = max([avg_time for _, avg_time, _ in enemy_stats]) if enemy_stats else 1
            
            pygame.draw.line(graph, WHITE, (50, 250), (550, 250))
            pygame.draw.line(graph, WHITE, (50, 250), (50, 50))
            
            bar_width = 400 // len(enemy_stats) if enemy_stats else 100
            for i, (enemy_type, avg_time, count) in enumerate(enemy_stats):
                bar_height = (avg_time / max_time) * 200 if max_time > 0 else 0
                x = 80 + i * (bar_width + 20)
                
                pygame.draw.rect(graph, PURPLE, (x, 250 - bar_height, bar_width, bar_height))
                
                type_label = self.font_small.render(enemy_type, True, WHITE)
                time_label = self.font_small.render(f"{avg_time:.1f}ms", True, WHITE)
                count_label = self.font_small.render(f"n={count}", True, WHITE)
                
                graph.blit(type_label, (x, 255))
                graph.blit(time_label, (x, 250 - bar_height - 20))
                graph.blit(count_label, (x, 275))
                
        return graph
        
    def render_stats_dashboard(self):
        self.load_data()
        
        running = True
        current_page = 0
        total_pages = 4
        
        while running:
            self.screen.fill(BLACK)
            
            title = self.font_large.render("Orbital Defense Statistics", True, WHITE)
            self.screen.blit(title, (SCREEN_WIDTH // 2 - 200, 20))
            
            nav_text = self.font_small.render("Press LEFT/RIGHT to navigate, ESC to exit", True, WHITE)
            self.screen.blit(nav_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 30))
            
            if current_page == 0:
                summary_title = self.font_medium.render("Game Summary", True, WHITE)
                self.screen.blit(summary_title, (SCREEN_WIDTH // 2 - 100, 80))
                
                if self.sessions:
                    latest = self.sessions[0]
                    stats = [
                        f"Date: {latest[1]}",
                        f"Duration: {latest[2]/1000:.1f} seconds",
                        f"Waves Completed: {latest[3]}",
                        f"Score: {latest[4]}",
                        f"Resources Collected: {latest[5]}",
                        f"Enemies Defeated: {latest[6]}",
                        f"Accuracy: {latest[7]*100:.1f}%"
                    ]
                    
                    for i, stat in enumerate(stats):
                        stat_text = self.font_small.render(stat, True, WHITE)
                        self.screen.blit(stat_text, (SCREEN_WIDTH // 2 - 150, 120 + i * 30))
                else:
                    no_data = self.font_medium.render("No game data available", True, RED)
                    self.screen.blit(no_data, (SCREEN_WIDTH // 2 - 120, 200))
                    
            elif current_page == 1:
                heatmap_title = self.font_medium.render("Defense Placement Heatmap", True, WHITE)
                self.screen.blit(heatmap_title, (SCREEN_WIDTH // 2 - 150, 80))
                
                heatmap = self.generate_heatmap()
                self.screen.blit(heatmap, (0, 0))
                
                pygame.draw.circle(self.screen, BLUE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), PLANET_RADIUS)
                
                red_label = self.font_small.render("Red: Laser Turrets", True, RED)
                green_label = self.font_small.render("Green: Resource Collectors", True, GREEN)
                
                self.screen.blit(red_label, (SCREEN_WIDTH - 200, 120))
                self.screen.blit(green_label, (SCREEN_WIDTH - 200, 150))
                
            elif current_page == 2:
                resource_title = self.font_medium.render("Resource Collection History", True, WHITE)
                self.screen.blit(resource_title, (SCREEN_WIDTH // 2 - 150, 80))
                
                resource_graph = self.plot_resource_graph()
                self.screen.blit(resource_graph, (SCREEN_WIDTH // 2 - 300, 120))
                
                x_label = self.font_small.render("Game Sessions (Most Recent First)", True, WHITE)
                y_label = self.font_small.render("Resources", True, WHITE)
                
                self.screen.blit(x_label, (SCREEN_WIDTH // 2 - 100, 430))
                
                y_surface = pygame.Surface((30, 100), pygame.SRCALPHA)
                y_surface.fill((0, 0, 0, 0))
                y_surface.blit(pygame.transform.rotate(y_label, 90), (0, 0))
                self.screen.blit(y_surface, (SCREEN_WIDTH // 2 - 290, 200))
                
            elif current_page == 3:
                enemy_title = self.font_medium.render("Enemy Survival Analysis", True, WHITE)
                self.screen.blit(enemy_title, (SCREEN_WIDTH // 2 - 150, 80))
                
                enemy_graph = self.display_enemy_analysis()
                self.screen.blit(enemy_graph, (SCREEN_WIDTH // 2 - 300, 120))
                
                x_label = self.font_small.render("Enemy Types", True, WHITE)
                y_label = self.font_small.render("Avg. Survival Time (ms)", True, WHITE)
                
                self.screen.blit(x_label, (SCREEN_WIDTH // 2 - 50, 430))
                
                y_surface = pygame.Surface((30, 180), pygame.SRCALPHA)
                y_surface.fill((0, 0, 0, 0))
                y_surface.blit(pygame.transform.rotate(y_label, 90), (0, 0))
                self.screen.blit(y_surface, (SCREEN_WIDTH // 2 - 290, 180))
                
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_LEFT:
                        current_page = (current_page - 1) % total_pages
                    elif event.key == pygame.K_RIGHT:
                        current_page = (current_page + 1) % total_pages
                        
        pygame.quit()

def main():
    game = GameController()
    game.main_loop()
    
    stats_display = StatsDisplay()
    stats_display.render_stats_dashboard()

if __name__ == "__main__":
    main()