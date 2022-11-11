from pynwb import register_map
from pynwb.io.base import TimeSeriesMap
from pynwb.io.core import NWBContainerMapper

from ..photostim import PhotostimulationSeries, HolographicPattern


@register_map(HolographicPattern)
class HolographicPatternMap(NWBContainerMapper):
    '''Map roi_size specifications.'''

    def __init__(self, spec):
        super().__init__(spec)
        pixel_roi_spec = self.spec.get_dataset('pixel_roi')
        self.map_spec('roi_size', pixel_roi_spec.get_attribute('roi_size'))


@register_map(PhotostimulationSeries)
class PhotostimulationSeriesMap(TimeSeriesMap):
    '''Map stimulus_method's attributes.'''

    def __init__(self, spec):
        super().__init__(spec)
        stim_method_spec = self.spec.get_dataset('stimulus_method')
        self.map_spec('sweep_pattern', stim_method_spec.get_attribute('sweep_pattern'))
        self.map_spec('time_per_sweep', stim_method_spec.get_attribute('time_per_sweep'))
        self.map_spec('num_sweeps', stim_method_spec.get_attribute('num_sweeps'))
