import os
from pynwb import load_namespaces, get_class
from pynwb.core import NWBContainer
from hdmf.utils import docval, get_docval, popargs
from pynwb import register_class, load_namespaces
from collections.abc import Iterable

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