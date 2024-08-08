import socket

HOST = 'localhost'
PORT = 6542

def start_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        username = input("What's your name: ")
        s.sendall(f"SET-PLAYER-NAME {username}".encode())
        data = s.recv(1024).decode()
        print(data)

        while True:
            labels = input("1 Create Room\n2 Join Room\n3 Exit\n>> ")
            s.sendall(f"SELECT-INSTRUCTION {labels}".encode())
            if labels == "1":
                data = s.recv(1024).decode()
                print(data)
            elif labels == "2":
                roomID = input("Enter room number: ")
                s.sendall(f"{roomID}".encode())
                data = s.recv(1024).decode()
                print(data)
                if "301 Room Full" in data:
                    continue
                elif "Room Doesn't Exist" in data:
                    continue
            elif labels == "3":
                break

            if labels == "1" or labels == "2":
                while True:
                    data = s.recv(1024).decode()
                    # if not data:
                    #     break
                    print(data)
                    if "007 End Game" in data:
                        break
                    if "005 Your Turn" in data:
                        move = input()
                        s.sendall(f"MOVE {move}".encode())


if __name__ == "__main__":
    start_client()
