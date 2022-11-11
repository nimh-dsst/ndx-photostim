import os
from datetime import datetime
import numpy as np
from dateutil.tz import tzlocal
from pynwb import NWBFile, NWBHDF5IO
from pynwb.testing import TestCase, remove_test_file

from ndx_photostim import SpatialLightModulator, PhotostimulationDevice, HolographicPattern, PhotostimulationSeries, PhotostimulationTable


def get_SLM():
    '''Return SpatialLightModulator container.'''
    slm = SpatialLightModulator(name="slm", size=np.array([1, 2]))
    return slm

def get_photostim_device():
    '''Return PhotostimulationDevice containing SLM.'''
    slm = get_SLM()
    photostim_dev = PhotostimulationDevice(name="photostim_dev", description="photostim_device", type='LED',
                                           wavelength=320, slm=slm,
                                           opsin='test_opsin', peak_pulse_energy=20,
                                           power=10, pulse_rate=5)

    return photostim_dev

def get_holographic_pattern():
    '''Return example HolographicPattern with image_mask_roi'''
    image_mask_roi = TestHolographicPattern._create_image_mask_roi()
    hp = HolographicPattern(name='pattern', image_mask_roi=image_mask_roi, roi_size=5)
    return hp

def get_photostim_series():
    '''Return example PhotostimulationSeries container.'''
    hp = get_holographic_pattern()

    photostim_series = PhotostimulationSeries(name="photosim series", pattern=hp, unit='SIunit',
                                              data=[1, -1, 1, -1],
                                              timestamps=[0.5, 1, 2, 4], format='interval')
    return photostim_series

def get_series():
    '''Return example PhotostimulationSeries.'''
    hp = get_holographic_pattern()
    series = PhotostimulationSeries(name="photosim series", format='interval', pattern=hp, data=[1, -1, 1, -1], timestamps=[0.5, 1, 2, 4], stimulus_method="stim_method", sweep_pattern="...", time_per_sweep=10, num_sweeps=20)
    return series

class TestSLM(TestCase):
    def test_init(self):
        '''Test spatial light monitor initialization.'''
        SpatialLightModulator(name="slm", size=np.array([1, 2]))

        with self.assertRaises(ValueError):
            SpatialLightModulator(name="slm", size=np.array([[1, 2], [3, 4]]))

class TestPhotostimulationDevice(TestCase):
    def test_init(self):
        '''Test PhotostimulationDevice initialization and the 'add_slm' method.'''
        dev = PhotostimulationDevice(name="device", description="...", manufacturer="manufacturer",
                                     type="LED", wavelength=320, opsin='test_opsin',power=10,
                                     peak_pulse_energy=20, pulse_rate=5)

        slm = get_SLM()
        dev.add_slm(slm)

class TestHolographicPattern(TestCase):
    def test_init_MaskROI(self):
        '''Test HolographicPattern with 'image_mask_roi' specification.'''
        mask_roi = self._create_image_mask_roi()
        HolographicPattern(name='hp', image_mask_roi=mask_roi)

        HolographicPattern(name='hp', image_mask_roi=np.round(np.random.rand(5, 5)))

        HolographicPattern(name='hp', image_mask_roi=np.round(np.random.rand(5, 5, 5)))

        with self.assertRaises(ValueError):
            HolographicPattern(name='hp', image_mask_roi=np.round(np.random.rand(5)))

        with self.assertRaises(ValueError):
            HolographicPattern(name='hp', image_mask_roi=np.round(np.random.rand(5, 5, 5, 5)))

        hp = HolographicPattern(name='hp', image_mask_roi=np.round(np.random.rand(5, 5)))
        assert hp.dimension == (5, 5)

        # Check image_mask_roi validation
        with self.assertRaises(ValueError):
            HolographicPattern(name='hp', image_mask_roi=np.random.rand(5, 5) * 10)

        with self.assertRaises(ValueError):
            HolographicPattern(name='hp', image_mask_roi=np.random.rand(5, 5) * -1)

    def test_init_PixelROI(self):
        '''Test HolographicPattern with 'pixel_roi' specification.'''

        pixel_roi = self._create_pixel_roi()
        hp = HolographicPattern(name='hp', pixel_roi=pixel_roi, roi_size=8, dimension=[100, 100])
        hp.pixel_to_image_mask_roi()
        hp.show_mask()

        hp = HolographicPattern(name='hp', pixel_roi=pixel_roi, roi_size=[8, 4], dimension=[100, 100])
        hp.pixel_to_image_mask_roi()
        hp.show_mask()

        with self.assertRaises(TypeError):
            HolographicPattern(name='hp', pixel_roi=pixel_roi, dimension=[100, 100])

        with self.assertRaises(TypeError):
            HolographicPattern(name='hp', pixel_roi=pixel_roi, roi_size=[8, 4])

    @staticmethod
    def _create_pixel_roi():
        '''Helper function to create pixel_roi at 5 randomly selected coordinates.'''
        pixel_roi = []

        for i in range(5):
            x = np.random.randint(0, 90)
            y = np.random.randint(0, 90)

            for ix in range(x, x + 1):
                for iy in range(y, y + 1):
                    pixel_roi.append((ix, iy))

        return pixel_roi

    @staticmethod
    def _create_image_mask_roi():
        '''Helper function to create an image mask with 3 ROIs on a [50, 50] grid.'''
        image_mask_roi = np.zeros((50, 50))
        x = np.random.randint(0, 3)
        y = np.random.randint(0, 3)
        image_mask_roi[x:x + 5, y:y + 5] = 1
        return image_mask_roi

