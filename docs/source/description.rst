Overview
========

.. note::
    This is an NWB extension for storing holographic photostimulation data.

    * Two containers are used to store **device-specific metadata**, `SpatialLightModulator` and `PhotostimulationDevice`,
    * `HolographicPattern` is used to store the **simulation pattern**.
    * `PhotostimulationSeries` contains the **time series data** corresponding to the presentation of a given stimulus (where the stimulus is represented by a `HolographicPattern` container linked to the `PhotostimulationSeries`).
    * We group **all the time series/patterns for a given experiment** together using the `PhotostimulationTable` container. This object is a dynamic table, where each row in the table contains a `PhotostimulationSeries`. Additionally, the table links to the `StimulationDevice` used to generate the patterns and record the results contained in the table.
