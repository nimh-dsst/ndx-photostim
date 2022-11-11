Overview
========

.. note::
    This is an NWB extension for storing holographic photostimulation data.

    * **Device metadata** Two containers are used to store device-specific metadata, `SpatialLightModulator` and `PhotostimulationDevice`,
    * **Stimulation pattern** A container called `HolographicPattern` is used to store the pattern used in the stimulation.
    * **Presentation data** `PhotostimulationSeries` is used to store the timeseries data corresponding to the presentation for a given simulation pattern (represented by a `HolographicPattern` container than is stored within `PhotostimulationSeries`).
    * **Multiple stimulation patterns** We group all `PhotostimulationSeries` containers (i.e., the set of stimulation time series/pattern pairs), along with the `StimulationDevice` used to collect the patterns, into a dynamic table called `PhotostimulationTable`. This allows all stimulation data and metadata for a given experiment to be grouped together clearly.


