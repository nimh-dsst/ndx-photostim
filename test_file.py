import file_classes
from ndx_photostim import SpatialLightModulator, PhotostimulationDevice, ImagingPlane, HolographicPattern, PhotostimulationSeries
from datetime import datetime
from dateutil.tz import tzlocal
from pynwb import NWBFile
from pynwb.testing import TestCase
import numpy as np
from pynwb import NWBHDF5IO


class TestExtension(TestCase):

    def setUp(self):
        self.nwb_file = NWBFile(session_description='test file', identifier='EXAMPLE_ID', session_start_time=datetime.now(tzlocal()))

    def test_SpatialLightModulator(self):
        slm = SpatialLightModulator(name="slm", dimensions=np.array([[1, 2], [3, 4]]))
        print(slm)


    def test_PhotostimulationDevice(self):
        photostim_dev = PhotostimulationDevice(name="photostim_dev", description="photostim_device", type='LED', wavelength=320)

        self.nwb_file.add_device(photostim_dev)
        assert "photostim_dev" in self.nwb_file.devices

        slm = SpatialLightModulator(name="slm", dimensions=[1, 2, 3])
        photostim_dev = PhotostimulationDevice(name="photostim_dev", description="photostim_device", type='LED',
                                                     wavelength=320, slm=slm)
        assert hasattr(photostim_dev, "slm")

    def test_ImagingPlane(self):
        photostim_dev = PhotostimulationDevice(name="photostim_dev", description="photostim_device", type='LED',
                                               wavelength=320)
        ImagingPlane(name="imaging_plane", device=photostim_dev)

    def test_HolographicPattern(self):
        mask_roi = self._create_mask_roi()
        hp = HolographicPattern(name='HolographicPattern', mask_roi=mask_roi)

        pixel_roi = self._create_pixel_roi()
        hp = HolographicPattern(name='HolographicPattern', pixel_roi=pixel_roi, stimulation_diameter=5, dimension=[100, 100])


    def test_PhotostimulationSeriesConstructor(self):
        mask_roi = self._create_mask_roi()
        photostim_dev = PhotostimulationDevice(name="photostim_dev", description="photostim_device", type='LED',
                                               wavelength=320)
        imaging_plane = ImagingPlane(name="imaging_plane", device=photostim_dev)
        hp = HolographicPattern(name='HolographicPattern', mask_roi=mask_roi)

        photostim_series = PhotostimulationSeries(name="photosim series", pattern=hp, unit='SIunit', data=[1, -1, 1, -1],
                                     timestamps=[0.5, 1, 2, 4], imaging_plane=imaging_plane)
        assert photostim_series.data == [1, -1, 1, -1]
        assert photostim_series.timestamps == [0.5, 1, 2, 4]

        photostim_series = PhotostimulationSeries(name="photosim series", pattern=hp, unit='SIunit', format='series',
                                                  data=[0, 0, 0, 1, 1, 0], rate=10., imaging_plane=imaging_plane)
        assert photostim_series.data == [0, 0, 0, 1, 1, 0]
        assert photostim_series.rate == 10.

        photostim_series = PhotostimulationSeries(name="photosim series", pattern=hp, unit='SIunit', format='series', stimulus_duration = 0.05,
                                                  data=[0, 0, 0, 1, 1, 0], timestamps=[0, 0.5, 1, 1.5, 3, 6], imaging_plane=imaging_plane)
        assert photostim_series.data == [0, 0, 0, 1, 1, 0]
        assert photostim_series.timestamps == [0, 0.5, 1, 1.5, 3, 6]

        self.nwb_file.add_stimulus(photostim_series)
        assert "photosim series" in self.nwb_file.stimulus

    def test_add_interval(self):
        mask_roi = self._create_mask_roi()
        photostim_dev = PhotostimulationDevice(name="photostim_dev", description="photostim_device", type='LED',
                                               wavelength=320)
        imaging_plane = ImagingPlane(name="imaging_plane", device=photostim_dev)
        hp = HolographicPattern(name='HolographicPattern', mask_roi=mask_roi)

        empty_series = PhotostimulationSeries(name="photosim series", pattern=hp, imaging_plane=imaging_plane,
                                              unit='SIunit')
        empty_series.add_interval(10, 20)
        empty_series.add_interval(30, 40)
        assert empty_series.data[0] == 1
        assert empty_series.data[3] == -1
        assert len(empty_series.data) == 4

        assert empty_series.timestamps[0] == 10
        assert empty_series.timestamps[1] == 20
        assert len(empty_series.timestamps) == 4

    @staticmethod
    def _create_pixel_roi():
        x = np.random.randint(0, 95)
        y = np.random.randint(0, 95)

        pixel_roi = []
        for ix in range(x, x + 5):
            for iy in range(y, y + 5):
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


    # def
#
# class TestExtension(TestCase):
#     def test_setup(self):
#         nwbfile = NWBFile(session_description='test file', identifier='EXAMPLE_ID', session_start_time=datetime.now(tzlocal()))
#
#         slm = SpatialLightModulator(name="slm", dimensions=[1, 2, 3])
#         self.assertEqual(slm.name, 'slm')
#         self.assertEqual(slm.dimensions, [1, 2, 3])
#
#         dev = PhotostimulationDevice(name="device", description="photostim_device", type='LED', wavelength=320.)
#         nwbfile.add_device(dev)
#



#
# import numpy as np
# slm = SpatialLightModulator(
#     name="slm",
#     dimensions = [1, 2, 3],#[32, 10],
# )
#
# dev = PhotostimulationDevice(name="device", description="photostim_device", type='LED', wavelength=320.)
# nwbfile.add_device(dev)
#
# dev = PhotostimulationDevice(name="device1")
# nwbfile.add_device(dev)
#
# imaging_plane = ImagingPlane(name="imaging_plane",  device=dev)
