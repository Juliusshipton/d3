"""
This file is part of pi3diamond.

pi3diamond is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pi3diamond is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with diamond. If not, see <http://www.gnu.org/licenses/>.

Copyright (C) 2009-2011 Helmut Fedder <helmut.fedder@gmail.com>
"""

import ctypes
import numpy
import time

import nidaqmx

import PyDAQmx as dll

# dll = ctypes.windll.LoadLibrary('nicaiu.dll')

DAQmx_Val_Cfg_Default             = ctypes.c_int32(-1)
DAQmx_Val_DoNotInvertPolarity     = ctypes.c_int32(0)
DAQmx_Val_GroupByChannel          = ctypes.c_int32(0)
DAQmx_Val_GroupByScanNumber       = ctypes.c_int32(1)
DAQmx_Val_ChanPerLine             = ctypes.c_int32(0)
DAQmx_Val_ChanForAllLines         = ctypes.c_int32(1)
DAQmx_Val_Acquired_Into_Buffer    = ctypes.c_int32(1)
DAQmx_Val_Ticks                   = ctypes.c_int32(10304)
DAQmx_Val_Rising                  = ctypes.c_int32(10280)
DAQmx_Val_Falling                 = ctypes.c_int32(10171)
DAQmx_Val_CountUp                 = ctypes.c_int32(10128)
DAQmx_Val_ContSamps               = ctypes.c_int32(10123)
DAQmx_Val_FiniteSamps             = ctypes.c_int32(10178)
DAQmx_Val_Hz                      = ctypes.c_int32(10373)
DAQmx_Val_Low                     = ctypes.c_int32(10214)
DAQmx_Val_Volts                   = ctypes.c_int32(10348)
DAQmx_Val_MostRecentSamp          = ctypes.c_uint32(10428)
DAQmx_Val_OverwriteUnreadSamps    = ctypes.c_uint32(10252)
DAQmx_Val_HWTimedSinglePoint      = ctypes.c_int32(12522)
DAQmx_Val_SampClk                 = ctypes.c_int32(10388)
DAQmx_Val_OnDemand                = ctypes.c_int32(10390)
DAQmx_Val_CurrReadPos             = ctypes.c_int32(10425)
DAQmx_Val_MostRecentSamp          = ctypes.c_int32(10428)
DAQmx_Val_OverwriteUnreadSamps    = ctypes.c_int32(10252)
DAQmx_Val_DoNotOverwriteUnreadSamps  = ctypes.c_int32(10159)

c_uint32_p = c_ulong_p = ctypes.POINTER(ctypes.c_uint32)
c_float64_p = c_double_p = ctypes.POINTER(ctypes.c_double)


def CHK(err):
	"""a simple error checking routine"""
	if err < 0:
		buf_size = 1000
		# PYTHON3 EDIT
		buf = ctypes.create_string_buffer(bytes('\000',"utf-8") * buf_size)
		#buf = bytes('Test', encoding='utf-8')

		dll.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)
		raise RuntimeError('nidaq call failed with error %d: %s'%(err,repr(buf.value)))


def Connect(source, destination):
	"""Connect terminal 'source' to terminal 'destination'."""
	CHK( dll.DAQmxConnectTerms(source, destination, DAQmx_Val_DoNotInvertPolarity )  )


def Disconnect(source, destination):
	"""Connect terminal 'source' to terminal 'destination'."""
	CHK( dll.DAQmxDisconnectTerms(source, destination)  )


