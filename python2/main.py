
from TimeTagger import TimeTagger

# from PulseGenerator.pulse_generator import PulseGenerator as PulseGeneratorBase

import socket
import sys
import json

print "Python 2 running ..."
HOST = '127.0.0.1' 

ports = [
    1234, 5678, 9012, 3456, 7890,
    2345, 6789, 1024, 2048, 3072,
    4096, 5120, 6144, 7168, 8192,
    9216, 10240, 11264, 12288, 13312,
    14336, 15360, 16384, 17408, 18432,
    19456, 20480, 21504, 22528, 23552
]

port_idx = 0


PORT = 8888
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)
conn, addr = s.accept()
print "Listening on port" + str(PORT)

# # tagger=TimeTagger.TimeTagger('2138000XH1')
# tagger=TimeTagger.TimeTagger('1634000FWP')
# params = [0, int(1e12), 10]
# counterA = TimeTagger.Counter(tagger, *params)
# print(counterA.getData())

time_tagger = None

# dictionary accessed by id
counters = {}

while True: 

	# 1 receive data and parse into json object for easy access
	data_received = conn.recv(1024).decode()	
	command_object = json.loads(data_received)
	# print "Command Received " + command_object["Command"]

	# 2 if time tagger is none initialize with new TimeTagger() using serial from data string
	if(time_tagger is None):
		serial_number = command_object["TimeTaggerSerial"]
		print "Time Tagger Initialized: " + serial_number
		time_tagger = TimeTagger.TimeTagger(str(serial_number))

	# 3 if command is Counter create a counter with the params, and set in dictionary by id key		
	if(command_object["Command"] == "Counter"):
		
		# create counter 
		counters[command_object["Id"]] = TimeTagger.Counter(time_tagger, *command_object["Params"])
		
		# indicate 
		# print(counters[command_object["Id"]].getData())
		
		# create and return message
		message = {
			"CommandRan": "Counter",
			"GetData": counters[command_object["Id"]].getData().tolist()
		}
		conn.sendall(json.dumps(message).encode())
		print("Counter Initialized ...")


	# If command is get data, get the correct counter to call get data from dictionary by id
	if(command_object["Command"] == "GetDataCounter"):
		
		# get counter from dictionary by id 
		counter = counters[command_object["Id"]]

		# console log
		# print(counter.getData())
		
		# create and return message
		message = {
			"CommandRan": "GetDataCounter",
			"Data": counter.getData().tolist()
		}

		conn.sendall(json.dumps(message).encode())
		# print("Response Sent getDataCounter ...")


	#  If command is Pulsed call TimeTagger.Pulsed() with the params, and set in dictionary by id key		
	if(command_object["Command"] == "Pulsed"):
		
		# create counter 
		counters[command_object["Id"]] = TimeTagger.Pulsed(time_tagger, *command_object["Params"])
		
		# create and return message
		# Example 2D array
		array_2d = counters[command_object["Id"]].getData()
		
		# Convert 2D array to Unicode string
		list_of_lists = array_2d.tolist()


		# create and return message
		message = {
			"CommandRan": "Pulsed",
			"Data": list_of_lists
		}

		conn.sendall(json.dumps(message).encode())
		print("Pulsed Initialized ...")



		# If command is get data, get the correct counter to call get data from dictionary by id
	
	
	if(command_object["Command"] == "GetDataPulsed"):
		
		# get counter from dictionary by id 
		counter = counters[command_object["Id"]]

		# Example 2D array
		array_2d = counters[command_object["Id"]].getData()
		
		# Convert 2D array to Unicode string
		list_of_lists = array_2d.tolist()

		# create and return message
		message = {
			"CommandRan": "GetDataPulsed",
			"Data": list_of_lists
		}

		conn.sendall(json.dumps(message).encode())
		# print("Response Sent getDataPulsed ...")


