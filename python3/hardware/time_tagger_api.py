
'''

This will be the Api class for TimeTagger that will send commands and parameters to python2 code running simutaniously. 

'''
import json
import numpy as np
import time
import socket
import sys

print("Python 3 running ...")

HOST = '127.0.0.1'
PORT = 8888

tt_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tt_socket.connect((HOST, PORT))

print("Connected")

class TimeTagger():

	ports = [
		1234, 5678, 9012, 3456, 7890,
		2345, 6789, 1024, 2048, 3072,
		4096, 5120, 6144, 7168, 8192,
		9216, 10240, 11264, 12288, 13312,
		14336, 15360, 16384, 17408, 18432,
		19456, 20480, 21504, 22528, 23552
	]

	port_idx = 0

	serial_number = "1634000FWP"

	# Only way counter is called in our code is with 3 integer parameters
	def Counter(channel: int, pSecPerPoint: int, traceLength: int):

		# Get port from connection and create new socket 
		connection_port = TimeTagger.ports[TimeTagger.port_idx]
		new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# Send message to server to start listening for connection on port
		params = [channel, int(pSecPerPoint), traceLength]
		unique_id = TimeTagger.generate_random_id(10)
		command = {
			"TimeTaggerSerial": TimeTagger.serial_number,
			"Command": "Counter",
			"Id": unique_id, 
			"Params": params,
			"Port": connection_port,
		}

		#This block of sends the command and stores received data in data string
		print("Sending connection request Counter ...")
		start_time = time.time()
		
		tt_socket.sendall(json.dumps(command).encode())
		data = tt_socket.recv(2000000000).decode()

		elapsed_time = time.time() - start_time
		
		# Once listening message received connect
		new_socket.connect((HOST, connection_port))
		print("Counter initialized in ", elapsed_time, "seconds, ", "on port", connection_port)
		TimeTagger.port_idx = TimeTagger.port_idx+1


		# return an object that contains a method called getData()
		class CounterResult:
			def __init__(self, socket, id):
				self.socket = socket
				self.id = id

			def getData(self):
				
				command = {
					"TimeTaggerSerial": TimeTagger.serial_number,
					"Command": "GetDataCounter",
					"Id": self.id,
				}

				#This block of sends the command and stores received data in data string
				# print("Sending request getDataCounter ...")
				start_time = time.time()

				self.socket.sendall(json.dumps(command).encode())
				data_received = self.socket.recv(2000000000).decode()

				elapsed_time = time.time() - start_time
				print("Received counter data in ", elapsed_time, "seconds")

				result_object = json.loads(data_received)

				result_list = result_object["Data"]

				return np.array(result_list)

		
		return CounterResult(new_socket, unique_id)


	# Only way pulsed is called in our code is with 6 integer parameters
	def Pulsed(nBins: int, binWidth: int, nLaser: int, c1: int, c2: int, c3: int):

		# Get port from connection and create new socket 
		connection_port = TimeTagger.ports[TimeTagger.port_idx]
		new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		params = [nBins, binWidth, nLaser, c2, c2, c3]
		unique_id = TimeTagger.generate_random_id(10)
		command = {
			"TimeTaggerSerial": TimeTagger.serial_number,
			"Command": "Pulsed",
			"Id": unique_id, 
			"Params": params,
			"Port": connection_port,
		}
	
		#This block of sends the command and stores received data in data string
		print("Sending connection request Pulsed ...")
		start_time = time.time()

		tt_socket.sendall(json.dumps(command).encode())
		data = tt_socket.recv(2000000000).decode()

		elapsed_time = time.time() - start_time
		
		# Once listening message received connect
		new_socket.connect((HOST, connection_port))
		print("Pulsed initialized in ", elapsed_time, "seconds, ", "on port", connection_port)
		TimeTagger.port_idx = TimeTagger.port_idx+1



		# return an object that contains a method called getData()
		class PulsedResult:
			def __init__(self, socket, id):
				self.socket = socket
				self.id = id

			def getData(self):
				
				command = {
					"TimeTaggerSerial": TimeTagger.serial_number,
					"Command": "GetDataPulsed",
					"Id": self.id,
				}

				#This block of sends the command and stores received data in data string
				print("Sending request pulsed getData...")
				start_time = time.time()

				self.socket.sendall(json.dumps(command).encode())
				data_received = self.socket.recv(2000000000).decode()

				elapsed_time = time.time() - start_time
				print("Received pulsed data in ", elapsed_time, "seconds")

				result_object = json.loads(data_received)

				result_list = result_object["Data"]

				return np.array(result_list)

		
		return PulsedResult(new_socket, unique_id)

	def generate_random_id(length):
		import random
		import string
		
		"""Generate a random ID string of a given length."""
		letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
		return ''.join(random.choice(letters) for _ in range(length))

