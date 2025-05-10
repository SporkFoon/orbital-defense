import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED, GREEN, BLUE, YELLOW, PURPLE
from defenses import LaserTurret, ResourceCollector

class UIManager:
    def __init__(self, game_controller):
        self.game_controller = game_controller
        self.font_small = pygame.font.SysFont(None, 24)
        self.font_medium = pygame.font.SysFont(None, 36)
        self.font_large = pygame.font.SysFont(None, 48)
        
    def render_ui(self):
        ui_overlay = pygame.Surface((SCREEN_WIDTH, 60), pygame.SRCALPHA)
        ui_overlay.fill((5, 5, 20, 220))
        pygame.display.get_surface().blit(ui_overlay, (0, 0))
    
        stats_x = 20
        stats_y = 10
    
        health_percent = self.game_controller.planet.health / 100
        health_width = 120
        health_height = 10
    
        health_color = (0, 230, 0) if health_percent > 0.5 else (230, 230, 0) if health_percent > 0.25 else (230, 0, 0)
        health_text = self.font_small.render(f"{int(self.game_controller.planet.health)}", True, health_color)
        pygame.display.get_surface().blit(health_text, (stats_x, stats_y - 2))
    
        pygame.draw.rect(pygame.display.get_surface(), (30, 30, 40), (stats_x + 30, stats_y, health_width, health_height), 0, 3)
        pygame.draw.rect(pygame.display.get_surface(), health_color, (stats_x + 30, stats_y, int(health_width * health_percent), health_height), 0, 3)
        pygame.draw.rect(pygame.display.get_surface(), (100, 100, 120), (stats_x + 30, stats_y, health_width, health_height), 1, 3)
    
        resource_y = stats_y + 22
        pygame.draw.circle(pygame.display.get_surface(), GREEN, (stats_x + 8, resource_y + 4), 6)  # Resource icon
        resource_text = self.font_small.render(f"{int(self.game_controller.planet.resources)}", True, WHITE)
        pygame.display.get_surface().blit(resource_text, (stats_x + 20, resource_y))
    
        center_x = SCREEN_WIDTH // 2 - 40
        wave_text = self.font_small.render(f"WAVE {self.game_controller.wave_manager.current_wave}", True, WHITE)
        pygame.display.get_surface().blit(wave_text, (center_x, stats_y))
    
        enemy_icon_size = 12
        enemy_count = len(self.game_controller.active_enemies)
        enemy_total = self.game_controller.wave_manager.enemies_in_wave
        enemy_text = self.font_small.render(f"{enemy_count}/{enemy_total}", True, PURPLE)
    
        enemy_icon_x = center_x + 5
        enemy_icon_y = resource_y + 2
        pygame.draw.circle(pygame.display.get_surface(), PURPLE, (enemy_icon_x, enemy_icon_y), enemy_icon_size // 2)
        pygame.display.get_surface().blit(enemy_text, (enemy_icon_x + 15, resource_y))
    
        score_x = SCREEN_WIDTH - 120
        score_text = self.font_small.render(f"SCORE: {self.game_controller.stats.player_score}", True, WHITE)
        pygame.display.get_surface().blit(score_text, (score_x, stats_y))
    
        if not self.game_controller.wave_in_progress:
            dock_height = 60
            dock_overlay = pygame.Surface((SCREEN_WIDTH, dock_height), pygame.SRCALPHA)
            dock_overlay.fill((5, 5, 20, 220))
            pygame.display.get_surface().blit(dock_overlay, (0, SCREEN_HEIGHT - dock_height))
        
            button_width = 120
            button_height = 40
            button_y = SCREEN_HEIGHT - dock_height + 10
        
            laser_button_x = SCREEN_WIDTH // 2 - button_width - 15
            laser_selected = self.game_controller.selected_defense_type == LaserTurret
        
            button_color = (60, 60, 200) if laser_selected else (30, 30, 80)
            border_color = (100, 100, 255) if laser_selected else RED
            border_width = 3 if laser_selected else 2
        
            pygame.draw.rect(pygame.display.get_surface(), button_color, (laser_button_x, button_y, button_width, button_height), 0, 6)
            pygame.draw.rect(pygame.display.get_surface(), border_color, (laser_button_x, button_y, button_width, button_height), border_width, 6)
        
            pygame.draw.circle(pygame.display.get_surface(), RED, (laser_button_x + 20, button_y + button_height//2), 8)
            pygame.draw.line(pygame.display.get_surface(), (255, 100, 100), 
                        (laser_button_x + 28, button_y + button_height//2 - 5),
                        (laser_button_x + 40, button_y + button_height//2 + 5), 2)
        
            laser_text = self.font_small.render("Laser", True, WHITE)
            pygame.display.get_surface().blit(laser_text, (laser_button_x + 45, button_y + 8))
            laser_cost = self.font_small.render(f"${150}", True, (150, 150, 255))
            pygame.display.get_surface().blit(laser_cost, (laser_button_x + 45, button_y + 23))
        
            collector_button_x = SCREEN_WIDTH // 2 + 15
            collector_selected = self.game_controller.selected_defense_type == ResourceCollector
        
            button_color = (60, 180, 60) if collector_selected else (30, 80, 30)
            border_color = (100, 255, 100) if collector_selected else GREEN
            border_width = 3 if collector_selected else 2
        
            pygame.draw.rect(pygame.display.get_surface(), button_color, (collector_button_x, button_y, button_width, button_height), 0, 6)
            pygame.draw.rect(pygame.display.get_surface(), border_color, (collector_button_x, button_y, button_width, button_height), border_width, 6)
        
            pygame.draw.circle(pygame.display.get_surface(), GREEN, (collector_button_x + 20, button_y + button_height//2), 8)
            pygame.draw.circle(pygame.display.get_surface(), YELLOW, (collector_button_x + 20, button_y + button_height//2), 4)
        
            collector_text = self.font_small.render("Collector", True, WHITE)
            pygame.display.get_surface().blit(collector_text, (collector_button_x + 45, button_y + 8))
            collector_cost = self.font_small.render(f"${100}", True, (150, 255, 150))
            pygame.display.get_surface().blit(collector_cost, (collector_button_x + 45, button_y + 23))
    
        if self.game_controller.placement_mode:
            placement_text = self.font_medium.render("PLACEMENT MODE", True, GREEN)
            text_width = placement_text.get_width()
            pygame.draw.rect(pygame.display.get_surface(), (0, 0, 0, 180), 
                            (SCREEN_WIDTH // 2 - text_width // 2 - 15, 70, text_width + 30, 40), 0, 10)
            pygame.draw.rect(pygame.display.get_surface(), GREEN, 
                            (SCREEN_WIDTH // 2 - text_width // 2 - 15, 70, text_width + 30, 40), 1, 10)
            pygame.display.get_surface().blit(placement_text, (SCREEN_WIDTH // 2 - text_width // 2, 75))
    
        if not self.game_controller.wave_in_progress and self.game_controller.wave_manager.current_wave > 0:
            complete_text = self.font_medium.render("Wave Complete! Press SPACE for next wave", True, WHITE)
            text_width = complete_text.get_width()
            pygame.draw.rect(pygame.display.get_surface(), (0, 0, 0, 200), 
                            (SCREEN_WIDTH // 2 - text_width // 2 - 15, SCREEN_HEIGHT - 100, text_width + 30, 40), 0, 10)
            pygame.draw.rect(pygame.display.get_surface(), WHITE, 
                            (SCREEN_WIDTH // 2 - text_width // 2 - 15, SCREEN_HEIGHT - 100, text_width + 30, 40), 1, 10)
            pygame.display.get_surface().blit(complete_text, (SCREEN_WIDTH // 2 - text_width // 2, SCREEN_HEIGHT - 95))
            
    def show_game_over(self):
        game_over_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            alpha = min(255, y * 0.6)
            color = (5, 5, max(5, 30 - y * 0.1))
            pygame.draw.line(game_over_bg, color, (0, y), (SCREEN_WIDTH, y))
        pygame.display.get_surface().blit(game_over_bg, (0, 0))
    
        box_width, box_height = 400, 300
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
    
        panel = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        panel.fill((10, 10, 40, 220))
        pygame.draw.rect(panel, (100, 100, 150), (0, 0, box_width, box_height), 2, 15)
        pygame.display.get_surface().blit(panel, (box_x, box_y))
    
        game_over_text = self.font_large.render("GAME OVER", True, RED)
        pygame.display.get_surface().blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, box_y + 30))
    
        score_text = self.font_medium.render(
            f"Final Score: {self.game_controller.stats.player_score}", True, WHITE)
        waves_text = self.font_medium.render(
            f"Waves Completed: {self.game_controller.stats.waves_completed}", True, WHITE)
    
        pygame.display.get_surface().blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, box_y + 100))
        pygame.display.get_surface().blit(waves_text, (SCREEN_WIDTH // 2 - waves_text.get_width() // 2, box_y + 150))
    
        continue_box_width, continue_box_height = 300, 50
        continue_box_x = SCREEN_WIDTH // 2 - continue_box_width // 2
        continue_box_y = box_y + box_height - 70
    
        pygame.draw.rect(pygame.display.get_surface(), (40, 40, 80), 
                        (continue_box_x, continue_box_y, continue_box_width, continue_box_height), 0, 10)
        pygame.draw.rect(pygame.display.get_surface(), (100, 100, 150), 
                        (continue_box_x, continue_box_y, continue_box_width, continue_box_height), 2, 10)
    
        continue_text = self.font_small.render("Press Any Key to Continue (ESC to Quit)", True, WHITE)
        pygame.display.get_surface().blit(continue_text, 
                (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, continue_box_y + 15))
    
        pygame.display.flip()
    
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        import sys
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
    
        pygame.display.get_surface().blit(overlay, (SCREEN_WIDTH - 230, 70))