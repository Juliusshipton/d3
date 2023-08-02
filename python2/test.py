

print("Running Python3 ..")

from NIDAQ.nidaq import Scanner


test = Scanner( CounterIn='/Dev1/Ctr1',
					CounterOut='/Dev1/Ctr0',
					TickSource='/Dev1/PFI3',
					AOChannels='/Dev1/ao0:2',
					x_range=(0.0,200.0),#100x
					y_range=(0.0,200.0),
					z_range=(0,100.0),
					v_range=(-1.0,10.00))

print("NIDAQ Scanner Successfully Created ...")