class TestPhotostimulationSeries(TestCase):
    def test_init(self):
        '''Test initialization of PhotostimulationSeries under different data, format, and time specifications.'''
        hp = get_holographic_pattern()
        PhotostimulationSeries(name="photosim series", format='interval', pattern=hp, data=[1, -1, 1, -1], timestamps=[0.5, 1, 2, 4], stimulus_method="stim_method", sweep_pattern="...", time_per_sweep=10, num_sweeps=20)

        PhotostimulationSeries(name="photosim series", pattern=hp, format='series', data=[0, 0, 0, 1, 1, 0],
                               rate=10., stimulus_duration=0.05)

        with self.assertRaises(ValueError):
            PhotostimulationSeries(name="photosim series", pattern=hp, format='series', data=[0, 0, 0, 1, 1, 0],
                               rate=10.)

            PhotostimulationSeries(name="photosim series", pattern=hp, format='series')

        PhotostimulationSeries(name="photosim series", pattern=hp, format='series',
                                                  stimulus_duration = 0.05, data=[0, 0, 0, 1, 1, 0],
                                                  timestamps=[0, 0.5, 1, 1.5, 3, 6])

    def test_format_data(self):
        '''Test data validation for PhotostimulationSeries.'''
        hp = get_holographic_pattern()
        data = [1, -1, 1, -1]
        timestamps=[0.5, 1, 2, 4]

        with self.assertRaises(ValueError):
            PhotostimulationSeries(name="photosim series", format='interval', pattern=hp, timestamps=timestamps)

        PhotostimulationSeries(name="photosim series", format='interval', pattern=hp, timestamps=timestamps, data=data)

        data = [1, -1, 1, 2]
        timestamps = [0.5, 1, 2, 4]
        with self.assertRaises(ValueError):
            PhotostimulationSeries(name="photosim series", pattern=hp, format='interval', data=data, timestamps=timestamps)

        with self.assertRaises(ValueError):
            PhotostimulationSeries(name="photosim series", pattern=hp, format='series',
                               data=[0, 0, 0, 1, 2, 0], rate=10.)

    def test_add_interval(self):
        '''Test 'add_interval' method on 'interval' type series.'''
        hp = get_holographic_pattern()
        #
        empty_series = PhotostimulationSeries(name="photosim series", pattern=hp, format='interval')
        empty_series.add_interval(10, 20)
        empty_series.add_interval(30, 40)
        assert empty_series.data[0] == 1
        assert empty_series.data[3] == -1
        assert len(empty_series.data) == 4

        assert empty_series.timestamps[0] == 10
        assert empty_series.timestamps[1] == 20
        assert len(empty_series.timestamps) == 4

        stim_series_2 = PhotostimulationSeries(name="series 2", format='interval',  data=[1, -1], timestamps=[1, 3], pattern=hp)
        stim_series_2.add_interval(10., 20.)
        stim_series_2.add_interval(35., 40.)

    def test_add_onset(self):
        '''Test 'add_onset' method on both 'interval' and 'series' formatted PhotostimulationSeries.'''
        hp = get_holographic_pattern()

        ps = PhotostimulationSeries(name="photosim series",  format='series', pattern=hp, stimulus_duration=10)
        ps.add_onset(10)
        ps.add_onset([30, 40, 50])

        assert all(ps.timestamps == np.array([10., 30., 40., 50.]))
        assert all(ps.data == np.array([1., 1., 1., 1.]))

        ps = PhotostimulationSeries(name="photosim series", format='interval', pattern=hp, stimulus_duration=2)
        ps.add_onset(10)
        ps.add_onset([30, 40, 50])

        assert all(ps.timestamps == np.array([10., 12., 30., 32., 40., 42., 50., 52.]))
        assert all(ps.data == np.array([ 1., -1.,  1., -1.,  1., -1.,  1., -1.]))

    def test_to_df(self):
        '''Test conversion to Pandas dataframe, showing data and timestamps in each columns.'''
        hp = get_holographic_pattern()

        ps = PhotostimulationSeries(name="photosim series", format='series', pattern=hp,
                               data=[0, 0, 0, 1, 1, 0], rate=10., stimulus_duration=4)
        ps.to_dataframe()

        ps = PhotostimulationSeries(name="photosim series",format='series', pattern=hp,
                                    stimulus_duration=0.05, data=[0, 0, 0, 1, 1, 0], timestamps=[0, 0.5, 1, 1.5, 3, 6])
        ps.to_dataframe()

        ps = PhotostimulationSeries(name="photosim series",format='interval', pattern=hp,  stimulus_duration=2)
        ps.add_onset([10, 40, 50])
        ps.to_dataframe()

    def test_start_stop_list(self):
        '''Test if helped function '_get_start_stop_list' correctly returns a list of the start and stop times, regardess of format and time specification.'''
        hp = get_holographic_pattern()
        ps = PhotostimulationSeries(name="photosim series", format='interval', pattern=hp, data=[1, -1, 1, -1],
                               timestamps=[0.5, 1, 2, 4])

        ps._get_start_stop_list()

        ps = PhotostimulationSeries(name="photosim series", pattern=hp, format='series',
                               data=[0, 0, 0, 1, 1, 0], rate=10., stimulus_duration=4)
        ps._get_start_stop_list()

        ps = PhotostimulationSeries(name="photosim series", pattern=hp,
                                                  format='series', stimulus_duration=0.05,
                                                  data=[0, 0, 0, 1, 1, 0], timestamps=[0, 0.5, 1, 1.5, 3, 6])
        ps._get_start_stop_list()

