from rdt import RDT
import time

port = int(input("port: "))
port2 = int(input("port sender: "))
sock = RDT('localhost', port)
sock.connect('localhost', port2)
sock.listen()

d = 90
while True:
    time.sleep(5)
    sock.send(d)
    time.sleep(1)
    print(sock.recv())
    d += 1
