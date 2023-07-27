import ctypes
import nidaqmx

print("Running python3 NIDAQ Test ...")

# Pulse Train Counter Test

print("Creating Pulse Train Counter ...")

DAQmx_Val_Low = ctypes.c_int32(10214)

COTask = nidaqmx.Task()

print("Pulse Train Counter Created ...")

COTask.co_channels.add_co_pulse_chan_freq(
    'Dev1/Ctr2', # Specifies the names of the counters to use to create the virtual channels. 
    '', # Optional to assign to channel
    units = nidaqmx.constants.FrequencyUnits.HZ, # Frequency unit
    idle_state = DAQmx_Val_Low, # Specifies the resting state of the output terminal
    initial_delay = ctypes.c_double(0), # Is the amount of time in seconds to wait before generating the first pulse.
    freq=1000.0, # Specifies at what frequency to generate pulses.
    duty_cycle=0.5 # Is the width of the pulse divided by the pulse period. NI-DAQmx uses this ratio combined with frequency to determine pulse width and the interval between pulses.
    )

COTask.timing.cfg_samp_clk_timing(
        source='Dev1/Ctr2',
        rate=10000.0,              # Sample rate in samples per second
        samps_per_chan=10000,    # Number of samples to acquire per channel
        sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS, # Continuous acquisition mode
    )

COTask.out_stream.output_buf_size = 50

print("Pulse Train Counter Configured ...")

print("Starting Pulse Train Counter ...")
COTask.start()




# # Config variables
# AOChannels='/Dev1/ao3'
# _PulseTrain = '/Dev1/Ctr0InternalOutput'
# v_range=(0.,10.)
# _f = 1000
# N = 1000

# # Create task
# AOTask = nidaqmx.Task()

# # Add voltage channel
# AOTask.ao_channels.add_ao_voltage_chan(
# 			AOChannels,		      
# 			'',
# 			v_range[0],
# 			v_range[1],
# 			nidaqmx.constants.VoltageUnits.VOLTS ) 

# # Configure voltage channel

# AOTask.timing.cfg_samp_clk_timing(
#     rate=ctypes.c_double(_f), 
# 	source = _PulseTrain,
# 	sample_mode=nidaqmx.constants.AcquisitionType.FINITE_SAMPLES, 
# 	active_edge=nidaqmx.constants.Edge.FALLING,
# 	samps_per_chan= ctypes.c_ulonglong(N))




