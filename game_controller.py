import pygame
import sys
import math
from config import SCREEN_WIDTH, SCREEN_HEIGHT, PLANET_RADIUS, MAX_ORBITAL_RADIUS, BACKGROUND_COLOR, WHITE, GREEN, RED
from game_objects import Planet
from defenses import LaserTurret, ResourceCollector
from ui_manager import UIManager
from game_stats import GameStats
from wave_manager import WaveManager

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
        screen = pygame.display.get_surface()
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
            pygame.time.Clock().tick(60)
            
        self.ui_manager.show_game_over()
        self.end_game()