import os
import csv
import sqlite3
import pygame
from datetime import datetime

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