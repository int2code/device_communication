import socket

recv_port = 12345
send_port = 54321
send_address = "127.0.0.1"

recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
recv_socket.bind(("0.0.0.0", recv_port))

send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"Listening na on port {recv_port} and sending on {send_address}:{send_port}")

while True:
    data, addr = recv_socket.recvfrom(1024)
    print(f"Receive: {data} from {addr}")
    echo = b"Echo: " + data
    send_socket.sendto(echo, (send_address, send_port))
    print(f"Send : {echo} to {send_address}:{send_port}")
