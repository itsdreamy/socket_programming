import socket

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 12345))
    
    while True:
        message = input("Enter your message (type 'exit' to quit): ")
        client_socket.sendall(message.encode('utf-8'))
        
        if message.lower() == 'exit':
            break
            
        response = client_socket.recv(1024).decode('utf-8')
        print(f"Server response: {response}")
        
    client_socket.close()
    
if __name__ == "__main__":
    start_client()