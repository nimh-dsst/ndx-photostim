
from pynwb.spec import NWBNamespaceBuilder, NWBGroupSpec, NWBAttributeSpec, NWBLinkSpec, NWBDtypeSpec, NWBDatasetSpec

ns_path = "test.namespace.yaml"
ext_source = "test.extensions.yaml"

ns_builder = NWBNamespaceBuilder('Test extension', "test", version='0.1.0')

ns_builder.include_type('NWBContainer', namespace='core')
ns_builder.include_type('Device', namespace='core')
ns_builder.include_type('NWBDataInterface', namespace='core')
ns_builder.include_type('TimeSeries', namespace='core')
ns_builder.include_type('DynamicTable', namespace='hdmf-common')

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
                               NWBAttributeSpec('wavelength', 'wavelength of photostimulation', 'numeric')],
                   groups=[NWBGroupSpec(name='slm', doc='slm', neurodata_type_inc='SpatialLightModulator', quantity='?')]
                   )

ns_builder.add_spec(ext_source, psd)

ip = NWBGroupSpec(neurodata_type_def='StimulationPlane',
                   neurodata_type_inc='NWBContainer',
                   doc=('ImagingPlane'),
                   attributes=[NWBAttributeSpec('opsin', 'opsin used', 'text', required=False),
                               NWBAttributeSpec('peak_pulse_power', 'peak pulse power (J)', 'numeric', required=False),
                               NWBAttributeSpec('power', 'power (in milliwatts)', 'numeric', required=False),
                               NWBAttributeSpec('pulse_rate', 'pulse rate (Hz)', 'numeric', required=False)],
                   groups=[NWBGroupSpec(name='device', doc='photostimulation device',
                                        neurodata_type_inc='PhotostimulationDevice')]
)

ns_builder.add_spec(ext_source, ip)

pixel_roi = NWBDatasetSpec(doc='[n,2] or [n,3] list of coordinates',
                           name='pixel_roi',
                           quantity='?',
                           attributes=[
                               NWBAttributeSpec(name='stimulation_diameter', doc='stimulation_diameter', dtype='numeric', required=False)
                           ])

mask_roi = NWBDatasetSpec(doc='mask of region of interest', name='mask_roi', quantity='?')

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
        groups=[ip, hp]
)



ns_builder.add_spec(ext_source, ps)

ns_builder.export(ns_path)