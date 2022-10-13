from pynwb import register_class, load_namespaces
from pynwb.core import NWBContainer, NWBDataInterface
from pynwb.base import TimeSeries
from collections.abc import Iterable
from pynwb.device import  Device
from hdmf.utils import docval, popargs, get_docval, popargs_to_dict
from pynwb.core import DynamicTable, VectorData
import numpy as np

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
        {'name': 'slm', 'type': SpatialLightModulator, 'doc': 'spatial light modulator', 'default': None},
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

    # __nwbfields__ = ('device', 'roi_coordinates', 'stimulation_diameter')

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

    '''
    #
    # __columns__ = (
    #     {'name': 'image_mask', 'description': 'Image masks for each ROI'},
    #     {'name': 'pixel_mask', 'description': 'Pixel masks for each ROI', 'index': True},
    #     {'name': 'voxel_mask', 'description': 'Voxel masks for each ROI', 'index': True}
    # )

    @docval(*get_docval(DynamicTable.__init__))
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @docval({'name': 'pixel_mask', 'type': 'array_data', 'default': None,
             'doc': 'pixel mask for 2D ROIs: [(x1, y1, weight1), (x2, y2, weight2), ...]',
             'shape': (None, 3)},
            {'name': 'voxel_mask', 'type': 'array_data', 'default': None,
             'doc': 'voxel mask for 3D ROIs: [(x1, y1, z1, weight1), (x2, y2, z2, weight2), ...]',
             'shape': (None, 4)},
            {'name': 'image_mask', 'type': 'array_data', 'default': None,
             'doc': 'image with the same size of image where positive values mark this ROI',
             'shape': [[None]*2, [None]*3]},
            {'name': 'id', 'type': int, 'doc': 'the ID for the ROI', 'default': None},
            allow_extra=True)
    def add_roi(self, **kwargs):
        """Add a Region Of Interest (ROI) data to this"""
        pixel_mask, voxel_mask, image_mask = popargs('pixel_mask', 'voxel_mask', 'image_mask', kwargs)
        if image_mask is None and pixel_mask is None and voxel_mask is None:
            raise ValueError("Must provide 'image_mask' and/or 'pixel_mask'")
        rkwargs = dict(kwargs)
        if image_mask is not None:
            rkwargs['image_mask'] = image_mask
        if pixel_mask is not None:
            rkwargs['pixel_mask'] = pixel_mask
        if voxel_mask is not None:
            rkwargs['voxel_mask'] = voxel_mask
        return super().add_row(**rkwargs)

    @staticmethod
    def pixel_to_image(pixel_mask):
        """Converts a 2D pixel_mask of a ROI into an image_mask."""
        image_matrix = np.zeros(np.shape(pixel_mask))
        npmask = np.asarray(pixel_mask)
        x_coords = npmask[:, 0].astype(np.int32)
        y_coords = npmask[:, 1].astype(np.int32)
        weights = npmask[:, -1]
        image_matrix[y_coords, x_coords] = weights
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
                pixel_mask.append([x, y, weight])
            it.iternext()
        return pixel_mask

    @docval({'name': 'description', 'type': str, 'doc': 'a brief description of what the region is'},
            {'name': 'region', 'type': (slice, list, tuple), 'doc': 'the indices of the table', 'default': slice(None)},
            {'name': 'name', 'type': str, 'doc': 'the name of the ROITableRegion', 'default': 'rois'})
    def create_roi_table_region(self, **kwargs):
        return self.create_region(**kwargs)

@register_class('PhotostimulationSeries', 'test')
class PhotostimulationSeries(TimeSeries):

    @docval(*get_docval(TimeSeries.__init__) + (
        {'name': 'pattern', 'type': HolographicPattern, 'doc': 'photostimulation pattern'},
        {'name': 'field_of_view', 'type': (int, float), 'doc': 'diameter of stimulation (pixels)', 'default': None},
        ))
    def __init__(self, **kwargs):
        keys_to_set = ("pattern", "field_of_view")
        args_to_set = popargs_to_dict(keys_to_set, kwargs)
        super().__init__(**kwargs)

        for key, val in args_to_set.items():
            setattr(self, key, val)
#
# @register_class('Photostimulation', 'test')
# class PhotostimulationPattern(NWBDataInterface):
#
#     # __nwbfields__ = ('device', 'roi_coordinates', 'stimulation_diameter')
#
#     @docval(*get_docval(NWBDataInterface.__init__) + (
#         {'name': 'device', 'type': PhotostimulationDevice, 'doc': 'photostimulation device'},
#         {'name': 'photostimulation_series', 'type': (list, PhotostimulationSeries), 'doc': 'photostimulation device', 'default': None},
#         {'name': 'opsin', 'type': str, 'doc': 'opsin used', 'default': None},
#         {'name': 'peak_pulse_power', 'type': (int, float), 'doc': 'peak pulse power (J)', 'default': None},
#         {'name': 'power', 'type': (int, float), 'doc': 'power (in milliwatts)', 'default': None},
#         {'name': 'pulse_rate', 'type': (int, float), 'doc': 'pulse rate (Hz)', 'default': None}
#         ))
#     def __init__(self, **kwargs):
#         keys_to_set = ("device", "photostimulation_series", "opsin", "peak_pulse_power", "power", "pulse_rate")
#         args_to_set = popargs_to_dict(keys_to_set, kwargs)
#         super().__init__(**kwargs)
#
#         for key, val in args_to_set.items():
#             setattr(self, key, val)
#         #
#         # if (self.roi_coordinates is None and self.stimulation_diameter is None) and (self.roi_mask is None):
#         #     raise TypeError("roi_coordinates & stimulation_diameter OR roi_mask must be specified")




# @register_class('PhotostimulationPattern', 'test')
# class PhotostimulationPattern(NWBDataInterface):
#
#     # __nwbfields__ = ('device', 'roi_coordinates', 'stimulation_diameter')
#
#     @docval(*get_docval(NWBDataInterface.__init__) + (
#         {'name': 'device', 'type': PhotostimulationDevice, 'doc': 'photostimulation device'},
#         {'name': 'roi_coordinates', 'type': Iterable, 'doc': '[n,2] or [n,3] list of coordinates', 'default': None},
#         {'name': 'stimulation_diameter', 'type': (int, float), 'doc': 'diameter of stimulation (pixels)', 'default': None},
#         {'name': 'roi_mask', 'type': 'array_data', 'doc': 'pixel mask for ROI', 'default': None},
#         {'name': 'opsin', 'type': str, 'doc': 'opsin used', 'default': None},
#         {'name': 'peak_pulse_power', 'type': (int, float), 'doc': 'peak pulse power (J)', 'default': None},
#         {'name': 'power', 'type': (int, float), 'doc': 'power (in milliwatts)', 'default': None},
#         {'name': 'pulse_rate', 'type': (int, float), 'doc': 'pulse rate (Hz)', 'default': None}
#         ))
#     def __init__(self, **kwargs):
#         keys_to_set = ("device", "roi_coordinates",
#                        "stimulation_diameter", "roi_mask", "opsin", "peak_pulse_power", "power", "pulse_rate")
#         args_to_set = popargs_to_dict(keys_to_set, kwargs)
#         super().__init__(**kwargs)
#
#         for key, val in args_to_set.items():
#             setattr(self, key, val)
#         #
#         # if (self.roi_coordinates is None and self.stimulation_diameter is None) and (self.roi_mask is None):
#         #     raise TypeError("roi_coordinates & stimulation_diameter OR roi_mask must be specified")
#




    #
    # def set_roi(self, **kwargs):
    #     """Add a Region Of Interest (ROI) data to this"""
    #     pixel_roi, mask_roi = popargs('pixel_roi', 'mask_roi', kwargs)
    #
    #     if pixel_roi is None and mask_roi is None:
    #         raise ValueError("Must provide 'pixel_roi' and/or 'mask_roi'")
    #
    #     rkwargs = dict(kwargs)
    #     if pixel_roi is not None:
    #         rkwargs['pixel_roi'] = pixel_roi
    #     if mask_roi is not None:
    #         rkwargs['mask_roi'] = mask_roi


    # @docval({'name': 'pixel_mask', 'type': 'array_data', 'default': None,
    #          'doc': 'pixel mask for 2D ROIs: [(x1, y1, weight1), (x2, y2, weight2), ...]',
    #          'shape': (None, 3)},
    #         {'name': 'voxel_mask', 'type': 'array_data', 'default': None,
    #          'doc': 'voxel mask for 3D ROIs: [(x1, y1, z1, weight1), (x2, y2, z2, weight2), ...]',
    #          'shape': (None, 4)},
    #         {'name': 'image_mask', 'type': 'array_data', 'default': None,
    #          'doc': 'image with the same size of image where positive values mark this ROI',
    #          'shape': [[None]*2, [None]*3]},
    #         {'name': 'id', 'type': int, 'doc': 'the ID for the ROI', 'default': None},
    #         allow_extra=True)
    # def add_roi(self, **kwargs):
    #     """Add a Region Of Interest (ROI) data to this"""
    #     pixel_mask, voxel_mask, image_mask = popargs('pixel_mask', 'voxel_mask', 'image_mask', kwargs)
    #     if image_mask is None and pixel_mask is None and voxel_mask is None:
    #         raise ValueError("Must provide 'image_mask' and/or 'pixel_mask'")
    #     rkwargs = dict(kwargs)
    #     if image_mask is not None:
    #         rkwargs['image_mask'] = image_mask
    #     if pixel_mask is not None:
    #         rkwargs['pixel_mask'] = pixel_mask
    #     if voxel_mask is not None:
    #         rkwargs['voxel_mask'] = voxel_mask
    #
    #     if pixel_mask is not None or voxel_mask is not None:
    #         if self.dimension is None:
    #             raise ValueError("If providing 'image_mask', must supply 'dimension' when defining 'HolographicPattern'")
    #
    #     return super().add_row(**rkwargs)

    # def pixel_to_image(self, pixel_mask):
    #     """Converts a 2D pixel_mask of a ROI into an image_mask."""
    #     image_matrix = np.zeros(self.dimension)
    #     npmask = np.asarray(pixel_mask)
    #
    #     x_coords = npmask[:, 0].astype(np.int32)
    #     y_coords = npmask[:, 1].astype(np.int32)
    #     if len(self.dimension) == 2:
    #         image_matrix[y_coords, x_coords] = 1
    #     else:
    #         z_coords = npmask[:, 2].astype(np.int32)
    #         image_matrix[y_coords, x_coords, z_coords] = 1
    #
    #     return image_matrix
    #
    # @staticmethod
    # def image_to_pixel(image_mask):
    #     """Converts an image_mask of a ROI into a pixel_mask"""
    #     pixel_mask = []
    #     it = np.nditer(image_mask, flags=['multi_index'])
    #     while not it.finished:
    #         weight = it[0][()]
    #         if weight > 0:
    #             x = it.multi_index[0]
    #             y = it.multi_index[1]
    #             pixel_mask.append([x, y, 1])
    #         it.iternext()
    #     return pixel_mask
    #
    # @docval({'name': 'description', 'type': str, 'doc': 'a brief description of what the region is'},
    #         {'name': 'region', 'type': (slice, list, tuple), 'doc': 'the indices of the table', 'default': slice(None)},
    #         {'name': 'name', 'type': str, 'doc': 'the name of the ROITableRegion', 'default': 'rois'})
    # def create_roi_table_region(self, **kwargs):
    #     return self.create_region(**kwargs)