class CounterBoard:
	"""nidaq Counter board.
	"""

	_CountAverageLength = 10

	_MaxCounts = 1e7

	_DefaultCountLength = 1000

	_RWTimeout = 1.0

	def __init__(self, CounterIn, CounterOut, TickSource, SettlingTime=2e-3, CountTime=8e-3):
		self._CODevice = CounterOut
		self._CIDevice = CounterIn

		self._PulseTrain = self._CODevice+'InternalOutput' # counter bins are triggered by CTR1
		self._TickSource = TickSource #the signal: ticks coming from the APDs

		# nidaq Tasks
		self.COTask = ctypes.c_ulong()
		self.CITask = ctypes.c_ulong()
		CHK(  dll.DAQmxCreateTask('', ctypes.byref(self.COTask))  )
		CHK(  dll.DAQmxCreateTask('', ctypes.byref(self.CITask))  )

		f = 1. / ( CountTime + SettlingTime )
		DutyCycle = CountTime * f

		# ctr1 generates a continuous square wave with given duty cycle. This serves simultaneously
		# as sampling clock for AO (update DAC at falling edge), and as gate for counter (count between
		# rising and falling edge)
		CHK(  dll.DAQmxCreateCOPulseChanFreq( self.COTask,
											  self._CODevice, '',
											  DAQmx_Val_Hz, DAQmx_Val_Low, ctypes.c_double(0),
											  ctypes.c_double(f),
											  ctypes.c_double(DutyCycle) )  )

		# ctr0 is used to count photons. Used to count ticks in N+1 gates
		CHK(  dll.DAQmxCreateCIPulseWidthChan( self.CITask,
											   self._CIDevice, '',
											   ctypes.c_double(0),
											   ctypes.c_double(self._MaxCounts*DutyCycle/f),
											   DAQmx_Val_Ticks, DAQmx_Val_Rising, '')   )

		CHK(  dll.DAQmxSetCIPulseWidthTerm( self.CITask, self._CIDevice, self._PulseTrain )  )
		CHK(  dll.DAQmxSetCICtrTimebaseSrc( self.CITask, self._CIDevice, self._TickSource )  )

		self._SettlingTime = None
		self._CountTime = None
		self._DutyCycle = None
		self._f = None
		self._CountSamples = self._DefaultCountLength
		
		self.setTiming(SettlingTime, CountTime)

		self._CINread = ctypes.c_int32()

		self.setCountLength(self._DefaultCountLength)

	def setCountLength(self, N, BufferLength=None, SampleLength=None):
		"""
		Set the number of counter samples / length of pulse train. If N is finite, a finite pulse train
		of length N is generated and N count samples are acquired. If N is infinity, an infinite pulse
		train is generated. BufferLength and SampleLength specify the length of the buffer and the length
		of a sample that is read in one read operation. In this case, always the most recent samples are read.
		"""
		if N < numpy.inf:
			CHK(  dll.DAQmxCfgImplicitTiming( self.COTask, DAQmx_Val_ContSamps, ctypes.c_ulonglong(N))  )
			CHK(  dll.DAQmxCfgImplicitTiming( self.CITask, DAQmx_Val_FiniteSamps, ctypes.c_ulonglong(N))  )
			# read samples from beginning of acquisition, do not overwrite
			CHK( dll.DAQmxSetReadRelativeTo(self.CITask, DAQmx_Val_CurrReadPos) )
			CHK( dll.DAQmxSetReadOffset(self.CITask, 0) )
			CHK( dll.DAQmxSetReadOverWrite(self.CITask, DAQmx_Val_DoNotOverwriteUnreadSamps) )
			self._CountSamples = N
			self._TaskTimeout = 4 * N / self._f
		else:
			CHK(  dll.DAQmxCfgImplicitTiming( self.COTask, DAQmx_Val_ContSamps, ctypes.c_ulonglong(BufferLength))  )
			CHK(  dll.DAQmxCfgImplicitTiming( self.CITask, DAQmx_Val_ContSamps, ctypes.c_ulonglong(BufferLength))  )
			# read most recent samples, overwrite buffer
			CHK( dll.DAQmxSetReadRelativeTo(self.CITask, DAQmx_Val_MostRecentSamp) )
			CHK( dll.DAQmxSetReadOffset(self.CITask, -SampleLength) )
			CHK( dll.DAQmxSetReadOverWrite(self.CITask, DAQmx_Val_OverwriteUnreadSamps) )
			self._CountSamples = SampleLength
		self._CountLength = N
		self._CIData = numpy.empty((self._CountSamples,), dtype=numpy.uint32)

	def CountLength(self):
		return self._CountLength

	def setTiming(self, SettlingTime, CountTime):
		if SettlingTime != self._SettlingTime or CountTime != self._CountTime: 
			f = 1. / ( CountTime + SettlingTime )
			DutyCycle = CountTime * f
			CHK( dll.DAQmxSetCOPulseFreq( self.COTask, self._CODevice, ctypes.c_double(f)  )  )
			CHK( dll.DAQmxSetCOPulseDutyCyc( self.COTask, self._CODevice, ctypes.c_double(DutyCycle)  )   )
			self._SettlingTime = SettlingTime
			self._CountTime = CountTime
			self._f = f
			self._DutyCycle = DutyCycle
			if self._CountSamples is not None:
				self._TaskTimeout = 4 * self._CountSamples / self._f

	def getTiming(self):
		return self._SettlingTime, self._CountTime

	def StartCO(self):
		CHK( dll.DAQmxStartTask(self.COTask) )
	def StartCI(self):
		CHK( dll.DAQmxStartTask(self.CITask) )

	def StopCO(self):
		CHK( dll.DAQmxStopTask(self.COTask) )
	def StopCI(self):
		CHK( dll.DAQmxStopTask(self.CITask) )

	def ReadCI(self):
		CHK( dll.DAQmxReadCounterU32(self.CITask
									 , ctypes.c_int32(self._CountSamples)
									 , ctypes.c_double(self._RWTimeout)
									 , self._CIData.ctypes.data_as(c_uint32_p)
									 , ctypes.c_uint32(self._CountSamples)
									 , ctypes.byref(self._CINread), None) )
		return self._CIData

	def WaitCI(self):
		CHK( dll.DAQmxWaitUntilTaskDone(self.CITask, ctypes.c_double(self._TaskTimeout))  )

	def startCounter(self, SettlingTime, CountTime):
		if self.CountLength() != numpy.inf:
			self.setCountLength(numpy.inf, max(1000, self._CountAverageLength), self._CountAverageLength)
		self.setTiming(SettlingTime, CountTime)
		self.StartCI()
		self.StartCO()
		time.sleep(self._CountSamples / self._f)

	def Count(self):
		"""Return a single count."""
		return self.ReadCI().mean() * self._f / self._DutyCycle

	def stopCounter(self):
		self.StopCI()
		self.StopCO()


