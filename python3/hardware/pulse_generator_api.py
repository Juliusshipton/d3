'''
This will be the PulseGeneratorApi that will talk to python 2 pulse generator instan

'''


class PulseGenerator():
	
	# STATIC CONFIGURATION VARIABLES
	serial='2021000TCD'
	channel_map={'green':0,'aom':0, 'mw_x':1, 'mw':1,'rf':2,'laser':3,'sequence':4, 'mw_2':5, 'test':6, 'blue':7, 'flip':8}

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
	
	@staticmethod
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
