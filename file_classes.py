import pandas as pd
from pynwb import register_class, load_namespaces
from pynwb.core import NWBContainer, NWBDataInterface
from pynwb.base import TimeSeries
from collections.abc import Iterable
from pynwb.device import  Device
from hdmf.utils import docval, popargs, get_docval, popargs_to_dict
from pynwb.core import DynamicTable, VectorData
import numpy as np
from hdmf.utils import docval, getargs, popargs, popargs_to_dict, get_docval, call_docval_func
import warnings
from pynwb.io.core import NWBContainerMapper
from pynwb import register_map
from pynwb.base import TimeSeries, TimeSeriesReferenceVectorData, TimeSeriesReference
from pynwb.file import MultiContainerInterface, NWBContainer
from hdmf.build import ObjectMapper
from hdmf.common.io.table import DynamicTableMap
import matplotlib.pyplot as plt
from pynwb import NWBFile
from pynwb.epoch import  TimeIntervals

ns_path = "test.namespace.yaml"
load_namespaces(ns_path)

namespace = 'test'
@register_class('SpatialLightModulator', namespace)
class SpatialLightModulator(Device):
    """
    Spatial light modulator used in photostimulation.
    """

    __nwbfields__ = ('size',)

    @docval(*get_docval(Device.__init__) ,
        {'name': 'size', 'type': Iterable, 'doc': 'Resolution of SpatialLightModulator (in pixels), formatted as ([width, height]).', 'default': None,
         'shape': ((2,), (3,))}
    )
    def __init__(self, **kwargs):
        size = popargs('size', kwargs)
        super().__init__(**kwargs)
        self.size = size


@register_class('PhotostimulationDevice', namespace)
class PhotostimulationDevice(Device):
    """
    Device used in photostimulation.
    """

    __nwbfields__ = ({'name': 'slm', 'child': True}, 'type', 'wavelength','opsin', 'peak_pulse_power', 'power', 'pulse_rate')

    @docval(*get_docval(Device.__init__) + (
        {'name': 'type', 'type': str, 'doc': 'Type of stimulation (laser or LED)'},
        {'name': 'slm', 'type': SpatialLightModulator, 'doc': 'Spatial light modulator used with device.', 'default': None},
        {'name': 'wavelength', 'type': (int, float), 'doc': 'Excitation wavelength of stimulation light (nanometers).', 'default': None},
        {'name': 'opsin', 'type': str, 'doc': 'Type of opsin used for photoactivation.', 'default': None},
        {'name': 'peak_pulse_power', 'type': (int, float), 'doc': 'Peak pulse power (J)', 'default': None},
        {'name': 'power', 'type': (int, float), 'doc': 'Power (in milliwatts)', 'default': None},
        {'name': 'pulse_rate', 'type': (int, float), 'doc': 'Pulse rate (Hz)', 'default': None}
    ))
    def __init__(self, **kwargs):
        keys_to_set = ('slm', 'type', 'wavelength', 'opsin', 'peak_pulse_power', 'power', 'pulse_rate')
        args_to_set = popargs_to_dict(keys_to_set, kwargs)
        super().__init__(**kwargs)

        for key, val in args_to_set.items():
            setattr(self, key, val)

    @docval({'name': 'slm', 'type': SpatialLightModulator, 'doc': 'spatial light modulator'})
    def add_slm(self, slm):
        '''
        Add a spatial light modulator to the photostimulation device.
        '''

        if self.slm is not None:
            raise ValueError("SpatialLightMonitor already exists in this device")
        else:
            self.slm = slm

