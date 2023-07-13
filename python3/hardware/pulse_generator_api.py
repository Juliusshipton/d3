'''
This will be the PulseGeneratorApi that will talk to python 2 pulse generator instan

'''


class PulseGenerator():
	
	def __init__(self, serial='', channel_map={'ch0':0,'ch1':1,'ch2':2,'ch3':3,'ch4':4,'ch5':5,'ch6':6,'ch7':7,'ch8':8,'ch9':9,'ch10':10,'ch11':11,'ch12':12,'ch13':13,'ch14':14,'ch15':15,'ch16':16,'ch17':17,'ch18':18,'ch19':19,'ch20':20,'ch21':21,'ch22':22,'ch23':23}, core='12x8'):
		self.serial = serial
		self.channel_map = channel_map
		self.xem = ok.FrontPanel()
		self.open_usb()
		self.load_core(core)
		self.setResetValue(0x00000000)
		self.reset()
		self.checkUnderflow()

	def Continuous(self, channels):
		# self.setContinuous(channels)
		return ""
		
	def Sequence(self, sequence, loop=True):	
		# self.setSequence(sequence, loop)
		return ""
		
	def Run(self, loop=None):
		# self.runSequence(loop=True)
		return ""
		
	def Night(self):
		# self.setContinuous(0x0000)
		return ""

	def Light(self):
		# self.Continuous(['green'])
		return ""

	def Open(self):
		# self.setContinuous(0xffff)
		return ""
		
	#for flip mirror
	def FlipMirror(self):
		self.Continuous(['green','test'])
		self.Continuous(['green'])
		return ""
