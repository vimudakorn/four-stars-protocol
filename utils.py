import random
import string
from constants import EMPTY, COLS, ROWS


def generate_unique_room_number(existing_numbers):
    while True:
        room_number = ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=6))
        if room_number not in existing_numbers:
            return room_number


def create_board():
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]


def format_board(board):
    board_display = " Player 1 = 1 , Player 2 = 2"
    for row in range(ROWS-1, -1, -1):
        board_display += "\n| "
        for col in range(COLS):
            board_display += f"{board[row][col]} | "
    board_display += "\n‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾"
    board_display += "\n  1   2   3   4   5   6   7  "
    return board_display


def drop_piece(board, col, player):
    for row in range(ROWS):
        if board[row][col] == EMPTY:
            board[row][col] = player
            return row, col
    return None


def is_winner(board, player):
    def check_line(start_row, start_col, delta_row, delta_col):
        for _ in range(4):
            if (0 <= start_row < ROWS and 0 <= start_col < COLS and board[start_row][start_col] == player):
                start_row += delta_row
                start_col += delta_col
            else:
                return False
        return True

    for row in range(ROWS):
        for col in range(COLS):
            if (check_line(row, col, 0, 1) or  # Horizontal
                check_line(row, col, 1, 0) or  # Vertical
                check_line(row, col, 1, 1) or  # Diagonal /
                    check_line(row, col, 1, -1)):  # Diagonal \
                return True
    return False


def reset_board(board):
    for row in range(ROWS):
        for col in range(COLS):
            board[row][col] = 0


def has_winner(board, PLAYER1, PLAYER2):
    return is_winner(board, PLAYER1) or is_winner(board, PLAYER2)


def send_to_every_players(players, message):
    for player in players.values():
        player.sendall(message.encode())


def enable_join_room(rooms, roomID):
    sizeRoom = len(rooms[roomID]["players"])
    if roomID in rooms.keys() and sizeRoom < 2:
        return True
    return False


def boardcast(rooms, roomID, players, message):
    for playerID in rooms[roomID]["players"]:
        print(1)
        players[playerID]["connection"].sendall(message.encode())


def boardcast_to_other_players(rooms, roomId, players, current_player, message):
    for playerID in rooms[roomId]["players"]:
        if current_player == playerID:
            continue
        players[playerID]["connection"].sendall(message.encode())


def get_other_player(players_in_room, current_player_id):
    for player in players_in_room:
        if player == current_player_id:
            continue
        return player
