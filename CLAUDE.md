# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Running the Application

```bash
# Source the environment
source setenv.sh

# Run the main application with a data file
python run_ubdl_app.py --files [path/to/datafile.root] --port 8891

# Run in batch mode with configuration file
python run_ubdl_app.py --batch --plot-config example_ubdl_viewer_config.yaml

# Run specific test viewers
python test_dlmerged.py --input-file [dlmerged root file] -e 0 -p 8005
python test_3d.py [options]
python test_crt.py [options]
```

### Development Setup on Fermilab Machines

```bash
# SSH with port forwarding
ssh -XY -L 8005:localhost:8005 username@uboonebuild02.fnal.gov

# Setup environment
source /cvmfs/uboone.opensciencegrid.org/products/setup_uboone.sh
setup dllee_unified v1_0_3 -q e17:prof

# First time only: install dependencies
pip install --user plotly dash==1.8.0
```

## Architecture Overview

Lardly is a web-based visualization tool for Liquid Argon Time Projection Chamber (LAr TPC) data from particle physics experiments. It uses Plotly Dash to create interactive 3D and 2D views.

### Key Components

- **`lardly/ubdl/core/`**: Application core
  - `app.py`: Main Dash application setup and layout
  - `state.py`: Global state management

- **`lardly/ubdl/plotters/`**: Modular plotting system
  - `base.py`: Abstract base class for all plotters
  - `registry.py`: Plotter registration and management
  - `implementations/`: Concrete plotter implementations (CRT, MC truth, reconstruction, etc.)

- **`lardly/data/`**: Data format handlers
  - Support for larlite (light-weight LAr data format) and larcv (computer vision format)
  - Handlers for various physics objects: tracks, showers, hits, optical flashes, etc.

- **`lardly/ubdl/ui/`**: User interface components
  - `det3d_viewer.py`: 3D detector visualization
  - `wireplane_viewer.py`: 2D wire plane projections
  - `io_navigation.py`: File and event navigation

### Adding New Plotters

To add a new visualization type:

1. Create a new plotter class in `lardly/ubdl/plotters/implementations/`
2. Inherit from `BasePlotter` and implement required methods
3. Register the plotter in `app.py`'s `init_plotters()` function

### Batch Mode Architecture

Key components added for automated visualization generation:

- **`lardly/ubdl/batch_runner.py`**: Main batch processing engine
  - `BatchRunner.generate_3d_visualization()`: Creates 3D plots with detector outline
  - `BatchRunner.generate_2d_wireplane_figures()`: Creates 2D wireplane heatmaps
  - `BatchRunner._create_combined_html()`: Combines all plots into single HTML file
- **Extended Config system**: `lardly/ubdl/config/settings.py` with plot-specific methods
- **Tick direction support**: Properly configures IOManager for TickForwards/TickBackwards
- **Available plotters**: MCTruth, RecoNu, CRT, IntimeFlash, LArFlowHits, NuInputClusters

### Data Flow

1. Data files (ROOT format) are loaded via `io_manager`
2. Event data is parsed by format-specific handlers in `lardly/data/`
3. Plotters convert physics objects into Plotly traces
4. UI components display the traces with interactive controls

## Dependencies

- **Physics Software**: larlite, larcv, larutil (from CVMFS or local builds)
- **Python**: Plotly, Dash, NumPy, collada
- **ROOT**: CERN's data analysis framework
- **Environment**: Requires either `ubdl` or `dllee_unified` repositories

## Batch Mode

The application supports batch mode for automated visualization generation:

```bash
python run_ubdl_app.py --batch --plot-config config.yaml
```

This mode:
- Loads data files specified in the configuration
- Generates both 3D and 2D wireplane visualizations automatically
- Saves output as standalone HTML files with embedded JavaScript
- Optionally exports static images (requires kaleido)
- Respects tick_direction configuration (TickForwards/TickBackwards)

### Batch Mode Features:
- **3D Visualization**: Particle tracks, showers, detector outline, optical flashes
- **2D Wireplane Views**: Automatically generated for all three planes (U, V, Y)
- **Combined HTML Output**: Professional layout with both 3D and 2D sections
- **Configuration-driven**: Specify which plotters to enable and their options
- **Detector Outline Color**: Configurable via `detector_color: [R, G, B]` (RGB 0-255)

### Configuration Structure:
```yaml
plot_config:
  input_files:
    - path: /path/to/file.root
      tick_direction: TickBackwards  # or TickForwards
  entry: 10
  output:
    html_file: visualization.html
    save_images: true
  plots:
    - name: "MC Truth"
      type: "MCTruth"
      enabled: true
  viewer_3d:
    detector_color: [150, 200, 255]  # Light blue
  viewer_2d:
    enabled: true
    colorscale: 'Viridis'
```

See `examples/` directory for configuration examples and `lardly/ubdl/config/plot_config_schema.yaml` for the full schema.