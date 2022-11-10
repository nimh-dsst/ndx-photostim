

from pynwb import NWBFile, NWBHDF5IO
from file_classes import SpatialLightModulator, PhotostimulationDevice, HolographicPattern, PhotostimulationSeries, PhotostimulationTable
# from ndx_photostim import SpatialLightModulator, PhotostimulationDevice, HolographicPattern, PhotostimulationSeries, PhotostimulationTable
from pynwb import TimeSeries
import numpy as np
from dateutil.tz import tzlocal
from datetime import datetime

print('')