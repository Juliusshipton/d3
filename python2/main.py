
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

while True: 

	# 1 receive data and parse into json object for easy access
	data_received = conn.recv(1024).decode()	
	command_object = json.loads(data_received)
	print 'RECEIVED: ' + data_received

	# 2 if time tagger is none initialize with new TimeTagger() using serial from data string
	if(time_tagger is None):
		serial_number = command_object["TimeTaggerSerial"]
		print serial_number
		time_tagger = TimeTagger.TimeTagger(str(serial_number))

	# 3 if command is Counter create a counter with the params		
	if(command_object["Command"] == "Counter"):
		# create counter 
		counterA = TimeTagger.Counter(time_tagger, *command_object["Params"])
		# indicate 
		print(counterA.getData())
		
		message = {
			"CommandRan": "Counter",
			"GetData": counterA.getData().tolist()
		}
		conn.sendall(json.dumps(message).encode())


	# Kill check
	if data_received == 'EXIT':
		s.close()
		sys.exit()