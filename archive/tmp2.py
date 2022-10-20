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


from file_classes import SpatialLightModulator, PhotostimulationDevice, StimulationPlane, HolographicPattern, PhotostimulationSeries, SeriesStack, StimulusPresentation
import matplotlib.pyplot as plt
import os
from hdmf.build import ObjectMapper
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

os.system('python file_defined_namespace.py')

ns_path = "../test.namespace.yaml"
load_namespaces(ns_path)

namespace = 'test'

@register_class('StimulusPresentation', namespace)
class StimulusPresentation(DynamicTable):
    """
    Table for storing Epoch data
    """

    __nwbfields__ = ('stimulus_method', 'sweeping_method', 'time_per_sweep', 'num_sweeps')

    __columns__ = (
        {'name': 'label', 'description': 'Start time of epoch, in seconds', 'required': True},
        {'name': 'stimulus_description', 'description': 'Stop time of epoch, in seconds', 'required': False},
        {'name': 'photostimulation_series', 'description': 'Stop time of epoch, in seconds', 'required': False},
        {'name': 'pattern', 'description': 'Stop time of epoch, in seconds', 'required': False}
    )

    @docval({'name': 'name', 'type': str, 'doc': 'name of this TimeIntervals'},  # required
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeIntervals'},
            {'name': 'stimulus_method', 'type': str, 'doc': 'Description of this TimeIntervals', 'default': None},
            {'name': 'sweeping_method', 'type': str, 'doc': 'Description of this TimeIntervals', 'default': None},
            {'name': 'time_per_sweep', 'type': (int, float), 'doc': 'Description of this TimeIntervals', 'default': None},
            {'name': 'num_sweeps', 'type': (int, float), 'doc': 'Description of this TimeIntervals', 'default': None},
            *get_docval(DynamicTable.__init__, 'id', 'columns', 'colnames'))
    def __init__(self, **kwargs):
        keys_to_set = ("stimulus_method", "sweeping_method", "time_per_sweep", "num_sweeps")
        args_to_set = popargs_to_dict(keys_to_set, kwargs)

        super().__init__(**kwargs)

        for key, val in args_to_set.items():
            setattr(self, key, val)

    @docval({'name': 'label', 'type': str, 'doc': 'name of this TimeIntervals'},
            {'name': 'stimulus_description', 'type': (str, list), 'doc': 'name of this TimeIntervals', 'default':''},
            {'name': 'photostimulation_series', 'type': PhotostimulationSeries, 'doc': 'name of this TimeIntervals', 'default':None},
            {'name': 'pattern', 'type':  HolographicPattern, 'doc': 'name of this TimeIntervals'},
            allow_extra=True
    )
    def add_event_type(self, **kwargs):
        """Add an event type as a row to this table."""

        super().add_row(**kwargs)

@register_map(StimulusPresentation)
class StimulusPresentationMap(ObjectMapper):

    def __init__(self, spec):
        super().__init__(spec)
        stim_method_spec = self.spec.get_dataset('stim_method')
        self.map_spec('sweeping_method', stim_method_spec.get_attribute('sweeping_method'))
        self.map_spec('time_per_sweep', stim_method_spec.get_attribute('time_per_sweep'))
        self.map_spec('num_sweeps', stim_method_spec.get_attribute('num_sweeps'))

