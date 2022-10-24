# -*- coding: utf-8 -*-
import os.path

# TODO: import other spec classes as needed
# from pynwb.spec import NWBDatasetSpec, NWBLinkSpec, NWBDtypeSpec, NWBRefSpec
from pynwb.spec import NWBNamespaceBuilder, NWBGroupSpec, NWBAttributeSpec, NWBLinkSpec, NWBDatasetSpec
from pynwb.spec import NWBRefSpec
from pynwb.spec import export_spec


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
    ns_builder.include_type("TimeSeries", namespace="core")
    ns_builder.include_type("NWBDataInterface", namespace="core")
    ns_builder.include_type("NWBContainer", namespace="core")
    ns_builder.include_type("Container", namespace="hdmf-common")
    ns_builder.include_type("DynamicTable", namespace="hdmf-common")
    ns_builder.include_type("DynamicTableRegion", namespace="hdmf-common")
    ns_builder.include_type("VectorData", namespace="hdmf-common")
    ns_builder.include_type("Data", namespace="hdmf-common")
    ns_builder.include_type("ElementIdentifiers", namespace="hdmf-common")
    ns_builder.include_type("Device", namespace="core")
    ns_builder.include_type("TimeIntervals", namespace="core")

    # TODO: define your new data types
    # see https://pynwb.readthedocs.io/en/latest/extensions.html#extending-nwb
    # for more information

    slm = NWBGroupSpec(neurodata_type_def='SpatialLightModulator', neurodata_type_inc='Device', name='slm',
                       doc='slm', quantity='?',
                       attributes=[NWBAttributeSpec('size', 'size of slm', 'numeric', shape=((2,), (3,)),
                                                    dims=(('num_rows', 'num_cols'), ('num_rows', 'num_cols', 'depth')),
                                                    required=False)])

    psd = NWBGroupSpec(neurodata_type_def='PhotostimulationDevice', neurodata_type_inc='Device',
                       doc=('PhotostimulationDevice'),
                       attributes=[NWBAttributeSpec('type', 'type of stimulation (laser or LED)', 'text'),
                                   NWBAttributeSpec('wavelength', 'wavelength of photostimulation', 'numeric',
                                                    required=False),
                                   NWBAttributeSpec('opsin', 'opsin used', 'text', required=False),
                                   NWBAttributeSpec('peak_pulse_power', 'peak pulse power (J)', 'numeric',
                                                    required=False),
                                   NWBAttributeSpec('power', 'power (in milliwatts)', 'numeric', required=False),
                                   NWBAttributeSpec('pulse_rate', 'pulse rate (Hz)', 'numeric', required=False)],
                       groups=[slm])

    pixel_roi = NWBDatasetSpec(name='pixel_roi', doc='[n,2] or [n,3] list of coordinates',
                               shape=([None] * 2, [None] * 3),
                               quantity='?',
                               attributes=[
                                   NWBAttributeSpec(name='ROI_size', doc='size of ROI', dtype='numeric',
                                                    required=False)])

    image_mask_roi = NWBDatasetSpec(
        doc='ROI masks for each ROI. Each image mask is the size of the original imaging plane (or'
            'volume) and members of the ROI are finite non-zero.', name='image_mask_roi', quantity='?',
        dims=(('num_rows', 'num_cols'), ('num_rows', 'num_cols', 'depth')),
        shape=([None] * 2, [None] * 3))

    hp = NWBGroupSpec(neurodata_type_def='HolographicPattern', neurodata_type_inc='NWBContainer',
                      doc=('holographic pattern'),
                      attributes=[
                          NWBAttributeSpec('dimension', 'dimension of hp', 'numeric', shape=((2,), (3,)),
                                           required=False)],
                      datasets=[pixel_roi, image_mask_roi])

    ps = NWBGroupSpec(neurodata_type_def='PhotostimulationSeries', neurodata_type_inc='TimeSeries',
                      doc=('PhotostimulationSeries container'),
                      attributes=[NWBAttributeSpec('format', 'format', 'text', required=True),
                                  NWBAttributeSpec('stimulus_duration', 'format', 'numeric', required=False),
                                  NWBAttributeSpec('field_of_view', 'fov', 'numeric', required=False)],
                      # links=[NWBLinkSpec(name='holographic_pattern', doc='photostimulation device',
                      #                    target_type='HolographicPattern')],
                      # datasets=[NWBDatasetSpec(name='timestamps', doc=('time stamps'))],
                      groups=[hp],
                      quantity='*')

    stim_col = NWBDatasetSpec(name='photostimulation_series', doc='asdas', neurodata_type_inc='VectorData',
                              dtype=NWBRefSpec(target_type='PhotostimulationSeries', reftype='object'))

    stim_method = NWBDatasetSpec(name='stimulus_method',
                                 doc='Scanning or scanless method for shaping optogenetic light (e.g., diffraction limited points, 3D shot, disks, etc.)',
                                 dtype='text', attributes=[
            NWBAttributeSpec(name='sweeping_method', doc='format', dtype='text', required=True),
            NWBAttributeSpec(name='time_per_sweep', doc='format', dtype='numeric', required=False),
            NWBAttributeSpec(name='num_sweeps', doc='format', dtype='numeric', required=False), ], quantity='?')

    sp = NWBGroupSpec(neurodata_type_def='PhotostimulationTable', neurodata_type_inc='DynamicTable',
                      doc=(
                          "Table to hold event timestamps and event metadata relevant to data preprocessing and analysis. Each "
                          "row corresponds to a different event type. Use the 'event_times' dataset to store timestamps for each "
                          "event type. Add user-defined columns to add metadata for each event type or event time."),
                      datasets=[stim_col, stim_method],
                      quantity='?',
                      links=[NWBLinkSpec(name='photostimulation_device', doc='photostimulation device',
                                         target_type='PhotostimulationDevice')]
                      )

    new_data_types = [slm, psd, ps, sp]

    # export the spec to yaml files in the spec folder
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'spec'))
    export_spec(ns_builder, new_data_types, output_dir)
    print('Spec files generated. Please make sure to rerun `pip install .` to load the changes.')


if __name__ == '__main__':
    # usage: python create_extension_spec.py
    main()
