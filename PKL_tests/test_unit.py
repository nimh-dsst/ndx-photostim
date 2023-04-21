from datetime import datetime
from dateutil.tz import tzlocal
from pynwb import NWBFile
from pynwb.testing import TestCase
import numpy as np
from pynwb import NWBHDF5IO
from pynwb import register_class, load_namespaces
from pynwb import register_map

from pynwb.image import GrayscaleImage
from file_classes_PKL import SpatialLightModulator, Laser, PhotostimulationMethod, HolographicPattern, \
                             PhotostimulationSeries, PhotostimulationTable
import os
from hdmf.build import ObjectMapper

os.system('python file_defined_namespace_PKL.py')

def get_SLM():
    '''Return SpatialLightModulator container.'''
    slm = SpatialLightModulator(name='slm',
                                model='Meadowlark',
                                size=np.array([512, 512]))
    return slm

def get_laser():
    laser = Laser(name='laser', model='Coherent', wavelength=1030, power=8,
              peak_pulse_energy=20, pulse_rate=500)
    return laser

def get_photostim_method():
    '''Return PhotostimulationDevice containing SLM.'''
    ps_method = PhotostimulationMethod(name="methodA",
                                       stimulus_method="scanless",
                                       sweep_pattern="none",
                                       sweep_size=0,
                                       time_per_sweep=0,
                                       num_sweeps=0)
    slm = get_SLM()
    laser = get_laser()
    ps_method.add_slm(slm)
    ps_method.add_laser(laser)

    return ps_method

def get_holographic_pattern():
    '''Return example HolographicPattern with image_mask_roi'''
    image_mask_roi = TestHolographicPattern._create_image_mask_roi()
    hp = HolographicPattern(name='pattern', image_mask_roi=image_mask_roi, roi_size=5)
    return hp

def get_photostim_series():
    '''Return example PhotostimulationSeries container.'''
    hp = get_holographic_pattern()
    ps_method = get_photostim_method()

    photostim_series = PhotostimulationSeries(name="series_1",
                                    format='interval',
                                    data=[1, -1, 1, -1],
                                    timestamps=[0.5, 1, 2, 4],
                                    pattern=hp,
                                    method=ps_method)
    return photostim_series

def get_series():
    '''Return example PhotostimulationSeries.'''
    hp = get_holographic_pattern()
    ps_method = get_photostim_method()
    series = PhotostimulationSeries(name="series_1",
                                    format='interval',
                                    data=[1, -1, 1, -1],
                                    timestamps=[0.5, 1, 2, 4],
                                    pattern=hp,
                                    method=ps_method)
    return series


class TestSLM(TestCase):
    def test_init(self):
        '''Test spatial light monitor initialization.'''
        SpatialLightModulator(name='slm',
                                    model='Meadowlark',
                                    size=np.array([512, 512]))

        with self.assertRaises(TypeError):
            SpatialLightModulator(name='slm', size=np.array([512, 512]))

class TestLaser(TestCase):
    def test_init(self):
        Laser(name='laser', model='Coherent', wavelength=1030, power=8,
              peak_pulse_energy=20, pulse_rate=500)


