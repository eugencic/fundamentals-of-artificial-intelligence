import math
from Board import Board
from ChessPiece import *
from functools import wraps
from Logger import Logger, BoardRepr
import random

logger = Logger()


def evaluate_board(board):
    # Scoring factors
    material_weight = 1.0
    positional_weight = 1.0
    king_safety_weight = 1.0
    mobility_weight = 0.1
    pawn_structure_weight = 0.1

    # Player colors
    player_color = board.get_player_color()
    opponent_color = 'black' if player_color == 'white' else 'white'

    # Evaluate material value
    material_score = evaluate_material_value(board)

    # Evaluate positional value
    player_positional_score = evaluate_positional_value(board, player_color)
    opponent_positional_score = evaluate_positional_value(board, opponent_color)
    positional_score = round(player_positional_score - opponent_positional_score, 3)

    # Evaluate king safety
    king_safety_score = evaluate_king_safety(board)

    # Evaluate mobility
    player_mobility_score = evaluate_mobility(board, player_color)
    opponent_mobility_score = evaluate_mobility(board, opponent_color)

    # Evaluate pawn structure
    pawn_structure_score = evaluate_pawn_structure(board)

    # Combine the scores with the specified weights
    total_score = (
            material_weight * material_score +
            positional_weight * positional_score +
            king_safety_weight * king_safety_score +
            mobility_weight * player_mobility_score +
            mobility_weight * opponent_mobility_score +
            pawn_structure_weight * pawn_structure_score
    )

    total_score = round(total_score, 3)
    print("\n")
    print(f"Material score: {material_score}")
    print(f"Positional score: {positional_score}")
    print(f"King safety score: {king_safety_score}")
    print(f"Player mobility score: {player_mobility_score}")
    print(f"Enemy mobility score: {opponent_mobility_score}")
    print(f"Pawn structure score: {pawn_structure_score}")
    print(f"Total score: {total_score}")

    return total_score


def evaluate_material_value(board):
    piece_values = {
        Pawn: 1,
        Knight: 3,
        Bishop: 3,
        Rook: 5,
        Queen: 9,
        King: 0,
    }

    material_score = 0
    for i in range(8):
        for j in range(8):
            piece = board[i][j]
            if isinstance(piece, ChessPiece):
                if piece.color == board.get_player_color():
                    material_score += piece_values[type(piece)]
                else:
                    material_score -= piece_values[type(piece)]
    return material_score


def evaluate_positional_value(board, player_color):
    # Positional values for each square on the chessboard
    positional_values = [
        [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2],
        [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.2],
        [0.2, 0.5, 0.7, 0.7, 0.7, 0.7, 0.5, 0.2],
        [0.2, 0.5, 0.7, 1.0, 1.0, 0.7, 0.5, 0.2],
        [0.2, 0.5, 0.7, 1.0, 1.0, 0.7, 0.5, 0.2],
        [0.2, 0.5, 0.7, 0.7, 0.7, 0.7, 0.5, 0.2],
        [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.2],
        [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]
    ]
    position_score = 0
    for i in range(8):
        for j in range(8):
            piece = board[i][j]
            if isinstance(piece, ChessPiece) and piece.color == player_color:
                position_score += positional_values[i][j]
    return position_score


