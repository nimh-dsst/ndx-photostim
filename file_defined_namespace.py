
from pynwb.spec import NWBNamespaceBuilder, NWBGroupSpec, NWBAttributeSpec, NWBLinkSpec, NWBDtypeSpec, NWBDatasetSpec, NWBRefSpec

ns_path = "test.namespace.yaml"
ext_source = "test.extensions.yaml"

ns_builder = NWBNamespaceBuilder('Test extension', "test", version='0.1.0')

ns_builder.include_type('NWBContainer', namespace='core')
ns_builder.include_type('Device', namespace='core')
ns_builder.include_type('NWBDataInterface', namespace='core')
ns_builder.include_type('TimeSeries', namespace='core')
ns_builder.include_type('DynamicTable', namespace='core')
ns_builder.include_type('VectorData', namespace='core')
ns_builder.include_type('VectorIndex', namespace='core')
ns_builder.include_type("DynamicTableRegion", namespace="core")

slm = NWBGroupSpec(
        neurodata_type_def='SpatialLightModulator',
        neurodata_type_inc='NWBContainer',
        doc='SpatialLightModulator',
        attributes=[NWBAttributeSpec('dimensions', 'dimensions ([w, h] or [w, h, d]) of SLM field', 'numeric', shape=((2,), (3,)))],
)

ns_builder.add_spec(ext_source, slm)

psd = NWBGroupSpec(neurodata_type_def='PhotostimulationDevice',
                   neurodata_type_inc='Device',
                   doc=('PhotostimulationDevice'),
                   attributes=[NWBAttributeSpec('type', 'type of stimulation (laser or LED)', 'text'),
                               NWBAttributeSpec('wavelength', 'wavelength of photostimulation', 'numeric'),
                               NWBAttributeSpec('opsin', 'opsin used', 'text', required=False),
                              NWBAttributeSpec('peak_pulse_power', 'peak pulse power (J)', 'numeric', required=False),
                              NWBAttributeSpec('power', 'power (in milliwatts)', 'numeric', required=False),
                              NWBAttributeSpec('pulse_rate', 'pulse rate (Hz)', 'numeric', required=False)
                               ],
                   groups=[NWBGroupSpec(name='slm', doc='slm', neurodata_type_inc='SpatialLightModulator', quantity='?')],
                   )

ns_builder.add_spec(ext_source, psd)

pixel_roi = NWBDatasetSpec(doc='[n,2] or [n,3] list of coordinates', name='pixel_roi', quantity='?',
                           attributes=[NWBAttributeSpec(name='stimulation_diameter', doc='stimulation_diameter', dtype='numeric', required=False)])

mask_roi = NWBDatasetSpec(doc='ROI masks for each ROI. Each image mask is the size of the original imaging plane (or'
                              'volume) and members of the ROI are finite non-zero.',
                          name='mask_roi', quantity='?', dims=(('num_rows', 'num_cols'), ('num_rows', 'num_cols', 'depth')),
                          shape=([None]*2, [None]*3), dtype='uint8')

hp = NWBGroupSpec(
        neurodata_type_def='HolographicPattern',
        neurodata_type_inc='NWBContainer',
        doc=('holographic pattern'),
        attributes = [
            NWBAttributeSpec('dimension', 'dimension', 'numeric', shape=((2, ), (3,)), required=False)
        ],
        datasets=[pixel_roi, mask_roi]
)

ns_builder.add_spec(ext_source, hp)

ps = NWBGroupSpec(
        neurodata_type_def='PhotostimulationSeries',
        neurodata_type_inc='TimeSeries',
        doc=('PhotostimulationSeries container'),
        attributes=[NWBAttributeSpec('format', 'format', 'text', required=False),
                    NWBAttributeSpec('stimulus_duration', 'format', 'numeric', required=False),
                    NWBAttributeSpec('field_of_view', 'fov', 'numeric', required=False)],
        groups=[hp],
        quantity='*'
)

ns_builder.add_spec(ext_source, ps)

label_col = NWBDatasetSpec(name='label',  dtype='text', doc='Label for each event type.', neurodata_type_inc='VectorData')
description_col = NWBDatasetSpec(name='stimulus_description',  dtype='text', doc='Label for each event type.', quantity='?', neurodata_type_inc='VectorData')
stim_col = NWBDatasetSpec(name='photostimulation_series', doc='asdas',   quantity='?', neurodata_type_inc='VectorData',
                       dtype=NWBRefSpec(target_type='PhotostimulationSeries', reftype='object'))
pattern_col = NWBDatasetSpec(name='pattern', doc='asdas',  quantity='?',neurodata_type_inc='VectorData',
                       dtype=NWBRefSpec(target_type='HolographicPattern', reftype='object'))


stim_method = NWBDatasetSpec(name='stimulus_method',
                          doc='Scanning or scanless method for shaping optogenetic light (e.g., diffraction limited points, 3D shot, disks, etc.)',
                            dtype='text',
                          attributes=[
                              NWBAttributeSpec(name='sweeping_method', doc='format', dtype='text', required=True),
                              NWBAttributeSpec(name='time_per_sweep', doc='format', dtype='numeric', required=False),
                              NWBAttributeSpec(name='num_sweeps', doc='format', dtype='numeric', required=False),
                          ],
                          quantity='?')

event_times_index = NWBDatasetSpec(
    name='event_times_index',
    neurodata_type_inc='VectorIndex',
    doc=('Index into the event_times dataset.'),
)



sp = NWBGroupSpec(
        neurodata_type_def='StimulusPresentation',
        neurodata_type_inc='DynamicTable',
        doc=("Table to hold event timestamps and event metadata relevant to data preprocessing and analysis. Each "
         "row corresponds to a different event type. Use the 'event_times' dataset to store timestamps for each "
         "event type. Add user-defined columns to add metadata for each event type or event time."),
    datasets=[
              label_col, description_col, stim_col, pattern_col
              ],
        groups=[NWBGroupSpec(name='photostimulation_device', doc='photostimulation device', neurodata_type_inc='PhotostimulationDevice', quantity='?')],
    attributes=[
        NWBAttributeSpec(name='stimulus_method', doc='format', dtype='text', required=True),
        NWBAttributeSpec(name='sweeping_method', doc='format', dtype='text', required=False),
        NWBAttributeSpec(name='time_per_sweep', doc='format', dtype='numeric', required=False),
        NWBAttributeSpec(name='num_sweeps', doc='format', dtype='numeric', required=False),
    ]
)

ns_builder.add_spec(ext_source, sp)


ns_builder.export(ns_path)