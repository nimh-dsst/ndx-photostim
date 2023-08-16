

import os
os.system("python src/spec/create_extension_spec.py")
os.system("pip install .")

from datetime import datetime
import numpy as np
from ndx_photostim import SpatialLightModulator, PhotostimulationDevice, HolographicPattern, PhotostimulationSeries, \
    PhotostimulationTable
from pynwb import NWBFile
from pynwb.testing import TestCase
from dateutil.tz import tzlocal


def get_SLM():
    '''Return SpatialLightModulator container.'''
    slm = SpatialLightModulator(name="slm", size=np.array([1, 2]))
    return slm


def get_photostim_device():
    '''Return PhotostimulationDevice containing SLM.'''
    slm = get_SLM()
    photostim_dev = PhotostimulationDevice(name="photostim_dev", description="photostim_device", type='LED',
                                           wavelength=320, slm=slm,
                                           opsin='test_opsin', peak_pulse_energy=20,
                                           power=10, pulse_rate=5)

    return photostim_dev


def get_holographic_pattern():
    '''Return example HolographicPattern with image_mask_roi'''
    image_mask_roi = np.zeros((50, 50))
    x = np.random.randint(0, 3)
    y = np.random.randint(0, 3)
    image_mask_roi[x:x + 5, y:y + 5] = 1
    hp = HolographicPattern(name='pattern', image_mask_roi=image_mask_roi, roi_size=5)
    return hp

def get_photostim_series():
    '''Return example PhotostimulationSeries container.'''
    hp = get_holographic_pattern()

    photostim_series = PhotostimulationSeries(name="photosim series", pattern=hp, unit='SIunit',
                                              data=[1, -1, 1, -1],
                                              timestamps=[0.5, 1, 2, 4], format='interval')
    return photostim_series

def get_series():
    '''Return example PhotostimulationSeries.'''
    hp = get_holographic_pattern()
    series = PhotostimulationSeries(name="photosim series", format='interval', pattern=hp, stimulus_method="stim_method",
                                    sweep_pattern="...",
                                    time_per_sweep=10, num_sweeps=20)
    return series

series = get_series()