
from pynwb.spec import NWBNamespaceBuilder, NWBGroupSpec, NWBAttributeSpec
from pynwb.spec import RefSpec

ns_path = "test.namespace.yaml"
ext_source = "test.extensions.yaml"

ns_builder = NWBNamespaceBuilder('Test extension', "test", version='0.1.0')

ns_builder.include_type('NWBContainer', namespace='core')
ns_builder.include_type('Device', namespace='core')
ns_builder.include_type('NWBDataInterface', namespace='core')
ns_builder.include_type('TimeSeries', namespace='core')
ns_builder.include_type('DynamicTable', namespace='hdmf-common')

ext = NWBGroupSpec(
        neurodata_type_def='SpatialLightModulator',
        neurodata_type_inc='NWBContainer',
        doc=('Spatial light modulator used in holographic photostimulation'),
        attributes=[
            NWBAttributeSpec('dimensions', 'dimensions ([w, h] or [w, h, d]) of SLM field', 'numeric', shape=((2, ), (3,)))
        ])
ns_builder.add_spec(ext_source, ext)

ext = NWBGroupSpec(
        neurodata_type_def='PhotostimulationDevice',
        neurodata_type_inc='Device',
        doc=('photostimDevice'),
        attributes=[
            NWBAttributeSpec('type', 'type of stimulation (laser or LED)', 'text', required=False),
            NWBAttributeSpec('wavelength', 'wavelength of photostimulation', 'numeric', required=False),
            NWBAttributeSpec('slm', 'spatial light modulator device', RefSpec('GroupSpec', 'object'), required=False)
        ])

ns_builder.add_spec(ext_source, ext)

ext = NWBGroupSpec(
        neurodata_type_def='ImagingPlane',
        neurodata_type_inc='NWBContainer',
        doc=('Photostimulation container'),
        attributes=[
            NWBAttributeSpec('device', 'photostimulation device', RefSpec('GroupSpec', 'object')),
            NWBAttributeSpec('opsin', 'opsin used', 'text'),
            NWBAttributeSpec('peak_pulse_power', 'peak pulse power (J)', 'numeric'),
            NWBAttributeSpec('power', 'power (in milliwatts)', 'numeric'),
            NWBAttributeSpec('pulse_rate', 'pulse rate (Hz)', 'numeric'),
        ])

ns_builder.add_spec(ext_source, ext)

ext = NWBGroupSpec(
        neurodata_type_def='HolographicPattern',
        neurodata_type_inc='NWBContainer',
        doc=('holographic pattern'),
        attributes=[
            NWBAttributeSpec('pixel_roi', '[n,2] or [n,3] list of coordinates', 'numeric', shape=((None, 2), (None, 3))),
            NWBAttributeSpec('mask_roi', 'mask of region of interest', 'numeric'),
            NWBAttributeSpec('stimulation_diameter', 'diameter of stimulation (pixels)', 'numeric'),
            NWBAttributeSpec('dimension', 'dimension', 'numeric', shape=((2, ), (3,)))
        ])

ns_builder.add_spec(ext_source, ext)

ext = NWBGroupSpec(
        neurodata_type_def='PhotostimulationSeries',
        neurodata_type_inc='TimeSeries',
        doc=('PhotostimulationSeries container'),
        attributes=[
            NWBAttributeSpec('pattern', 'photostimulation pattern', RefSpec('GroupSpec', 'object')),
            NWBAttributeSpec('field_of_view', 'fov', 'numeric')
        ])

ns_builder.add_spec(ext_source, ext)
ns_builder.export(ns_path)