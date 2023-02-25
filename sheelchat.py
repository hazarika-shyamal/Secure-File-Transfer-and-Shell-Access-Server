import socket
import ssl
import sys
import subprocess
import threading
import os
import gzip
import hashlib

# Configure SSL context
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="server.crt", keyfile="server.key")

# Create TCP/IP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind socket to a specific port
server_address = ('localhost', 10000)
server_socket.bind(server_address)

# Listen for incoming connections
server_socket.listen(1)

print("Server is listening on {}:{}".format(
    server_address[0], server_address[1]))


def handle_client(ssl_connection, client_address):
    # Send a welcome message to the client
    ssl_connection.sendall(b"Welcome to the secure server!\n")

    # Handle client communication
    while True:
        data = ssl_connection.recv(1024).decode('utf-8')
        if not data:
            break

        # Check if the client wants to switch to file transfer mode
        if data.strip().lower() == "file":
            print("Client switched to file transfer mode")

            try:
                # Receive the file size from the client
                file_size = int(ssl_connection.recv(1024).decode('utf-8'))

                # Receive the compressed file from the client
                compressed_data = b""
                while len(compressed_data) < file_size:
                    compressed_data += ssl_connection.recv(1024)

                # Decompress the file
                file_data = gzip.decompress(compressed_data)

                # Compute the file hash
                file_hash = hashlib.sha256(file_data).hexdigest()

                # Save the file to disk
                with open('received_file', 'wb') as f:
                    f.write(file_data)

                # Send the file hash to the client for verification
                ssl_connection.sendall(file_hash.encode('utf-8'))

            except Exception as e:
                error_msg = "Error during file transfer: {}".format(str(e))
                ssl_connection.sendall(error_msg.encode('utf-8'))

        # Check if the client wants to switch to shell mode
        elif data.strip().lower() == "shell":
            print("Client switched to shell mode")

            # Receive the shell command from the client
            command = ssl_connection.recv(1024).decode('utf-8')

            # Execute the shell command and send the output back to the client
            try:
                output = subprocess.check_output(
                    command, shell=True).decode('utf-8')
            except subprocess.CalledProcessError as e:
                output = e.output.decode('utf-8')
            ssl_connection.sendall(output.encode('utf-8'))

        # Handle chat messages
        else:
            print("Received chat message from client: {}".format(data.strip()))

            # Send a confirmation message to the client
            ssl_connection.sendall(b"Message received successfully\n")

    ssl_connection.close()


# Accept incoming connections
while True:
    try:
        connection, client_address = server_socket.accept()
        print("New client connected from {}:{}".format(
            client_address[0], client_address[1]))

        # Wrap the socket in an SSL context
        ssl_connection = context.wrap_socket(connection, server_side=True)

        # Start a new thread to handle the client
        client_thread = threading.Thread(
            target=handle_client, args=(ssl_connection, client_address))
        client_thread.start()

    except KeyboardInterrupt:
        break

    except Exception as e:
        print("Error accepting client connection: {}".format(str(e)))

server_socket.close()
