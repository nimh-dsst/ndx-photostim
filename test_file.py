import file_classes
# from ndx_photostim import SpatialLightModulator, PhotostimulationDevice, ImagingPlane, HolographicPattern, PhotostimulationSeries
from datetime import datetime
from dateutil.tz import tzlocal
from pynwb import NWBFile
from pynwb.testing import TestCase
import numpy as np
from pynwb import NWBHDF5IO

from file_classes import SpatialLightModulator, PhotostimulationDevice, StimulationPlane, HolographicPattern, PhotostimulationSeries, StimulusPresentation
import matplotlib.pyplot as plt
import os

os.system('python file_defined_namespace.py')


class TestExtension(TestCase):

    def setUp(self):
        self.nwb_file = NWBFile(session_description='test file', identifier='EXAMPLE_ID', session_start_time=datetime.now(tzlocal()))

    def test_SpatialLightModulator(self):
        slm = self._get_SLM()
        print(slm)

        with self.assertRaises(ValueError):
            SpatialLightModulator(name="slm", dimensions=np.array([[1, 2], [3, 4]]))

    def test_PhotostimulationDevice(self):
        photostim_dev = self._get_photostim_device()

        self.nwb_file.add_device(photostim_dev)
        assert "photostim_dev" in self.nwb_file.devices

        slm = self._get_SLM()
        photostim_dev = PhotostimulationDevice(name="photostim_dev", description="photostim_device", type='LED',
                                                     wavelength=320, slm=slm)
        assert hasattr(photostim_dev, "slm")

    def test_StimulationPlane(self):
        photostim_dev = self._get_photostim_device()
        sim_plane = StimulationPlane(name="imaging_plane",  device=photostim_dev, opsin='test opsin', pulse_rate=10)

    def test_HolographicPattern(self):
        mask_roi = self._create_mask_roi()
        hp = HolographicPattern(name='HolographicPattern', mask_roi=mask_roi, stimulation_diameter=5)

        pixel_roi = self._create_pixel_roi()
        hp = HolographicPattern(name='HolographicPattern', pixel_roi=pixel_roi, stimulation_diameter=8, dimension=[100, 100])
        center_points = [[roi[0], roi[1]] for roi in pixel_roi]
        center_points = np.array(center_points)
        mask_roi = hp.pixel_to_mask_roi()
        plt.imshow(mask_roi, 'gray', interpolation='none')
        plt.scatter(center_points[:, 0], center_points[:, 1], color='red', s=10)
        plt.show()


    def test_PhotostimulationSeriesConstructor(self):
        stim_plane = self._get_stim_plane()
        hp = self._get_holographic_pattern()

        photostim_series = PhotostimulationSeries(name="photosim series", holographic_pattern=hp, unit='SIunit', data=[1, -1, 1, -1],
                                     timestamps=[0.5, 1, 2, 4], stimulation_plane=stim_plane)
        assert photostim_series.data == [1, -1, 1, -1]
        assert photostim_series.timestamps == [0.5, 1, 2, 4]

        photostim_series = PhotostimulationSeries(name="photosim series", holographic_pattern=hp, unit='SIunit', format='series',
                                                  data=[0, 0, 0, 1, 1, 0], rate=10., stimulation_plane=stim_plane)
        assert photostim_series.data == [0, 0, 0, 1, 1, 0]
        assert photostim_series.rate == 10.

        photostim_series = PhotostimulationSeries(name="photosim series", holographic_pattern=hp, unit='SIunit', format='series', stimulus_duration = 0.05,
                                                  data=[0, 0, 0, 1, 1, 0], timestamps=[0, 0.5, 1, 1.5, 3, 6], stimulation_plane=stim_plane)
        assert photostim_series.data == [0, 0, 0, 1, 1, 0]
        assert photostim_series.timestamps == [0, 0.5, 1, 1.5, 3, 6]

        self.nwb_file.add_stimulus(photostim_series)
        assert "photosim series" in self.nwb_file.stimulus

    def test_add_interval(self):
        stim_plane = self._get_stim_plane()
        hp = self._get_holographic_pattern()

        empty_series = PhotostimulationSeries(name="photosim series", holographic_pattern=hp, stimulation_plane=stim_plane,
                                              unit='SIunit')
        empty_series.add_interval(10, 20)
        empty_series.add_interval(30, 40)
        assert empty_series.data[0] == 1
        assert empty_series.data[3] == -1
        assert len(empty_series.data) == 4

        assert empty_series.timestamps[0] == 10
        assert empty_series.timestamps[1] == 20
        assert len(empty_series.timestamps) == 4


    def test_StimulusPresentation(self):
        stim = self._get_holographic_pattern()
        pres = self._get_photostim_series()

        sp = StimulusPresentation(name='test_presentation_table', description='abcd')
        sp.add_event_type(label='stim1', description='d stim1', stimulus=stim, presentation=pres)
        sp.add_event_type(label='stim2', description='d stim2', stimulus=stim)
        df = sp.to_dataframe()
        print(df)

    @staticmethod
    def _get_photostim_series():
        stim_plane = TestExtension._get_stim_plane()
        hp = TestExtension._get_holographic_pattern()

        photostim_series = PhotostimulationSeries(name="photosim series", holographic_pattern=hp, unit='SIunit',
                                                  data=[1, -1, 1, -1],
                                                  timestamps=[0.5, 1, 2, 4], stimulation_plane=stim_plane)
        return photostim_series

    @staticmethod
    def _get_holographic_pattern():
        mask_roi = TestExtension._create_mask_roi()
        hp = HolographicPattern(name='HolographicPattern', mask_roi=mask_roi, stimulation_diameter=5)
        return hp

    @staticmethod
    def _get_stim_plane():
        photostim_dev = TestExtension._get_photostim_device()
        sim_plane = StimulationPlane(name="imaging_plane", device=photostim_dev, opsin='test opsin', pulse_rate=10)
        return sim_plane

    @staticmethod
    def _get_SLM():
        slm = SpatialLightModulator(name="slm", dimensions=np.array([1, 2, 3]))
        return slm

    @staticmethod
    def _get_photostim_device():
        photostim_dev = PhotostimulationDevice(name="photostim_dev", description="photostim_device", type='LED',
                                               wavelength=320)
        return photostim_dev

    @staticmethod
    def _create_pixel_roi():

        pixel_roi = []

        for i in range(3):
            x = np.random.randint(0, 95)
            y = np.random.randint(0, 95)

            for ix in range(x, x + 1):
                for iy in range(y, y + 1):
                    pixel_roi.append((ix, iy, 1))

        return pixel_roi

    @staticmethod
    def _create_mask_roi():
        mask_roi = np.zeros((50, 50))
        x = np.random.randint(0, 3)
        y = np.random.randint(0, 3)
        mask_roi[x:x + 5, y:y + 5] = 1
        return mask_roi

