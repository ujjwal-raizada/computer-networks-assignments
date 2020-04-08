import socket
import json
from pprint import pprint
from threading import Thread, Lock
import time
import random
import builtins
from copy import deepcopy

PRODUCTION = True  # change it to false to stop stdout prints from protocol

def print(*args, **kargs):
    if (PRODUCTION == False):
        builtins.print(*args, **kargs)



class socketNotCreatedException(RuntimeError):
    def __init__(self, args):
        self.args = args


class connectionNotCreatedException(RuntimeError):
    def __init__(self, args):
        self.args = args


class RDT:
    BUFSIZE = 1500
    PACKET_SIZE = 1000  # in bytes
    WINDOW_SIZE = 10000  # size of buffer windows
    TIMEOUT = 1  # in seconds: starting of retransmission thread
    PACKET_LOSS = 0  # in range(0, 11), 0 for no loss
    BLOCKING_SLEEP = 0.00001


    def __init__ (self, interface, port):
        self.interface = interface
        self.port = port
        self.sock = self.__create_socket(interface, port)
        self.recv_buffer = []
        self.sent_buffer = []
        self.seq_num = 0
        self.seq_map = {}
        self.connection_status = False
        self.sent_lock = Lock()
        self.sock_recv_lock = Lock()
        self.sock_send_lock = Lock()
        self.seq_lock = Lock()
        self.seq_to_app_lock = Lock()
        self.next_seq_to_app = self.seq_num + 1  # last seq number of packet transferred to application


    def packet_loss_rate(self, value):
        if (10 >= value >= 0):
            RDT.PACKET_LOSS = value
        else:
            raise Exception("Value not in range. (0 - 10)")


    def __create_socket(self, interface, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((interface, port))
        return sock


    def __retransmit(self):

        while True:
            time.sleep(2 * RDT.TIMEOUT)
            with self.sent_lock:
                print("Retransmitting thread aquired the lock...")
                for packet in self.sent_buffer:
                    time_now = time.time()
                    if ((time_now - packet[2]) >= RDT.TIMEOUT):
                        print("Retransmitting: ", packet[0])
                        self.__write_socket(packet[1], "DATA", retransmit=True)
                    else:
                        break  # rest of the packets in the queue are yet to timeout
            print("# packets in buffer: ", len(self.sent_buffer))


    def connect(self, interface, port):
        self.sock.connect((interface, port))
        self.connection_status = True


    def __next_seq(self):
        with self.seq_lock:
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

        ack_counter = 0  # counts number of acke'd packets still in sent list
        ack_map = set()

        print("listening for datagrams at {}:".format(self.sock.getsockname()))
        while True:
            with self.sock_recv_lock:
                data, address = self.sock.recvfrom(RDT.BUFSIZE)

            data_recv = data.decode('utf-8')
            print('client at {}'.format(address))
            data_recv = json.loads(data_recv)
            print(data_recv)

            if (data_recv["type"] == "ACK"):
                print("recv ACK for: ", data_recv["seq_ack"])
                print("# packets in buffer: ", len(self.sent_buffer))
                ack_counter += 1
                ack_map.add(data_recv["seq_ack"])
                if (ack_counter >= (RDT.WINDOW_SIZE / 10)):
                    ack_counter = 0
                    temp_sent_buffer = []
                    with self.sent_lock:
                        print("listening thread aquired lock.")
                        for packet in self.sent_buffer:
                            if packet[0] not in ack_map:
                                temp_sent_buffer.append(packet)
                        self.sent_buffer = temp_sent_buffer
                        ack_map = set()


            else:

                if (data_recv["seq"] >= (self.next_seq_to_app + (RDT.WINDOW_SIZE - RDT.WINDOW_SIZE / 10))):
                    # the recieved data is outside 90% of the buffer window size
                    continue

                # if (hash(json.dumps(data_recv["data"])) != data_recv["hash"]):
                #     # check if any inconsistant data has arrived
                #     print(json.dumps(data_recv["data"]))
                #     print(hash(json.dumps(data_recv["data"])), " ", data_recv["hash"])
                #     return

                if ((len(self.recv_buffer) < RDT.WINDOW_SIZE) or self.seq_map.get(data_recv["seq"]) != None):
                    print("sending ACK for: ", data_recv["seq"])
                    data_snd = {}
                    data_snd["seq_ack"] = data_recv["seq"]
                    
                    self.__write_socket(data_snd, "ACK")

                if (len(self.recv_buffer) < RDT.WINDOW_SIZE and self.seq_map.get(data_recv["seq"]) == None):
                    self.recv_buffer.append((data_recv["seq"], data_recv))
                    self.seq_map[data_recv["seq"]] = True

                else:
                    print("data rejected: data already recieved or buffer full")


    def __read_socket(self):

        if (len(self.recv_buffer) == 0):
            return None

        data = min(self.recv_buffer)
        if ("data" in data[1] and data[0] == self.next_seq_to_app):
            print("packet to application: ", self.next_seq_to_app)
            with self.seq_to_app_lock:
                self.next_seq_to_app += 1
            self.recv_buffer.remove(data)
            return data[1]["data"]  # removing header information before forwarding data to application
        else:
            return None


    def __write_socket(self, data, data_type, retransmit=False):
        if (self.sock == None):
            raise socketNotCreatedException("Socket not created")
        
        data = deepcopy(data)
        data["type"] = data_type  # setting type of packet in header information
        if (data_type == "DATA" and retransmit == False):

            with self.sent_lock:
                self.sent_buffer.append((data["seq"], data, time.time()))

        data_send = (json.dumps(data)).encode('utf-8')
        if (len(data_send) > RDT.PACKET_SIZE):
            raise Exception('Packet size greater the allowed size.')

        rn = random.randint(0, 11)
        if (rn >= RDT.PACKET_LOSS):  # simulating ACK packet loss
            with self.sock_send_lock:
                self.sock.send(data_send)
        else:
            print("packet lost")


    def get_buffer(self):
        return self.recv_buffer


    def recv(self, blocking=True):
        if (blocking == True):
            while True:
                data = self.__read_socket()
                if (data != None):
                    data = deepcopy(data)
                    return data
                time.sleep(RDT.BLOCKING_SLEEP)
        else:
            data = self.__read_socket()
            data = deepcopy(data)
            return data


    def __non_blocking_send(self, data):

        if (len(self.sent_buffer) > RDT.WINDOW_SIZE):
            print("buffer size full")
            return False
        
        data = deepcopy(data)  # if user modify the object, the shouldn't be changed
        seq = self.__next_seq()

        data_snd = {}  # it will store header information
        data_snd["seq"] = seq
        data_snd["data"] = data
        # TODO: Add hash check functionality
        # data_snd["hash"] = hash(json.dumps(data))
        # print(json.dumps(data))
        self.__write_socket(data_snd, "DATA")
        return True


    def send(self, data, blocking=True):
        if (blocking == True):
            while (self.__non_blocking_send(data) == False):
                time.sleep(RDT.BLOCKING_SLEEP)
        else:
            return self.__non_blocking_send(data)


    def print_config():
        print("BUFSIZE (bytes recv function accepts): ", RDT.BUFSIZE)
        print("WINDOW_SIZE (number of packets in send or recv buffer): ", RDT.WINDOW_SIZE)
        print("PACKET_SIZE (Max size of send packet in bytes): ", RDT.PACKET_SIZE)
        print("TIMEOUT (time in seconds to retransmit packet): ", RDT.TIMEOUT)
        print("BLOCKING_SLEEP (time in seconds to recheck buffer): ", RDT.BLOCKING_SLEEP)
