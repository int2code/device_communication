import socket

recv_port = 12345
send_address = "127.0.0.1"

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", recv_port))
server_socket.listen(1)

print(f"Listening on port {recv_port} for TCP connections")

while True:
    conn, addr = server_socket.accept()
    print(f"Connection established with {addr}")
    while True:
        try:
            data = conn.recv(1024)
        except ConnectionResetError:
            print(f"Connection reset by {addr}")
            conn.close()
            break
        if not data:
            break
        print(f"Receive: {data} from {addr}")
        echo = b"Echo: " + data
        conn.sendall(echo)
        print(f"Send : {echo} to {addr}")
    conn.close()
    print(f"Connection with {addr} closed")