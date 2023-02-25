import socket
import ssl
import sys
import threading
import gzip

# Configure SSL context
context = ssl.create_default_context()

# Create TCP/IP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
server_address = ('localhost', 10000)

try:
    client_socket.connect(server_address)
except ConnectionRefusedError:
    print("Error: Connection refused")
    sys.exit(1)

# Wrap the socket in an SSL context
ssl_socket = context.wrap_socket(
    client_socket, server_hostname=server_address[0])

# Receive the welcome message from the server
data = ssl_socket.recv(1024)
print(data.decode('utf-8'))


def receive_data():
    while True:
        data = ssl_socket.recv(1024)
        if data:
            print(data.decode('utf-8'))


# Handle incoming data from the server in a separate thread
threading.Thread(target=receive_data, daemon=True).start()

# Handle user input
while True:
    # Ask the user for input
    user_input = input("> ")

    # Check if the user wants to switch to file transfer mode
    if user_input.strip().lower() == "file":
        print("Switching to file transfer mode")

        # Send the file to the server
        with open('test.txt', 'rb') as f:
            file_data = f.read()
        compressed_data = gzip.compress(file_data)
        ssl_socket.sendall(user_input.strip().lower().encode('utf-8'))
        ssl_socket.sendall(compressed_data)

        # Receive confirmation message from the server
        data = ssl_socket.recv(1024)
        print(data.decode('utf-8'))

    # Check if the user wants to switch to shell mode
    elif user_input.strip().lower() == "shell":
        print("Switching to shell mode")

        # Ask the user for a shell command
        command = input("Enter a shell command: ")

        # Send the shell command to the server
        ssl_socket.sendall(user_input.strip().lower().encode('utf-8'))
        ssl_socket.sendall(command.encode('utf-8'))

        # Receive the output from the shell command
        while True:
            data = ssl_socket.recv(1024)
            if data:
                print(data.decode('utf-8'))
            else:
                break

    # Handle chat messages
    else:
        ssl_socket.sendall(user_input.strip().lower().encode('utf-8'))
        data = ssl_socket.recv(1024)
        print(data.decode('utf-8'))

ssl_socket.close()