@register_class('HolographicPattern', namespace)
class HolographicPattern(NWBContainer):
    '''
    Holographic pattern.
    '''

    __nwbfields__ = ('pixel_roi', 'image_mask_roi', 'ROI_size', 'dimension')

    @docval(*get_docval(NWBContainer.__init__) + (
            {'name': 'pixel_roi', 'type': 'array_data', 'doc': 'pixel_mask ([x1, y1]) or voxel_mask ([x1, y1, z1])', 'default': None, 'shape': ((None, 2), (None, 3))},
            {'name': 'image_mask_roi', 'type': 'array_data', 'doc': 'image with the same size of image where positive values mark this ROI', 'default': None, 'shape': ([None]*2, [None]*3)},
            {'name': 'ROI_size', 'type': (int, float, Iterable), 'doc': 'diameter of stimulation (pixels)', 'default': None},
            {'name': 'dimension', 'type': Iterable, 'doc': 'Number of pixels on x, y, (and z) axes.', 'default': None, 'shape': ((2,), (3,))}
    ))
    def __init__(self, **kwargs):
        keys_to_set = ("pixel_roi", "image_mask_roi", "ROI_size", "dimension")
        args_to_set = popargs_to_dict(keys_to_set, kwargs)

        roi_size = args_to_set['ROI_size']
        if isinstance(roi_size, Iterable):
            if len(roi_size) != 2 and len(roi_size) != 3:
                raise ValueError("ROI_size must be a scalar, a 2D iterable, or a 3D iterable")

        super().__init__(**kwargs)

        if args_to_set['pixel_roi'] is None and args_to_set['image_mask_roi'] is None:
            raise TypeError("Must provide 'pixel_roi' or 'image_mask_roi' when constructing HolographicPattern")

        if args_to_set['dimension'] is not None and isinstance(args_to_set['dimension'], list):
            args_to_set['dimension'] = tuple(args_to_set['dimension'])

        if args_to_set['pixel_roi'] is not None:
            if args_to_set['ROI_size'] is None:
                raise TypeError("'ROI_size' must be specified when using a pixel mask")

            if args_to_set['dimension'] is None:
                raise TypeError("'dimension' must be specified when using a pixel mask")


        if args_to_set['image_mask_roi'] is not None:
            mask_dim = args_to_set['image_mask_roi'].shape

            if args_to_set['dimension'] is None:
                args_to_set['dimension'] = mask_dim

            if len(np.setdiff1d(np.unique((args_to_set['image_mask_roi'].astype(int))), np.array([0, 1]))) > 0:
                    raise ValueError("'image_mask_roi' data must be either -1 (offset) or 1 (onset)")

        for key, val in args_to_set.items():
            setattr(self, key, val)

    def show_mask(self):
        if len(self.dimension) == 3:
            raise ValueError("Cannot display 3D masks")

        if self.pixel_roi is not None:
            center_points = [[roi[0], roi[1]] for roi in self.pixel_roi]
            center_points = np.array(center_points)
            image_mask_roi = self.pixel_to_image_mask_roi()
            plt.imshow(image_mask_roi, 'gray', interpolation='none')
            plt.scatter(center_points[:, 0], center_points[:, 1], color='red', s=10)

        if self.image_mask_roi is not None:
            image_mask_roi = self.image_mask_roi
            plt.imshow(image_mask_roi, 'gray', interpolation='none')

        plt.axis('off')
        plt.show()

    # @staticmethod
    # def _create_circular_mask(img_width, img_height, center, diameter, img_depth=None):
    #
    #     if img_depth is None:
    #         X, Y = np.ogrid[:img_width, :img_height]
    #         dist_from_center = np.sqrt((X - center[0]) ** 2 + (Y - center[1]) ** 2)
    #     else:
    #         X, Y, Z = np.ogrid[:img_width, :img_height, :img_depth]
    #         dist_from_center = np.sqrt((X - center[0]) ** 2 + (Y - center[1]) ** 2 + (Z - center[2]) ** 2)
    #
    #     mask = dist_from_center <= diameter/2
    #     return mask

    @staticmethod
    def _create_circular_mask(dimensions, center, diameter):
        Y, X = np.ogrid[:dimensions[1], :dimensions[0]]
        dist_from_center = np.sqrt((X - center[0]) ** 2 + (Y - center[1]) ** 2)

        mask = dist_from_center <= diameter/2
        return mask

    @staticmethod
    def _create_rectangular_mask(dimensions, center, roi_size, img_depth=None):

        if img_depth is None:
            Y, X = np.ogrid[:dimensions[1], :dimensions[0]]
            X_dist_from_center = (X - center[0])
            Y_dist_from_center = (Y - center[1])
            mask = (np.abs(X_dist_from_center) <= roi_size[0] / 2) & (np.abs(Y_dist_from_center) <= roi_size[1] / 2)
        return mask

    def pixel_to_image_mask_roi(self):
        if len(self.dimension) == 3:
            raise ValueError("Cannot convert 3D pixel_roi to image_mask_roi")

        mask = np.zeros(shape=self.dimension)
        for roi in self.pixel_roi:

            if not isinstance(self.ROI_size, Iterable):
                tmp_mask = self._create_circular_mask(self.dimension, roi, self.ROI_size)
            else:
                tmp_mask = self._create_rectangular_mask(self.dimension, roi, self.ROI_size)
            mask[tmp_mask] = 1

        return mask

    @staticmethod
    def image_to_pixel(image_mask):
        """Converts an image_mask of a ROI into a pixel_mask"""
        pixel_mask = []
        it = np.nditer(image_mask, flags=['multi_index'])
        while not it.finished:
            weight = it[0][()]
            if weight > 0:
                x = it.multi_index[0]
                y = it.multi_index[1]
                pixel_mask.append([x, y, 1])
            it.iternext()
        return pixel_mask

