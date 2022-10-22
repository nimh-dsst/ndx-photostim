# ndx-photostim Extension for NWB

This is an NWB extension for storing holographic photostimulation data.

* **Device metadata** Two containers are used to store device-specific metadata, `SpatialLightModulator` and `PhotostimulationDevice`,
* **Stimulation pattern** A container called `HolographicPattern` is used to store the pattern used in the stimulation.
* **Presentation data** `PhotostimulationSeries` is used to store the timeseries data corresponding to the presentation for a given simulation pattern
(represented by a `HolographicPattern` container than is stored within `PhotostimulationSeries`).
* **Multiple stimulation patterns** We group all `PhotostimulationSeries` containers (i.e., the set of stimulation time series/pattern pairs), along
with the `StimulationDevice` used to collect the patterns, into a dynamic table called `PhotostimulationTable`. This allows all
stimulation data and metadata for a given experiment to be grouped together clearly.

## Installation

First, clone the `ndx_photostim` repository in the desired folder using the command
```angular2svg
git clone hhttps://github.com/carlwharris/nwb-photostim.git
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

Below is example code to:
1. Create a device used in photostimulation
2. Simulate and store photostimulation ROIs
3. Store the time series corresponding to each stimulation
4. Record all time series and patterns used in an experiment in a table
5. Write the above to an NWB file and read it back

```python
# create an example NWB file
nwbfile = NWBFile('my first synthetic recording', 'EXAMPLE_ID', datetime.now(tzlocal()))

# store the spatial light modulator used
slm = SpatialLightModulator(name='example_SLM', description="example SLM", manufacturer="SLM manufacturer", size=[500, 500])

# create a container for the device used for photostimulation, and link the SLM to it
photostim_dev = PhotostimulationDevice(name='photostimulation_device', description="example photostimulation device",
                                       manufacturer="device manufacturer", type='LED', wavelength=320, opsin="example opsin", slm=slm)
photostim_dev.add_slm(slm)

# add the device to the NWB file
nwbfile.add_device(photostim_dev)

image_mask_roi = np.zeros((50, 50))

# simulate a mask of ROIs corresponding to stimulated regions in the FOV (5 ROIs on a 50x50 pixel image)
n_rois = 5
for _ in range(n_rois):
    x = np.random.randint(0, 45)
    y = np.random.randint(0, 45)
    mask_roi[x:x + 5, y:y + 5] = 1

# store the stimulation as "pattern_1"
hp_1 = HolographicPattern(name='pattern_1', image_mask_roi=mask_roi)

# store the time steps in which 'hp' was presented 
stim_series_1 = PhotostimulationSeries(name="series_1", format='interval', holographic_pattern=hp_1, 
                                       data=[1, -1, 1, -1], timestamps=[0.5, 1, 2, 4])

# add the stimulus to the NWB file
nwbfile.add_stimulus(stim)

# create a table to store the time series/patterns for all stimuli together, along with experiment-specific parameters
sp = StimulusPresentation(name='test', description='test desc', photostimulation_device=photostim_dev, stimulus_method='asas')

# add the stimulus to the table
sp.add_series(sp)

# create a processing module and add the PresentationTable to it
behavior_module = nwbfile.create_processing_module(name="holographic_photostim", description="initial data")
behavior_module.add(sp)

# write to an NWB file and read it back
with NWBHDF5IO("photostim_example.nwb", "w") as io:
    io.write(sp)

with NWBHDF5IO("photostim_example.nwb", "r", load_namespaces=True) as io:
    read_nwbfile = io.read()
```

---



This extension was created using [ndx-template](https://github.com/nwb-extensions/ndx-template).

