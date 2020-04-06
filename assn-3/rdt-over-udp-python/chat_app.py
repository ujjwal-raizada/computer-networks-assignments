import time
from threading import Thread

from termcolor import colored

from rdt import RDT

username = input("enter your username: ")
port1 = int(input("Enter port of this system: "))
port2 = int(input("Enter port of the other system: "))

socket = RDT('localhost', port1)
socket.connect('localhost', port2)

socket.listen()

def print_msg():
    while True:
        time.sleep(0.5)
        data = socket.recv()
        if (data != None):
            print("{}: {}".format(colored(data["username"] + ": ", 'blue'), data["message"]))
            # print("recv buffer size: ", len(socket.recv_buffer))


Thread(target=print_msg).start()
print("Enter your message and press enter. ", colored("'start test' to run reliability test" ,'red'))
while True:
    msg = input()
    data = {}
    data["username"] = username
    data["message"] = msg
    print(colored(username + ": ", 'green'), msg)

    if (msg == "start test"):
        for i in range(1, 101):
            data["message"] = i
            time.sleep(0.5)
            while (socket.send(data) == False):
                time.sleep(0.5)
            print(colored(username + ": ", 'green'), i)
            # print("recv buffer size: ", len(socket.recv_buffer))
            # print("sent buffer size: ", len(socket.sent_buffer))
    else:
        while (socket.send(data) == False):
            time.sleep(0.5)
