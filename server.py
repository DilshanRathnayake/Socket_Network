import socket
import threading
from shared import send_frame, recv_frame

clients = {}  

def broadcast_raw(data, sender=None):
    for c in list(clients.keys()):
        if c != sender:
            try:
                send_frame(c, data)
            except:
                pass

def handle_client(conn, addr):
    name = recv_frame(conn)
    if not name:
        conn.close()
        return

    name = name.decode()
    clients[conn] = name
    print(f"[+] {name} joined from {addr}")

    broadcast_raw(b"\x01" + f"{name} joined the chat".encode(), conn)

    while True:
        try:
            data = recv_frame(conn)
            if not data:
                break

            msg_type = data[0]
            payload = data[1:]

            if msg_type == 0x01:  
                print(f"[text] {payload.decode()}")
                broadcast_raw(data, conn)

            elif msg_type == 0x02:  
                broadcast_raw(data, conn)
                filedata = recv_frame(conn)
                broadcast_raw(filedata, conn)
                print(f"[file] {name} sent {len(filedata)} bytes")

        except:
            break

    print(f"[-] {name} disconnected")
    del clients[conn]
    conn.close()
    broadcast_raw(b"\x01" + f"{name} left the chat".encode())

def main():
    HOST = "0.0.0.0"
    PORT = 9000

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()

    print(f"Server running on {HOST}:{PORT}")

    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
 