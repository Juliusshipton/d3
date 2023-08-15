
from tools.utility import edit_singleton
from datetime import date
import os
import time

# start confocal including auto_focus tool and Toolbox
if __name__ == '__main__':
    
    print("Running Python3 ...")
    # Photon Time Trace Startup
    from measurements.photon_time_trace1 import PhotonTimeTrace
    photon_time_trace = PhotonTimeTrace()
    photon_time_trace.edit_traits()

    # Start confocal including auto_focus tool
    from measurements.confocal import Confocal
    confocal = Confocal()
    confocal.edit_traits()

    # Start autofocus tool
    from measurements.auto_focus import AutoFocus
    auto_focus = AutoFocus(confocal)
    auto_focus.edit_traits()

    # Start ODMR
    from measurements.odmr import ODMR
    odmr = ODMR()
    odmr.edit_traits()

    # Start Rabi / PulsedAnalyser
    from analysis.pulsed import PulsedAnalyser
    pa = PulsedAnalyser()
    pa.edit_traits()


        
