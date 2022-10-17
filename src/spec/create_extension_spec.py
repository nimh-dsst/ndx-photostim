# -*- coding: utf-8 -*-
import os.path
from pynwb.spec import NWBDatasetSpec, NWBDtypeSpec, RefSpec

from pynwb.spec import NWBNamespaceBuilder, export_spec, NWBGroupSpec, NWBAttributeSpec
# TODO: import other spec classes as needed
# from pynwb.spec import NWBDatasetSpec, NWBLinkSpec, NWBDtypeSpec, NWBRefSpec
from collections.abc import Iterable
from pynwb.spec import NWBNamespaceBuilder, NWBGroupSpec, NWBAttributeSpec, NWBLinkSpec, NWBDtypeSpec, NWBDatasetSpec


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
    ns_builder.include_type('TimeSeries', namespace='core')
    ns_builder.include_type('DynamicTable', namespace='hdmf-common')

    # TODO: define your new data types
    # see https://pynwb.readthedocs.io/en/latest/extensions.html#extending-nwb
    # for more information
    slm = NWBGroupSpec(
        neurodata_type_def='SpatialLightModulator',
        neurodata_type_inc='NWBContainer',
        doc='SpatialLightModulator',
        attributes=[NWBAttributeSpec('dimensions', 'dimensions ([w, h] or [w, h, d]) of SLM field', 'numeric',
                                     shape=((2,), (3,)))])

    psd = NWBGroupSpec(neurodata_type_def='PhotostimulationDevice',
                       neurodata_type_inc='Device',
                       doc=('PhotostimulationDevice'),
                       attributes=[NWBAttributeSpec('type', 'type of stimulation (laser or LED)', 'text'),
                                   NWBAttributeSpec('wavelength', 'wavelength of photostimulation', 'numeric')],
                       links=[NWBLinkSpec(doc='slm', target_type='SpatialLightModulator', name='slm name')]
                       )

    ip = NWBGroupSpec(neurodata_type_def='ImagingPlane',
                      neurodata_type_inc='NWBContainer',
                      doc=('ImagingPlane'),
                      attributes=[NWBAttributeSpec('opsin', 'opsin used', 'text'),
                                  NWBAttributeSpec('peak_pulse_power', 'peak pulse power (J)', 'numeric'),
                                  NWBAttributeSpec('power', 'power (in milliwatts)', 'numeric'),
                                  NWBAttributeSpec('pulse_rate', 'pulse rate (Hz)', 'numeric')],
                      links=[NWBLinkSpec(doc='PhotostimulationDevice', target_type='PhotostimulationDevice')]
                      )

    pixel_roi = NWBDatasetSpec(doc='[n,2] or [n,3] list of coordinates', name='pixel_roi',
                               attributes=[
                                   NWBAttributeSpec(name='stimulation_diameter', doc='stimulation_diameter',
                                                    dtype='numeric')
                               ])

    mask_roi = NWBDatasetSpec(doc='mask of region of interest', name='mask_roi')

    hp = NWBGroupSpec(
        neurodata_type_def='HolographicPattern',
        neurodata_type_inc='NWBContainer',
        doc=('holographic pattern'),
        attributes=[NWBAttributeSpec('dimension', 'dimension', 'numeric', shape=((2,), (3,)))],
        datasets=[pixel_roi, mask_roi]
    )

    ps = NWBGroupSpec(
        neurodata_type_def='PhotostimulationSeries',
        neurodata_type_inc='TimeSeries',
        doc=('PhotostimulationSeries container'))

    # TODO: add all of your new data types to this list
    new_data_types = [slm, psd, ip, hp, ps]

    # export the spec to yaml files in the spec folder
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'spec'))
    export_spec(ns_builder, new_data_types, output_dir)
    print('Spec files generated. Please make sure to rerun `pip install .` to load the changes.')


if __name__ == '__main__':
    # usage: python create_extension_spec.py
    main()
