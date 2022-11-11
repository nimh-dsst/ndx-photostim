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
Then, to install the requisite python packages and install the extension, run:
```angular2svg
python -m pip install -r requirements.txt -r requirements-dev.txt
python setup.py install
```
The extension can then be imported into python via `import ndx_photostim`.

## Usage

**For full example usage, see [tutorial.ipynb](./tutorial.ipynb)**

Below is example code to:
1. Create a device used in photostimulation
2. Simulate and store photostimulation ROIs
3. Store the time series corresponding to each stimulation
4. Record all time series and patterns used in an experiment in a table
5. Write the above to an NWB file and read it back


```python
import numpy as np
from dateutil.tz import tzlocal
from datetime import datetime
from pynwb import NWBFile, NWBHDF5IO
from ndx_photostim import SpatialLightModulator, PhotostimulationDevice, HolographicPattern, \
    PhotostimulationSeries, PhotostimulationTable

# create an example NWB file
nwbfile = NWBFile('nwb-photostim_example', 'EXAMPLE_ID', datetime.now(tzlocal()))

# store the spatial light modulator used
slm = SpatialLightModulator(name='example_SLM', description="example SLM", manufacturer="SLM manufacturer",
                            size=[500, 500])

# create a container for the device used for photostimulation, and link the SLM to it
device = PhotostimulationDevice(name="device", description="...", manufacturer="manufacturer", type="LED",
                                wavelength=320, opsin='test_opsin', power=10, peak_pulse_energy=20, pulse_rate=5)
device.add_slm(slm)

# add the device to the NWB file
nwbfile.add_device(device)

# simulate a mask of ROIs corresponding to stimulated regions in the FOV (5 ROIs on a 50x50 pixel image)
image_mask_roi = np.zeros((50, 50))
for _ in range(5):
    x = np.random.randint(0, 45)
    y = np.random.randint(0, 45)
    image_mask_roi[x:x + 5, y:y + 5] = 1

# store the stimulation as "pattern_1"
hp = HolographicPattern(name='pattern_1', image_mask_roi=image_mask_roi)

# show the mask
hp.show_mask()

# store the time steps in which 'hp' was presented (seconds 10-20 and 35-40)
stim_series = PhotostimulationSeries(name="series 2", format='interval', pattern=hp,
                                     stimulus_method="stim_method", sweep_pattern="...", time_per_sweep=10,
                                     num_sweeps=20)
stim_series.add_interval(10, 20)
stim_series.add_interval(35, 40)

# add the stimulus to the NWB file
nwbfile.add_stimulus(stim_series)

# create a table to store the time series/patterns for all stimuli together, along with experiment-specific
# parameters
stim_table = PhotostimulationTable(name="test_table", description="test_description", device=device)

# add the stimulus to the table
stim_table.add_series(stim_series)

# plot the timestamps when the stimulus was presented
stim_table.plot_presentation_times()

# create a processing module and add the PresentationTable to it
module = nwbfile.create_processing_module(name="photostimulation", description="example photostimulation table")
module.add(stim_table)

# write to an NWB file and read it back
with NWBHDF5IO("example_file.nwb", "w") as io:
    io.write(nwbfile)

with NWBHDF5IO("example_file.nwb", "r", load_namespaces=True) as io:
    read_nwbfile = io.read()

    # Check the file & processing module
    print(read_nwbfile)
    print(read_nwbfile.processing['photostimulation'])
```
## Running tests

Unit and integration tests can run via the command `pytest` from the root of the extension directory. In addition,
`pytest` will also test that the example section of this document functions runs.


### Specification docs

Documentation for the extension's specification, which is based on the YAML files, is generated and stored in
the `./docs` folder. To generate this documentation, navigate to this folder (i.e., `cd docs`) and run the command
```angular2svg
make fulldoc
```
This will produce documentation in `./docs/build`, which can be accessed via the 
`./docs/build/html/index.html` file.

### API docs

To generate documentation for the Python API, we use Sphinx and a template from ReadTheDocs. API documentation can
be created by running 
```angular2svg
sphinx-build -b html api_docs/source/ api_docs/build/
```
from the home folder. As with the specification docs, documentation is stored in `./api_docs/build`. Select 
`./api_docs/build/html/index.html` to access the API documentation in a website format.

This extension was created using [ndx-template](https://github.com/nwb-extensions/ndx-template).

