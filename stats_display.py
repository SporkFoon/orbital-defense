import pygame
import math
import sqlite3
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, RED, GREEN, BLUE, YELLOW, CYAN, PURPLE

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
                
                pygame.draw.circle(self.screen, BLUE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 50)
                
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