from pynwb import register_class, load_namespaces
from pynwb.core import NWBContainer, NWBDataInterface
from pynwb.base import TimeSeries
from collections.abc import Iterable
from pynwb.device import  Device
from hdmf.utils import docval, popargs, get_docval, popargs_to_dict
from pynwb.core import DynamicTable, VectorData
import numpy as np
from hdmf.utils import docval, getargs, popargs, popargs_to_dict, get_docval
import warnings

ns_path = "test.namespace.yaml"
load_namespaces(ns_path)

@register_class('SpatialLightModulator', 'test')
class SpatialLightModulator(NWBContainer):
    """
    Spatial light modulator class.
    """

    __nwbfields__ = ('dimensions',)

    @docval(
        {'name': 'name', 'type': str, 'doc': 'name of spatial light modulator'},
        {'name': 'dimensions', 'type': Iterable, 'doc': 'dimensions ([w, h] or [w, h, d]) of SLM field'}
    )
    def __init__(self, **kwargs):
        dimensions = popargs('dimensions', kwargs)
        super().__init__(**kwargs)
        self.dimensions = dimensions

@register_class('PhotostimulationDevice', 'test')
class PhotostimulationDevice(Device):
    """
    Device used in photostimulation.
    """

    __nwbfields__ = ('type', 'wavelength', 'slm')

    @docval(*get_docval(Device.__init__) + (
        {'name': 'type', 'type': str, 'doc': 'type of stimulation (laser or LED)', 'default': None},
        {'name': 'wavelength', 'type': float, 'doc': 'wavelength of photostimulation', 'default': None},
        {'name': 'slm', 'type': SpatialLightModulator, 'doc': 'spatial light modulator', 'default': None}
    ))
    def __init__(self, **kwargs):
        keys_to_set = ("type",
                       "wavelength",
                       "slm")
        args_to_set = popargs_to_dict(keys_to_set, kwargs)
        super().__init__(**kwargs)

        for key, val in args_to_set.items():
            setattr(self, key, val)

@register_class('ImagingPlane', 'test')
class ImagingPlane(NWBContainer):
    '''
    Imaging plane.
    '''

    __nwbfields__ = ('device', 'opsin', 'peak_pulse_power', 'power', 'pulse_rate')

    @docval(*get_docval(NWBContainer.__init__) + (
        {'name': 'device', 'type': PhotostimulationDevice, 'doc': 'photostimulation device'},
        {'name': 'opsin', 'type': str, 'doc': 'opsin used', 'default': None},
        {'name': 'peak_pulse_power', 'type': (int, float), 'doc': 'peak pulse power (J)', 'default': None},
        {'name': 'power', 'type': (int, float), 'doc': 'power (in milliwatts)', 'default': None},
        {'name': 'pulse_rate', 'type': (int, float), 'doc': 'pulse rate (Hz)', 'default': None}
        ))
    def __init__(self, **kwargs):
        keys_to_set = ("device", "opsin", "peak_pulse_power", "power", "pulse_rate")
        args_to_set = popargs_to_dict(keys_to_set, kwargs)
        super().__init__(**kwargs)

        for key, val in args_to_set.items():
            setattr(self, key, val)

@register_class('HolographicPattern', 'test')
class HolographicPattern(NWBContainer):
    '''
    Holographic pattern.
    '''

    __nwbfields__ = ('pixel_roi', 'mask_roi', 'stimulation_diameter', 'dimension')

    @docval(*get_docval(NWBContainer.__init__) + (
            {'name': 'pixel_roi', 'type': Iterable, 'doc': 'pixel_mask ([x1, y1]) or voxel_mask ([x1, y1, z1])', 'default': None},
            {'name': 'mask_roi', 'type': Iterable, 'doc': 'image with the same size of image where positive values mark this ROI', 'default': None},
            {'name': 'stimulation_diameter', 'type': (int, float), 'doc': 'diameter of stimulation (pixels)',
             'default': None},
            {'name': 'dimension', 'type': Iterable, 'doc': 'Number of pixels on x, y, (and z) axes.', 'default': None}
    ))
    def __init__(self, **kwargs):
        keys_to_set = ("pixel_roi", "mask_roi", "stimulation_diameter", "dimension")
        args_to_set = popargs_to_dict(keys_to_set, kwargs)

        super().__init__(**kwargs)
        for key, val in args_to_set.items():
            setattr(self, key, val)

        if self.pixel_roi is not None and self.stimulation_diameter is None:
            raise TypeError("'pixel_roi' & 'stimulation_diameter' OR 'roi_mask' must be specified")

        if self.pixel_roi is not None and self.dimension is None:
            raise ValueError("If providing 'image_mask', must supply 'dimension' when defining 'HolographicPattern'")

        if self.dimension is None and self.mask_roi is not None:
            self.dimension = np.array(self.mask_roi).shape

    def pixel_to_image(self, pixel_mask):
        """Converts a 2D pixel_mask of a ROI into an image_mask."""
        image_matrix = np.zeros(self.dimension)
        npmask = np.asarray(pixel_mask)

        x_coords = npmask[:, 0].astype(np.int32)
        y_coords = npmask[:, 1].astype(np.int32)
        if len(self.dimension) == 2:
            image_matrix[y_coords, x_coords] = 1
        else:
            z_coords = npmask[:, 2].astype(np.int32)
            image_matrix[y_coords, x_coords, z_coords] = 1

        return image_matrix

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

    @docval({'name': 'description', 'type': str, 'doc': 'a brief description of what the region is'},
            {'name': 'region', 'type': (slice, list, tuple), 'doc': 'the indices of the table', 'default': slice(None)},
            {'name': 'name', 'type': str, 'doc': 'the name of the ROITableRegion', 'default': 'rois'})
    def create_roi_table_region(self, **kwargs):
        return self.create_region(**kwargs)

