import chess

class ChessBoard:
    def __init__(self):
        self.board = chess.Board()
        

    def getBoard(self):
        return self.board  

    def makeMove(self, move):
        self.board.push_san(move)
    def getPiece(self, field):
        return str(self.board.piece_at(chess.parse_square(field)))
