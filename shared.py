import struct

def send_frame(conn, data_bytes: bytes):
    conn.sendall(struct.pack("!I", len(data_bytes)) + data_bytes)

def recv_frame(conn):
    header = conn.recv(4)
    if not header:
        return None
    (size,) = struct.unpack("!I", header)

    buf = b""
    while len(buf) < size:
        data = conn.recv(size - len(buf))
        if not data:
            return None
        buf += data
    return buf