def evaluate_king_safety(board):
    king_safety_score = 0
    player_color = board.get_player_color()
    opponent_color = 'black' if player_color == 'white' else 'white'
    player_king = None
    for i in range(8):
        for j in range(8):
            piece = board[i][j]
            if isinstance(piece, King):
                if piece.color == player_color:
                    player_king = (i, j)
    if player_king:
        player_king_row, player_king_col = player_king
        # Factor: Presence of enemy queen or other enemy pieces near player's king
        # Iterate two squares in all directions
        for i in range(-2, 3):
            for j in range(-2, 3):
                # Calculate the target cell position relative to the player's king
                target_row = player_king_row + i
                target_col = player_king_col + j
                # Check if the target cell position is within the chessboard bounds
                if 0 <= target_row < 8 and 0 <= target_col < 8:
                    piece = board[target_row][target_col]
                    # Check if the piece in the target cell is an enemy queen
                    if isinstance(piece, Queen) and piece.color == opponent_color:
                        king_safety_score -= 0.5
                    # Check if the piece in the target cell is another enemy piece
                    elif isinstance(piece, ChessPiece) and piece.color == opponent_color:
                        king_safety_score -= 0.3
        # Factor: Presence of player pieces near player's king
        # Iterate two squares in all directions
        for i in range(-1, 2):
            for j in range(-1, 2):
                # Calculate the target cell position relative to the player's king
                target_row = player_king_row + i
                target_col = player_king_col + j
                # Check if the target cell position is within the chessboard bounds
                if 0 <= target_row < 8 and 0 <= target_col < 8:
                    piece = board[target_row][target_col]
                    # Check if the piece in the target cell is a player piece
                    if isinstance(piece, ChessPiece) and not (isinstance(piece, King)) and piece.color == player_color:
                        king_safety_score += 0.1
        # Factor: Pawn Shield (Checking for pawns in front of the player's king)
        front_piece = board[player_king_row + 1][player_king_col]
        left_front_piece = board[player_king_row + 1][player_king_col - 1]
        right_front_piece = board[player_king_row + 1][player_king_col + 1]
        if player_king_row >= 0 and isinstance(front_piece, Pawn):
            king_safety_score += 1
        if player_king_row >= 0 and isinstance(left_front_piece, Pawn):
            king_safety_score += 1
        if player_king_row >= 0 and isinstance(right_front_piece, Pawn):
            king_safety_score += 1
    king_safety_score = round(king_safety_score, 3)
    return king_safety_score


def evaluate_mobility(board, player_color):
    if player_color == board.get_player_color():
        # Calculate the mobility for the player
        player_moves = 0
        for i in range(8):
            for j in range(8):
                piece = board[i][j]
                if isinstance(piece, ChessPiece) and piece.color == player_color:
                    # Count the legal moves for each of the player's pieces
                    player_moves += len(piece.get_moves(board))
        return player_moves
    else:
        # Calculate the mobility for the opponent
        opponent_moves = 0
        for i in range(8):
            for j in range(8):
                piece = board[i][j]
                if isinstance(piece, ChessPiece) and piece.color == player_color:
                    # Count the legal moves for each of the opponent's pieces
                    opponent_moves += len(piece.get_moves(board))
        return opponent_moves


def evaluate_pawn_structure(board):
    isolated_pawns = 0  # Counter for isolated pawns
    strong_chain_pawns = 0  # Counter for pawns in strong pawn chains
    # Iterate through the chessboard
    for i in range(8):
        for j in range(8):
            piece = board[i][j]
            if isinstance(piece, Pawn) and piece.color == board.get_player_color():
                is_isolated = True  # Flag to detect isolated pawns
                is_supported = False  # Flag to detect pawns in strong chains
                # Check for friendly pawns on adjacent files (left and right)
                if j > 0:
                    left_piece = board[i][j - 1]
                    if isinstance(left_piece, Pawn) and left_piece.color == board.get_player_color():
                        is_isolated = False  # The pawn is not isolated
                        is_supported = True  # It's part of a strong pawn chain
                if j < 7:
                    right_piece = board[i][j + 1]
                    if isinstance(right_piece, Pawn) and right_piece.color == board.get_player_color():
                        is_isolated = False  # The pawn is not isolated
                        is_supported = True  # It's part of a strong pawn chain
                # Update counters based on the isolated and supported pawns
                if is_isolated:
                    isolated_pawns -= 1  # Isolated pawns reduce the score
                if is_supported:
                    strong_chain_pawns += 1  # Pawns in strong chains increase the score
    # Calculate the overall pawn structure score by summing isolated and strong chain pawns
    pawn_structure_score = isolated_pawns + strong_chain_pawns
    return pawn_structure_score