class TestReadWrite(TestCase):
    def setUp(self):
        self.nwb_file = NWBFile(session_description='test file', identifier='EXAMPLE_ID',
                                session_start_time=datetime.now(tzlocal()))

        mask_roi = TestExtension._create_mask_roi()
        photostim_dev = PhotostimulationDevice(name="photostim_dev", description="photostim_device", type='LED',
                                               wavelength=320)
        self.nwb_file.add_device(photostim_dev)

        imaging_plane = ImagingPlane(name="imaging_plane", device=photostim_dev)
        hp = HolographicPattern(name='HolographicPattern', mask_roi=mask_roi)

        photostim_series = PhotostimulationSeries(name="photostim_series", pattern=hp, unit='SIunit',
                                                  data=[1, -1, 1, -1],
                                                  timestamps=[0.5, 1, 2, 4], imaging_plane=imaging_plane)
        self.nwb_file.add_stimulus(photostim_series)

        self.path = 'test.nwb'

    def test_write_to_nwb(self):
        with NWBHDF5IO(self.path, mode='w') as io:
            # io.write(self.nwb_file.devices['photostim_dev'], link_data=True)
            # io.write(self.nwb_file.devices['photostim_dev'])
            slm =SpatialLightModulator(name="slm", dimensions=[1, 2, 3])
            photostim_dev = PhotostimulationDevice(name="photostim_dev", description="photostim_device", type='LED',
                                                   wavelength=320, slm=slm)

            io.write(photostim_dev)
            # io.write(self.nwb_file.stimulus['photostim_series'])
            io.write(self.nwb_file)
