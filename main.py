import random

import chess
import chess.pgn
import chess.polyglot

from headers import *
from parameters import *
from piece_square_tables import *
from piece_values import *

PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING = range(1, 7)
WHITE, BLACK = 0, 1

zobrist_keys = {
    piece: {color: {square: random.getrandbits(64) for square in range(64)} for color in range(2)}
    for piece in range(1, 7)
}

initial_zobrist_key = random.getrandbits(64)
current_key = random.getrandbits(64)


def update_zobrist_key(move, current_key):
    from_square, to_square = move.from_square, move.to_square
    from_piece = board.piece_at(from_square)

    if from_piece is not None:
        piece = from_piece.piece_type
        color = from_piece.color
        new_key = current_key ^ zobrist_keys[piece][color][from_square] ^ zobrist_keys[piece][color][to_square]
    else:
        new_key = current_key  # No piece on the from_square

    return new_key


def capture_heuristic(move):
    capture_value = {
        chess.PAWN: 1, chess.KNIGHT: 3,
        chess.BISHOP: 3, chess.ROOK: 5,
        chess.QUEEN: 9
    }

    if board.is_capture(move):
        captured_piece = board.piece_at(move.to_square).piece_type
        return capture_value.get(captured_piece, 0)
    else:
        return 0


class TranspositionTable:
    def __init__(self):
        self.table = {}

    def lookup(self, zobrist_key):
        return self.table.get(zobrist_key)

    def store(self, entry):
        self.table[entry.zobrist_key] = entry


class TranspositionTableEntry:
    def __init__(self, zobrist_key, depth, score, flag, best_move):
        self.zobrist_key = zobrist_key
        self.depth = depth
        self.score = score
        self.flag = flag
        self.best_move = best_move


# Constants for transposition table flags
EXACT = 0
LOWER = 1
UPPER = 2

# Initialize the transposition table
transposition_table = TranspositionTable()


def make_move(depth):
    try:
        book_moves = chess.polyglot.MemoryMappedReader("opening_books/gm2600.bin").weighted_choice(board).move
        moves.append(book_moves)
        return book_moves

    except:
        best_evaluated_move = None
        best_value = float('-inf')

        alpha = float('-inf')
        beta = float('inf')

        for move in board.legal_moves:
            board.push(move)
            new_key = update_zobrist_key(move, current_key)  # Update the zobrist key
            boardValue = -alpha_beta_pruning(-beta, -alpha, depth - 1, new_key)  # Pass the new_key
            board.pop()

            if boardValue > best_value:
                best_value = boardValue
                best_evaluated_move = move

            alpha = max(alpha, boardValue)

        moves.append(best_evaluated_move)
        return best_evaluated_move


def has_non_pawn_material(board):
    non_pawn_material = {
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9
    }

    total_non_pawn_material = 0
    for square, piece in board.piece_map().items():
        if piece.piece_type in non_pawn_material:
            total_non_pawn_material += non_pawn_material[piece.piece_type]

    return total_non_pawn_material >= 10


def quiescence_search(alpha, beta):
    stand_pat = evaluation_function()

    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    legal_captures = [move for move in board.legal_moves if board.is_capture(move)]

    for move in legal_captures:
        board.push(move)
        score = -quiescence_search(-beta, -alpha)
        board.pop()

        if score >= beta:
            return beta

        if score > alpha:
            alpha = score

    return alpha


