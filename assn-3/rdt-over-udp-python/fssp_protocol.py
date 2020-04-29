import socket
import pickle
from pprint import pprint
from threading import Thread, Lock
import time
import random
import builtins
import hashlib
from copy import deepcopy
from collections.abc import Hashable


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


class FSSP:
    """ Fail-Safe and Simple (FSSP) Protocol """

    BUFSIZE = 1500
    PACKET_SIZE = 1400  # in bytes
    WINDOW_SIZE = 1000  # size of buffer windows
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
        self.conn_close_time = 0
        self.connection_status = False
        self.sent_lock = Lock()
        self.sock_recv_lock = Lock()
        self.sock_send_lock = Lock()
        self.seq_lock = Lock()
        self.seq_to_app_lock = Lock()
        self.next_seq_to_app = self.seq_num + 1  # last seq number of packet transferred to application


    def packet_loss_rate(self, value):
        if (10 >= value >= 0):
            FSSP.PACKET_LOSS = value
        else:
            raise Exception("Value not in range. (0 - 10)")


    def __create_socket(self, interface, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((interface, port))
        return sock


    def __retransmit(self):

        while True:
            time.sleep(FSSP.TIMEOUT)

            if (self.connection_status == False and len(self.sent_buffer) == 0):
                return

            with self.sent_lock:
                print("Retransmitting thread aquired the lock...")
                for packet in self.sent_buffer:
                    time_now = time.time()
                    if ((time_now - packet[2]) >= FSSP.TIMEOUT):
                        print("Retransmitting: ", packet[0])
                        self.__write_socket(packet[1], "DATA", retransmit=True)
                    else:
                        break  # rest of the packets in the queue are yet to timeout
            print("# packets in buffer: ", len(self.sent_buffer))


    def connect(self, interface, port):
        self.sock.connect((interface, port))
        self.connection_status = True

    def close(self):
        self.connection_status = False
        self.conn_close_time = time.time()


    def __next_seq(self):
        with self.seq_lock:
            self.seq_num += 1
            return (self.seq_num)


    def listen(self):
        if (self.connection_status == False):
            raise connectionNotCreatedException("First connect to other peer.")

        listening_thread = Thread(target=self.__start_listening)
        restransmission_thread = Thread(target=self.__retransmit)

        listening_thread.start()
        restransmission_thread.start()


    def __start_listening(self):
        if (self.sock == None):
            raise socketNotCreatedException("Socket not created")

        ack_counter = 0  # counts number of acke'd packets still in sent list
        ack_map = set()

        print("listening for datagrams at {}:".format(self.sock.getsockname()))
        while True:

            try:
                with self.sock_recv_lock:
                    data, address = self.sock.recvfrom(FSSP.BUFSIZE)
            except Exception as _:
                return

            data_recv = data
            print('client at {}'.format(address))
            data_recv = pickle.loads(data_recv)
            print(data_recv)

            if (data_recv["type"] == "ACK"):
                print("recv ACK for: ", data_recv["seq_ack"])
                print("# packets in buffer: ", len(self.sent_buffer))
                ack_counter += 1
                ack_map.add(data_recv["seq_ack"])
                if (ack_counter >= (FSSP.WINDOW_SIZE / 10) or 
                    (((time.time() - self.conn_close_time) >= 5 * FSSP.TIMEOUT) and self.connection_status == False)):

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

                if (data_recv["seq"] >= (self.next_seq_to_app + (FSSP.WINDOW_SIZE - (FSSP.WINDOW_SIZE / 10)))):
                    # the recieved data is outside 90% of the buffer window size
                    continue

                data = data_recv["data"]
                if (hashlib.md5(pickle.dumps(data)).hexdigest() != data_recv["hash"]):
                    # check if any inconsistant data has arrived
                    print("inconsistent data received")
                    continue

                if ((len(self.recv_buffer) < FSSP.WINDOW_SIZE) or self.seq_map.get(data_recv["seq"]) != None):
                    print("sending ACK for: ", data_recv["seq"])
                    data_snd = {}
                    data_snd["seq_ack"] = data_recv["seq"]
                    
                    self.__write_socket(data_snd, "ACK")

                if (len(self.recv_buffer) < FSSP.WINDOW_SIZE and self.seq_map.get(data_recv["seq"]) == None):
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

        data_send = (pickle.dumps(data))
        if (len(data_send) > FSSP.PACKET_SIZE):
            raise Exception('Packet size greater the allowed size.')

        rn = random.randint(0, 11)
        if (rn >= FSSP.PACKET_LOSS):  # simulating ACK packet loss
            try:
                with self.sock_send_lock:
                    self.sock.sendall(data_send)
            except Exception as _:
                return
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
                time.sleep(FSSP.BLOCKING_SLEEP)
        else:
            data = self.__read_socket()
            data = deepcopy(data)
            return data


    def __non_blocking_send(self, data):

        if (len(self.sent_buffer) > FSSP.WINDOW_SIZE):
            print("buffer size full")
            return False
        
        data = deepcopy(data)  # if user modify the object, the shouldn't be changed
        seq = self.__next_seq()

        data_snd = {}  # it will store header information
        data_snd["seq"] = seq
        data_snd["data"] = data
        # TODO: Add hash check functionality
        data_snd["hash"] = hashlib.md5(pickle.dumps(data)).hexdigest()
        self.__write_socket(data_snd, "DATA")
        return True


    def send(self, data, blocking=True):

        if (not isinstance(data, Hashable)):
            raise Exception("Data object is not hashable.")

        if (blocking == True):
            while (self.__non_blocking_send(data) == False):
                time.sleep(FSSP.BLOCKING_SLEEP)
        else:
            return self.__non_blocking_send(data)


    @staticmethod
    def print_config():
        print("BUFSIZE (bytes recv function accepts): ", FSSP.BUFSIZE)
        print("WINDOW_SIZE (number of packets in send or recv buffer): ", FSSP.WINDOW_SIZE)
        print("PACKET_SIZE (Max size of send packet in bytes): ", FSSP.PACKET_SIZE)
        print("TIMEOUT (time in seconds to retransmit packet): ", FSSP.TIMEOUT)
        print("BLOCKING_SLEEP (time in seconds to recheck buffer): ", FSSP.BLOCKING_SLEEP)
