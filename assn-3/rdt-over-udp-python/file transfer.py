from rdt import RDT
import time
import os
from tqdm import tqdm
import sys

port1 = 2000
port2 = 3000

BUFFERSIZE = 512

def server():
    socket = RDT('localhost', port1)
    socket.connect('localhost', port2)
    socket.listen()

    filename = input("filename (in storage folder): ")
    if (filename == ""):
        filename = "assignment-3.pdf"


    time.sleep(5)

    f = open("storage/" + filename, 'rb')
    filesize = os.path.getsize("storage/" + filename)
    print(f"sending {filename} to client")

    data = (filename, filesize)  # protocol can send any python hashable object
    socket.send(data)
    print(f"filesize: {filesize}")

    data_sent = 0
    with tqdm(total=filesize) as pbar:
        data = f.read(BUFFERSIZE)
        while(data):
            socket.send(data)
            # print(f"sent: {data_sent} / {filesize}", end="\r")
            update_value = min(BUFFERSIZE, filesize - data_sent)
            data_sent += BUFFERSIZE
            pbar.update(update_value)

            data = f.read(BUFFERSIZE)

    f.close()

    print('\ndone sending')
    f.close()
    socket.close()
    sys.exit()


def client():
    socket = RDT('localhost', port2)
    socket.connect('localhost', port1)
    socket.listen()
    time.sleep(5)

    filename, filesize = socket.recv()
    print(f"filename: {filename}, filesize: {filesize}")

    data_recv = 0

    with open('storage/received_files/' + filename, 'wb+') as f:
        with tqdm(total=filesize) as pbar:
            while True:
                data = socket.recv()
                data_recv += len(data)
                f.write(data)
                # print(f"received: {data_recv} / {filesize}", end="\r")
                pbar.update(len(data))
                if (data_recv >= filesize):
                    break
            
            
    print("\ntransfer complete")
    socket.close()
    sys.exit()


t = input("type (server or client): ")
if (t == 'server'):
    server()
elif (t == 'client'):
    client()
else:
    print("wrong input.")