def alpha_beta_pruning(alpha, beta, depth, zobrist_key):
    tt_entry = transposition_table.lookup(zobrist_key)

    if tt_entry and tt_entry.depth >= depth:
        if tt_entry.flag == EXACT:
            return tt_entry.score
        elif tt_entry.flag == LOWER and tt_entry.score >= beta:
            return beta
        elif tt_entry.flag == UPPER and tt_entry.score <= alpha:
            return alpha

    if depth == 0:
        return quiescence_search(alpha, beta)

    legal_moves = list(board.legal_moves)
    in_check = board.is_check()

    best_score = -float('inf')

    # Null move pruning
    if depth >= 3 and not in_check and not has_non_pawn_material(board):
        null_move_depth = depth - 3
        board.push(chess.Move.null())
        new_key = update_zobrist_key(chess.Move.null(), zobrist_key)
        score = -alpha_beta_pruning(-beta, -beta + 1, null_move_depth, new_key)
        board.pop()
        if score >= beta:
            return beta

    # Move ordering
    legal_moves.sort(key=lambda move: capture_heuristic(move), reverse=True)

    for move in legal_moves:
        board.push(move)
        new_key = update_zobrist_key(move, zobrist_key)
        score = -alpha_beta_pruning(-beta, -alpha, depth - 1, new_key)
        board.pop()

        best_score = max(best_score, score)
        alpha = max(alpha, best_score)

        if alpha >= beta:
            tt_entry = TranspositionTableEntry(zobrist_key, depth, best_score, EXACT, move)
            transposition_table.store(tt_entry)
            break

    return best_score


def evaluation_function():
    white_pawn = len(board.pieces(chess.PAWN, chess.WHITE))
    black_pawn = len(board.pieces(chess.PAWN, chess.BLACK))
    white_knight = len(board.pieces(chess.KNIGHT, chess.WHITE))
    black_knight = len(board.pieces(chess.KNIGHT, chess.BLACK))
    white_bishop = len(board.pieces(chess.BISHOP, chess.WHITE))
    black_bishop = len(board.pieces(chess.BISHOP, chess.BLACK))
    white_rook = len(board.pieces(chess.ROOK, chess.WHITE))
    black_rook = len(board.pieces(chess.ROOK, chess.BLACK))
    white_queen = len(board.pieces(chess.QUEEN, chess.WHITE))
    black_queen = len(board.pieces(chess.QUEEN, chess.BLACK))

    if board.is_checkmate():
        if board.turn:
            return -9999
        else:
            return 9999

    if board.is_insufficient_material() or board.is_stalemate():
        return 0

    piece_difference = pawn_piece_value * (white_pawn - black_pawn) + knight_piece_value * (white_knight - black_knight) \
                       + bishop_piece_value * (white_bishop - black_bishop) + rook_piece_value * (
                               white_rook - black_rook) \
                       + queen_piece_value * (white_queen - black_queen)

    piece_types = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]
    color_multiplier = [1, -1]

    total_score = 0

    for piece_type in piece_types:
        for color in color_multiplier:
            piece_square_table = None

            if piece_type == chess.PAWN:
                piece_square_table = pawn_piece_square_table
            elif piece_type == chess.KNIGHT:
                piece_square_table = knight_piece_square_table
            elif piece_type == chess.BISHOP:
                piece_square_table = bishop_piece_square_table
            elif piece_type == chess.ROOK:
                piece_square_table = rook_piece_square_table
            elif piece_type == chess.QUEEN:
                piece_square_table = queen_piece_square_table
            elif piece_type == chess.KING:
                piece_square_table = king_piece_square_table_middle_game

            for square in board.pieces(piece_type, color):
                total_score += color * piece_square_table[square]

    if board.turn:
        return total_score + piece_difference
    else:
        return -(total_score + piece_difference)


moves = []
board = chess.Board()

number_of_moves = 0.5

while not board.is_game_over(claim_draw=draw_agreement_allowed):
    board.push(make_move(40 ))

    print(f"The move is: {moves[-1]}\n" f"The number of moves: {number_of_moves}\n"
          f"\n" f"{board}\n")

    number_of_moves = number_of_moves + 0.5

game = chess.pgn.Game()

for key, value in headers.items():
    game.headers[key] = value

game.headers["Result"] = str(board.result(claim_draw=draw_agreement_allowed))
game.add_line(moves)
print(game)
