Overview
========

.. note::
    This is an NWB extension for storing holographic photostimulation data.

    * **Device metadata:** stored using the `SpatialLightModulator` and `PhotostimulationDevice` containers.
    * **Stimulation pattern:** contained in the `HolographicPattern` container.
    * **Presentation data:** `PhotostimulationSeries` stores the timeseries data corresponding to the presentation of a given simulation pattern (represented by a corresponding `HolographicPattern` container than is stored within `PhotostimulationSeries`).
    * **Multiple stimulation patterns:** all `PhotostimulationSeries` containers for a given experiment (i.e., the set of stimulation time series/pattern pairs), along with the `StimulationDevice` used to collect the patterns, are grouped into the `PhotostimulationTable` dynamic table. This allows all stimulation data and metadata for a given experiment to be grouped together clearly.
