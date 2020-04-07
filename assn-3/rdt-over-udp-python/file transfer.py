from rdt import RDT

port1 = 2000
port2 = 3000

def server():
    socket = RDT('localhost', port1)
    socket.connect('localhost', port2)
    socket.listen()

    filename = 'file_test.txt'
    f = open(filename, 'rb')
    l = f.read(100)
    while(l):
        
        if (type(l) == str):
            break

        l = l.decode()
        socket.send(l)
        print("Sent: ", l)
        l = f.read(512)
    f.close()

    print('done sending')


def client():
    socket = RDT('localhost', port2)
    socket.connect('localhost', port1)
    socket.listen()

    with open('recieved_file.txt', 'wb') as f:
        while True:
            data = socket.recv()
            data = data.encode()
            print("recv data: ", data)
            if not data:
                break
            f.write(data)
    print("transfer complete")

t = input("type: ")
if (t == 'server'):
    server()
else:
    client()