@register_map(HolographicPattern)
class HolographicPatternMap(NWBContainerMapper):

    def __init__(self, spec):
        super().__init__(spec)
        pixel_roi_spec = self.spec.get_dataset('pixel_roi')
        self.map_spec('ROI_size', pixel_roi_spec.get_attribute('ROI_size'))

@register_class('PhotostimulationSeries', namespace)
class PhotostimulationSeries(TimeSeries):

    __nwbfields__ = ({'name': 'holographic_pattern', 'child': True}, 'format', 'stimulus_duration', 'field_of_view', {'name': 'unit', 'settable': False})

    @docval(*get_docval(TimeSeries.__init__, 'name'),
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries), 'shape': (None,),
             'doc': 'The data values over time. Must be 1D.', 'default': None},
            {'name': 'timestamps', 'type': ('array_data', 'data', TimeSeries), 'shape': (None,),
             'doc': 'Timestamps corresponding to data.', 'default': None},
            {'name': 'holographic_pattern', 'type': HolographicPattern, 'doc': 'photostimulation pattern'},
            {'name': 'format', 'type': str, 'doc': 'name', 'default': 'interval'},
             {'name': 'stimulus_duration', 'type': (int, float), 'doc': 'name', 'default': None},
             {'name': 'field_of_view', 'type': (int, float), 'doc': 'diameter of stimulation (pixels)', 'default': None},
            {'name': 'unit', 'type': str, 'doc': 'unit of time', 'default': 'seconds'},
            *get_docval(TimeSeries.__init__, 'resolution', 'conversion',  'starting_time', 'rate',
                        'comments', 'description', 'control', 'control_description', 'offset')
    )
    def __init__(self, **kwargs):
        self.__interval_data = kwargs['data']
        self.__interval_timestamps = kwargs['timestamps']

        kwargs['format'] = kwargs['format'].lower()
        if kwargs['format'] not in ['interval', 'series']:
            raise ValueError("'format' must be one of 'interval' or 'series'")

        # Convert data to np array
        if isinstance(kwargs['data'], (list, tuple)):
            kwargs['data'] = np.array(kwargs['data'])

        if isinstance(kwargs['timestamps'], (list, tuple)):
            kwargs['timestamps'] = np.array(kwargs['timestamps'])


        # If using interval format...
        if kwargs['format'] == 'interval':
            if kwargs['data'] is None:
                kwargs['data'] = np.array([])

                if kwargs['timestamps'] is not None:
                    raise ValueError("'timestamps' can't be specified without corresponding 'data'")

                kwargs['timestamps'] = np.array([])
            # if intervals are input, check that formatted correctly
            else:
                # check that timestamps are also input
                if kwargs['timestamps'] is None:
                    raise ValueError("Need to specify corresponding 'timestamps' for each entry in 'data'")

                # check data and timestamps are same length
                if len(kwargs['data']) != len(kwargs['timestamps']):
                    raise ValueError("'data' and 'timestamps' need to be the same length")

                if len(np.setdiff1d(np.unique((kwargs['data'].astype(int))), np.array([-1, 1]))) > 0:
                    raise ValueError("'interval' data must be either -1 (offset) or 1 (onset)")

        # if using series format
        if kwargs['format'] == 'series':
            if kwargs['stimulus_duration'] is None:
                raise ValueError("if 'format' is 'series', 'stimulus_duration' must be specified")

            if kwargs['data'] is None:
                kwargs['data'] = np.array([])

                if kwargs['timestamps'] is not None:
                    raise ValueError("'timestamps' can't be specified without corresponding 'data'")

                kwargs['timestamps'] = np.array([])
            else:
                if kwargs['timestamps'] is None and kwargs['rate'] is None:
                    raise ValueError("either 'timestamps' or 'rate' must be specified")

            if kwargs['timestamps'] is not None:
                # check data and timestamps are same length
                if len(kwargs['data']) != len(kwargs['timestamps']):
                    raise ValueError("'data' and 'timestamps' need to be the same length")

                if len(np.setdiff1d(np.unique((kwargs['data'].astype(int))), np.array([0, 1]))) > 0:
                    raise ValueError("'series' data must be either 0 or 1")

        keys_to_set = ('holographic_pattern',  'format', 'stimulus_duration', 'field_of_view')
        args_to_set = popargs_to_dict(keys_to_set, kwargs)

        self.__interval_data = kwargs['data']
        self.__interval_timestamps = kwargs['timestamps']
        kwargs['unit'] = 'seconds'

        super().__init__(**kwargs)

        for key, val in args_to_set.items():
            setattr(self, key, val)

        self.__interval_timestamps = self.timestamps
        self.__interval_data = self.data



    @docval({'name': 'start', 'type': (int, float), 'doc': 'The start time of the interval'},
            {'name': 'stop', 'type': (int, float), 'doc': 'The stop time of the interval'})
    def add_interval(self, **kwargs):
        '''

        '''
        start, stop = getargs('start', 'stop', kwargs)
        if self.format == 'series':
            raise ValueError("Cannot add interval to PhotostimulationSeries with 'format' of 'series'")

        self.__interval_data = np.append(self.__interval_data, 1)
        self.__interval_data = np.append(self.__interval_data, -1)
        self.__interval_timestamps = np.append(self.__interval_timestamps, start)
        self.__interval_timestamps = np.append(self.__interval_timestamps, stop)

    def to_dataframe(self):
        '''

        '''
        data = self.data
        ts = self.timestamps

        if len(data) == 0:
            raise ValueError("No data")

        if ts is None:
            # end = self.starting_time + self.stimulus_duration * (len(data)-1)
            end = self.starting_time + (1/self.rate) * (len(data) - 1)
            ts = np.linspace(self.starting_time, end, num=len(data), endpoint=True)

        df_dict = {'data': data, 'timestamps': ts}
        df = pd.DataFrame(df_dict)
        return df

    @docval({'name': 'timestamp', 'type': (int, float, Iterable), 'doc': 'The start time of the interval'})
    def add_onset(self, **kwargs):
        '''
        Add new presentation of stimulus at time 'timestamp', denoting the onset of stimulation from time 'timestamp'
        for a length of self.stimulus_duration.
        '''
        if self.stimulus_duration is None:
            raise ValueError("Cannot add presentation to PhotostimulationSeries without 'stimulus_duration'")

        timestamps = getargs('timestamp', kwargs)

        if not isinstance(timestamps, Iterable):
            timestamps = [timestamps]

        for ts in timestamps:
            if self.format == 'interval':
                self.add_interval(ts, ts+self.stimulus_duration)
            else:
                self.__interval_data = np.append(self.__interval_data, 1)
                self.__interval_timestamps = np.append(self.__interval_timestamps, ts)


    def get_starting_time(self):
        if self.starting_time is not None:
            return self.starting_time

        if self.timestamps is None:
            return self.timestamps[0]

        if len(self.data) != 0:
            return 0

        return np.nan

    def get_end_time(self):
        if len(self.data) == 0:
            return np.nan

        if self.timestamps is None:
            end = self.get_starting_time() + self.stimulus_duration * (len(self.data)-1)
            return end

        return self.timestamps[-1]

    @property
    def data(self):
        return self.__interval_data

    @property
    def timestamps(self):
        return self.__interval_timestamps

    @staticmethod
    def _format_data_series(ts_data):
        """Convert a list/tuple of integer label indices to a numpy array of unsigned integers. Raise error if negative
                or non-numeric values are found. If something other than a list/tuple/np.ndarray of ints or unsigned ints
                is provided, return the original array.
                """

        if ts_data is None or len(ts_data) == 0:
            return ts_data

        if isinstance(ts_data, (list, tuple)):
            ts_data = np.array(ts_data)

        ts_data = ts_data.astype(np.int8)
        diff = np.setdiff1d(np.unique(ts_data), [0, 1])

        if len(diff) > 0:
            raise ValueError("'Series' data must be either -1 (offset) or 1 (onset)")

        return ts_data

    @staticmethod
    def _format_data_interval(ts_data):
        """Convert a list/tuple of integer label indices to a numpy array of unsigned integers. Raise error if negative
                or non-numeric values are found. If something other than a list/tuple/np.ndarray of ints or unsigned ints
                is provided, return the original array.
                """

        if ts_data is None or len(ts_data) == 0:
            return ts_data

        if isinstance(ts_data, (list, tuple)):
            ts_data = np.array(ts_data)

        ts_data = ts_data.astype(np.int8)
        diff = np.setdiff1d(np.unique(ts_data), [-1, 1])

        if len(diff) > 0:
            raise ValueError("'Interval' data must be either -1 (offset) or 1 (onset)")

        return ts_data


