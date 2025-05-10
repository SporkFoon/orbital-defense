from game_controller import GameController
from stats_display import StatsDisplay

def main():
    game = GameController()
    game.main_loop()
    
    stats_display = StatsDisplay()
    stats_display.render_stats_dashboard()

if __name__ == "__main__":
    main()