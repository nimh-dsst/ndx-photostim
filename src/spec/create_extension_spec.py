# -*- coding: utf-8 -*-
import os.path
from pynwb.spec import NWBDatasetSpec, NWBDtypeSpec, RefSpec

from pynwb.spec import NWBNamespaceBuilder, export_spec, NWBGroupSpec, NWBAttributeSpec
# TODO: import other spec classes as needed
# from pynwb.spec import NWBDatasetSpec, NWBLinkSpec, NWBDtypeSpec, NWBRefSpec
from collections.abc import Iterable


def main():
    # these arguments were auto-generated from your cookiecutter inputs
    ns_builder = NWBNamespaceBuilder(
        doc="""holographic photostimulation extension to NWB standard""",
        name="""ndx-photostim""",
        version="""0.1.0""",
        author=list(map(str.strip, """Carl Harris""".split(','))),
        contact=list(map(str.strip, """carlwharris1@gmail.com""".split(',')))
    )

    # TODO: specify the neurodata_types that are used by the extension as well
    # as in which namespace they are found.
    # this is similar to specifying the Python modules that need to be imported
    # to use your new data types.
    # all types included or used by the types specified here will also be
    # included.
    # ns_builder.include_type('ElectricalSeries', namespace='core')
    ns_builder.include_type('NWBContainer', namespace='core')
    ns_builder.include_type('Device', namespace='core')
    ns_builder.include_type('NWBDataInterface', namespace='core')

    # TODO: define your new data types
    # see https://pynwb.readthedocs.io/en/latest/extensions.html#extending-nwb
    # for more information
    slm = NWBGroupSpec(
        neurodata_type_def='SpatialLightModulator',
        neurodata_type_inc='NWBContainer',
        doc=('Spatial light modulator used in holographic photostimulation'),
        attributes=[
            NWBAttributeSpec('dimensions', 'dimensions ([w, h] or [w, h, d]) of SLM field', 'numeric',
                             shape=((2,), (3,)),
                             )
        ])

    photostim_device = NWBGroupSpec(
        neurodata_type_def='PhotostimulationDevice',
        neurodata_type_inc='Device',
        doc=('photostimDevice'),
        attributes=[
            NWBAttributeSpec('type', 'type of stimulation (laser or LED)', 'text'),
            NWBAttributeSpec('wavelength', 'wavelength of photostimulation', 'numeric'),
            NWBAttributeSpec('slm', 'spatial light modulator device', RefSpec('GroupSpec', 'object'))
        ])

    photostim = NWBGroupSpec(
        neurodata_type_def='Photostimulation',
        neurodata_type_inc='NWBDataInterface',
        doc=('photostimulation container'),
        attributes=[
            NWBAttributeSpec('device', 'photostimulation device', RefSpec('GroupSpec', 'object')),
            NWBAttributeSpec('roi_coordinates', '[n,2] or [n,3] list of coordinates', 'numeric',
                             shape=((None, 2), (None, 3))),
            NWBAttributeSpec('stimulation_diameter', 'diameter of stimulation (pixels)', 'numeric'),
            NWBAttributeSpec('roi_mask', 'mask of region of interest', 'numeric'),
            NWBAttributeSpec('opsin', 'opsin used', 'text'),
            NWBAttributeSpec('peak_pulse_power', 'peak pulse power (J)', 'numeric')
        ])

    # TODO: add all of your new data types to this list
    new_data_types = [slm, photostim_device, photostim]

    # export the spec to yaml files in the spec folder
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'spec'))
    export_spec(ns_builder, new_data_types, output_dir)
    print('Spec files generated. Please make sure to rerun `pip install .` to load the changes.')


if __name__ == '__main__':
    # usage: python create_extension_spec.py
    main()
