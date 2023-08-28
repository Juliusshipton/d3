
from TimeTagger import TimeTagger

# from PulseGenerator.pulse_generator import PulseGenerator as PulseGeneratorBase

import socket
import sys
import json
import threading


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

# Define a class to represent the object
class ObjectThread(object):
	def __init__(self, name, counter, connection):
		self.name = name
		self.counter = counter
		self.connection = connection

	def run(self):
		if(self.name == 'Counter'):
			print "Starting counter thread ..."
			thread = threading.Thread(target=self.counter_get_data, name="counter thread")
			thread.start()

		if(self.name == 'Pulsed'):
			print "Starting pulsed thread ..."
			thread = threading.Thread(target=self.pulsed_get_data, name="pulsed thread")
			thread.start()


	def pulsed_get_data(self):
		print "Running Pulsed Object Thread ..."
		while True: 
			# 1 receive data and parse into json object for easy access
			data_received = self.connection.recv(1024).decode()	
			command_object = json.loads(data_received)
			
			# If command is get data, get the correct counter to call get data from dictionary by id
			if(command_object["Command"] == "GetDataPulsed"):
				
				# get counter from dictionary by id 
				counter_thread = counters[command_object["Id"]]

				# Example 2D array
				array_2d = self.counter.getData()
				
				# Convert 2D array to Unicode string
				list_of_lists = array_2d.tolist()

				# create and return message
				message = {
					"CommandRan": "GetDataPulsed",
					"Data": list_of_lists
				}

				# size indicator for return
				print 'Sending ...'
				print array_2d.shape

				self.connection.sendall(json.dumps(message).encode())


	def counter_get_data(self):
		print "Running Counter Object Thread ..."
		while True: 
			# 1 receive data and parse into json object for easy access
			data_received = self.connection.recv(1024).decode()	
			command_object = json.loads(data_received)
			
			# If command is get data, get the correct counter to call get data from dictionary by id
			# if(command_object["Command"] == "GetDataCounter"):
				
				# get counter from dictionary by id 
				# counter_thread = counters[command_object["Id"]]

				# console log
				# print(counter.getData())
				
				# create and return message
			message = {
				"CommandRan": "GetDataCounter",
				"Data": self.counter.getData().tolist()
			}

			self.connection.sendall(json.dumps(message).encode())
				# print("Response Sent getDataCounter ...")
	
while True: 

	thread_count = threading.activeCount()
	print "Number of threads running:", thread_count

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
		
		# create new socket connection and listen for connections on the port parameter
		new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		port = command_object["Port"]
		new_socket.bind((HOST, port))
		new_socket.listen(5)


		# create and return message to let client know we are listening
		message = {
			"CommandRan": "Counter",
		}
		conn.sendall(json.dumps(message).encode())

		# after return message sent we accept connection from client creat counter object and return
		new_conn, addr = new_socket.accept()

		# create counter object and set
		counter_obj = TimeTagger.Counter(time_tagger, *command_object["Params"])
		new_thread = ObjectThread('Counter', counter_obj, new_conn)
		new_thread.run()
		counters[command_object["Id"]] = new_thread

		print "Counter Initialized on port", port, "..."

		# indicate 
		# print(counters[command_object["Id"]].getData())
		
		
	# # If command is get data, get the correct counter to call get data from dictionary by id
	# if(command_object["Command"] == "GetDataCounter"):
		
	# 	# get counter from dictionary by id 
	# 	counter_thread = counters[command_object["Id"]]

	# 	# console log
	# 	# print(counter.getData())
		
	# 	# create and return message
	# 	message = {
	# 		"CommandRan": "GetDataCounter",
	# 		"Data": counter_thread.counter.getData().tolist()
	# 	}

	# 	counter_thread.connection.sendall(json.dumps(message).encode())
	# 	# print("Response Sent getDataCounter ...")


	#  If command is Pulsed call TimeTagger.Pulsed() with the params, and set in dictionary by id key		
	if(command_object["Command"] == "Pulsed"):
		
		# create new socket connection and listen for connections on the port parameter
		new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		port = command_object["Port"]
		new_socket.bind((HOST, port))
		new_socket.listen(5)

		# create and return message to let client know socket is listening
		message = {
			"CommandRan": "Pulsed",
		}
		conn.sendall(json.dumps(message).encode())		
		new_conn, addr = new_socket.accept()

		# create counter object and set
		pulsed_obj = TimeTagger.Pulsed(time_tagger, *command_object["Params"])
		new_thread = ObjectThread('Pulsed', pulsed_obj, new_conn)
		new_thread.run()
		counters[command_object["Id"]] = new_thread

		print "Pulsed Initialized on port", port, "..."




		# If command is get data, get the correct counter to call get data from dictionary by id
	
	
	# if(command_object["Command"] == "GetDataPulsed"):
		
	# 	# get counter from dictionary by id 
	# 	counter = counters[command_object["Id"]]

	# 	# Example 2D array
	# 	array_2d = counters[command_object["Id"]].getData()
		
	# 	# Convert 2D array to Unicode string
	# 	list_of_lists = array_2d.tolist()

	# 	# create and return message
	# 	message = {
	# 		"CommandRan": "GetDataPulsed",
	# 		"Data": list_of_lists
	# 	}

	# 	conn.sendall(json.dumps(message).encode())
	# 	# print("Response Sent getDataPulsed ...")


