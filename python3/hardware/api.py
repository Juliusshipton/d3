
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

# TimeTagger Singleton Initialization
from . import time_tagger_control
TimeTagger= time_tagger_control.TimeTaggerControl()

# NIDAQ Scanner Initialization
from tools.utility import singleton
@singleton
def Scanner():
	from .nidaq import Scanner
	
	return Scanner( CounterIn='/Dev1/Ctr1',
					CounterOut='/Dev1/Ctr0',
					TickSource='/Dev1/PFI3',
					AOChannels='/Dev1/ao0:2',
					x_range=(0.0,344.0),
					y_range=(0.0,344.0),
					z_range=(0,100.0),
					v_range=(-1.00,10.00))

# Microvave Source Initialization
@singleton
def Microwave():
    from . import microwave_sources
    return microwave_sources.SMIQ(visa_address='GPIB0::25')

# Pulse Generator Inidialization
# @singleton
# def PulseGenerator():
# 	# return PulseGeneratorClass(serial='1634000FWV',channel_map={'green':0,'aom':0, 'mw_x':1, 'mw':1,'rf':2,'laser':3,'sequence':4, 'mw_2':5, 'test':6, 'blue':7, 'flip':8})
# 	#return PulseGeneratorClass(serial='1729000I9M',channel_map={'green':0,'aom':0, 'mw_x':1, 'mw':1,'rf':2,'laser':3,'sequence':4, 'blue':7})
# 	return PulseGenerator.__init__(serial='2021000TCD',channel_map={'green':0,'aom':0, 'mw_x':1, 'mw':1,'rf':2,'laser':3,'sequence':4, 'mw_2':5, 'test':6, 'blue':7, 'flip':8})
from . import ciqtek_asg
asg_device = ciqtek_asg.ASG8x00()

@singleton
def PulseGenerator():
    return ASG('asg8100', asg_device,
               channel_map={'green':8,'aom':8, 
                            'mw_x': 2, 'mw': 2, 'mw_A': 2, #2/2
                            'laser': 7,
                            'sequence':4, 
                            'awg_dis': 5,
                            'rf':5, 'rf1':5, 
                            'mw_b':6, 'mw_y': 6, 'SmiqRf': 2,
                            'awg':1,'awgA':3, 'rf_y': 3})

class ASG(ciqtek_asg.PulseGenerator):
        
    def Continuous(self, channels):
        self.setContinuous(channels)
        
    def Sequence(self, sequence, loop=True):
        self.setSequence(sequence, loop)

    def Loadseq(self, c_pulses, length, loop0, seg_num, loop=True):
        self.loadSequence(c_pulses, length, loop0, seg_num, loop)

    def SaveSeq(self, sequence):
        c_pulses, length, loop, seg_num = self.saveSequence(sequence)
        return c_pulses, length, loop, seg_num
        
    def Run(self, loop=None):
        self.runSequence(loop=True)
        
    def Night(self):
        self.setContinuous(0x0000)
        # self.open_usb() # check usb connection

    def Light(self):
        self.Continuous(['green'])

    def Open(self):
        self.setContinuous(0xffff)



############# OLD #############


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



class RFSource():
	def setOutput(self, power, frequency):
		pass

from tools.utility import singleton



@singleton
def Counter():
	from nidaq import PulseTrainCounter
	return PulseTrainCounter( CounterIn='/Dev1/Ctr3',
							  CounterOut='/Dev1/Ctr2',
							  TickSource='/Dev1/PFI3' )

CounterA=Counter


@singleton
def RFSource():
	import rf_source

	return rf_source.SMIQ_RF(visa_address='GPIB0::29')


