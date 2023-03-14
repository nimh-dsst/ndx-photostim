import os
from datetime import datetime
import numpy as np
from dateutil.tz import tzlocal
from pynwb import NWBFile, NWBHDF5IO
from pynwb.testing import TestCase
from pynwb.ophys import TwoPhotonSeries, OpticalChannel, ImageSegmentation
import matplotlib.pyplot as plt

# regenerate namespace from specification language
os.system('python file_defined_namespace_PKL.py')

# load ndx-photostim classes
from file_classes_PKL import SpatialLightModulator, Laser, PhotostimulationMethod, HolographicPattern, \
                             PhotostimulationSeries, PhotostimulationTable

# run tests
class TestIO(TestCase):
    """
    Integration tests to ensure read/write compatability.
    """
    def setUp(self):
        """
        Create a blank NWBFile.
        """
        self.nwbfile = NWBFile(
            session_description='session_description',
            identifier='identifier',
            session_start_time=datetime.now(tzlocal()))
        self.path = 'test.nwb'

    def test_roundtrip(self):
        """
        Create an SLM and Laser device, a photostimulation methods object, a holographic pattern,
        and three series containers.
        Wrap up the stimulation data into a PhotostimulationTable, and ensure it can be written
        and read back in correctly.
        """

        # set device and methods information
        slm = SpatialLightModulator(name='slm',
                                    model='Meadowlark',
                                    size=np.array([512, 512]))
        laser = Laser(name='laser',
                      model='Coherent',
                      wavelength=1030,
                      power=8,
                      peak_pulse_energy=20,
                      pulse_rate=500)
        ps_method = PhotostimulationMethod(name="methodA",
                                           stimulus_method="scanless",
                                           sweep_pattern="none",
                                           sweep_size=0,
                                           time_per_sweep=0,
                                           num_sweeps=0)
        ps_method.add_slm(slm)
        ps_method.add_laser(laser)

        # add devices to nwb file
        self.nwbfile.add_device(slm)
        self.nwbfile.add_device(laser)

        # define holographic pattern
        hp = HolographicPattern(name='pattern1',
                                image_mask_roi=np.round(np.random.rand(5, 5)),
                                stim_duration=0.300,
                                power_per_target=8)

        # define stimulation time series using holographic pattern
        s1 = PhotostimulationSeries(name="series_1",
                                    format='interval',
                                    data=[1, -1, 1, -1],
                                    timestamps=[0.5, 1, 2, 4],
                                    pattern=hp,
                                    method=ps_method)
        s2 = PhotostimulationSeries(name="series_2",
                                    format='interval',
                                    data=[-1, 1, -1, 1],
                                    timestamps=[0.4, 0.9, 1.9, 3.9],
                                    pattern=hp,
                                    method=ps_method)
        s3 = PhotostimulationSeries(name="series_3",
                                    format='series',
                                    stim_duration=0.05,
                                    data=[0, 0, 0, 1, 1, 0],
                                    timestamps=[0, 0.5, 1, 1.5, 3, 6],
                                    pattern = hp,
                                    method=ps_method)
        # add photostim series data to nwb file
        [self.nwbfile.add_stimulus(s) for s in [s1, s2, s3]]

        # create table of photostimulation series data
        stim_table = PhotostimulationTable(name='test', description='...')
        stim_table.add_series([s1, s2, s3])

        # add table to nwb file
        module = self.nwbfile.create_processing_module(name="test_module", description="...")
        module.add(stim_table)

        # save output
        with NWBHDF5IO(self.path, "w") as io:
            io.write(self.nwbfile)

        # read output and test that it is correct
        with NWBHDF5IO(self.path, mode='r', load_namespaces=True) as io:
            read_nwbfile = io.read()
            self.assertContainerEqual(slm, read_nwbfile.devices['slm'])
            self.assertContainerEqual(laser, read_nwbfile.devices['laser'])
            self.assertContainerEqual(module, read_nwbfile.modules['test_module'])

        # cleanup workspace
        if os.path.exists(self.path):
            os.remove(self.path)
