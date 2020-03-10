import pickle
from tabulate import tabulate
import csv

db_file = open('server_scan_db', 'rb+')
scan_details = pickle.load(db_file)
db_file.close()


server_counter = 0

# for x in scan_details[1]:
# 	print(x)
# exit()

csv_data = []

for host in scan_details:

	csv_temp_data = []

	open_ports = 0
	for port in host[1]['portused']:
		if port['state'] == 'open':
			open_ports += 1

	if (open_ports == 0):
		continue

	server_counter += 1
	print()
	print("Server#{}".format(server_counter))
	print("IP Address: ", host[0])
	csv_temp_data.append(host[0])
	print("Status: ", host[1]['status']['state'])
	print()

	table_list = []
	open_port_list = ""
	for port in host[1]['portused']:
		table_list.append([port['portid'], port['state'], port['proto']])
		open_port_list += (port['proto'] + "({})".format(port['portid']) + " ")
	csv_temp_data.append(open_port_list)
	print(tabulate(table_list, headers=['Port No.', 'Status', 'Port Name']))
	print()
	print("Possible Operating System(s): {}".format(len(host[1]['osmatch'])))
	for os in host[1]['osmatch']:
		print(os['name'])
	if (len(host[1]['osmatch']) > 0):
		csv_temp_data.append(host[1]['osmatch'][0]['name'])
	csv_data.append(csv_temp_data)


with open('host_scan.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(csv_data)
