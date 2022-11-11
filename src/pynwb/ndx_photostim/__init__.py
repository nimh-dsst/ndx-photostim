import os
from collections.abc import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from hdmf.utils import docval, getargs, popargs, popargs_to_dict, get_docval
from pynwb import register_class, load_namespaces
from pynwb import register_map
from pynwb.base import TimeSeries
from pynwb.core import DynamicTable
from pynwb.device import Device
from pynwb.file import NWBContainer
from pynwb.io.base import TimeSeriesMap
from pynwb.io.core import NWBContainerMapper

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

from . import io as __io  # noqa: E402,F401
from .photostim import SpatialLightModulator, PhotostimulationDevice, HolographicPattern, PhotostimulationSeries, PhotostimulationTable