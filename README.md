# ndx-photostim Extension for NWB

<div style="display:inline">
<div style="display:inline-grid">
<img src="./docs/images/nwb.png" height="60em" style="margin: 0em 0em 0em 0em; " align="right">
</div>
This is a <a href="https://www.nwb.org/">NeuroData Without Borders (NWB)</a> extension for storing data and metadata from <a href="https://www.nature.com/articles/nmeth.3217">holographic photostimulation</a>
methods. It includes containers for storing photostimulation-specific device parameters, holographic patterns 
(either 2D or 3D), and time series data related to photostimulation.
<img src="./docs/images/ext.png" height="60em" style="margin: 0em 0em 0em 0em;" align="right">
</div>

<br>We release five <a href="https://pynwb.readthedocs.io/en/stable/">PyNWB</a> containers as part of this extension:

* Two containers are used to store **device-specific metadata**: `SpatialLightModulator` and `PhotostimulationDevice`.
* `HolographicPattern` stores the **holographic pattern** used in stimulation.
* `PhotostimulationSeries` contains the **time series data** corresponding to the presentation of a given stimulus (where the stimulus is represented by a `HolographicPattern` container linked to the `PhotostimulationSeries`).
* We group **all time series & patterns for a given experiment** together using the `PhotostimulationTable` container. This object is a dynamic table, where each row in the table corresponds to a single `PhotostimulationSeries`. Additionally, the table links to the `StimulationDevice` used in the experiment.


## Background

<img src="./docs/images/Cap1.PNG" width="225em" align="left" style=" margin:0.5em 0.5em 0.5em 0.5em;">
State-of-the-art <a href="https://www.nature.com/articles/s41467-017-01031-3">holographic photostimulation methods</a>, used in concert with <a href="https://www.nature.com/articles/nmeth818">two-photon imaging</a>, 
allow unprecedented 
control and measurement of cell activity in the living brain. Methods for managing data for two-photon imaging 
experiments are improving, but there is little to no standardization of data for holographic stimulation methods. 
Stimulation in vivo depends on fine-tuning many experimental variables, which poses a challenge for reproducibility 
and data sharing between researchers. To improve <a href="https://www.sciencedirect.com/science/article/pii/S0896627321009557">standardization</a> of photostimulation data storage and processing, 
we release this extension as a generic data format for simultaneous holographic stimulation experiments, 
using the NWB format to store experimental details and data relating to both acquisition 
and photostimulation.

## Installation

To install the extension, first clone the `ndx_photostim` repository to the desired folder using the command
```angular2svg
git clone https://github.com/carlwharris/nwb-photostim.git
```
Then, to install the requisite python packages and extension, run:
```angular2svg
python -m pip install -r requirements.txt -r requirements-dev.txt
python setup.py install
```
The extension can then be imported into python scripts via `import ndx_photostim`.

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

<a href="https://pynwb.readthedocs.io/en/stable/software_process.html#continuous-integration">Unit and integration
tests</a> are implemented using <a href="https://docs.pytest.org/en/7.2.x/">pytest</a>, and can be run via the command 
`pytest` from the root of the extension directory. In addition, the
`pytest` command will also run a test of the example code above.

## Documentation

### Specification


Documentation for the extension's <a href="https://schema-language.readthedocs.io/en/latest/">specification</a>, which is based on the YAML files, is generated and stored in
the `./docs` folder. To create it, run the following from the home directory:
```angular2svg
cd docs
make fulldoc
```
This will save documentation to the `./docs/build` folder, and can be accessed via the 
`./docs/build/html/index.html` file.

### API

To generate documentation for the Python API (stores in `./api_docs`), we use <a href="https://www.sphinx-doc.org/en/master/">Sphinx</a> 
and a template from <a href="https://readthedocs.org/">ReadTheDocs</a>. API documentation can
be created by running 
```angular2svg
sphinx-build -b html api_docs/source/ api_docs/build/
```
from the home folder. Similar to the specification docs, API documentation is stored in `./api_docs/build`. Select 
`./api_docs/build/index.html` to access the API documentation in a website format.



This extension was created using [ndx-template](https://github.com/nwb-extensions/ndx-template).

