import os
from datetime import datetime
import numpy as np
from dateutil.tz import tzlocal
from pynwb import NWBFile, NWBHDF5IO
from pynwb.testing import TestCase

from ndx_photostim import SpatialLightModulator, PhotostimulationDevice, HolographicPattern, PhotostimulationSeries, PhotostimulationTable
# from file_classes import SpatialLightModulator, PhotostimulationDevice, HolographicPattern, PhotostimulationSeries, \
#     PhotostimulationTable



def test_example_usage():
    '''Test example use script from README.'''

    # create an example NWB file
    nwbfile = NWBFile('nwb-photostim_example', 'EXAMPLE_ID', datetime.now(tzlocal()))

    # store the spatial light modulator used
    slm = SpatialLightModulator(name='example_SLM', description="example SLM", manufacturer="SLM manufacturer",
                                size=[500, 500])

    # create a container for the device used for photostimulation, and link the SLM to it
    photostim_dev = PhotostimulationDevice(name="device", description="...", manufacturer="manufacturer",
                                 type="LED", wavelength=320, opsin='test_opsin', power=10,
                                 peak_pulse_energy=20, pulse_rate=5)
    photostim_dev.add_slm(slm)

    # add the device to the NWB file
    nwbfile.add_device(photostim_dev)

    # simulate a mask of ROIs corresponding to stimulated regions in the FOV (5 ROIs on a 50x50 pixel image)
    image_mask_roi = np.zeros((50, 50))
    for _ in range(5):
        x = np.random.randint(0, 45)
        y = np.random.randint(0, 45)
        image_mask_roi[x:x + 5, y:y + 5] = 1

    # store the stimulation as "pattern_1"
    hp = HolographicPattern(name='pattern_1', image_mask_roi=image_mask_roi)

    # show the mask
    hp.show_mask()

    # store the time steps in which 'hp' was presented (seconds 10-20 and 35-40)
    stim_series = PhotostimulationSeries(name="series 2", format='interval', pattern=hp,
                                         stimulus_method="stim_method", sweep_pattern="...", time_per_sweep=10,
                                         num_sweeps=20)
    stim_series.add_interval(10, 20)
    stim_series.add_interval(35, 40)

    # add the stimulus to the NWB file
    nwbfile.add_stimulus(stim_series)

    # create a table to store the time series/patterns for all stimuli together, along with experiment-specific parameters
    stim_table = PhotostimulationTable(name='test', description='test desc', device=photostim_dev)

    # add the stimulus to the table
    stim_table.add_series(stim_series)

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