TODO LIST:

- Make and test TimeTagger Custom API
- Make and test PulseGenerator Custom API
- Test confocal on device (import is working, uncomment in diamond_custom)
- Test autofocus on device (import is working, uncomment in diamond_custom)

Where Configuration Info Lives:

- time_tagger_api.py
  - holds the TimeTagger Serial number that is used when a time tagger is created in api.pi
- api.py Scanner()
  - holds the NIDAQ specific info

NIDAQ dll calls

- dll.DAQmxCreateTask('', ctypes.byref(self.AOTask))

# new imp Create a task

import nidaqmx
task = nidaqmx.Task()

- dll.DAQmxCreateAOVoltageChan( self.AOTask,
  self.\_AODevice, '',
  ctypes.c_double(v_range[0]),
  ctypes.c_double(v_range[1]),
  DAQmx_Val_Volts,'')

- dll.DAQmxSetSampTimingType( self.AOTask, DAQmx_Val_OnDemand)
- dll.DAQmxCfgSampClkTiming( self.AOTask,
  self.\_PulseTrain,
  ctypes.c_double(self.\_f),
  DAQmx_Val_Falling, DAQmx_Val_FiniteSamps,
  ctypes.c_ulonglong(N))
- dll.DAQmxStartTask(self.AOTask)
- dll.DAQmxStopTask(self.AOTask)
- dll.DAQmxWriteAnalogF64( self.AOTask,
  ctypes.c_int32(self.\_AOLength),
  start,
  ctypes.c_double(self.\_RWTimeout),
  DAQmx_Val_GroupByChannel,
  data.ctypes.data_as(c_float64_p),
  ctypes.byref(self.\_AONwritten), None)

NIDAQ Counterboard dll calls

- dll.DAQmxCreateCOPulseChanFreq( self.COTask,
  self.\_CODevice, '',
  DAQmx_Val_Hz, DAQmx_Val_Low, ctypes.c_double(0),
  ctypes.c_double(f),
  ctypes.c_double(DutyCycle)
- dll.DAQmxCreateCIPulseWidthChan( self.CITask,
  self.\_CIDevice, '',
  ctypes.c_double(0),
  ctypes.c_double(self.\_MaxCounts\*DutyCycle/f),
  DAQmx_Val_Ticks, DAQmx_Val_Rising, '')
- dll.DAQmxSetCIPulseWidthTerm( self.CITask, self.\_CIDevice, self.\_PulseTrain )
- dll.DAQmxSetCICtrTimebaseSrc( self.CITask, self.\_CIDevice, self.\_TickSource )
