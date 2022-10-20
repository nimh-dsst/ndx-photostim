import file_classes
# from ndx_photostim import SpatialLightModulator, PhotostimulationDevice, ImagingPlane, HolographicPattern, PhotostimulationSeries
from datetime import datetime
from dateutil.tz import tzlocal
from pynwb import NWBFile
from pynwb.testing import TestCase
import numpy as np
from pynwb import NWBHDF5IO
from pynwb import register_class, load_namespaces
from pynwb import register_map


from file_classes import SpatialLightModulator, PhotostimulationDevice, HolographicPattern, PhotostimulationSeries, StimulusPresentation
import matplotlib.pyplot as plt
import os
from hdmf.build import ObjectMapper

os.system('python file_defined_namespace.py')

def get_SLM():
    slm = SpatialLightModulator(name="slm", dimensions=np.array([1, 2, 3]))
    return slm

def get_photostim_device():
    slm = get_SLM()
    photostim_dev = PhotostimulationDevice(name="photostim_dev", description="photostim_device", type='LED',
                                           wavelength=320, slm=slm,
                                           opsin='test_opsin', peak_pulse_power=20,
                                           power=10, pulse_rate=5)

    return photostim_dev

def get_photostim_series():
    hp = get_holographic_pattern()

    photostim_series = PhotostimulationSeries(name="photosim series", holographic_pattern=hp, unit='SIunit',
                                              data=[1, -1, 1, -1],
                                              timestamps=[0.5, 1, 2, 4])
    return photostim_series

def get_holographic_pattern():
    mask_roi = TestExtension._create_mask_roi()
    hp = HolographicPattern(name='pattern', mask_roi=mask_roi, stimulation_diameter=5)
    return hp

def create_NWB_file():
    nwb_file = NWBFile(session_description='test file', identifier='EXAMPLE_ID',
                       session_start_time=datetime.now(tzlocal()))
    return nwb_file

class TestPhotostimulationSeries(TestCase):

    def test_PhotostimulationSeriesConstructor(self):
        hp = get_holographic_pattern()

        ps = PhotostimulationSeries(name="photosim series", holographic_pattern=hp, unit='SIunit', format='series')


        PhotostimulationSeries(name="photosim series", holographic_pattern=hp, unit='SIunit', data=[1, -1, 1, -1], timestamps=[0.5, 1, 2, 4])
        PhotostimulationSeries(name="photosim series", holographic_pattern=hp, unit='SIunit', format='series', data=[0, 0, 0, 1, 1, 0], rate=10.)
        photostim_series = PhotostimulationSeries(name="photosim series", holographic_pattern=hp, unit='SIunit', format='series', stimulus_duration = 0.05,
                                                  data=[0, 0, 0, 1, 1, 0], timestamps=[0, 0.5, 1, 1.5, 3, 6])
        nwb_file = create_NWB_file()
        nwb_file.add_stimulus(photostim_series)
        assert "photosim series" in nwb_file.stimulus



    def test_PhotostimulationSeriesFormatData(self):
        hp = get_holographic_pattern()
        data = [1, -1, 1, -1]
        timestamps=[0.5, 1, 2, 4]
        # PhotostimulationSeries(name="photosim series", holographic_pattern=hp, unit='SIunit', data=data, timestamps=timestamps)

        PhotostimulationSeries(name="photosim series", holographic_pattern=hp, unit='SIunit')
        with self.assertRaises(ValueError):
            PhotostimulationSeries(name="photosim series", holographic_pattern=hp, unit='SIunit', timestamps=timestamps)
        PhotostimulationSeries(name="photosim series", holographic_pattern=hp, unit='SIunit', timestamps=timestamps, data=data)

        data = [1, -1, 1, 2]
        timestamps = [0.5, 1, 2, 4]
        with self.assertRaises(ValueError):
            PhotostimulationSeries(name="photosim series", holographic_pattern=hp, unit='SIunit', data=data, timestamps=timestamps)

        PhotostimulationSeries(name="photosim series", holographic_pattern=hp, unit='SIunit', format='series',
                               data=[0, 0, 0, 1, 1, 0], rate=10.)

        with self.assertRaises(ValueError):
            PhotostimulationSeries(name="photosim series", holographic_pattern=hp, unit='SIunit', format='series',
                               data=[0, 0, 0, 1, 2, 0], rate=10.)



    def test_add_interval(self):
        hp = get_holographic_pattern()

        empty_series = PhotostimulationSeries(name="photosim series", holographic_pattern=hp, unit='SIunit')
        empty_series.add_interval(10, 20)
        empty_series.add_interval(30, 40)
        assert empty_series.data[0] == 1
        assert empty_series.data[3] == -1
        assert len(empty_series.data) == 4

        assert empty_series.timestamps[0] == 10
        assert empty_series.timestamps[1] == 20
        assert len(empty_series.timestamps) == 4

    def test_add_presentation(self):
        hp = get_holographic_pattern()

        ps = PhotostimulationSeries(name="photosim series", holographic_pattern=hp, unit='SIunit', format='series', stimulus_duration=10)
        ps.add_presentation(10)
        ps.add_presentation(20)

        ps = PhotostimulationSeries(name="photosim series", holographic_pattern=hp, unit='SIunit', format='interval', stimulus_duration=2)
        ps.add_presentation(10)
        ps.add_presentation(40)

        with self.assertRaises(ValueError):
            ps = PhotostimulationSeries(name="photosim series", holographic_pattern=hp, unit='SIunit')
            ps.add_presentation(10)

    def test_to_df(self):
        hp = get_holographic_pattern()

        ps = PhotostimulationSeries(name="photosim series", holographic_pattern=hp, unit='SIunit', format='series',
                               data=[0, 0, 0, 1, 1, 0], rate=10., stimulus_duration=4)
        df = ps.to_dataframe()

        ps = PhotostimulationSeries(name="photosim series", holographic_pattern=hp, unit='SIunit',
                                                  format='series', stimulus_duration=0.05,
                                                  data=[0, 0, 0, 1, 1, 0], timestamps=[0, 0.5, 1, 1.5, 3, 6])
        df = ps.to_dataframe()

        ps = PhotostimulationSeries(name="photosim series", holographic_pattern=hp, unit='SIunit', format='interval', stimulus_duration=2)
        ps.add_presentation(10)
        ps.add_presentation(40)

        ps.to_dataframe()


