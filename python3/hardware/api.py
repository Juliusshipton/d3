
"""
Hardware API is defined here.

Example of usage:

from hardware.api import PulseGenerator
PG = PulseGenerator

Default hardware api hooks are dummy classes.

Provide a file 'custom_api.py' to define actual hardware API hooks.
This can be imported names, modules, factory functions and factory functions
that emulate singleton behavior.

See 'custom_api_example.py' for examples.
"""

import numpy as np
import logging
import time
from .pulse_generator_api import PulseGenerator

class Scanner(  ):
	def getXRange(self):
		return (0.,100.)
	def getYRange(self):
		return (0.,100.)
	def getZRange(self):
		return (-20.,20.)
	def setx(self, x):
		pass
	def sety(self, y):
		pass
	def setz(self, z):
		pass
	def setPosition(self, x, y, z):
		"""Move stage to x, y, z"""
		pass
	def scanLine(self, Line, SecondsPerPoint, return_speed=None):
		time.sleep(0.1)
		return (1000*np.sin(Line[0,:])*np.sin(Line[1,:])*np.exp(-Line[2,:]**2)).astype(int)
		#return np.random.random(Line.shape[1])

class Counter(  ):
	def configure(self, n, SecondsPerPoint, DutyCycle=0.8):
		x = np.arange(n)
		a = 100.
		c = 50.
		x0 = n/2.
		g = n/10.
		y = np.int32( c - a / np.pi * (  g**2 / ( (x-x0)**2 + g**2 )  ) )
		Counter._sweeps = 0
		Counter._y = y
	def run(self):
		time.sleep(1)
		Counter._sweeps+=1
		return np.random.poisson(Counter._sweeps*Counter._y)
	def clear(self):
		pass

class Microwave(  ):
	def setPower(self, power):
		logging.getLogger().debug('Setting microwave power to '+str(power)+'.')
	def setOutput(self, power, frequency):
		logging.getLogger().debug('Setting microwave to p='+str(power)+' f='+str(frequency)+'.')
	def initSweep(self, f, p):
		logging.getLogger().debug('Setting microwave to sweep between frequencies %e .. %e with power %f.'%(f[0],f[-1],p[0]))
	def resetListPos(self):
		pass

MicrowaveA = Microwave
MicrowaveB = Microwave
MicrowaveC = Microwave
MicrowaveD = Microwave
MicrowaveE = Microwave

class RFSource():
	def setOutput(self, power, frequency):
		pass

from tools.utility import singleton

@singleton
def Scanner():
	from .nidaq import Scanner
	
	# PYTHON3 EDIT Uncomment when NIDAC plugged in
	# return Scanner( CounterIn='/Dev1/Ctr1',
	# 				CounterOut='/Dev1/Ctr0',
	# 				TickSource='/Dev1/PFI3',
	# 				AOChannels='/Dev1/ao0:2',
	# 				x_range=(0.0,200.0),#100x
	# 				y_range=(0.0,200.0),
	# 				z_range=(0,100.0),
	# 				v_range=(-1.00,1.00))

ScnnerA=Scanner

def DigitalOut():
	import do
	return do.DigitalOut('/Dev1/port0/line8' )

@singleton
def Counter():
	from nidaq import PulseTrainCounter
	return PulseTrainCounter( CounterIn='/Dev1/Ctr3',
							  CounterOut='/Dev1/Ctr2',
							  TickSource='/Dev1/PFI3' )

CounterA=Counter


# def CountTask(bin_width, length):
#     return  TimeTagger.Counter(0,int(bin_width*1e12), length)


@singleton
def Microwave():
	import microwave_sources
	return microwave_sources.SMIQ(visa_address='GPIB0::25')

MicrowaveA = Microwave

@singleton
def RFSource():
	import rf_source

	return rf_source.SMIQ_RF(visa_address='GPIB0::29')

def PulseGenerator():
	# return PulseGeneratorClass(serial='1634000FWV',channel_map={'green':0,'aom':0, 'mw_x':1, 'mw':1,'rf':2,'laser':3,'sequence':4, 'mw_2':5, 'test':6, 'blue':7, 'flip':8})
	#return PulseGeneratorClass(serial='1729000I9M',channel_map={'green':0,'aom':0, 'mw_x':1, 'mw':1,'rf':2,'laser':3,'sequence':4, 'blue':7})
	return PulseGenerator(serial='2021000TCD',channel_map={'green':0,'aom':0, 'mw_x':1, 'mw':1,'rf':2,'laser':3,'sequence':4, 'mw_2':5, 'test':6, 'blue':7, 'flip':8})

# PYTHON3 EDIT
from .time_tagger_api import TimeTagger as tt
#tagger=tt.TimeTagger('1634000FWQ')
#tagger=tt.TimeTagger('2138000XIC')
tagger=tt.TimeTagger('1634000FWP')
from . import time_tagger_control
TimeTagger=time_tagger_control.TimeTaggerControl(tagger)
