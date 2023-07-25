
'''

This will be the Api class for TimeTagger that will send commands and parameters to python2 code running simutaniously. 

'''
import json
import numpy as np


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
		print("Sending data...")
		tt_socket.sendall(json.dumps(command).encode())
		data = tt_socket.recv(1024).decode()
		print('Received from server: ' + str(data))

		# return an object that contains a method called getData()
		class CounterResult:
			def __init__(self, socket, id):
				self.socket = socket
				self.id = id

			def getData(self):
				
				command = {
					"TimeTaggerSerial": TimeTagger.serial_number,
					"Command": "GetData",
					"Id": self.id,
				}

				#This block of sends the command and stores received data in data string
				print("Sending data...")
				self.socket.sendall(json.dumps(command).encode())
				data_received = self.socket.recv(1024).decode()
				print('Received from server: ' + str(data))

				result_object = json.loads(data_received)

				result_list = result_object["Data"]

				return np.array(result_list)

		
		return CounterResult(tt_socket, unique_id)


	# Only way pulsed is called in our code is with 6 integer parameters
	def Pulsed(tt_socket, a: int, b: int, c: int, d: int, e: int, f: int):
		print("Sending data...")

		test = ' '.join(map(str, [a, b, c]))
		tt_socket.sendall(test.encode())
		
		data = tt_socket.recv(1024).decode()
		print('Received from server: ' + data)
		# TODO: Return a reference class that contains a method .getData(), and populate with data


	def generate_random_id(length):
		import random
		import string
		
		"""Generate a random ID string of a given length."""
		letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
		return ''.join(random.choice(letters) for _ in range(length))

