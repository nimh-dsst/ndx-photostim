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

class TestSLM(TestCase):
    def test_init(self):
        '''Test spatial light monitor initialization.'''
        SpatialLightModulator(name='slm',
                                    model='Meadowlark',
                                    size=np.array([512, 512]))

        with self.assertRaises(TypeError):
            SpatialLightModulator(name='slm', size=np.array([512, 512]))

