import socket
import threading
import time
import cv2
import pickle
import multiprocessing as mp
import base64
import struct ## new
# mp.set_start_method('spawn')
HEADER = 64
PORT = 5055
SERVER = "192.168.0.104"
# hostname = socket.gethostname()
# SERVER = socket.gethostbyname(hostname)
ADDR = (SERVER,PORT)
FORMAT = "utf-8"
DISCONECT = "!DISCONECT"
print(SERVER, ADDR)

def cv_proccesing(q):
    print(f"Proccess [START]: cv_proccesing")
    while True:
        if q.empty() == False:
            data = q.get()
            # data = base64.b32decode(data)
            data = pickle.loads(data)
            left_frame = cv2.imdecode(data['ImageLeft'], cv2.IMREAD_COLOR)
            rigth_frame = cv2.imdecode(data['ImageRigth'], cv2.IMREAD_COLOR)
            cv2.imshow("left_frame",left_frame)
            cv2.imshow("rigth_frame",rigth_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): 
                break

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected")
    connected = True
    send_to_q = False
    data = b""
    payload_size = struct.calcsize(">L")
    print("payload_size: {}".format(payload_size))
    while connected:
        while len(data) < payload_size:
            data += conn.recv(4096)
            if not data:
                conn,addr = server.accept()
                continue

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]
        while len(data) < msg_size:
            data += conn.recv(4096)
        frame_data = data[:msg_size]
        data = data[msg_size:]
        q.put(frame_data)

        # x = conn.recvfrom(1000000)
        # clientip = x[1][0]
        # data = x[0]
        # 
        # data = pickle.loads(data)
        # left_frame = cv2.imdecode(data['ImageLeft'], cv2.IMREAD_COLOR)
        # rigth_frame = cv2.imdecode(data['ImageRigth'], cv2.IMREAD_COLOR)

        # cv2.imshow("left_frame",left_frame)
        # cv2.imshow("rigth_frame",rigth_frame)

        # if cv2.waitKey(1) & 0xFF == 27:
        #     break

    conn.close()
    cv2.destroyAllWindows()

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTION] {threading.active_count() - 1}, addr - {addr}")

q = mp.Queue()
p = mp.Process(target=cv_proccesing, args=(q,))

if __name__ == '__main__':
    
    p.start()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    print("[STARTING] server is starting...")

    start()
    p.join()

