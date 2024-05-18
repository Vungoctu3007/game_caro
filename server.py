import socket
import threading
import sys

# Server IP and port
IP = "localhost"
PORT = 5555

turn = "X"

# Socket type and options
server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))
server_socket.listen()

# Dictionary of client sockets and their nicknames
clients = {}

print(f"Listening for connections on {IP}:{PORT}...")

# Sending messages to all connected clients
def broadcast(message, client_socket):
    for client in clients.keys():
        if client is not client_socket:
            client.send(message.encode("utf-8"))

def handle(client_socket):
    while True:
        message = client_socket.recv(1024).decode("utf-8")
        print(message)
        if "!exit" in message:
            client_socket.close()
            broadcast("{} left!".format(clients[client_socket]), client_socket)
            clients.pop(client_socket)
            print(clients)
            sys.exit()
        elif "WINNER:" in message:
            broadcast(message, client_socket)
        else:
            broadcast(message, client_socket)

def receive():
    global turn
    while True:
        client_socket, address = server_socket.accept()
        print("Connected with {}".format(str(address)))
        
        # Receive the player's name
        name = client_socket.recv(1024).decode("utf-8").split(":")[1]
        clients.update({client_socket: name})
        
        client_socket.send(turn.encode('utf-8'))
        nickname = f'player {turn} ({name})'
        if turn == "X":
            turn = "O"
        elif turn == "O":
            turn = "X"

        thread = threading.Thread(target=handle, args=(client_socket,))
        thread.start()

receive()
