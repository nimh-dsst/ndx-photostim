import file_classes
from file_classes import Events

from datetime import datetime
from dateutil.tz import tzlocal
from pynwb import load_namespaces

from pynwb import NWBFile

name = "test"
ns_path = name + ".namespace.yaml"
load_namespaces(ns_path)

nwbfile = NWBFile(
    'my first synthetic recording',
    'EXAMPLE_ID',
    datetime.now(tzlocal()),
)

events = Events(
            name='Events',
            description='events from my experiment',
            timestamps=[0., 1., 2.],
            resolution=1e-5
        )

from pynwb import NWBHDF5IO

with NWBHDF5IO("basics_tutorial.nwb", "w") as io:
    io.write(events)

with NWBHDF5IO("basics_tutorial.nwb", "r", load_namespaces=True) as io:
    read_nwbfile = io.read()


print('')