class TestStimulusPresentation(TestCase):
    def test_StimulusPresentationConstructor(self):
        hp = get_holographic_pattern()
        series = get_photostim_series()
        dev = get_photostim_device()
        sp = StimulusPresentation(name='test', description='test desc',
                                  photostimulation_device=dev)  # , stim_method='method', sweeping_method='none')
        sp = StimulusPresentation(name='test', description='test desc', photostimulation_device=dev,
                                  stimulus_method='method', sweeping_method='none')
        sp = StimulusPresentation(name='test', description='test desc', photostimulation_device=dev,
                                  stimulus_method='method')
        print('')

    def test_StimulusPresentation(self):
        hp = self._get_holographic_pattern()
        series = self._get_photostim_series()
        dev = self._get_photostim_device()
        sp = StimulusPresentation(name='test', description='test desc', photostimulation_device=dev)
        sp.add_event_type(label='stim1', stimulus_description='d1', photostimulation_series=series, pattern=hp)
        sp.add_event_type(label='stim2', stimulus_description='d2', photostimulation_series=series, pattern=hp)
        df = sp.to_dataframe()
        print(df)

        # from pynwb import NWBHDF5IO
        #
        # nwbfile = NWBFile(
        #     'my first synthetic recording',
        #     'EXAMPLE_ID',
        #     datetime.now(tzlocal()),
        # )
        #
        # nwbfile.add_acquisition(sp)
        # with NWBHDF5IO("basics_tutorial.nwb", "w") as io:
        #     io.write(series)
        #     io.write(hp)
        #     io.write(nwbfile)
        #
        # with NWBHDF5IO("basics_tutorial.nwb", "r", load_namespaces=True) as io:
        #     read_nwbfile = io.read()
        #     print(read_nwbfile)


