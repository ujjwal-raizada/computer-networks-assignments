the actual protocol fssp_protocol.py doesn't have any dependency other than python3.
but the file transfer uses "tqdm" library to display progress bar.

1) File Transfer

	setup:
		$ pip3 install pipenv
		$ pipenv install

		terminal 1:
			$ pipenv shell
			$ python3 file-transfer.py
			$ client

		terminal 2:
			$ pipenv shell
			$ python3 file-transfer.py
			$ server

	description:
		Now, server will ask for a path, the path can be a file or a folder,
		if it's a file it will be transfered and if it's a folder, all the files
		in it's root location will be transferred sequentially. Server will look for
		files inside the./storage folder only. (you can leave the path blank to transfer
		the default file i.e. 'assignment-3.pdf')

		All the files received by the client are stored inside ./storage/received_files

	NOTE: Client should be started first in all the cases.


2) Performance measurement

to measure the bandwidth of the protocol, you have to run performance_measurement.py in two different
terminals, first start the client (receiver) by inputing '2' then start the server (sender) by inputing
'1'. This script will run for 1 minute and then output the bandwidth and bytes sent.

setup:

	in terminal 1
		$ python3 performance_test.py
		$ 2

	in terminal 2
		$ python3 performance_test.py
		$ 1

3) Reliability test

to test reliability, just run reliablity_test.py in both the terminals and server will send 100 packets in sequence
and client which check if all 100 packets reached and are in order.


setup:

	in terminal 1
		$ python3 reliability_test.py
		$ 2

	in terminal 2
		$ python3 reliability_test.py
		$ 1