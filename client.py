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
        print("Connected to the Internet")
    except (requests.ConnectionError, requests.Timeout) as exception:
        return False

def handler(signum, frame):
    print("Forever is over")
    raise Exception("End of time")

#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect((HOST, PORT))
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
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    print('Connected to main server IP: ', HOST)
    data = 'ID: 0x0001'
    e_data = data.encode('utf-8')
    s.sendall(e_data)
    while True:
        try:
            while True:
                try:
                    signal.signal(signal.SIGALRM,handler)
                    signal.alarm(30)
                    x_data = s.recv(1024).decode('utf-8')
                    signal.alarm(0)
                    break
                except:
                    if testCon() == False:
                        raise Exception("QANTO")
            if x_data == 'detect':
                camera(s)
            elif x_data == 'read':
                read(s)
        except:
            print( "connection lost... reconnecting" )
            connected = False
            time.sleep(5)
            while not connected:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((HOST, PORT))
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