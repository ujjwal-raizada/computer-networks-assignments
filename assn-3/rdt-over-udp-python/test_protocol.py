from rdt import RDT
import time
import random

port = int(input("port: "))
port2 = int(input("port sender: "))
sock = RDT('localhost', port)
sock.connect('localhost', port2)
sock.listen()
d = random.randint(0, 1000)
while True:
    
    time.sleep(7)
    sock.send(d)
    time.sleep(3)
    print("Recieved: ", sock.recv())
    d += 1