class TestPhotostimulationTable(TestCase):
    def test_init(self):
        '''Test PhotostimulationTable initialization.'''
        dev = get_photostim_device()
        hp = get_holographic_pattern()

        nwbfile = NWBFile('my first synthetic recording', 'EXAMPLE_ID', datetime.now(tzlocal()), )
        nwbfile.add_device(dev)

        sp = PhotostimulationTable(name='test', description='test desc', device=dev)
        s1 = get_series()
        s2 = PhotostimulationSeries(name="series2", pattern=hp, format='interval',
                                    stimulus_duration=2, data=[1, -1, 1, -1], timestamps=[0.5, 1, 2, 4])
        s3 = PhotostimulationSeries(name="series3", pattern=hp, format='interval',
                                    stimulus_duration=2, data=[1, -1, 1, -1], timestamps=[0.5, 1, 2, 4])

        [nwbfile.add_stimulus(s) for s in [s1, s2, s3]]
        sp.add_series([s1, s2, s3])#, row_name=["row_1", "row_2", "row_3"])

        behavior_module = nwbfile.create_processing_module(
            name="holographic_photostim", description="initial data"
        )
        behavior_module.add(sp)

    def test_plot_presentation_times(self):
        '''Check that PhotostimulationTable can be plotted correctly.'''
        hp = get_holographic_pattern()
        dev = get_photostim_device()

        nwbfile = NWBFile('my first synthetic recording', 'EXAMPLE_ID', datetime.now(tzlocal()), )

        nwbfile.add_device(dev)
        sp = PhotostimulationTable(name='test', description='test desc', device=dev)
        s1 = PhotostimulationSeries(name="series1", pattern=hp, format='interval',
                                    stimulus_duration=2, data=[1, -1, 1, -1], timestamps=[0.5, 1, 2, 4])
        s2 = PhotostimulationSeries(name="series2", pattern=hp, format='interval',
                                    stimulus_duration=2, data=[1, -1, 1, -1], timestamps=[0.5, 1, 2, 4])
        s3 = PhotostimulationSeries(name="series3", pattern=hp, format='interval',
                                    stimulus_duration=2, data=[1, -1, 1, -1], timestamps=[0.5, 1, 2, 4])

        [nwbfile.add_stimulus(s) for s in [s1, s2, s3]]
        sp.add_series([s1, s2, s3])

        sp.plot_presentation_times()
