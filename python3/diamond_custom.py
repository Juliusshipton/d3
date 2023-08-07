
from hardware.pulse_generator_api import PulseGenerator
from tools.utility import edit_singleton
from datetime import date
import os
import time

# start confocal including auto_focus tool and Toolbox
if __name__ == '__main__':
    

    # # Photon Time Trace Startup
    # from measurements.photon_time_trace1 import PhotonTimeTrace
    # photon_time_trace = PhotonTimeTrace()
    # photon_time_trace.edit_traits()

    # start confocal including auto_focus tool
    from measurements.confocal import Confocal
    confocal = Confocal()
    confocal.edit_traits()

    from measurements.auto_focus import AutoFocus
    auto_focus = AutoFocus(confocal)
    auto_focus.edit_traits()


        
