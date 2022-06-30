from re import X
import socket
import struct
import pickle
import cv2

HOST = '197.165.135.122'
PORT = 3000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

def camera():
    print("Capturing...")
    vid = cv2.VideoCapture(-1)
    img, frame = vid.read()
    x = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    a = pickle.dumps(x)
    message = struct.pack("Q",len(a))+a
    s.sendall(message)


def main():
    data = 'ID: 0x0001'
    e_data = data.encode('utf-8')
    s.sendall(e_data)
    print('Connected to', HOST)
    while True:
        x_data = s.recv(1024).decode('utf-8')
        if x_data == 'detect':
            camera()


if __name__ == "__main__":
	while 1:
		main()