# Decorator for logging the game tree
def log_tree(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        board: Board = args[0]
        if board.log:
            depth = args[1]
            write_to_file(board, depth)
        return func(*args, **kwargs)

    return wrapper


def write_to_file(board: Board, current_depth):
    global logger
    if board.depth == current_depth:
        logger.clear()
    board_repr = BoardRepr(board.unicode_array_repr(), current_depth, evaluate_board(board))
    logger.append(board_repr)


def minimax(board, depth, alpha, beta, max_player, save_move, data):
    # Base case: If we've reached the desired depth or the game is over, evaluate the current state.
    if depth == 0 or board.is_terminal():
        data[1] = evaluate_board(board)  # Store the evaluation in data[1].
        return data
    if max_player:
        max_eval = -math.inf
        for piece, move in generate_possible_moves(board, max_player):
            board.make_move(piece, move[0], move[1], keep_history=True)  # Make a move on the board.
            evaluation = minimax(board, depth - 1, alpha, beta, False, False, data)[1]
            if save_move:
                if evaluation >= max_eval:
                    if evaluation > data[1]:
                        data.clear()  # Clear previous best moves since we found a better one.
                        data[1] = evaluation  # Update the best evaluation.
                        data[0] = [(piece, move, evaluation)]  # Store the current best move.
                    elif evaluation == data[1]:
                        data[0].append((piece, move, evaluation))  # Add to the list of best moves if tied.
            board.unmake_move(piece)  # Undo the move on the board.
            max_eval = max(max_eval, evaluation)  # Update the maximum evaluation.
            alpha = max(alpha, evaluation)  # Update the alpha value for pruning.
            if beta <= alpha:
                break  # Beta pruning: No need to explore further if beta is less than or equal to alpha.
        return data
    else:
        min_eval = math.inf
        for piece, move in generate_possible_moves(board, max_player):
            board.make_move(piece, move[0], move[1], keep_history=True)  # Make a move on the board.
            evaluation = minimax(board, depth - 1, alpha, beta, True, False, data)[1]
            board.unmake_move(piece)  # Undo the move on the board.
            min_eval = min(min_eval, evaluation)  # Update the minimum evaluation.
            beta = min(beta, evaluation)  # Update the beta value for pruning.
            if beta <= alpha:
                break  # Alpha pruning: No need to explore further if alpha is greater than or equal to beta.
        return data


def generate_possible_moves(board, max_player):
    moves = []
    for i in range(8):
        for j in range(8):
            piece = board[i][j]

            # Check if the current position contains a chess piece of the correct color.
            if isinstance(piece, ChessPiece) and (max_player == (piece.color != board.get_player_color())):
                valid_moves = piece.filter_moves(piece.get_moves(board), board)  # Generate valid moves for the piece.
                for move in valid_moves:
                    moves.append((piece, move))  # Add the piece-move pair to the list of possible moves.

    return moves


def get_ai_move(board):
    # Initialize a variable to store the best move
    best_move = None
    # Iterate through different depths
    for depth in range(1, board.depth + 1):
        print(f"Searching at depth {depth}...")
        # Use the minimax function to search for the best move at the current depth
        moves = minimax(board, depth, -math.inf, math.inf, True, True, [[], 0])
        # Check if valid moves were found at the current depth
        if moves and len(moves[0]) > 0:
            # Find the move with the best score
            best_score = max(moves[0], key=lambda x: x[2])[2]
            # Print all moves and their scores
            # print("All moves and scores:")
            # for move in moves[0]:
            #     print(f"Move: {move[0]} to {move[1]} with score {move[2]}")
            # Select a random move from the best moves with the highest score
            piece_and_move = random.choice([move for move in moves[0] if move[2] == best_score])
            # Check if the selected piece and move are not None
            if piece_and_move[0] is not None and len(piece_and_move[1]) > 0 and isinstance(piece_and_move[1], tuple):
                # Update the best move if a better move was found
                best_move = piece_and_move
            # Check if the best move is not None and is a valid tuple
            if best_move[0] is not None and len(best_move[1]) > 0 and isinstance(best_move[1], tuple):
                piece = best_move[0]
                move = best_move[1]
                # Apply the best move to the board
                board.make_move(piece, move[0], move[1])
                # Print the best move and its score
                print(f"Best move: {piece} to {move} with score {best_score}")
            else:
                print("No valid move found.")
        else:
            print("No valid move found.")
    return True


def get_random_move(board):
    pieces = []
    moves = []
    for i in range(8):
        for j in range(8):
            if isinstance(board[i][j], ChessPiece) and board[i][j].color != board.get_player_color():
                pieces.append(board[i][j])
    for piece in pieces[:]:
        piece_moves = piece.filter_moves(piece.get_moves(board), board)
        if len(piece_moves) == 0:
            pieces.remove(piece)
        else:
            moves.append(piece_moves)
    if len(pieces) == 0:
        return
    piece = random.choice(pieces)
    move = random.choice(moves[pieces.index(piece)])
    if isinstance(piece, ChessPiece) and len(move) > 0:
        board.make_move(piece, move[0], move[1])
