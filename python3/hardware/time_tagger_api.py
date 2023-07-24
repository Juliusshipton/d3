
'''

This will be the Api class for TimeTagger that will send commands and parameters to python2 code running simutaniously. 

'''
import json


class TimeTagger():

	serial_number = "2138000XH1"

	# Only way counter is called in our code is with 3 integer parameters
	def Counter(tt_socket, channel: int, pSecPerPoint: int, traceLength: int):


		params = [channel, pSecPerPoint, traceLength]

		command = {
			"TimeTaggerSerial": TimeTagger.serial_number,
			"Command": "Counter",
			"Params": params,
		}

		#This block of sends the command and stores received data in data string
		print("Sending data...")
		tt_socket.sendall(json.dumps(command).encode())
		data = tt_socket.recv(1024).decode()
		print('Received from server: ' + data)


	# Only way pulsed is called in our code is with 6 integer parameters
	def Pulsed(tt_socket, a: int, b: int, c: int, d: int, e: int, f: int):
		print("Sending data...")

		test = ' '.join(map(str, [a, b, c]))
		tt_socket.sendall(test.encode())
		
		data = tt_socket.recv(1024).decode()
		print('Received from server: ' + data)
		# TODO: Return a reference class that contains a method .getData(), and populate with data

