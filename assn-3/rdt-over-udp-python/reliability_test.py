import time

from fssp_protocol import FSSP

def sender():

    conn = FSSP('localhost', 2000)
    conn.connect('localhost', 3000)
    conn.listen()
    time.sleep(5)

    counter = 1
    while True:

        if (counter > 100):
            break

        conn.send(counter)
        print("sent: ", counter)
        counter += 1
        time.sleep(0.1)


def receiver():

    conn = FSSP('localhost', 3000)
    conn.connect('localhost', 2000)
    conn.listen()
    test_val = 1

    while True:
        data = conn.recv()
        if (data == test_val):
            test_val += 1
        print("received: ", data)

        if (data == 100):
            if (test_val == 101):
                print("reliability test passed.")
            break


mode = input("mode (1 - sender, 2 - receiver): ")
if (mode == '1'):
    sender()
else:
    receiver()
