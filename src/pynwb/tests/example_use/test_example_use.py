import os
from datetime import datetime

import numpy as np
from dateutil.tz import tzlocal
from ndx_photostim import SpatialLightModulator, Laser, PhotostimulationMethod, HolographicPattern, \
                             PhotostimulationSeries, PhotostimulationTable
from pynwb import NWBFile, NWBHDF5IO
from pynwb.testing import TestCase


class TestExampleUse(TestCase):
    import numpy as np
    from dateutil.tz import tzlocal
    from datetime import datetime
    from pynwb import NWBFile, NWBHDF5IO

    # create an example NWB file
    nwbfile = NWBFile('nwb-photostim_example', 'EXAMPLE_ID', datetime.now(tzlocal()))

    # store the spatial light modulator used
    slm = SpatialLightModulator(name='slm',
                                model='Meadowlark',
                                size=np.array([512, 512]))

    # store the laser used
    laser = Laser(name='laser',
                  model='Coherent',
                  wavelength=1030,
                  power=8,
                  peak_pulse_energy=20,
                  pulse_rate=500)

    # create a container for the method used for photostimulation, and link the SLM and laser to it
    ps_method = PhotostimulationMethod(name="methodA",
                                       stimulus_method="scanless",
                                       sweep_pattern="none",
                                       sweep_size=0,
                                       time_per_sweep=0,
                                       num_sweeps=0)
    ps_method.add_slm(slm)
    ps_method.add_laser(laser)

    # define holographic pattern
    hp = HolographicPattern(name='pattern1',
                            image_mask_roi=np.round(np.random.rand(5, 5)),
                            stim_duration=0.300,
                            method=ps_method)

    # show the mask
    hp.show_mask()

    # define stimulation time series using holographic pattern
    ps_series = PhotostimulationSeries(name="series_1",
                                format='interval',
                                data=[1, -1, 1, -1],
                                timestamps=[0.5, 1, 2, 4],
                                pattern=hp)

    # add the stimulus to the NWB file
    nwbfile.add_stimulus(ps_series)

    # create a table to store the time series/patterns for all stimuli together, along with experiment-specific
    # parameters
    stim_table = PhotostimulationTable(name='test', description='...')
    stim_table.add_series(ps_series)

    # plot the timestamps when the stimulus was presented
    stim_table.plot_presentation_times()

    # create a processing module and add the PresentationTable to it
    module = nwbfile.create_processing_module(name="photostimulation", description="example photostimulation table")
    module.add(stim_table)

    # write to an NWB file and read it back
    with NWBHDF5IO("example_file.nwb", "w") as io:
        io.write(nwbfile)

    with NWBHDF5IO("example_file.nwb", "r", load_namespaces=True) as io:
        read_nwbfile = io.read()

        # Check the file & processing module
        print(read_nwbfile)
        print(read_nwbfile.processing['photostimulation'])

    if os.path.exists("example_file.nwb"):
        os.remove("example_file.nwb")