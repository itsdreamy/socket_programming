import socket
import time

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))
    server_socket.listen(5) 
    print("Server is listening on port 12345...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"[{time.strftime('%H:%M:%S')}] Connected by {client_address}")
        
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message or message.lower() == 'exit':
                print(f"Connection closed by {client_address}")
                break
                
            print(f"Received message: {message}")
            response = "Message received successfully!"
            client_socket.sendall(response.encode('utf-8'))
            
        client_socket.close()

if __name__ == "__main__":
    start_server()