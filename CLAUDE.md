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
python run_ubdl_app.py --batch --plot-config examples/config_mctruth_only.yaml

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
- Generates visualizations without starting the web server
- Saves output as standalone HTML files
- Optionally exports static images (requires kaleido)

See `examples/` directory for configuration examples and `lardly/ubdl/config/plot_config_schema.yaml` for the full schema.