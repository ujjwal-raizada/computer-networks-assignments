import nmap
import time
import pickle
from pathlib import Path

scanner = nmap.PortScanner()
print("Welcome to nmap automation tool!!")

print("Enter scanner config (leave empty for default values):\n")
host = input("Enter host IP address: ")
block_size = input("Enter CIDR block size: ")
args = input("Enter nmap arguments: ")

if (host == ''): host = '172.16.38.63'
if (block_size == ''): block_size = '24'
if (args == ''): args = '-n -sP'

hosts = host + '/' + block_size

print("hosts: {}, args: {}".format(hosts, args))

my_file = Path("db_file")
if not my_file.is_file():
	db_file = open('db_file', 'wb')
	pickle.dump([], db_file)
	db_file.close()

db_file = open('db_file', 'rb+')
scan_details = pickle.load(db_file)
print("scan details so far: ", scan_details)
scan_counter = len(scan_details)

while True:
	scanner.scan(hosts=hosts, arguments=args)
	scan_counter += 1
	hosts_list = [(host, scanner[host]['status']['state']) for host in scanner.all_hosts()]

	# for host, status in hosts_list:
	# 	print('{0}: {1}'.format(host, status))

	scan_time = time.time()
	number_of_hosts = len(hosts_list)
	scan_details.append((scan_counter, scan_time, number_of_hosts))
	# save the data persistently
	db_file = open('db_file', 'wb')
	pickle.dump(scan_details, db_file)
	db_file.close()

	print("Scan#{} => time: {}, number of hosts: {}".format(scan_counter, scan_time, number_of_hosts))
	time.sleep(600)



