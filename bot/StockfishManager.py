import chess.engine

class StockfishManager:

    def __init__(self, stockfish_path_name, skill_level=0):
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path_name)
        print(self.engine.options["Threads"])
        print(self.engine.options["Hash"])
        print(self.engine.options["Ponder"])
        print(self.engine.options["MultiPV"])
        print(self.engine.options["UCI_LimitStrength"])
        print(self.engine.options["UCI_Elo"])
        print(self.engine.options["Skill Level"])
        print(self.engine.options["Slow Mover"])
        self.engine.configure({"Skill Level": skill_level,
                               "Threads": 10,
                               "Hash": 16,
                               "Slow Mover": 10,
                               "UCI_LimitStrength": False,
                               "UCI_Elo": 1400
                               })

    def get_best_move(self, board, depth=None):
        return str(self.engine.play(board, chess.engine.Limit(time = 0.8742, depth=depth), draw_offered=True).move)
    
    def set_option(self, option, value):
        print(f"set_option: {option}={value}")
        self.engine.configure({option: value})
        