class MultiBoard( CounterBoard ):
	"""nidaq Multifuntion board."""

	_DefaultAOLength = 1000

	def __init__(self, CounterIn, CounterOut, TickSource, AOChannels, v_range=(0.,10.)):
		# CounterBoard.__init__(self, CounterIn, CounterOut, TickSource)
		self._AODevice = AOChannels
		
		self.AOTask = nidaqmx.Task()
		
		CHK ( self.AOTask.ao_channels.add_ao_voltage_chan(
			AOChannels,		      
			'',
			v_range[0],
			v_range[1],
			nidaqmx.constants.VoltageUnits.VOLTS ) )
		# CHK(  dll.DAQmxCreateTask('', ctypes.byref(self.AOTask))  )
		# CHK(  dll.DAQmxCreateAOVoltageChan( self.AOTask,
		# 									self._AODevice, '',
		# 									ctypes.c_double(v_range[0]),
		# 									ctypes.c_double(v_range[1]),
		# 									DAQmx_Val_Volts,'')    )
		self._AONwritten = ctypes.c_int32()

		self.setAOLength(self._DefaultAOLength)

	def setAOLength(self, N):
		if N == 1:
			CHK ( self.AOTask.timing.cfg_samp_clk_timing(rate=1, sample_mode=nidaqmx.constants.SampleTimingType.FINITE, samps_per_chan=1) )
			self.AOTask.timing.samp_timing_type = nidaqmx.constants.SampleTimingType.ON_DEMAND
			# CHK( dll.DAQmxSetSampTimingType( self.AOTask, DAQmx_Val_OnDemand)  )
		else:
			#CHK ( self.AOTask.timing.cfg_samp_clk_timing(rate=1, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS, active_edge=nidaqmx.constants.Edge.RISING ) )
			# CHK( dll.DAQmxSetSampTimingType( self.AOTask, DAQmx_Val_SampClk)  )
			if N < numpy.inf:

				CHK ( self.AOTask.timing.cfg_samp_clk_timing(
					rate=ctypes.c_double(self._f), 
					source = self._PulseTrain,
					sample_mode=nidaqmx.constants.AcquisitionType.FINITE_SAMPLES, 
					active_edge=nidaqmx.constants.Edge.FALLING,
					samps_per_chan= ctypes.c_ulonglong(N)) )
				
				# CHK( dll.DAQmxCfgSampClkTiming( self.AOTask,
				# 								self._PulseTrain,
				# 								ctypes.c_double(self._f),
				# 								DAQmx_Val_Falling, 
				# 								DAQmx_Val_FiniteSamps,
				# 								ctypes.c_ulonglong(N)) )
		self._AOLength = N

	def AOLength(self):
		return self._AOLength

	def StartAO(self):
		CHK( self.AOTask.start() )
		# CHK( dll.DAQmxStartTask(self.AOTask) )

	def StopAO(self):
		CHK( self.AOTask.stop() )
		# CHK( dll.DAQmxStopTask(self.AOTask) )

	def WriteAO(self, data, start=False):

		written_value = self.AOTask.write(
			data,
			auto_start = start,
			timeout = self._RWTimeout,
		)

		# CHK( dll.DAQmxWriteAnalogF64( self.AOTask,
		# 							  ctypes.c_int32(self._AOLength),
		# 							  start,
		# 							  ctypes.c_double(self._RWTimeout),
		# 							  DAQmx_Val_GroupByChannel,
		# 							  data.ctypes.data_as(c_float64_p),
		# 							  ctypes.byref(self._AONwritten), None) )
		# return self._AONwritten.value
		return written_value
	

