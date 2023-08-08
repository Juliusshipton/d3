from .core import ASG8x00

import logging

logger = logging.getLogger()

class ImplementationError(Exception):
	pass

class ASGError(Exception):
	pass

class BadInputError(Exception):
	pass

# Check that the function call is correctly executed
def _check(_status, accepted = [0]):
	if _status not in accepted:
		print(_status)
		raise ASGError("Error Code: %i" % _status)

class PulseGenerator():

	_underflow = False

	_decoder = False
	_pulse_mode = False

	def _set_model(self, model):
		self.model = model

		# Units in nanosecond
		if self.model == "asg8100":
			self.min_pulse = 1
			self.pulse_resolution = 1
			self.max_pulse = 1600000000
			self.min_segment = 160
		elif self.model == "asg8200":
			self.min_pulse = 2
			self.pulse_resolution = 2
			self.max_pulse = 1600000000
			# Not tested
			self.min_segment = 160
		elif self.model == "asg8400":
			self.min_pulse = 4
			self.pulse_resolution = 4
			self.max_pulse = 1600000000
			# Not tested
			self.min_segment = 160
		else:
			raise ImplementationError("Model not supported")

	# Translate the channels mask from original PulseGenerator to ASG series pulse generator
	def _translate_channel_mask(self, channels):
		_bits = 0
		for _b in range(0, 8):
			_bits |= (channels >> _b & 1) << 15 - _b

		return _bits

	def _set_trigger(self, trigger):
		if trigger:
			self.enableTrigger()
		else:
			self.disableTrigger()

	def __init__(self, model, device, channel_map={'ch1': 1, 'ch2': 2, 'ch3': 3,'ch4': 4,'ch5': 5,'ch6': 6,'ch7': 7,'ch8': 8}):
		self.channel_map = channel_map

		self._set_model(model)
		self.device = device

		_status = _check(self.device.connect())

	def setSequence(self, sequence, loop=True, triggered=False):
		"""
		Output a pulse sequence.

		Input:
			sequence	List of tuples (channels, time) specifying the pulse sequence.
						'channels' is a list of strings specifying the channels that
						should be high and 'time' is a float specifying the time in ns.

		Optional arguments:
			loop		bool, defaults to True, specifying whether the sequence should be
						excecuted once or repeated indefinitely.
			triggered	bool, defaults to False, specifies whether the execution
						should be delayed until an external trigger is received
		"""

		self._underflow = False

		self.setContinuous(0)

		self._set_trigger(triggered)

		_total_time = 0
		_seq = []

		for _pulse in sequence:
			_channels = _pulse[0]
			_len = _pulse[1]

			_time = int(_len // self.pulse_resolution) * self.pulse_resolution
			
			if _time:
				_row = [0, 0, 0, 0, 0, 0, 0, 0]

				for _ch in _channels:
					_idx = self.channel_map.get(_ch, None)
					_row[_idx - 1] = 1

				_seq.append((_time, _row))
				
				_total_time += _time

		if _total_time <= self.min_segment:
			self._underflow = True

		self.device.AsgDownload(((1, _seq), ))

		self.device.ASG8x00_AsgSetChannelEnable(0x1ff)

		if not loop:
			_check(self.device.start(1))
		else:
			_check(self.device.start())

	def saveSequence(self, sequence):
		_total_time = 0
		_seq = []

		for _pulse in sequence:
			_channels = _pulse[0]
			_len = _pulse[1]

			_time = int(_len // self.pulse_resolution) * self.pulse_resolution
			
			if _time:
				_row = [0, 0, 0, 0, 0, 0, 0, 0]

				for _ch in _channels:
					_idx = self.channel_map.get(_ch, None)
					_row[_idx - 1] = 1

				_seq.append((_time, _row))
				
				_total_time += _time

		if _total_time <= self.min_segment:
			self._underflow = True
		c_pulses, length, loop, seg_num = self.device.Asg_prepare(((1, _seq), ))

		return c_pulses, length, loop, seg_num

	def loadSequence(self, c_pulses, length, loop0, seg_num, loop=True, triggered=False):
		"""
		Output a pulse sequence.

		Input:
			sequence	List of tuples (channels, time) specifying the pulse sequence.
						'channels' is a list of strings specifying the channels that
						should be high and 'time' is a float specifying the time in ns.

		Optional arguments:
			loop		bool, defaults to True, specifying whether the sequence should be
						excecuted once or repeated indefinitely.
			triggered	bool, defaults to False, specifies whether the execution
						should be delayed until an external trigger is received
		"""

		self._underflow = False

		self.setContinuous(0)

		self._set_trigger(triggered)


		self.device.AsgDownload_prepared(c_pulses, length, loop0, seg_num)

		self.device.ASG8x00_AsgSetChannelEnable(0x1ff)

		if not loop:
			_check(self.device.start(1))
		else:
			_check(self.device.start())

	def setContinuous(self, channels):
		"""
		Set the outputs continuously high or low.

		Input:
			channels	can be an integer or a list of channel names (strings).
						If 'channels' is an integer, each bit corresponds to a channel.
						A channel is set to low/high when the bit is 0/1, respectively.
						If 'channels' is a list of strings, the specified channels
						are set high, while all others are set low.
		"""

		_bits = 0

		# Control for the 8 channels starts from 9th bit, from channel 8 to channel 1
		# For first 8 bits, only the lowest bit is used, for controlling the counters
		if hasattr(channels, "__iter__"):
			for ch in channels:
				_ch_no = self.channel_map.get(ch, None)
				if _ch_no:
					_bits |= 1 << 16 - _ch_no
				else:
					pass

		elif isinstance(channels, int):
			_bits = self._translate_channel_mask(channels)

		# Stop call sometimes return with error code 6, even when it has succeeded
		_check(self.device.stop(), [0, 6])

		_check(self.device.AsgSetHightLevel(_bits))

	def checkUnderflow(self):
		return self._underflow

	def setResetValue(self,bits):
		if isinstance(bits, int):
			self.setContinuous(_bits)
		else:
			raise BadInputError("Invalid Input")

	def enableTrigger(self):
		# Disable input ch1, put ch2 into trigger mode
		_check(self.device.SetClockAndWorkMode(0x0, 0x1))
		
		logger.warning("ASG8x00: Trigger has been enabled, note that the trigger on the original Pulse Generator is supposedly non-functional, so the behaviors might differ.")

	def disableTrigger(self):
		# Disable both inputs
		_check(self.device.SetClockAndWorkMode(0x0, 0x0))

	def run(self,triggered=False):
		self._set_trigger(triggered)

		self.device.start()

		logger.warning("ASG8x00: run function has been evoked, note that the behavior might differ from the original Pulse Generator, especially when used in tandem with other low level functions.")

	def halt(self):
		_check(self.device.stop(), [0, 6])

		logger.warning("ASG8x00: halt function has been evoked, note that the behavior might differ from the original Pulse Generator, especially when used in tandem with other low level functions.")

	def getState(self):
		"""
		Return the state of the device in ASG8x00 Series
		
		The state is returned as one of the following string

		TBD

		"""

		raise ImplementationError("getState not implemented")

	def checkState(self, wanted):
		pass

		logger.warning("ASG8x00: checkState has been evoked, note that no error will be raised as the internal states of the device is not accessible.")

	def reset(self):
		raise ImplementationError("reset not implemented")

	def getInfo(self):
		raise ImplementationError("getInfo not implemented")

	def ctrlPulser(self, command):
		raise ImplementationError("ctrlPulser not implemented")
