import nmap
import time
import pickle
from pathlib import Path
import json

scanner = nmap.PortScanner()
print("Welcome to nmap automation tool!! - Server Scanner")

print("Enter scanner config (leave empty for default values):\n")
host = input("Enter host IP address: ")
block_size = input("Enter CIDR block size: ")
args = input("Enter nmap arguments: ")

if (host == ''): host = '172.16.38.63'
if (block_size == ''): block_size = '24'
if (args == ''): args = '-n -O -F'

# -O for OS scan.
# -F for fast scan i.e. it will scan 100 most common ports.

hosts = host + '/' + block_size

print("hosts: {}, args: {}".format(hosts, args))


scanner.scan(hosts=hosts, arguments=args)
hosts_list = [(host, scanner[host]) for host in scanner.all_hosts()]

# save host list in pickle
FILE_NAME = "server_scan_db"

db_file = open(FILE_NAME, 'wb')
pickle.dump(hosts_list, db_file)
db_file.close()

print(json.dumps(hosts_list, sort_keys=True, indent=4))

