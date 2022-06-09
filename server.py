import socket
import struct
import pickle
from _thread import *

import torch
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
model.conf = 0.5

host = ''
port = 3000
ThreadCount = 0
IDs = {}

def camera(conn):
    data = b""
    payload_size = struct.calcsize("Q")
    #while True:
    while len(data) < payload_size:
        packet = conn.recv(4*1024)
        if not packet: break
        data += packet
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("Q",packed_msg_size)[0]

    while len(data) < msg_size:
        data += conn.recv(4*1024)
    frame_data = data[:msg_size]
    data = data[msg_size:]
    frame = pickle.loads(frame_data)
    result = model(frame)
    result.show()
    x = result.pandas().xywh[0]['name'].tolist()
    print(x)
    conn.sendall(pickle.dumps(x))

def client_handler(conn):
    data = conn.recv(1024).decode('utf-8')
    if data == "detect":
        camera(conn)
        conn.close()
    elif data.split(' ')[0] == "call":
        IDs[str(data.split(' ')[2])].send((data.split(' ')[0] + ' ' + data.split(' ')[1]).encode('utf-8'))
        print(data)
        conn.close()
    elif data.split(' ')[0] == "sos":
        IDs[str(data.split(' ')[1])].send((data.split(' ')[0]).encode('utf-8'))
        print(data)
        conn.close()
    elif data.split(' ')[0] == "alarm":
        IDs[str(data.split(' ')[3])].send((data.split(' ')[0] + ' ' + data.split(' ')[1] + ' ' + data.split(' ')[2]).encode('utf-8'))
        print(data)
        conn.close()
    elif data.split(' ')[0] == "clear":
        IDs[str(data.split(' ')[1])].send((data.split(' ')[0]).encode('utf-8'))
        print(data)
        conn.close()
    elif data.split(' ')[0] == "private":
        IDs[str(data.split(' ')[2])].send((data.split(' ')[0] + ' ' + data.split(' ')[1]).encode('utf-8'))
        print(data)
        conn.close()
    elif data.split(' ')[0] == 'nav':
        IDs[str(data.split(' ')[2])].send((data.split(' ')[0] + ' ' + data.split(' ')[1]).encode('utf-8'))
        print(data)
        path = ""
        while(path != "stop"):
            path = IDs[str(data.split(' ')[2])].recv(1024).decode('utf-8')
            print(path)
            conn.send(path.encode('utf-8'))
        conn.close()
    elif data.split(' ')[0] == 'ID:':
        IDs[data.split(' ')[1]] = conn
        print(data)
    else:
        print(data)

def accept_connections(ServerSocket):
    Client, address = ServerSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(client_handler, (Client, ))

def start_server(host, port):
    ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        ServerSocket.bind((host, port))
    except socket.error as e:
        print(str(e))
    print(f'Server is listing on the port {port}...')
    ServerSocket.listen()

    while True:
        accept_connections(ServerSocket)

start_server(host, port)