# Lardly Batch Mode Examples

This directory contains example configuration files for running Lardly in batch mode to generate visualizations automatically.

## Usage

To run Lardly in batch mode with a configuration file:

```bash
python run_ubdl_app.py --batch --plot-config example_ubdl_viewer_config.yaml
```

This will:
1. Load the specified data files
2. Generate the configured visualizations
3. Save the output as an HTML file (and optionally images)
4. Exit without starting the interactive server

## Configuration Files

### Basic Examples

- **`config_mctruth_only.yaml`** - Minimal example showing only MC truth particles
- **`config_cosmic_analysis.yaml`** - Focus on cosmic ray muons and CRT data
- **`config_full_reconstruction.yaml`** - Shows all available reconstruction products

### Main Template

- **`../example_ubdl_viewer_config.yaml`** - Main template configuration file

## Configuration Structure

Each configuration file has the following sections:

1. **`input_files`** - Specify data files to load
2. **`entry`** - Which event entry to visualize (0-based)
3. **`output`** - Where to save the visualization
4. **`plots`** - Which plotters to enable and their options
5. **`viewer_3d`** - 3D viewer settings (camera, layout, etc.)
6. **`viewer_2d`** - 2D wireplane viewer settings (optional)

## Available Plotters

- `MCTruth` - MC truth particles (tracks, showers, vertices)
- `RecoNu` - Reconstructed neutrino information
- `CRT` - Cosmic Ray Tagger hits and tracks
- `IntimeFlash` - Optical flash information
- `LArFlowHits` - LArFlow hit reconstruction
- `NuInputClusters` - Neutrino input clusters

## Tips

1. Start with a minimal configuration and add plotters incrementally
2. Use `save_images: true` to generate static images for presentations
3. Adjust camera position for different viewing angles
4. Set `show_all_hits: false` for large events to improve performance
5. Use meaningful output filenames that include the entry number
6. Customize detector outline color with `detector_color: [R, G, B]` (RGB values 0-255)
7. Adjust `detector_opacity` to make the outline more or less visible

## Example Workflow

```bash
# 1. Copy and edit a configuration file
cp example_ubdl_viewer_config.yaml my_event_config.yaml
# Edit my_event_config.yaml with your file path and settings

# 2. Run batch mode
python run_ubdl_app.py --batch --plot-config my_event_config.yaml

# 3. Open the output HTML file in a web browser
firefox mctruth_visualization.html
```