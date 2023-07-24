
from TimeTagger import TimeTagger

# from PulseGenerator.pulse_generator import PulseGenerator as PulseGeneratorBase

import socket
import sys

print "Python 2 running ..."

# HOST = '127.0.0.1' 
# PORT = 8888

# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.bind((HOST, PORT))
# s.listen(5)
# conn, addr = s.accept()

# print "Listening on port" + str(PORT)



# tagger=TimeTagger.TimeTagger('2138000XH1')

tagger=TimeTagger.TimeTagger('1634000FWP')


params = [0, 1000, 10]

test = TimeTagger.Counter(tagger, *params)

print(test.getData())


# while True: 
	
# 	# String data received from client
# 	data = conn.recv(1024).decode()
	
# 	# Display and manipulate
# 	print data
# 	data = data.upper()
	
# 	# Return
# 	conn.sendall(data)

# 	# Kill check
# 	if data == 'EXIT':
# 		s.close()
# 		sys.exit()