class TestPhotostimulationMethod(TestCase):
    def test_init(self):
        ps_method = PhotostimulationMethod(name="methodA",
                               stimulus_method="scanless",
                               sweep_pattern="none",
                               sweep_size=0,
                               time_per_sweep=0,
                               num_sweeps=0)
        slm = get_SLM()
        laser = get_laser()
        ps_method.add_slm(slm)
        ps_method.add_laser(laser)


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
        ps_method = get_photostim_method()

        PhotostimulationSeries(name="series_1",
                               format='interval',
                                    data=[1, -1, 1, -1],
                                    timestamps=[0.5, 1, 2, 4],
                                    pattern=hp,
                                    method=ps_method)

        with self.assertRaises(ValueError):
            PhotostimulationSeries(name="photosim series", pattern=hp, format='series', data=[0, 0, 0, 1, 1, 0],
                               rate=10., method=ps_method)

            PhotostimulationSeries(name="photosim series", pattern=hp, format='series', method=ps_method)

        PhotostimulationSeries(name="photosim series", pattern=hp, format='series',
                                                  stim_duration = 0.05, data=[0, 0, 0, 1, 1, 0],
                                                  timestamps=[0, 0.5, 1, 1.5, 3, 6], method=ps_method)

    def test_format_data(self):
        '''Test data validation for PhotostimulationSeries.'''
        hp = get_holographic_pattern()
        data = [1, -1, 1, -1]
        timestamps=[0.5, 1, 2, 4]
        ps_method = get_photostim_method()

        with self.assertRaises(ValueError):
            PhotostimulationSeries(name="photosim series", format='interval', pattern=hp, timestamps=timestamps, method=ps_method)

        PhotostimulationSeries(name="photosim series", format='interval', pattern=hp, timestamps=timestamps, data=data, method=ps_method)

        data = [1, -1, 1, 2]
        timestamps = [0.5, 1, 2, 4]
        with self.assertRaises(ValueError):
            PhotostimulationSeries(name="photosim series", pattern=hp, format='interval', data=data, timestamps=timestamps, method=ps_method)

        with self.assertRaises(ValueError):
            PhotostimulationSeries(name="photosim series", pattern=hp, format='series',
                               data=[0, 0, 0, 1, 2, 0], rate=10., method=ps_method)

    def test_add_interval(self):
        '''Test 'add_interval' method on 'interval' type series.'''
        hp = get_holographic_pattern()
        ps_method = get_photostim_method()
        #
        empty_series = PhotostimulationSeries(name="photosim series", pattern=hp, format='interval', method=ps_method)
        empty_series.add_interval(10, 20)
        empty_series.add_interval(30, 40)
        assert empty_series.data[0] == 1
        assert empty_series.data[3] == -1
        assert len(empty_series.data) == 4

        assert empty_series.timestamps[0] == 10
        assert empty_series.timestamps[1] == 20
        assert len(empty_series.timestamps) == 4

        stim_series_2 = PhotostimulationSeries(name="series 2", format='interval',  data=[1, -1], timestamps=[1, 3], pattern=hp, method=ps_method)
        stim_series_2.add_interval(10., 20.)
        stim_series_2.add_interval(35., 40.)

    def test_add_onset(self):
        '''Test 'add_onset' method on both 'interval' and 'series' formatted PhotostimulationSeries.'''
        hp = get_holographic_pattern()
        ps_method = get_photostim_method()
        ps = PhotostimulationSeries(name="photosim series",  format='series', pattern=hp, stim_duration=10, method=ps_method)
        ps.add_onset(10)
        ps.add_onset([30, 40, 50])

        assert all(ps.timestamps == np.array([10., 30., 40., 50.]))
        assert all(ps.data == np.array([1., 1., 1., 1.]))

        ps = PhotostimulationSeries(name="photosim series", format='interval', pattern=hp, stim_duration=2, method=ps_method)
        ps.add_onset(10)
        ps.add_onset([30, 40, 50])

        assert all(ps.timestamps == np.array([10., 12., 30., 32., 40., 42., 50., 52.]))
        assert all(ps.data == np.array([ 1., -1.,  1., -1.,  1., -1.,  1., -1.]))

    def test_to_df(self):
        '''Test conversion to Pandas dataframe, showing data and timestamps in each columns.'''
        hp = get_holographic_pattern()
        ps_method = get_photostim_method()
        ps = PhotostimulationSeries(name="photosim series", format='series', pattern=hp,
                               data=[0, 0, 0, 1, 1, 0], rate=10., stim_duration=4, method=ps_method)
        ps.to_dataframe()

        ps = PhotostimulationSeries(name="photosim series",format='series', pattern=hp,
                                    stim_duration=0.05, data=[0, 0, 0, 1, 1, 0], timestamps=[0, 0.5, 1, 1.5, 3, 6], method=ps_method)
        ps.to_dataframe()

        ps = PhotostimulationSeries(name="photosim series",format='interval', pattern=hp,  stim_duration=2, method=ps_method)
        ps.add_onset([10, 40, 50])
        ps.to_dataframe()

    def test_start_stop_list(self):
        '''Test if helped function '_get_start_stop_list' correctly returns a list of the start and stop times, regardess of format and time specification.'''
        hp = get_holographic_pattern()
        ps_method = get_photostim_method()
        ps = PhotostimulationSeries(name="photosim series", format='interval', pattern=hp, data=[1, -1, 1, -1],
                               timestamps=[0.5, 1, 2, 4], method=ps_method)

        ps._get_start_stop_list()

        ps = PhotostimulationSeries(name="photosim series", pattern=hp, format='series',
                               data=[0, 0, 0, 1, 1, 0], rate=10., stim_duration=4, method=ps_method)
        ps._get_start_stop_list()

        ps = PhotostimulationSeries(name="photosim series", pattern=hp,
                                                  format='series', stim_duration=0.05,
                                                  data=[0, 0, 0, 1, 1, 0], timestamps=[0, 0.5, 1, 1.5, 3, 6], method=ps_method)
        ps._get_start_stop_list()

class TestPhotostimulationTable(TestCase):
    def test_init(self):
        '''Test PhotostimulationTable initialization.'''
        ps_method = get_photostim_method()
        hp = get_holographic_pattern()

        nwbfile = NWBFile('my first synthetic recording', 'EXAMPLE_ID', datetime.now(tzlocal()), )

        sp = PhotostimulationTable(name='test', description='test desc')
        s1 = get_series()
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

        [nwbfile.add_stimulus(s) for s in [s1, s2, s3]]
        sp.add_series([s1, s2, s3])#, row_name=["row_1", "row_2", "row_3"])

        behavior_module = nwbfile.create_processing_module(
            name="holographic_photostim", description="initial data"
        )
        behavior_module.add(sp)

    def test_plot_presentation_times(self):
        '''Check that PhotostimulationTable can be plotted correctly.'''
        ps_method = get_photostim_method()
        hp = get_holographic_pattern()

        nwbfile = NWBFile('my first synthetic recording', 'EXAMPLE_ID', datetime.now(tzlocal()), )

        sp = PhotostimulationTable(name='test', description='test desc')
        s1 = get_series()
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
                                    pattern=hp,
                                    method=ps_method)

        [nwbfile.add_stimulus(s) for s in [s1, s2, s3]]
        sp.add_series([s1, s2, s3])  # , row_name=["row_1", "row_2", "row_3"])

        sp.plot_presentation_times()






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