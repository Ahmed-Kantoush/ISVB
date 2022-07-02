from re import X
import socket
import struct
import pickle
import cv2
import time
import pytesseract
import signal
import requests

HOST = '197.160.2.29'
PORT = 3000

url = "http://www.google.com"
timeout = 5

def testCon():
    try:
        request = requests.get(url, timeout=timeout)
        print("...")
    except (requests.ConnectionError, requests.Timeout) as exception:
        return False

def handler(signum, frame):
    print("...")
    raise Exception("End of time")


def set_keepalive_linux(sock, after_idle_sec=1, interval_sec=3, max_fails=1):
    """Set TCP keepalive on an open socket.

    It activates after 1 second (after_idle_sec) of idleness,
    then sends a keepalive ping once every 3 seconds (interval_sec),
    and closes the connection after 5 failed ping (max_fails), or 15 seconds
    """
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, after_idle_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails)

#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect((HOST, PORT))
#set_keepalive_linux(s,after_idle_sec=1, interval_sec=3, max_fails=1)
connected = True
#print('Connected to main server IP: ', HOST)


def camera(s):
    print("Capturing...")
    vid = cv2.VideoCapture(-1)
    img, frame = vid.read()
    x = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    a = pickle.dumps(x)
    message = struct.pack("Q",len(a))+a
    s.sendall(message)

def read(s):
    print("Capturing...")
    vid = cv2.VideoCapture(-1)
    img, frame = vid.read()
    x = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    data4= pytesseract.image_to_data(x)
    filewrite = open("string.txt", "w")
    for z, a in enumerate(data4.splitlines()):
        if z != 0:
            a = a.split()
            if len(a) == 12:
                x, y = int(a[6]), int(a[7])
                w, h = int(a[8]), int(a[9])
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0 ,0), 1)
                cv2.putText(frame, a[11], (x, y + 25), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)
                filewrite.write(a[11] + " ")
    filewrite.close()
    with open('string.txt') as f:
        lines = f.readlines()
    f_data = lines.encode('utf-8')
    s.sendall(f_data)

def main():
    #global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    set_keepalive_linux(s,after_idle_sec=1, interval_sec=3, max_fails=1)
    print('Connected to main server IP: ', HOST)
    data = 'ID: 0x0001'
    e_data = data.encode('utf-8')
    s.sendall(e_data)
    while True:
        try:      
            x_data = s.recv(1024).decode('utf-8')    
            if x_data == 'detect':
                camera(s)
            elif x_data == 'read':
                read(s)
        except:
            print("connection lost... reconnecting")
            connected = False
            time.sleep(5)
            while not connected:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((HOST, PORT))
                    set_keepalive_linux(s,after_idle_sec=1, interval_sec=3, max_fails=1)
                    print('Connected to main server IP: ', HOST)
                    data = 'ID: 0x0001'
                    e_data = data.encode('utf-8')
                    s.sendall(e_data)
                    print("re-connection successful")
                    connected = True
                except socket.error:
                    time.sleep(5)

if __name__ == "__main__":
	while 1:
		main()