class Scanner( MultiBoard ):

	def __init__(self, CounterIn, CounterOut, TickSource, AOChannels,
				 x_range, y_range, z_range, v_range=(0.,10.),
				 invert_x=False, invert_y=False, invert_z=False, swap_xy=False, TriggerChannels=None):
		MultiBoard.__init__(self, CounterIn=CounterIn,
								  CounterOut=CounterOut,
								  TickSource=TickSource,
								  AOChannels=AOChannels,
								  v_range=v_range)
		if TriggerChannels is not None:
			self._trigger_task = DOTask(TriggerChannels)
		self.xRange = x_range
		self.yRange = y_range
		self.zRange = z_range
		self.vRange = v_range
		self.x = 0.0
		self.y = 0.0
		self.z = 0.0
		self.invert_x = invert_x
		self.invert_y = invert_y
		self.invert_z = invert_z
		self.swap_xy = swap_xy

	def getXRange(self):
		return self.xRange

	def getYRange(self):
		return self.yRange

	def getZRange(self):
		return self.zRange

	def setx(self, x):
		"""Move stage to x, y, z
		"""
		if self.AOLength() != 1:
			self.setAOLength(1)
		self.WriteAO(self.PosToVolt((x, self.y, self.z)), start=True)
		self.x = x

	def sety(self, y):
		"""Move stage to x, y, z
		"""
		if self.AOLength() != 1:
			self.setAOLength(1)
		self.WriteAO(self.PosToVolt((self.x, y, self.z)), start=True)
		self.y = y

	def setz(self, z):
		"""Move stage to x, y, z
		"""
		if self.AOLength() != 1:
			self.setAOLength(1)
		self.WriteAO(self.PosToVolt((self.x, self.y, z)), start=True)
		self.z = z

	def scanLine(self, Line, SecondsPerPoint, return_speed=None):
		"""Perform a line scan. If return_speed is not None, return to beginning of line
		with a speed 'return_speed' times faster than the speed currently set.
		"""
		self.setTiming(SecondsPerPoint*0.1, SecondsPerPoint*0.9)

		N = Line.shape[1]

		if self.AOLength() != N: # set buffers of nidaq Tasks, data read buffer and timeout if needed
			self.setAOLength(N)

		if self.CountLength() != N+1:
			self.setCountLength(N+1)

		# send line start trigger
		if hasattr(self, '_trigger_task'):
			self._trigger_task.Write(numpy.array((1,0), dtype=numpy.uint8) )
			time.sleep(0.001)
			self._trigger_task.Write(numpy.array((0,0), dtype=numpy.uint8) )

		# acquire line
		self.WriteAO( self.PosToVolt(Line) )

		self.StartAO()
		self.StartCI()
		self.StartCO()

		self.WaitCI()

		# send line stop trigger
		if hasattr(self, '_trigger_task'):
			self._trigger_task.Write(numpy.array((0,1), dtype=numpy.uint8) )
			time.sleep(0.001)
			self._trigger_task.Write(numpy.array((0,0), dtype=numpy.uint8) )

		data = self.ReadCI()

		self.StopAO()
		self.StopCI()
		self.StopCO()

		if return_speed is not None:
			self.setTiming(SecondsPerPoint*0.5/return_speed, SecondsPerPoint*0.5/return_speed)
			self.WriteAO( self.PosToVolt(Line[:,::-1]) )
			self.StartAO()
			self.StartCI()
			self.StartCO()
			self.WaitCI()
			self.StopAO()
			self.StopCI()
			self.StopCO()
		self.setTiming(SecondsPerPoint*0.1, SecondsPerPoint*0.9)

		return data[1:] * self._f / self._DutyCycle

	def setPosition(self, x, y, z):
		"""Move stage to x, y, z"""
		if self.AOLength() != 1:
			self.setAOLength(1)
		self.WriteAO(self.PosToVolt((x, y, z)), start=True)
		self.x, self.y, self.z = x, y, z

	def PosToVolt(self, r):
		x = self.xRange
		y = self.yRange
		z = self.zRange
		v = self.vRange
		v0 = v[0]
		dv = v[1]-v[0]
		if self.invert_x:
			#vx = v0+(x[1]-r[0])/(x[1]-x[0])*2.5
			vx = v0+(x[1]-r[0])/(x[1]-x[0])*dv
		else:
			#vx = v0+(r[0]-x[0])/(x[1]-x[0])*2.5
			vx = v0+(r[0]-x[0])/(x[1]-x[0])*dv
		if self.invert_y:
			#vy = v0+(y[1]-r[1])/(y[1]-y[0])*2.5
			vy = v0+(y[1]-r[1])/(y[1]-y[0])*dv
		else:
			#vy = v0+(r[1]-y[0])/(y[1]-y[0])*2.5            
			vy = v0+(r[1]-y[0])/(y[1]-y[0])*dv
		if self.invert_z:
			#vz = v0+(z[1]-r[2])/(z[1]-z[0])*dv            
			vz = 0.0+(z[1]-r[2])/(z[1]-z[0])*10.0            
		else:
			vz = v0+(r[2]-z[0])/(z[1]-z[0])*dv
			#vz = v0+(r[2]-z[0])/(z[1]-z[0])*dv
		if self.swap_xy:
			vt = vx
			vx = vy
			vy = vt            
		return numpy.vstack( (vx,vy,vz) )


