import os
from datetime import datetime
import numpy as np
from dateutil.tz import tzlocal
from pynwb import NWBFile, NWBHDF5IO
from pynwb.testing import TestCase, remove_test_file

from ndx_photostim import SpatialLightModulator, PhotostimulationDevice, HolographicPattern, PhotostimulationSeries, PhotostimulationTable
# from file_classes import SpatialLightModulator, PhotostimulationDevice, HolographicPattern, PhotostimulationSeries, \
#     PhotostimulationTable


class TestIO(TestCase):
    def setUp(self):
        self.nwbfile = NWBFile(
            session_description='session_description',
            identifier='identifier',
            session_start_time=datetime.now(tzlocal()))
        self.path = 'test.nwb'

    def test_roundtrip(self):
        slm = SpatialLightModulator(name="slm", size=np.array([1, 2]))
        dev = PhotostimulationDevice(name="device", description="...", manufacturer="manufacturer",
                                     type="LED", wavelength=320, opsin='test_opsin', power=10,
                                     peak_pulse_energy=20, pulse_rate=5)
        dev.add_slm(slm)
        self.nwbfile.add_device(dev)

        hp = HolographicPattern(name='hp', image_mask_roi=np.round(np.random.rand(5, 5)))
        s1 = PhotostimulationSeries(name="series_1", format='interval', pattern=hp, data=[1, -1, 1, -1],
                               timestamps=[0.5, 1, 2, 4], stimulus_method="stim_method", sweep_pattern="...",
                               time_per_sweep=10, num_sweeps=20)
        s2 = PhotostimulationSeries(name="series_2", format='interval', pattern=hp, data=[1, -1, 1, -1],
                               timestamps=[0.5, 1, 2, 4])
        s3 = PhotostimulationSeries(name="series_3", pattern=hp, format='series', stimulus_duration=0.05,
                                      data=[0, 0, 0, 1, 1, 0], timestamps=[0, 0.5, 1, 1.5, 3, 6])
        [self.nwbfile.add_stimulus(s) for s in [s1, s2, s3]]

        stim_table = PhotostimulationTable(name='test', description='...', device=dev)
        stim_table.add_series([s1, s2, s3])

        module = self.nwbfile.create_processing_module(name="test_module", description="...")
        module.add(stim_table)

        with NWBHDF5IO(self.path, "w") as io:
            io.write(self.nwbfile)

        with NWBHDF5IO(self.path, mode='r', load_namespaces=True) as io:
            read_nwbfile = io.read()
            self.assertContainerEqual(dev, read_nwbfile.devices['device'])
            self.assertContainerEqual(module, read_nwbfile.modules['test_module'])

        if os.path.exists(self.path):
            os.remove(self.path)
