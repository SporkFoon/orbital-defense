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
        try:
            self.cursor.execute("SELECT * FROM game_sessions ORDER BY date DESC LIMIT 10")
            self.sessions = self.cursor.fetchall()
        
            if self.sessions:
                latest_session_id = self.sessions[0][0]
            
                self.cursor.execute("""
                SELECT defense_type, orbital_radius, angle 
                FROM defense_placements 
                WHERE session_id = ?
                """, (latest_session_id,))
                self.placements = self.cursor.fetchall()
            
                self.cursor.execute("""
                SELECT enemy_type, AVG(survival_time), COUNT(*) 
                FROM enemy_data 
                WHERE session_id = ?
                GROUP BY enemy_type
                """, (latest_session_id,))
                self.enemy_data = self.cursor.fetchall()
            else:
                self.placements = []
                self.enemy_data = []
            
        except sqlite3.Error as e:
            print(f"Database error while loading data: {e}")
            self.sessions = []
            self.placements = []
            self.enemy_data = []
        
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
        try:
            self.cursor.execute("""
            SELECT resources_collected, date FROM game_sessions 
            ORDER BY date DESC LIMIT 10
            """)
            resources_data = self.cursor.fetchall()
        
            graph = pygame.Surface((600, 350), pygame.SRCALPHA)
            graph.fill((0, 0, 0, 150))
        
            pygame.draw.line(graph, (255, 255, 255), (70, 290), (570, 290), 2)  # X-axis
            pygame.draw.line(graph, (255, 255, 255), (70, 290), (70, 40), 2)    # Y-axis
        
            x_label = self.font_small.render("Game Sessions (Most Recent First)", True, (255, 255, 255))
            graph.blit(x_label, (250, 320))
        
            y_label = pygame.Surface((25, 150), pygame.SRCALPHA)
            y_label_text = self.font_small.render("Resources Collected", True, (255, 255, 255))
            y_label.blit(pygame.transform.rotate(y_label_text, 90), (0, 0))
            graph.blit(y_label, (20, 100))
        
            if not resources_data:
                no_data_text = self.font_small.render("No game history available", True, (255, 0, 0))
                graph.blit(no_data_text, (200, 150))
                return graph
            
            max_value = max(max([r[0] for r in resources_data] or [1]), 1)
        
            max_value = max_value * 1.1
        
            bar_width = min(40, 400 // len(resources_data))
            spacing = min(15, 60 // len(resources_data))
        
            for i in range(5):
                y_pos = 290 - (i * 250 / 4)
                value = int(max_value * i / 4)
                marker_text = self.font_small.render(str(value), True, (255, 255, 255))
                graph.blit(marker_text, (40 - marker_text.get_width(), y_pos - 10))
                pygame.draw.line(graph, (100, 100, 100), (65, y_pos), (570, y_pos), 1)  # Horizontal grid line
        
            for i, (resource_value, date_str) in enumerate(resources_data):
                resource_value = round(resource_value)
            
                bar_height = (resource_value / max_value) * 250 if max_value > 0 else 0
            
                x_pos = 80 + i * (bar_width + spacing)
            
                pygame.draw.rect(graph, (0, 255, 0), 
                                (x_pos, 290 - bar_height, bar_width, bar_height))
            
                value_text = self.font_small.render(str(resource_value), True, (255, 255, 255))
                text_x = x_pos + (bar_width // 2) - (value_text.get_width() // 2)
                text_y = 285 - bar_height - value_text.get_height()
                if bar_height > 20:
                    graph.blit(value_text, (text_x, text_y))
            
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    date_short = date.strftime('%m/%d %H:%M')
                except:
                    date_short = f"Game {i+1}"
                
                session_text = self.font_small.render(f"{i+1}", True, (255, 255, 255))
                graph.blit(session_text, (x_pos + bar_width // 2 - 5, 295))
            
                if i % 2 == 0:
                    date_label = self.font_small.render(date_short, True, (200, 200, 200))
                    rotated_label = pygame.transform.rotate(date_label, 45)
                    graph.blit(rotated_label, (x_pos - 5, 300))
                
            return graph
        
        except sqlite3.Error as e:
            error_graph = pygame.Surface((600, 350), pygame.SRCALPHA)
            error_graph.fill((0, 0, 0, 150))
            error_text = self.font_small.render(f"Database error: {e}", True, (255, 0, 0))
            error_graph.blit(error_text, (50, 150))
            return error_graph
        
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
    
        background_color = (5, 5, 20)
        title_color = (220, 220, 255)
        highlight_color = (100, 100, 220)
    
        while running:
            self.screen.fill(background_color)
        
            header_bar = pygame.Surface((SCREEN_WIDTH, 80), pygame.SRCALPHA)
            header_bar.fill((20, 20, 40, 180))
            self.screen.blit(header_bar, (0, 0))
        
            title = self.font_large.render("Orbital Defense Statistics", True, title_color)
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))
        
            footer_bar = pygame.Surface((SCREEN_WIDTH, 40), pygame.SRCALPHA)
            footer_bar.fill((20, 20, 40, 180))
            self.screen.blit(footer_bar, (0, SCREEN_HEIGHT - 40))
        
            nav_text = self.font_small.render(
                f"Page {current_page+1}/{total_pages} - Press LEFT/RIGHT to navigate, ESC to exit", 
                True, (255, 255, 255))
            self.screen.blit(nav_text, (SCREEN_WIDTH // 2 - nav_text.get_width() // 2, SCREEN_HEIGHT - 30))
        
            if current_page == 0:
                page_title = "Game Summary"
            elif current_page == 1:
                page_title = "Defense Placement Heatmap"
            elif current_page == 2:
                page_title = "Resource Collection History"
            elif current_page == 3:
                page_title = "Enemy Survival Analysis"
            
            page_title_text = self.font_medium.render(page_title, True, highlight_color)
            self.screen.blit(page_title_text, (SCREEN_WIDTH // 2 - page_title_text.get_width() // 2, 80))
        
            if current_page == 0:
                if self.sessions:
                    latest = self.sessions[0]
                
                    panel = pygame.Surface((500, 350), pygame.SRCALPHA)
                    panel.fill((30, 30, 60, 180))
                    pygame.draw.rect(panel, highlight_color, (0, 0, 500, 350), 2, 10)
                    self.screen.blit(panel, (SCREEN_WIDTH // 2 - 250, 120))
                
                    stats = [
                        ("Date", f"{latest[1]}"),
                        ("Duration", f"{latest[2]/1000:.1f} seconds"),
                        ("Waves Completed", f"{latest[3]}"),
                        ("Score", f"{latest[4]}"),
                        ("Resources Collected", f"{latest[5]}"),
                        ("Enemies Defeated", f"{latest[6]}"),
                        ("Accuracy", f"{latest[7]*100:.1f}%")
                    ]
                
                    for i, (label, value) in enumerate(stats):
                        label_text = self.font_small.render(f"{label}:", True, (200, 200, 255))
                        value_text = self.font_small.render(value, True, (255, 255, 255))
                    
                        self.screen.blit(label_text, (SCREEN_WIDTH // 2 - 220, 150 + i * 40))
                        self.screen.blit(value_text, (SCREEN_WIDTH // 2 + 20, 150 + i * 40))
                else:
                    no_data = self.font_medium.render("No game data available", True, (255, 100, 100))
                    self.screen.blit(no_data, (SCREEN_WIDTH // 2 - no_data.get_width() // 2, 200))
                
            elif current_page == 1:
                if self.placements:
                    heatmap = self.generate_heatmap()
                    self.screen.blit(heatmap, (0, 0))
                
                    pygame.draw.circle(self.screen, (50, 50, 200), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 50)
                    pygame.draw.circle(self.screen, (100, 100, 255), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 50, 2)
                
                    legend_panel = pygame.Surface((200, 100), pygame.SRCALPHA)
                    legend_panel.fill((20, 20, 40, 200))
                    pygame.draw.rect(legend_panel, (100, 100, 150), (0, 0, 200, 100), 2, 5)
                    self.screen.blit(legend_panel, (SCREEN_WIDTH - 220, 120))
                
                    legend_title = self.font_small.render("Legend", True, (200, 200, 255))
                    self.screen.blit(legend_title, (SCREEN_WIDTH - 190, 125))
                
                    pygame.draw.circle(self.screen, (255, 0, 0), (SCREEN_WIDTH - 200, 155), 8)
                    pygame.draw.circle(self.screen, (0, 255, 0), (SCREEN_WIDTH - 200, 180), 8)
                
                    red_label = self.font_small.render("Laser Turrets", True, (255, 100, 100))
                    green_label = self.font_small.render("Resource Collectors", True, (100, 255, 100))
                
                    self.screen.blit(red_label, (SCREEN_WIDTH - 180, 150))
                    self.screen.blit(green_label, (SCREEN_WIDTH - 180, 175))
                else:
                    no_data = self.font_medium.render("No placement data available", True, (255, 100, 100))
                    self.screen.blit(no_data, (SCREEN_WIDTH // 2 - no_data.get_width() // 2, 200))
                
            elif current_page == 2:
                resource_graph = self.plot_resource_graph()
                self.screen.blit(resource_graph, (SCREEN_WIDTH // 2 - 300, 120))
                
            elif current_page == 3:
                if self.enemy_data:
                    enemy_graph = self.display_enemy_analysis()
                    self.screen.blit(enemy_graph, (SCREEN_WIDTH // 2 - 300, 120))
                else:
                    no_data = self.font_medium.render("No enemy data available", True, (255, 100, 100))
                    self.screen.blit(no_data, (SCREEN_WIDTH // 2 - no_data.get_width() // 2, 200))
                
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