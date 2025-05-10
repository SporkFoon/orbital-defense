from game_controller import GameController
from stats_display import StatsDisplay

def main():
    # Initialize and run the game
    game = GameController()
    game.main_loop()
    
    # After game is over, show statistics dashboard
    stats_display = StatsDisplay()
    stats_display.render_stats_dashboard()

if __name__ == "__main__":
    main()