@register_class('PhotostimulationTable', namespace)
class PhotostimulationTable(TimeIntervals):
    """
    Table for storing Epoch data
    """

    __fields__ = ( 'photostimulation_device', "stimulus_method", "sweeping_method", "time_per_sweep", "num_sweeps")
    # __fields__ = ({'name': 'photostimulation_device', 'child': True}, "stimulus_method", "sweeping_method", "time_per_sweep", "num_sweeps")

    __columns__ = (
        {'name': 'label', 'description': 'Start time of epoch, in seconds', 'required': True},
        {'name': 'start_time', 'description': 'Stop time of epoch, in seconds', 'required': True},
        {'name': 'stop_time', 'description': 'Stop time of epoch, in seconds', 'required': True},
        {'name': 'series_name', 'description': 'Stop time of epoch, in seconds', 'required': True},
        {'name': 'pattern_name', 'description': 'Stop time of epoch, in seconds', 'required': True},
        {'name': 'photostimulation_series', 'description': 'Stop time of epoch, in seconds', 'required': True},
    )

    @docval(*get_docval(TimeIntervals.__init__),
            # {'name': 'name', 'type': str, 'doc': 'name of this TimeIntervals'},  # required
            # {'name': 'description', 'type': str, 'doc': 'Description of this TimeIntervals'},
            {'name': 'photostimulation_device', 'type': PhotostimulationDevice, 'doc': 'photostimulation device', 'default': None},
            {'name': 'stimulus_method', 'type': str, 'doc': 'Description of this TimeIntervals', 'default': None},
            {'name': 'sweeping_method', 'type': str, 'doc': 'Description of this TimeIntervals', 'default': None},
            {'name': 'time_per_sweep', 'type': (int, float), 'doc': 'Description of this TimeIntervals', 'default': None},
            {'name': 'num_sweeps', 'type': (int, float), 'doc': 'Description of this TimeIntervals', 'default': None},
            # *get_docval(DynamicTable.__init__, 'id', 'columns', 'colnames')
            )
    def __init__(self, **kwargs):
        keys_to_set = ("photostimulation_device", "stimulus_method", "sweeping_method", "time_per_sweep", "num_sweeps")
        # keys_to_set = ( "stimulus_method", "sweeping_method", "time_per_sweep", "num_sweeps")
        args_to_set = popargs_to_dict(keys_to_set, kwargs)

        super().__init__(**kwargs)

        for key, val in args_to_set.items():
            setattr(self, key, val)

    # @docval(*get_docval(TimeIntervals.add_interval),
    #     {'name': 'label', 'type': str, 'doc': 'name of this TimeIntervals', 'default': None},
    #         {'name': 'stimulus_description', 'type': (str, list), 'doc': 'name of this TimeIntervals', 'default':''},
    #         # {'name': 'start', 'type': (int, float), 'doc': 'name of this TimeIntervals', 'default': None},
    #         # {'name': 'end', 'type': (int, float), 'doc': 'name of this TimeIntervals', 'default': None},
    #         {'name': 'photostimulation_series', 'type': PhotostimulationSeries, 'doc': 'name of this TimeIntervals'},
    #         {'name': 'holographic_pattern', 'type':  HolographicPattern, 'doc': 'name of this TimeIntervals'},
    #         allow_extra=True
    # )


    def add_series(self, photostimulation_series, **kwargs):
        """Add an event type as a row to this table."""

        if not isinstance(photostimulation_series, Iterable):
            photostimulation_series = [photostimulation_series]

        for i, series in enumerate(photostimulation_series):
            new_args = {}
            new_args['label'] = f"series_{i}"
            new_args['series_name'] = series.name
            new_args['start_time'] = float(series.get_starting_time())
            new_args['stop_time'] = float(series.get_end_time())
            new_args['pattern_name'] = series.holographic_pattern.name
            new_args['photostimulation_series'] = series
            super().add_interval(**new_args)

