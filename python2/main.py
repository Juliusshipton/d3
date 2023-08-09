
from TimeTagger import TimeTagger

# from PulseGenerator.pulse_generator import PulseGenerator as PulseGeneratorBase

import socket
import sys
import json

print "Python 2 running ..."
HOST = '127.0.0.1' 
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
	# print 'RECEIVED: ' + data_received

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

	#  If command is Pulsed call TimeTagger.Pulsed() with the params, and set in dictionary by id key		
	if(command_object["Command"] == "Pulsed"):
		
		# create counter 
		counters[command_object["Id"]] = TimeTagger.Pulsed(time_tagger, *command_object["Params"])
		
		# create and return message
		# Example 2D array
		array_2d = counter.getData()
		
		print(array_2d)

		# Convert 2D array to Unicode string
		array_2d_string = [[unicode(int(item)) for item in row] for row in array_2d]

		print(array_2d_string)
		
		# create and return message
		message = {
			"CommandRan": "GetDataPulsed",
			"Data": array_2d_string
		}

		conn.sendall(json.dumps(message).encode())

		# If command is get data, get the correct counter to call get data from dictionary by id
	if(command_object["Command"] == "GetDataPulsed"):
		
		# get counter from dictionary by id 
		counter = counters[command_object["Id"]]

		# Example 2D array
		array_2d = counter.getData()

		print(array_2d)

		# Convert 2D array to Unicode string
		array_2d_string = [[unicode(int(item)) for item in row] for row in array_2d]

		print(array_2d_string)

		# create and return message
		message = {
			"CommandRan": "GetDataPulsed",
			"Data": array_2d_string
		}

		conn.sendall(json.dumps(message).encode())