class TestExtension(TestCase):

    def setUp(self):
        self.nwb_file = NWBFile(session_description='test file', identifier='EXAMPLE_ID', session_start_time=datetime.now(tzlocal()))

    def test_SpatialLightModulator(self):
        slm = self._get_SLM()
        print(slm)

        with self.assertRaises(ValueError):
            SpatialLightModulator(name="slm", dimensions=np.array([[1, 2], [3, 4]]))

        self.nwb_file.add_acquisition(slm)
        with NWBHDF5IO("basics_tutorial.nwb", "w") as io:
            io.write(slm)

        with NWBHDF5IO("basics_tutorial.nwb", "r", load_namespaces=True) as io:
            read_nwbfile = io.read()

    def test_PhotostimulationDevice(self):
        photostim_dev = self._get_photostim_device()

        self.nwb_file.add_device(photostim_dev)
        assert "photostim_dev" in self.nwb_file.devices

        slm = self._get_SLM()
        photostim_dev = PhotostimulationDevice(name="photostim_dev", description="photostim_device", type='LED',
                                                     wavelength=320, slm=slm, opsin='test_opsin', peak_pulse_power=20,
                                               power=10, pulse_rate = 5)
        assert hasattr(photostim_dev, "slm")

        with NWBHDF5IO("basics_tutorial.nwb", "w") as io:
            io.write(self.nwb_file)

        with NWBHDF5IO("basics_tutorial.nwb", "r", load_namespaces=True) as io:
            read_nwbfile = io.read()

            read_dev = read_nwbfile.get_device('photostim_dev')
            assert read_dev.slm.name == slm.name
            assert all(read_dev.slm.dimensions == slm.dimensions)

            assert read_dev.name == photostim_dev.name
            assert read_dev.description == photostim_dev.description
            assert read_dev.type == photostim_dev.type
            assert read_dev.wavelength == photostim_dev.wavelength

    def test_PhotostimulationDeviceMethods(self):
        slm = self._get_SLM()
        photostim_dev = PhotostimulationDevice(name="photostim_dev", description="photostim_device", type='LED',
                                               wavelength=320)

        photostim_dev.add_slm(slm)
        assert photostim_dev.slm is not None

        with self.assertRaises(ValueError):
            photostim_dev.add_slm(slm)

    def test_HolographicPatternConstructionMaskROI(self):
        mask_roi = self._create_mask_roi()
        HolographicPattern(name='HolographicPattern', mask_roi=mask_roi, stimulation_diameter=5)

        HolographicPattern(name='HolographicPattern', mask_roi=np.round(np.random.rand(5, 5)), stimulation_diameter=5)
        HolographicPattern(name='HolographicPattern', mask_roi=np.round(np.random.rand(5, 5, 5)),
                           stimulation_diameter=5)

        with self.assertRaises(ValueError):
            HolographicPattern(name='HolographicPattern', mask_roi=np.round(np.random.rand(5)),
                                stimulation_diameter=5)

        with self.assertRaises(ValueError):
            HolographicPattern(name='HolographicPattern', mask_roi=np.round(np.random.rand(5, 5, 5, 5)),
                                stimulation_diameter=5)

        hp = HolographicPattern(name='HolographicPattern', mask_roi=np.round(np.random.rand(5, 5)), stimulation_diameter=5)
        assert hp.dimension == (5, 5)

        with self.assertRaises(ValueError):
            HolographicPattern(name='HolographicPattern', mask_roi=np.round(np.random.rand(5, 5)), stimulation_diameter=5, dimension=(5, 10))

        # Check mask_roi validation
        with self.assertRaises(ValueError):
            HolographicPattern(name='HolographicPattern', mask_roi=np.random.rand(5, 5)*10, stimulation_diameter=5)

        with self.assertRaises(ValueError):
            HolographicPattern(name='HolographicPattern', mask_roi=np.random.rand(5, 5) * -1, stimulation_diameter=5)

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



    @staticmethod
    def _create_pixel_roi():

        pixel_roi = []

        for i in range(5):
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

        hp = HolographicPattern(name='HolographicPattern', mask_roi=mask_roi)

        photostim_series = PhotostimulationSeries(name="photostim_series", pattern=hp, unit='SIunit',
                                                  data=[1, -1, 1, -1],
                                                  timestamps=[0.5, 1, 2, 4])
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

