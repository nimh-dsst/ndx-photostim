import os
from pynwb import load_namespaces, get_class
from hdmf.utils import docval, get_docval, popargs
from pynwb import register_class, load_namespaces
from collections.abc import Iterable
from pynwb.core import NWBContainer, NWBDataInterface
from pynwb.device import Device
from hdmf.utils import docval, popargs, get_docval, get_data_shape, popargs_to_dict


# Set path of the namespace.yaml file to the expected install location
ndx_photostim_specpath = os.path.join(
    os.path.dirname(__file__),
    'spec',
    'ndx-photostim.namespace.yaml'
)

# If the extension has not been installed yet but we are running directly from
# the git repo
if not os.path.exists(ndx_photostim_specpath):
    ndx_photostim_specpath = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '..', '..', '..',
        'spec',
        'ndx-photostim.namespace.yaml'
    ))

# Load the namespace
load_namespaces(ndx_photostim_specpath)

# TODO: import your classes here or define your class using get_class to make
# them accessible at the package level
# SpatialLightModulator = get_class('SpatialLightModulator', 'ndx-photostim')
register_class('SpatialLightModulator', 'ndx-photostim')
class SpatialLightModulator(NWBContainer):

    __nwbfields__ = ('dimensions',)

    @docval(
        {'name': 'name', 'type': str, 'doc': 'name of spatial light modulator'},
        {'name': 'dimensions', 'type': Iterable, 'doc': 'dimensions ([w, h] or [w, h, d]) of SLM field'}
    )
    def __init__(self, **kwargs):
        dimensions = popargs('dimensions', kwargs)
        super().__init__(**kwargs)
        self.dimensions = dimensions

@register_class('PhotostimulationDevice', 'ndx-photostim')
class PhotostimulationDevice(Device):

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


@register_class('Photostimulation', 'ndx-photostim')
class Photostimulation(NWBDataInterface):

    # __nwbfields__ = ('device', 'roi_coordinates', 'stimulation_diameter')

    @docval(*get_docval(NWBDataInterface.__init__) + (
        {'name': 'device', 'type': PhotostimulationDevice, 'doc': 'photostimulation device'},
        {'name': 'roi_coordinates', 'type': Iterable, 'doc': '[n,2] or [n,3] list of coordinates', 'default': None},
        {'name': 'stimulation_diameter', 'type': (int, float), 'doc': 'diameter of stimulation (pixels)', 'default': None},
        {'name': 'roi_mask', 'type': 'array_data', 'doc': 'pixel mask for ROI', 'default': None},
        {'name': 'opsin', 'type': str, 'doc': 'opsin used', 'default': None},
        {'name': 'peak_pulse_power', 'type': (int, float), 'doc': 'peak pulse power (J)', 'default': None}
        ))
    def __init__(self, **kwargs):
        keys_to_set = ("device", "roi_coordinates",
                       "stimulation_diameter", "roi_mask", "opsin", "peak_pulse_power")
        args_to_set = popargs_to_dict(keys_to_set, kwargs)
        super().__init__(**kwargs)

        for key, val in args_to_set.items():
            setattr(self, key, val)

        if (self.roi_coordinates is None and self.stimulation_diameter is None) and (self.roi_mask is None):
            raise TypeError("roi_coordinates & stimulation_diameter OR roi_mask must be specified")


# @register_class('SpatialLightModulator' 'ndx-photostim')
# class SpatialLightModulator(NWBContainer):
#     __nwbfields__ = ('description',
#                      'emission_lambda')
#
#     @docval({'name': 'name', 'type': str, 'doc': 'the name of this electrode'},  # required
#             {'name': 'size', 'type': Iterable, 'doc': 'Any notes or comments about the channel.', 'shape': ((2, ), (3, ))},
#             {'name': 'emission_lambda', 'type': float, 'doc': 'Emission wavelength for channel, in nm.'})  # required
#     def __init__(self, **kwargs):
#         description, emission_lambda = popargs("description", "emission_lambda", kwargs)
#         super().__init__(**kwargs)
#         self.description = description
#         self.emission_lambda = emission_lambda