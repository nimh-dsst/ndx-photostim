
import os

os.system('python file_defined_namespace.py')


from file_classes import SpatialLightModulator, PhotostimulationDevice, StimulationPlane, HolographicPattern, PhotostimulationSeries

from datetime import datetime
from dateutil.tz import tzlocal

from pynwb import NWBFile

nwbfile = NWBFile(
    'my first synthetic recording',
    'EXAMPLE_ID',
    datetime.now(tzlocal()),
)

import numpy as np
slm = SpatialLightModulator(
    name="slm",
    dimensions = [1, 2]
)

dev = PhotostimulationDevice(name="device", description="photostim_device", type='LED', wavelength=320, slm=slm)
imaging_plane = StimulationPlane(name="imaging_plane",  device=dev, opsin='test opsin', pulse_rate=10)

x = np.random.randint(0, 95)
y = np.random.randint(0, 95)

pixel_roi = []
for ix in range(x, x + 5):
    for iy in range(y, y + 5):
        pixel_roi.append((ix, iy, 1))

hp2 = HolographicPattern(name='HolographicPattern', pixel_roi=pixel_roi, stimulation_diameter=5)

from file_classes import PhotostimulationSeries
ser = PhotostimulationSeries(name='hi', field_of_view=1,unit='seconds', format='series', data=[0, 1, 0, 1], holographic_pattern=hp2, stimulus_duration=10, rate=10., stimulation_plane=imaging_plane)

nwbfile.add_stimulus(ser)

from pynwb import NWBHDF5IO

# with NWBHDF5IO("basics_tutorial.nwb", "w") as io:
#     io.write(nwbfile)
#
# with NWBHDF5IO("basics_tutorial.nwb", "r", load_namespaces=True) as io:
#     read_nwbfile = io.read()
#

from file_classes import StimulusPresentation

sp = StimulusPresentation(name='test_presentation_table', description='abcd')
sp.add_row(label='stim1', stimulus=hp2, presentation=ser)
sp.add_row(label='stim2', stimulus=hp2)
df = sp.to_dataframe()
print(df)

