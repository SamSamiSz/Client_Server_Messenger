import sys
import socket
import threading
import getopt

def usage(script_name):
    print(f"Usage: python {script_name} [-l] <port number> [<server address>]")

def client_connection(server, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if server:
            sock.connect((server, int(port)))
        else:
            sock.connect(('localhost', int(port)))
        return sock
    except Exception as e:
        print(f"Error connecting to server: {e}")
        sys.exit(1)

def connection_listener(port):
    try:
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serversocket.bind(('', int(port)))
        serversocket.listen(1)
        print(f"Listening on port {port}...")
        sock, addr = serversocket.accept()
        print(f"Connection established with {addr}")
        serversocket.close()  # Close the server socket after accepting the connection
        return sock
    except Exception as e:
        print(f"Error setting up server: {e}")
        sys.exit(1)

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024)
            if len(msg) == 0:  # Connection shut down by the peer
                print("Connection closed by the other side.")
                sys.exit(0)
            print(f"{msg.decode()}")
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

def send_messages(sock):
    while True:
        try:
            message = sys.stdin.readline()  # Read from standard input
            if not message:  # If standard input is closed
                sock.shutdown(socket.SHUT_WR)
                sock.close()
                print("Connection closed by the client.")
                break
            sock.send(message.encode())  # Send the message
        except Exception as e:
            print(f"Error sending message: {e}")
            break

if __name__ == '__main__':
    # Parse command line arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'l')
    except getopt.GetoptError as err:
        print(err)
        usage(sys.argv[0])
        sys.exit(2)

    is_server = False
    for opt, _ in opts:
        if opt == '-l':
            is_server = True

    if len(args) < 1:
        usage(sys.argv[0])
        sys.exit(2)

    # Validate port number
    try:
        port = int(args[0])
    except ValueError:
        print("Port number must be an integer.")
        sys.exit(2)

    server_address = args[1] if len(args) == 2 else None

    # Set up the socket either as a server or a client
    if is_server:
        sock = connection_listener(port)
    else:
        sock = client_connection(server_address, port)

    # Start the receiver thread to receive messages
    receiver_thread = threading.Thread(target=receive_messages, args=(sock,))
    receiver_thread.daemon = True
    receiver_thread.start()

    # Send messages in the main thread
    send_messages(sock)
