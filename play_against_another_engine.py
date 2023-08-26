import random

import chess
import chess.pgn
import chess.polyglot

from headers import *
from parameters import *
from piece_square_tables import *
from piece_values import *

from main import make_move

moves = []
board = chess.Board()
number_of_moves = 1

while not board.is_game_over(claim_draw=draw_agreement_allowed):

    if board.turn:
        board.push(make_move(40))

        print(f"The move is: {moves[-1]}\n" f"The number of moves: {number_of_moves}\n"
              f"\n" f"{board}\n")

    else:
        board.push(make_move(40))

        print(f"The move is: {moves[-1]}\n" f"The number of moves: {number_of_moves}\n"
              f"\n" f"{board}\n")

    number_of_moves = number_of_moves + 1

game = chess.pgn.Game()

for key, value in headers.items():
    game.headers[key] = value

game.headers["Result"] = str(board.result(claim_draw=draw_agreement_allowed))
game.add_line(moves)
print(game)