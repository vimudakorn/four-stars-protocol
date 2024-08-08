# problem
# - user can play only 1 time , i the game has already done , it not send choice to choose
# - it show Youn Turn before Game start in player 1
# - when close the terminal it has an error
# - handle in case of doesn't have this room number in rooms
# - if player send 2 can this room doesn't exist , it cann't create room
# - bug in case of join room , sometimes don't show , show in wrong order , send waiting 2 times , doesn't send when the first user join

import socket
import threading
import random
import string
# from constants import HOST, PORT, COLS, ROWS, EMPTY
# from utils import generate_unique_room_number, boardcast, boardcast_to_other_players, create_board, drop_piece, enable_join_room, format_board, has_winner, is_winner, reset_board, get_other_player

# global board
COLS = 7
ROWS = 6
EMPTY = 0
PLAYER1 = 1
PLAYER2 = 2

HOST = 'localhost'
PORT = 6542

dict = {
    "000": "Set Username",
    "001": "Room Created",
    "002": "Join Room",
    "003": "Other Player Join Room",
    "004": "Game Start",
    "005": "Your Turn",
    "006": "Show Board",
    "007": "End Game",
    "008": "Waiting Another Player",
    
    # error
    "301": "Room Full",
    "302": "Room Closed",
    "303": "Column Not In Range",
    "304": "Invalid Move",
    "305": "Room Doesn't Exist"
    
}

players = {}
"""
{
    {
        "player-id" : {
            "name" : <player-name>,
            "connection" : <connection-socket>
        }
    }
}
"""

rooms = {}
"""
{
    roomId : {
    "players": [],
    "current-player" : <player-id>,
    "status": "playing" | "ended"
    }
}
"""

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



def start_game(roomID, player):

    players_in_room = rooms[roomID]["players"]
    while True:
        if len(players_in_room) == 2:
            break

    board = rooms[roomID]["board"]

    already_sent_message = False

    while True:
        current_player_id = rooms[roomID]["current-player"]
        current_player = players[current_player_id]

        other_player_id = get_other_player(players_in_room, current_player_id)

        if rooms[roomID]["status"] == 'ended':
            break
        if player is current_player_id:
            col = -1
            is_in_range_col = False
            while not is_in_range_col:
                current_player["connection"].sendall(
                    "005 Your Turn\nYour turn! Choose a column(1-7): ".encode())

                text = current_player["connection"].recv(
                    1024).decode().strip().split()
                col = int(text[1]) - 1
                if col in range(0, 7):
                    is_in_range_col = True
                else:
                    current_player["connection"].sendall(
                        "303 Column Not In Range\nPlease try again!\n".encode())
            if 0 <= col < COLS and board[ROWS-2][col] == EMPTY:
                other_player_index = players_in_room.index(other_player_id) + 1
                current_player_index = players_in_room.index(
                    current_player_id) + 1
                row, _ = drop_piece(board, col, current_player_index)
                board_display = format_board(board)

                boardcast(rooms, roomID, players, f"006 Show Board\nBoard:\n{board_display}\n")

                if has_winner(board, current_player_index, other_player_index):
                    if is_winner(board, current_player_index):
                        current_conn = players[current_player_id]["connection"]
                        other_conn = players[other_player_id]["connection"]
                        current_conn.sendall(
                            "007 End Game\nYou win!\n".encode())
                        other_conn.sendall(
                            "007 End Game\nThe other player wins!\n".encode())
                        reset_board(board)
                        rooms[roomID]["status"] = "ended"
                        break
                already_sent_message = False
                rooms[roomID]["current-player"] = other_player_id
            else:
                current_player["connection"].sendall(
                    "304 Invalid Move\nInvalid move. Try again.\n".encode())
        else:
            if not already_sent_message:
                other_conn = players[other_player_id]["connection"]
                other_conn.sendall(
                    "008 Waiting Another Player\nWaiting for the other player...\n".encode())
                already_sent_message = True
            # if not waiting_message_sent:
            #     current_player["connection"].sendall(
            #         "server: 102 Waiting Another Player\nWaiting for the other player...\n".encode())
            #     waiting_message_sent = True


def handle_client(conn, addr):
    # conn.sendall(f"server: 100 Set Player\nYou are Player {player}\n".encode())
    # conn.sendall(f"server: 001 Game Started\nGame Started\n".encode())

    playerName = ""
    roomID = ""
    while True:
        instruction, value = conn.recv(1024).decode().strip().split(" ", 1)
        HOST, PORT = addr
        playerID = str(HOST)+str(PORT)
        if instruction == "SET-PLAYER-NAME":
            players[playerID] = {"name": value, "connection": conn}
            playerName = players[playerID]["name"]
            conn.sendall(f"000 Set Username\nAlready set your username : {playerName}".encode())
            print(f"{value} has joined the server")
        if instruction == "SELECT-INSTRUCTION":
            if value == "1":  # CREATE ROOM
                roomID = generate_unique_room_number(rooms.keys())
                rooms[roomID] = {"board": create_board(), "players": [
                    playerID], "current-player": playerID, "status": "playing"}
                conn.sendall(f"001 Room Created\nRoom number: {roomID}".encode())
                print(f"{playerName} creates room {roomID}")
                start_game(roomID, playerID)
            elif value == "2":  # JOIN ROOM
                roomID = conn.recv(1024).decode().strip().upper()
                if roomID not in rooms.keys():
                    conn.sendall(f"305 Room Doesn't Exist\nRoom {roomID} doesn't exist\n".encode())
                    continue
                else:
                    if enable_join_room(rooms, roomID):
                        rooms[roomID]["players"].append(playerID)
                        conn.sendall(f"002 Join Room\nYou have joined room {roomID}".encode())
                        print(f"{playerName} has joined room {roomID}")
                        boardcast_to_other_players(rooms, roomID, players, playerID, f"003 Other Player Join Room\n{playerName} has joined this room\n")
                        boardcast(rooms, roomID, players,f"004 Game Start\nGame Start")

                        start_game(roomID, playerID)
                    else:
                        roomID = ""
                        conn.sendall(
                            f"301 Room Full\nThis room is already full\n".encode())
                        print(f"{playerName} can't join room {roomID}")
            elif value == "3":  # EXIT
                conn.close()
                break


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("Server is listening...")

        while True:

            conn, addr = s.accept()
            # conn.sendall("103 Waiting Another Player To Join\nWaiting for the other player to join...\n".encode())

            player_thread = threading.Thread(
                target=handle_client, args=(conn, addr))
            player_thread.start()


if __name__ == "__main__":
    start_server()
