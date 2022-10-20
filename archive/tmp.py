from pynwb.spec import NWBNamespaceBuilder, NWBGroupSpec, NWBDatasetSpec, NWBRefSpec
from datetime import datetime
from dateutil.tz import tzlocal

from pynwb import NWBFile
from datetime import datetime

from dateutil.tz import tzlocal
from pynwb import NWBFile
from pynwb.spec import NWBNamespaceBuilder, NWBGroupSpec, NWBDatasetSpec, NWBRefSpec

ns_path = "../mylab.namespace.yaml"
ext_source = "mylab.extensions.yaml"

ns_builder = NWBNamespaceBuilder('Extension for use in my Lab', "mylab", version='0.1.0')

ns_builder.include_type('NWBContainer', namespace='core')
ns_builder.include_type('Device', namespace='core')
ns_builder.include_type('NWBDataInterface', namespace='core')
ns_builder.include_type('TimeSeries', namespace='core')
ns_builder.include_type('DynamicTable', namespace='core')
ns_builder.include_type('VectorData', namespace='core')
ns_builder.include_type('VectorIndex', namespace='core')
ns_builder.include_type("DynamicTableRegion", namespace="core")
# ns_builder.include_type("TimeSeriesReferenceVectorData", namespace="core")
# ns_builder.include_type("TimeSeriesReference", namespace="core")

series = NWBGroupSpec(
    neurodata_type_def='Series',
    neurodata_type_inc='TimeSeries',
    doc=('PhotostimulationSeries container'),
)

ns_builder.add_spec(ext_source, series)

events = NWBGroupSpec(
    neurodata_type_def='Events',
    neurodata_type_inc='DynamicTable',
    doc='A list of timestamps, stored in seconds, of an event.',
    datasets=[
        NWBDatasetSpec(name='time_series', doc='pres', quantity='?',  neurodata_type_inc='VectorData',
                       dtype=NWBRefSpec(target_type='Series', reftype='object'))
    ]
)

ns_builder.add_spec(ext_source, events)

ns_builder.export(ns_path)

from pynwb import register_class, load_namespaces
from pynwb.base import TimeSeries
from pynwb.core import DynamicTable
from hdmf.utils import docval, get_docval

ns_path = "../mylab.namespace.yaml"
load_namespaces(ns_path)


@register_class('Series', 'mylab')
class Series(TimeSeries):
    # __nwbfields__ = ('data',)

    @docval(*get_docval(TimeSeries.__init__)
    )
    def __init__(self, **kwargs):
       super().__init__(**kwargs)

@register_class('Events', 'mylab')
class Events(DynamicTable):
    """
    A list of timestamps, stored in seconds, of an event.
    """

    __columns__ = (
            {'name': 'time_series', 'description': 'PatchClampSeries with the same sweep number'},
    )

    @docval({'name': 'name', 'type': str, 'doc': 'name of this SweepTable', 'default': 'sweep_table'},
            {'name': 'description', 'type': str, 'doc': 'Description of this SweepTable',
             'default': "A sweep table groups different PatchClampSeries together."},
            *get_docval(DynamicTable.__init__, 'id', 'columns', 'colnames'))
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # @docval({'name': 'time_series', 'type': (list, tuple, Series), 'doc': 'the TimeSeries this epoch applies to'},
    #         allow_extra=True)
    # def add_event_type(self, **kwargs):
    #     return super().add_row(**kwargs)

series = Series(name='test', description='test d', data = [0, 1, 2, 3, 4, 5], unit='sec', rate=10.)

sp = Events()#, stimulus_method='method', sweeping_method='sweeping')
sp.add_row(time_series=series)
sp.add_row(time_series=series)
# df = sp.to_dataframe()
# print(df)
from pynwb import NWBHDF5IO

nwbfile = NWBFile(
    'my first synthetic recording',
    'EXAMPLE_ID',
    datetime.now(tzlocal()),
)

nwbfile.add_acquisition(sp)
with NWBHDF5IO("basics_tutorial.nwb", "w") as io:
    io.write(series)
    io.write(nwbfile)

with NWBHDF5IO("basics_tutorial.nwb", "r", load_namespaces=True) as io:
    read_nwbfile = io.read()

print('')



