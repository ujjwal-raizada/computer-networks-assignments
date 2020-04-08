import time

from rdt import RDT

def sender():

    data = "Sample data to be sent over by the RDT protocol" * 20  # 470 bytes
    conn = RDT('localhost', 3000)
    conn.connect('localhost', 2000)
    conn.listen()
    data_size = 0
    while True:
        conn.send(data)
        data_size += len(data)
        print("sent: ", data_size, " Bytes", end="\r")
        print("sent: {} Bytes - buffer: ({})".format(data_size, len(conn.sent_buffer)), end="\r")


def receiver():

    conn = RDT('localhost', 2000)
    conn.connect('localhost', 3000)
    conn.listen()
    time_start = time.time()
    data_size = 0
    bandwidth = 0
    while True:
        data = conn.recv()
        data_size += len(data)

        bandwidth = data_size / (time.time() - time_start)
        print("bandwidth: {} B/s - buffer: ({})".format(str(bandwidth)[0:10], len(conn.recv_buffer)), end='\r')

mode = input("mode (1 - sender, 2 - receiver): ")
if (mode == '1'):
    sender()
else:
    receiver()