@register_class('PhotostimulationSeries', 'test')
class PhotostimulationSeries(TimeSeries):

    __nwbfields__ = ('pattern', 'field_of_view')

    @docval({'name': 'name', 'type': str, 'doc': 'name'},
             {'name': 'data', 'type': ('array_data', 'data'), 'doc': 'name', 'default': None},
             {'name': 'format', 'type': str, 'doc': 'name', 'default': 'interval'},
             {'name': 'stimulus_duration', 'type': (int, float), 'doc': 'name', 'default': None},
             {'name': 'pattern', 'type': HolographicPattern, 'doc': 'photostimulation pattern'},
             {'name': 'field_of_view', 'type': (int, float), 'doc': 'diameter of stimulation (pixels)', 'default': None},
             {'name': 'timestamps', 'type': ('array_data', 'data'), 'doc': 'name', 'default': None},
            *get_docval(TimeSeries.__init__, 'unit', 'resolution', 'conversion', 'offset', 'starting_time',
                  'rate', 'comments', 'description', 'control', 'control_description', 'continuity')
    )
    def __init__(self, **kwargs):
        keys_to_set = ("pattern", "field_of_view", "format", "stimulus_duration")
        args_to_set = popargs_to_dict(keys_to_set, kwargs)

        if args_to_set['format'] not in ['interval', 'series']:
            raise ValueError("'format' must be one of 'interval' or 'series'")

        if args_to_set['format'] == 'series' and kwargs['data'] is None:
            raise ValueError("if 'format' is 'series', 'data' must be specified")

        # if using interval format...
        if args_to_set['format'] == 'interval':

            # if no intervals input, set data to empty array and create empty timestamps array
            if kwargs['data'] is None:
                kwargs['data'] = np.zeros(0)

                if kwargs['timestamps'] is not None:
                    raise ValueError("'timestamps' can't be specified without corresponding 'data'")

                kwargs['timestamps'] = np.zeros(0)
            # if intervals are input, check that formatted correctly
            else:

                # check that timestamps are also input
                if kwargs['timestamps'] is None:
                    raise ValueError("need to specify corresponding 'timestamps' for each entry in 'data'")

                # check data and timestamps are same length
                if len(kwargs['data']) != len(kwargs['timestamps']):
                    raise ValueError("'data' and 'timestamps' need to be the same length")

                # check that data only consists of -1s and 1s (stim off/on)
                for stim in kwargs['data']:
                    if stim not in [-1, 1]:
                        raise ValueError("interval data needs to be only a -1 or 1")

            if args_to_set['stimulus_duration'] is not None:
                warnings.warn("'stimulus_duration' should not be specified for 'PhotostimulationSeries' with interval format. Overriding.")
                args_to_set['stimulus_duration'] = None

        # if args_to_set['format'] == 'series'

        super().__init__(**kwargs)

        for key, val in args_to_set.items():
            setattr(self, key, val)

        self.format = self.format.lower()

        if self.format == 'series' and self.stimulus_duration is None:
            raise ValueError("'stimulus_duration' must be specified when 'format' is 'series'")

    @docval({'name': 'start', 'type': (int, float), 'doc': 'The start time of the interval'},
            {'name': 'stop', 'type': (int, float), 'doc': 'The stop time of the interval'})
    def add_interval(self, **kwargs):
        start, stop = getargs('start', 'stop', kwargs)
        if self.format == 'series':
            raise ValueError("Cannot add interval to PhotostimulationSeries with 'format' of 'series'")

        self.data.append(1)
        self.data.append(-1)
        self.timestamps.append(start)
        self.timestamps.append(stop)

