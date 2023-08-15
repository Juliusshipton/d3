
'''

This will be the Api class for TimeTagger that will send commands and parameters to python2 code running simutaniously. 

'''
import json
import numpy as np
import time

class TimeTagger():

	serial_number = "1634000FWP"

	# Only way counter is called in our code is with 3 integer parameters
	def Counter(tt_socket, channel: int, pSecPerPoint: int, traceLength: int):

		params = [channel, int(pSecPerPoint), traceLength]
		unique_id = TimeTagger.generate_random_id(10)
		command = {
			"TimeTaggerSerial": TimeTagger.serial_number,
			"Command": "Counter",
			"Id": unique_id, 
			"Params": params,
		}

		#This block of sends the command and stores received data in data string
		print("Sending request getDataCounter ...")
		start_time = time.time()
		
		tt_socket.sendall(json.dumps(command).encode())
		data = tt_socket.recv(2000000000).decode()

		elapsed_time = time.time() - start_time
		print("Received in ", elapsed_time, "seconds")
		
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
				print("Sending request getDataCounter ...")
				start_time = time.time()

				self.socket.sendall(json.dumps(command).encode())
				data_received = self.socket.recv(2000000000).decode()

				elapsed_time = time.time() - start_time
				print("Received in ", elapsed_time, "seconds")

				result_object = json.loads(data_received)

				result_list = result_object["Data"]

				return np.array(result_list)

		
		return CounterResult(tt_socket, unique_id)


	# Only way pulsed is called in our code is with 6 integer parameters
	def Pulsed(tt_socket, nBins: int, binWidth: int, nLaser: int, c1: int, c2: int, c3: int):

		params = [nBins, binWidth, nLaser, c2, c2, c3]
		unique_id = TimeTagger.generate_random_id(10)
		command = {
			"TimeTaggerSerial": TimeTagger.serial_number,
			"Command": "Pulsed",
			"Id": unique_id, 
			"Params": params,
		}
	
		#This block of sends the command and stores received data in data string
		print("Sending request Pulsed ...")
		start_time = time.time()

		tt_socket.sendall(json.dumps(command).encode())
		data = tt_socket.recv(2000000000).decode()

		elapsed_time = time.time() - start_time
		print("Received in ", elapsed_time, "seconds")

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
				print("Received in ", elapsed_time, "seconds")

				result_object = json.loads(data_received)

				result_list = result_object["Data"]

				return np.array(result_list)

		
		return PulsedResult(tt_socket, unique_id)

	def generate_random_id(length):
		import random
		import string
		
		"""Generate a random ID string of a given length."""
		letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
		return ''.join(random.choice(letters) for _ in range(length))

