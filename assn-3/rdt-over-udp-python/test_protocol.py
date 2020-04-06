from rdt import RDT
import time
import random

port = int(input("port: "))
port2 = int(input("port sender: "))
sock = RDT('localhost', port)
sock.connect('localhost', port2)
sock.listen()
d = random.randint(0, 1000)
time.sleep(7)
while True:
    
    time.sleep(1)
    sock.send(d)
    print("Recieved: ", sock.recv())
    print("buffer size: ", len(sock.sent_buffer))
    d += 1
