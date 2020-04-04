import socket
import json
from pprint import pprint
from threading import Thread, Lock
import time
import random


class socketNotCreatedException(RuntimeError):
    def __init__(self, args):
        self.args = args


class connectionNotCreatedException(RuntimeError):
    def __init__(self, args):
        self.args = args


class RDT:
    BUFSIZE = 1500
    WINDOW_SIZE = 1000
    TIMEOUT = 1  # in seconds

    def __init__ (self, interface, port):
        self.interface = interface
        self.port = port
        self.sock = self.__create_socket(interface, port)
        self.recv_buffer = []
        self.sent_buffer = []
        self.seq_num = random.randint(0, 1000)
        self.seq_map = {}
        self.connection_status = False
        self.sent_lock = Lock()


    def __create_socket(self, interface, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((interface, port))
        return sock


    def __retransmit(self):

        while True:
            time.sleep(2 * RDT.TIMEOUT)
            print()
            print("starting retransmission...")
            print()

            self.sent_lock.acquire()
            print("retransmitting thread aquired lock.")
            for i in range(min(5, len(self.sent_buffer))):
                tn = time.time()
                if ((tn - self.sent_buffer[i][2]) >= RDT.TIMEOUT):
                    print("retransmitting sq#: ", self.sent_buffer[i][0])
                    self.__write_socket(self.sent_buffer[i][1], "DATA", retransmit=True)
            self.sent_lock.release()
            print("# packets in buffer: ", len(self.sent_buffer))


    def connect(self, interface, port):
        self.sock.connect((interface, port))
        self.connection_status = True


    def __next_seq(self):
        self.seq_num += 1
        return (self.seq_num)


    def listen(self):
        if (self.connection_status == False):
            raise connectionNotCreatedException("First connect to other peer.")

        Thread(target=self.__start_listening).start()
        Thread(target=self.__retransmit).start()


    def __start_listening(self):
        if (self.sock == None):
            raise socketNotCreatedException("Socket not created")

        print("listening for datagrams at {}:".format(self.sock.getsockname()))
        while True:
            data, address = self.sock.recvfrom(RDT.BUFSIZE)
            data_recv = data.decode('utf-8')
            print('client at {}'.format(address))
            pprint(data_recv)
            data_recv = json.loads(data_recv)
            print("# seq: ", data_recv["seq"])
            if (data_recv["type"] == "ACK"):
                print("recv ACK for: ", data_recv["seq_ack"])
                print("# packets in buffer: ", len(self.sent_buffer))

                self.sent_lock.acquire()
                print("listening thread aquired lock.")
                for packet in self.sent_buffer:
                    if packet[0] == data_recv["seq_ack"]:
                        self.sent_buffer.remove(packet)
                self.sent_lock.release()

            else:
                if ((len(self.recv_buffer) < RDT.WINDOW_SIZE) or self.seq_map.get(data_recv["seq"]) != None):
                    print("sending ACK for: ", data_recv["seq"])
                    data_snd = {}
                    data_snd["seq"] = self.__next_seq()
                    data_snd["seq_ack"] = data_recv["seq"]
                    
                    rn = random.randint(0, 1000)
                    if (rn >= 200):  # simulating 20% packet loss
                        self.__write_socket(data_snd, "ACK")
                    else:
                        print("ACK lost for seq: ", data_recv["seq"])

                if (len(self.recv_buffer) < RDT.WINDOW_SIZE and self.seq_map.get(data_recv["seq"]) == None):
                    self.recv_buffer.append(data_recv)
                    self.seq_map[data_recv["seq"]] = True

                else:
                    print("buffer full, data rejected or data already recieved")


    def __read_socket(self):

        if (len(self.recv_buffer) == 0):
            return None

        data = self.recv_buffer.pop()
        if ("data" in data):
            return data["data"]  # removing header information before forwarding data to application
        else:
            print("Error in data block")
            print(data)
            print()


    def __write_socket(self, data, data_type, retransmit=False):
        if (self.sock == None):
            raise socketNotCreatedException("Socket not created")

        data["type"] = data_type  # setting type of packet in header information
        if (data_type == "DATA" and retransmit == False):
            self.sent_buffer.append((data["seq"], data, time.time()))

        data_send = (json.dumps(data)).encode('utf-8')
        self.sock.send(data_send)


    def get_buffer(self):
        return self.recv_buffer


    def recv(self):
        return self.__read_socket()


    def send(self, data):

        if (len(self.sent_buffer) > RDT.WINDOW_SIZE):
            # TODO: Raise error
            print("buffer size full")
            return

        seq = self.__next_seq()

        data_snd = {}  # it will store header information
        data_snd["seq"] = seq
        data_snd["data"] = data
        self.__write_socket(data_snd, "DATA")