class PIScanner( MultiBoard ):

	def __init__(self, CounterIn, CounterOut, TickSource, AOChannels,
				 x_range, y_range, z_range, v_range=(0.,10.),
				 invert_x=False, invert_y=False, invert_z=False, swap_xy=False, TriggerChannels=None):
		MultiBoard.__init__(self, CounterIn=CounterIn,
								  CounterOut=CounterOut,
								  TickSource=TickSource,
								  AOChannels=AOChannels,
								  v_range=v_range)
		if TriggerChannels is not None:
			self._trigger_task = DOTask(TriggerChannels)
		self.xRange = x_range
		self.yRange = y_range
		self.zRange = z_range
		self.vRange = v_range
		self.x = 0.0
		self.y = 0.0
		self.z = 0.0
		self.invert_x = invert_x
		self.invert_y = invert_y
		self.invert_z = invert_z
		self.swap_xy = swap_xy

	def getXRange(self):
		return self.xRange

	def getYRange(self):
		return self.yRange

	def getZRange(self):
		return self.zRange

	def setx(self, x):
		"""Move stage to x, y, z
		"""
		if self.AOLength() != 1:
			self.setAOLength(1)
		self.WriteAO(self.PosToVolt((x, self.y, self.z)), start=True)
		self.x = x

	def sety(self, y):
		"""Move stage to x, y, z
		"""
		if self.AOLength() != 1:
			self.setAOLength(1)
		self.WriteAO(self.PosToVolt((self.x, y, self.z)), start=True)
		self.y = y

	def setz(self, z):
		"""Move stage to x, y, z
		"""
		if self.AOLength() != 1:
			self.setAOLength(1)
		self.WriteAO(self.PosToVolt((self.x, self.y, z)), start=True)
		self.z = z

	def scanLine(self, Line, SecondsPerPoint, return_speed=None):
		"""Perform a line scan. If return_speed is not None, return to beginning of line
		with a speed 'return_speed' times faster than the speed currently set.
		"""
		self.setTiming(SecondsPerPoint*0.3, SecondsPerPoint*0.7)  #original 0.1 , 0.9

		N = Line.shape[1]

		if self.AOLength() != N: # set buffers of nidaq Tasks, data read buffer and timeout if needed
			self.setAOLength(N)

		if self.CountLength() != N+1:
			self.setCountLength(N+1)

		# send line start trigger
		if hasattr(self, '_trigger_task'):
			self._trigger_task.Write(numpy.array((1,0), dtype=numpy.uint8) )
			time.sleep(0.001)
			self._trigger_task.Write(numpy.array((0,0), dtype=numpy.uint8) )

		# acquire line
		self.WriteAO( self.PosToVolt(Line) )

		self.StartAO()
		self.StartCI()
		self.StartCO()

		self.WaitCI()

		# send line stop trigger
		if hasattr(self, '_trigger_task'):
			self._trigger_task.Write(numpy.array((0,1), dtype=numpy.uint8) )
			time.sleep(0.001)
			self._trigger_task.Write(numpy.array((0,0), dtype=numpy.uint8) )

		data = self.ReadCI()

		self.StopAO()
		self.StopCI()
		self.StopCO()

		if return_speed is not None:
			self.setTiming(SecondsPerPoint*0.5/return_speed, SecondsPerPoint*0.5/return_speed)
			self.WriteAO( self.PosToVolt(Line[:,::-1]) )
			self.StartAO()
			self.StartCI()
			self.StartCO()
			self.WaitCI()
			self.StopAO()
			self.StopCI()
			self.StopCO()
		self.setTiming(SecondsPerPoint*0.1, SecondsPerPoint*0.9)

		return data[1:] * self._f / self._DutyCycle

	def setPosition(self, x, y, z):
		"""Move stage to x, y, z"""
		if self.AOLength() != 1:
			self.setAOLength(1)
		self.WriteAO(self.PosToVolt((x, y, z)), start=True)
		self.x, self.y, self.z = x, y, z

	def PosToVolt(self, r):
		x = self.xRange
		y = self.yRange
		z = self.zRange
		v = self.vRange
		v0 = v[0]
		dv = v[1]-v[0]
		if self.invert_x:
			vx = v0+(x[1]-r[0])/(x[1]-x[0])*dv            
		else:
			vx = v0+(r[0]-x[0])/(x[1]-x[0])*dv            
		if self.invert_y:
			vy = v0+(y[1]-r[1])/(y[1]-y[0])*dv            
		else:
			vy = v0+(r[1]-y[0])/(y[1]-y[0])*dv            
		if self.invert_z:
			vz = v0+(z[1]-r[2])/(z[1]-z[0])*dv*0.2            
		else:
			vz = v0+(r[2]-z[0])/(z[1]-z[0])*dv*0.2
		if self.swap_xy:
			vt = vx
			vx = vy
			vy = vt            
		return numpy.vstack( (vx,vy,vz) )
	

