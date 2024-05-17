import socket
import threading
import sys


# Server IP and port
IP = "192.168.1.2"
PORT = 5555

turn = "X"


# Socket type and options
server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))
server_socket.listen()

# dictionary of client sockets and their nicknames
clients = {}

# debugging
print(f"Listening for connections on {IP}:{PORT}...")


# Sending Messages To All Connected Clients
def broadcast(message, client_socket):
    # Send messages to all clients except to the original sender
    for client in clients.keys():
        if client is not client_socket:
            client.send(message.encode("utf-8"))


# Trong phương thức handle
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
        elif "WINNER:" in message:  # Kiểm tra nếu là thông điệp chiến thắng
            broadcast(message, client_socket)  # Gửi lại thông điệp này cho tất cả các client
        else:
            broadcast(message, client_socket)

# Receiving / Listening Function
def receive():
    global turn
    while True:
        # Accept Connection
        client_socket, address = server_socket.accept()
        print("Connected with {}".format(str(address)))
        client_socket.send(turn.encode('utf-8'))
        nickname = f'player {turn}'
        if turn == "X":
            turn = "O"
        elif turn == "O":
            turn = "X"
        # Add client info to the dictionary
        clients.update({client_socket: nickname})
        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client_socket,))
        thread.start()


receive()
