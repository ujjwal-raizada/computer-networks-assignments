from fssp_protocol import FSSP
import time
import os
from tqdm import tqdm
import sys

port1 = 2000
port2 = 3000

BUFFERSIZE = 512

def get_files(filename):
    file_list = []
    if (os.path.isfile("storage/" + filename)):
        return [filename]
    elif (os.path.isdir("storage/" + filename)):
        for file in os.listdir("storage/" + filename):
            if (os.path.isfile("storage/" + file)):
                file_list.append(file)
        return file_list
    else:
        print("file / folder not found")
        return []


def server():
    socket = FSSP('localhost', port1)
    socket.connect('localhost', port2)
    socket.listen()
    while True:
        filename = input("\nfile or folder name (in storage folder): ")
        if (filename == ""):
            filename = "assignment-3.pdf"


        time.sleep(5)
        file_list = get_files(filename)
        print(f"sending {len(file_list)} files to client.")

        for file in file_list:
            file_path = "storage/" + file
            f = open(file_path, 'rb')
            filesize = os.path.getsize(file_path)
            print(f"sending {file} to client")

            data = (file, filesize)  # protocol can send any python hashable object
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



def client():
    socket = FSSP('localhost', port2)
    socket.connect('localhost', port1)
    socket.listen()
    time.sleep(5)

    while True:
        print("\nwaiting for another file...")
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



t = input("type (server or client): ")
if (t == 'server'):
    server()
elif (t == 'client'):
    client()
else:
    print("wrong input.")