class PulseTrainCounter:
	"""Outputs pulsed train and performs gated count."""

	def __init__(self, CounterIn, CounterOut, TickSource):
		
		self._CounterIn = CounterIn
		self._CounterOut = CounterOut
		self._TickSource = TickSource

	def configure(self, SampleLength, SecondsPerPoint, DutyCycle=0.9, MaxCounts=1e7, RWTimeout=1.0):

		if hasattr(self, '_CITask') or hasattr(self, '_COTask'):
			self.clear()

		f = 1. / SecondsPerPoint

		# nidaq Tasks
		self._COTask = ctypes.c_ulong()
		self._CITask = ctypes.c_ulong()

		CHK(  dll.DAQmxCreateTask('', ctypes.byref(self._COTask))  )
		CHK(  dll.DAQmxCreateTask('', ctypes.byref(self._CITask))  )

		# ctr1 generates a continuous square wave with given duty cycle. This serves simultaneously
		# as sampling clock for AO (update DAC at falling edge), and as gate for counter (count between
		# rising and falling edge)
		CHK(  dll.DAQmxCreateCOPulseChanFreq( self._COTask,
											  self._CounterOut, '',
											  DAQmx_Val_Hz, DAQmx_Val_Low, ctypes.c_double(0),
											  ctypes.c_double(f),
											  ctypes.c_double(DutyCycle) )  )

		# ctr0 is used to count photons. Used to count ticks in N+1 gates
		CHK(  dll.DAQmxCreateCIPulseWidthChan( self._CITask,
											   self._CounterIn, '',
											   ctypes.c_double(0),
											   ctypes.c_double(MaxCounts*DutyCycle/f),
											   DAQmx_Val_Ticks, DAQmx_Val_Rising, '')   )

		CHK(  dll.DAQmxSetCIPulseWidthTerm( self._CITask, self._CounterIn, self._CounterOut+'InternalOutput' )  )
		CHK(  dll.DAQmxSetCICtrTimebaseSrc( self._CITask, self._CounterIn, self._TickSource )  )

		CHK(  dll.DAQmxCfgImplicitTiming( self._COTask, DAQmx_Val_ContSamps, ctypes.c_ulonglong(SampleLength))  )
		CHK(  dll.DAQmxCfgImplicitTiming( self._CITask, DAQmx_Val_FiniteSamps, ctypes.c_ulonglong(SampleLength))  )

		# read samples from beginning of acquisition, do not overwrite
		CHK( dll.DAQmxSetReadRelativeTo(self._CITask, DAQmx_Val_CurrReadPos) )
		CHK( dll.DAQmxSetReadOffset(self._CITask, 0) )
		CHK( dll.DAQmxSetReadOverWrite(self._CITask, DAQmx_Val_DoNotOverwriteUnreadSamps) )

		self._CIData = numpy.empty((SampleLength,), dtype=numpy.uint32)
		self._CINread = ctypes.c_int32()

		self._SampleLength = SampleLength
		self._TaskTimeout = 4 * SampleLength / f
		self._RWTimeout = RWTimeout
			
	def run(self):
		CHK( dll.DAQmxStartTask(self._CITask) )
		CHK( dll.DAQmxStartTask(self._COTask) )
		CHK( dll.DAQmxWaitUntilTaskDone(self._CITask, ctypes.c_double(self._TaskTimeout))  )
		CHK( dll.DAQmxReadCounterU32(self._CITask,
									 ctypes.c_int32(self._SampleLength),
									 ctypes.c_double(self._RWTimeout),
									 self._CIData.ctypes.data_as(c_uint32_p),
									 ctypes.c_uint32(self._SampleLength),
									 ctypes.byref(self._CINread), None) )
		CHK( dll.DAQmxStopTask(self._COTask) )
		CHK( dll.DAQmxStopTask(self._CITask) )
		return self._CIData

	def clear(self):
		CHK( dll.DAQmxClearTask((self._CITask)) )
		CHK( dll.DAQmxClearTask((self._COTask)) )
		del self._CITask
		del self._COTask

	def __del__(self):
		try:
			self.clear()
		except Exception as e:
			print(str(e))


