# ndx-photostim Extension for NWB

This is an NWB extension for storing holographic photostimulation data.

* **Device metadata** Two containers are used to store device-specific metadata, `SpatialLightModulator` and `PhotostimulationDevice`,
* **Stimulation pattern** A container called `HolographicPattern` is used to store the pattern used in the stimulation.
* **Presentation data** `PhotostimulationSeries` is used to store the timeseries data corresponding to the presentation for a given simulation pattern
(represented by a `HolographicPattern` container than is stored within `PhotostimulationSeries`).
* **Multiple stimulation patterns** We group all `PhotostimulationSeries` containers (i.e., the set of stimulation time series/pattern pairs), along
with the `StimulationDevice` used to collect the patterns, into a dynamic table called `PhotostimulationTable`. This allows all
stimulation data and metadata for a given experiment to be grouped together clearly.

**For full example use, see [tutorial.ipynb](./tutorial.ipynb)**.

## Installation

First, clone the `ndx_photostim` repository in the desired folder using the command
```angular2svg
git clone https://github.com/carlwharris/nwb-photostim.git
```
Then use `python -m pip install -r requirements.txt -r requirements-dev.txt` to install the requisite
python packages. To install `ndx_photostim`, run `python setup.py install`. The extension can then be imported into 
scripts via `import ndx_photostim`. 

## Tests & documentation

Unit tests can be run via the command `pytest` from the root of the extension directory.

To produce documentation for the extension from the YAML specification, run:
```angular2svg
cd docs
make fulldocs
```
This will generate documents, stored in `/docs/build`.

## Usage

**For full example usage, see `[tutorial.ipynb](./tutorial.ipynb)`**

Below is example code to:
1. Create a device used in photostimulation
2. Simulate and store photostimulation ROIs
3. Store the time series corresponding to each stimulation
4. Record all time series and patterns used in an experiment in a table
5. Write the above to an NWB file and read it back


```python
from pynwb import NWBFile, NWBHDF5IO
from ndx_photostim import SpatialLightModulator, PhotostimulationDevice, HolographicPattern, PhotostimulationSeries, PhotostimulationTable
import numpy as np
from dateutil.tz import tzlocal
from datetime import datetime

# create an example NWB file
nwbfile = NWBFile('my first synthetic recording', 'EXAMPLE_ID', datetime.now(tzlocal()))

# store the spatial light modulator used
slm = SpatialLightModulator(name='example_SLM', description="example SLM", manufacturer="SLM manufacturer", size=[500, 500])

# create a container for the device used for photostimulation, and link the SLM to it
photostim_dev = PhotostimulationDevice(name='photostimulation_device', description="example photostimulation device",
                                       manufacturer="device manufacturer", type='LED', wavelength=320, opsin="example opsin")
photostim_dev.add_slm(slm)

# add the device to the NWB file
nwbfile.add_device(photostim_dev)

# simulate a mask of ROIs corresponding to stimulated regions in the FOV (5 ROIs on a 50x50 pixel image)
image_mask_roi = np.zeros((50, 50))
for _ in range(5):
    x = np.random.randint(0, 45)
    y = np.random.randint(0, 45)
    image_mask_roi[x:x + 5, y:y + 5] = 1

# store the stimulation as "pattern_1"
hp = HolographicPattern(name='pattern 1', image_mask_roi=image_mask_roi)

# show the mask
hp.show_mask()

# store the time steps in which 'hp' was presented (seconds 10-20 and 35-40)
stim_series = PhotostimulationSeries(name="series 2", format='interval',  holographic_pattern=hp)
stim_series.add_interval(10, 20)
stim_series.add_interval(35, 40)

# add the stimulus to the NWB file
nwbfile.add_stimulus(stim_series)

# create a table to store the time series/patterns for all stimuli together, along with experiment-specific parameters
stim_table = PhotostimulationTable(name='test', description='test desc', photostimulation_device=photostim_dev, 
                           stimulus_method='asas', sweeping_method="sweeping_method", time_per_sweep=0.01, num_sweeps=10)

# add the stimulus to the table
stim_table.add_series(stim_series)

# plot the timestamps when the stimulus was presented
stim_table.plot()

# create a processing module and add the PresentationTable to it
module = nwbfile.create_processing_module(name="photostimulation", description="example photostimulation table")
module.add(stim_table)

# write to an NWB file and read it back
with NWBHDF5IO("photostim_example.nwb", "w") as io:
    io.write(nwbfile)

with NWBHDF5IO("photostim_example.nwb", "r", load_namespaces=True) as io:
    read_nwbfile = io.read()

# Check the file & processing module
print(read_nwbfile)
print(read_nwbfile.processing['holographic_photostim'])

```

---



This extension was created using [ndx-template](https://github.com/nwb-extensions/ndx-template).

