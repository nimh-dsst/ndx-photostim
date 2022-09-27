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

    # TODO: define your new data types
    # see https://pynwb.readthedocs.io/en/latest/extensions.html#extending-nwb
    # for more information
    tetrode_series = NWBGroupSpec(
        neurodata_type_def='SpatialLightModulator',
        neurodata_type_inc='NWBContainer',
        doc=('slm'),
        attributes=[
            NWBAttributeSpec(
                # name='size',
                doc='vertices for surface, points in 3D space',
                shape=(2, ),
                name='size', dtype='float'
            )
        ],
    )

    ext = NWBGroupSpec(
        neurodata_type_def='PhotostimulationDevice',
        neurodata_type_inc='NWBContainer',
        doc=('photostimDevice'),
        attributes=[
            NWBAttributeSpec(
                # name='size',
                name='slm',
                doc='slm',
                dtype=RefSpec('GroupSpec', 'object')
            )
        ])
    # TODO: add all of your new data types to this list
    new_data_types = [tetrode_series, ext]

    # export the spec to yaml files in the spec folder
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'spec'))
    export_spec(ns_builder, new_data_types, output_dir)
    print('Spec files generated. Please make sure to rerun `pip install .` to load the changes.')


if __name__ == '__main__':
    # usage: python create_extension_spec.py
    main()