class DOTask(object):

    def __init__(self, DOChannels, write_timeout=1.0):
        self.write_timeout = write_timeout
        self.Nwritten = ctypes.c_long()
        self.Task = ctypes.c_ulong()
        CHK( dll.DAQmxCreateTask('', ctypes.byref(self.Task)) )
        #CHK(  dll.DAQmxCreateDOChan( self.Task,
        #                                    DOChannels, 
        #                                    DAQmx_Val_ChanForAllLines)    )
        CHK( dll.DAQmxCreateDOChan(self.Task, DOChannels, '',  DAQmx_Val_ChanPerLine) )

    def Write(self, data):
        #CHK( dll.DAQmxWriteDigitalScalarU32(self.Task, ctypes.c_long(1), ctypes.c_double(self.write_timeout), ctypes.c_uint32(value), None)  )
        
        CHK( dll.DAQmxWriteDigitalLines(self.Task,
                                        ctypes.c_long(1),
                                        1, 
                                        ctypes.c_double(self.write_timeout),
                                        1,
                                        data.ctypes.data_as(c_uint32_p),
                                        ctypes.byref(self.Nwritten),
                                        None ) )
        
        
        
        #CHK( dll.DAQmxWriteDigitalU32(self.Task, ctypes.c_long(1), 1,  ctypes.c_double(self.write_timeout), DAQmx_Val_GroupByChannel, data.ctypes.data, ctypes.byref(self.Nwritten), None ) )

    def Start(self):
        CHK( dll.DAQmxStartTask(self.Task)  )

    def Wait(self, timeout):
        CHK( dll.DAQmxWaitUntilTaskDone(self.Task, ctypes.c_double(timeout)) )

    def Stop(self):
        CHK( dll.DAQmxStopTask(self.Task)  )

    def __del__(self):
        CHK( dll.DAQmxClearTask(self.Task)  )


def test():
	#stage = nidaqStage(1, 1, 0, '0:2')
	stage = 1
	x = stage._xRange
	y = stage._yRange
	z = stage._zRange
	stage.setPosition(0.3*(x[0]+x[1]), y[0], z[0])
	stage.startCounter()
	time.sleep(0.1)
	print(stage.Count())
	stage.stopCounter()
	X = numpy.linspace(x[0], x[1], 100)
	Y = numpy.linspace(y[0], y[1], 100)
	Z = numpy.linspace(z[0], z[1], 100)
	print(stage.ScanLine( numpy.vstack((X,Y,Z)) ))
	stage.setPosition(0.7*(x[0]+x[1]), y[0], z[0])

	print('board 2')

	Connect('/dev1/pfi8', '/dev2/pfi8')

	counter = CounterBoard(2,1,0)
	counter.startCounter()
	time.sleep(0.1)
	print(counter.Count())
	counter.stopCounter()

	del stage
	del counter

if __name__=='__main__':
	test()

