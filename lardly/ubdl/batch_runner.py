"""
Batch mode runner for automated plot generation

This module provides functionality to run Lardly in batch mode,
generating visualizations based on configuration files without
launching the interactive Dash server.
"""
import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from lardly.ubdl.config.settings import config, load_config
from lardly.ubdl.core.state import state_manager
from lardly.ubdl.io.io_manager import io_manager
from lardly.ubdl.plotters.registry import registry, register_plotter
from lardly.detectoroutline import DetectorOutline

# Import plotter implementations
from lardly.ubdl.plotters.implementations.reconu import RecoNuPlotter
from lardly.ubdl.plotters.implementations.mctruth import MCTruthPlotter
from lardly.ubdl.plotters.implementations.crt import CRTPlotter
from lardly.ubdl.plotters.implementations.intimeflash import IntimeFlashPlotter
from lardly.ubdl.plotters.implementations.nuinputclusters import NuInputClustersPlotter
from lardly.ubdl.plotters.implementations.larflowhits import LArFlowHitsPlotter

logger = logging.getLogger(__name__)

class BatchRunner:
    """
    Batch runner for automated visualization generation
    """
    
    def __init__(self, config_file: str):
        """
        Initialize batch runner with configuration file
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.fig_3d = None
        self.fig_2d = None
        self.traces_3d = []
        self.traces_2d = []
        
        # Initialize plotters
        self._init_plotters()
    
    def _init_plotters(self) -> None:
        """
        Initialize and register all available plotters
        """
        # Register all plotters
        register_plotter(RecoNuPlotter())
        register_plotter(MCTruthPlotter())
        register_plotter(CRTPlotter())
        register_plotter(IntimeFlashPlotter())
        register_plotter(NuInputClustersPlotter())
        register_plotter(LArFlowHitsPlotter())
        
    def load_configuration(self) -> bool:
        """
        Load configuration from file
        
        Returns:
            True if configuration loaded successfully
        """
        success = load_config(self.config_file)
        if not success:
            logger.error(f"Failed to load configuration from {self.config_file}")
            return False
            
        plot_config = config.get_plot_config()
        if not plot_config:
            logger.error("No plot_config section found in configuration")
            return False
            
        return True
    
    def load_data_files(self) -> bool:
        """
        Load data files specified in configuration
        
        Returns:
            True if files loaded successfully
        """
        input_files = config.get_input_files()
        if not input_files:
            logger.error("No input files specified in configuration")
            return False
        
        # Collect file paths and tick directions
        file_paths = []
        tick_dirs = []
        
        for file_info in input_files:
            path = file_info.get('path')
            if not path:
                logger.error("Input file missing 'path' field")
                return False
                
            if not os.path.exists(path):
                logger.error(f"Input file not found: {path}")
                return False
                
            file_paths.append(path)
            tick_dirs.append(file_info.get('tick_direction', 'TickForwards'))
        
        # Load files into io_manager
        try:
            io_manager.load_files(file_paths, tick_dirs)
            logger.info(f"Loaded {len(file_paths)} data files")
            
            # Load the specified entry
            plot_config = config.get_plot_config()
            entry = plot_config.get('entry', 0)
            
            if entry >= io_manager.get_total_entries():
                logger.error(f"Entry {entry} exceeds total entries ({io_manager.get_total_entries()})")
                return False
                
            io_manager.load_entry(entry)
            logger.info(f"Loaded entry {entry}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading data files: {e}")
            return False
    
    def initialize_plotters(self) -> List[Any]:
        """
        Initialize and filter plotters based on configuration
        
        Returns:
            List of initialized plotters
        """
        enabled_plots = config.get_enabled_plots()
        if not enabled_plots:
            logger.warning("No plots enabled in configuration")
            return []
        
        # Get plotter instances
        active_plotters = []
        for plot_config in enabled_plots:
            plot_type = plot_config.get('type')
            if not plot_type:
                logger.warning(f"Plot configuration missing 'type': {plot_config}")
                continue
            
            plotter = registry.get_plotter(plot_type)
            if not plotter:
                logger.warning(f"Unknown plotter type: {plot_type}")
                continue
            
            # Check if plotter is applicable
            available_trees = io_manager.get_available_trees()
            if plotter.is_applicable(available_trees):
                # Set plotter options from config
                options = plot_config.get('options', {})
                for key, value in options.items():
                    state_manager.set_state(value, plot_type, key)
                
                active_plotters.append({
                    'plotter': plotter,
                    'config': plot_config,
                    'type': plot_type
                })
                logger.info(f"Initialized plotter: {plot_config.get('name', plot_type)}")
            else:
                logger.warning(f"Plotter not applicable: {plot_type}")
        
        return active_plotters
    
    def generate_3d_visualization(self, plotters: List[Dict[str, Any]]) -> go.Figure:
        """
        Generate 3D visualization figure
        
        Args:
            plotters: List of plotter configurations
            
        Returns:
            Plotly figure object
        """
        # Get viewer configuration
        viewer_config = config.get_viewer_3d_config()
        
        # Create figure
        fig = go.Figure()
        
        # Add detector outline if requested
        if viewer_config.get('show_detector', True):
            # Add detector outline
            detector_outline = DetectorOutline()
            detector_color = viewer_config.get('detector_color', [100, 150, 200])  # Default light blue
            detector_traces = detector_outline.getlines(color=tuple(detector_color))
            for trace in detector_traces:
                trace['opacity'] = viewer_config.get('detector_opacity', 0.1)
                fig.add_trace(trace)
        
        # Generate traces from each plotter
        for plotter_info in plotters:
            plotter = plotter_info['plotter']
            plot_name = plotter_info['config'].get('name', plotter_info['type'])
            
            try:
                # Get tree dictionary from IO manager
                tree_dict = io_manager.get_tree_dict()
                traces = plotter.make_traces(tree_dict)
                if traces:
                    # Add plotter name to trace names for legend
                    for trace in traces:
                        if 'name' in trace:
                            trace['name'] = f"{plot_name}: {trace['name']}"
                        else:
                            trace['name'] = plot_name
                    
                    for trace in traces:
                        fig.add_trace(trace)
                    
                    logger.info(f"Added {len(traces)} traces from {plot_name}")
                    
            except Exception as e:
                logger.error(f"Error generating traces from {plot_name}: {e}")
        
        # Update layout
        layout_config = viewer_config.get('layout', {})
        camera_config = viewer_config.get('camera', {})
        
        fig.update_layout(
            scene=dict(
                camera=camera_config,
                xaxis=dict(title='X (cm)'),
                yaxis=dict(title='Y (cm)'),
                zaxis=dict(title='Z (cm)'),
                aspectmode='data'
            ),
            width=layout_config.get('width', 1200),
            height=layout_config.get('height', 800),
            showlegend=layout_config.get('showlegend', True),
            paper_bgcolor=layout_config.get('paper_bgcolor', 'white'),
            plot_bgcolor=layout_config.get('plot_bgcolor', 'rgba(0,0,0,0)'),
            title=layout_config.get('title', 'Lardly 3D Visualization')
        )
        
        return fig
    
    def save_visualization(self, fig: go.Figure, output_config: Dict[str, Any]) -> bool:
        """
        Save visualization to HTML and optionally images
        
        Args:
            fig: Plotly figure to save
            output_config: Output configuration
            
        Returns:
            True if saved successfully
        """
        try:
            # Save HTML file
            html_file = output_config.get('html_file', 'output.html')
            html_path = Path(html_file)
            
            # Create directory if needed
            html_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write HTML with embedded plotly.js for standalone viewing
            fig.write_html(
                str(html_path),
                include_plotlyjs='cdn',  # Use CDN for smaller file size
                config={'displayModeBar': True, 'displaylogo': False}
            )
            logger.info(f"Saved HTML visualization to {html_path}")
            
            # Save images if requested
            if output_config.get('save_images', False):
                image_format = output_config.get('image_format', 'png')
                image_dir = Path(output_config.get('image_dir', './images'))
                image_dir.mkdir(parents=True, exist_ok=True)
                
                # Generate image filename from HTML filename
                image_name = html_path.stem + f'.{image_format}'
                image_path = image_dir / image_name
                
                # Save image (requires kaleido package)
                try:
                    if image_format == 'png':
                        fig.write_image(str(image_path), width=1400, height=900, scale=2)
                    elif image_format == 'svg':
                        fig.write_image(str(image_path))
                    elif image_format == 'jpeg':
                        fig.write_image(str(image_path), width=1400, height=900, scale=2)
                    else:
                        logger.warning(f"Unknown image format: {image_format}")
                        
                    logger.info(f"Saved image to {image_path}")
                    
                except Exception as e:
                    logger.warning(f"Could not save image (install kaleido for image export): {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving visualization: {e}")
            return False
    
    def run(self) -> bool:
        """
        Run the batch visualization generation
        
        Returns:
            True if successful
        """
        logger.info(f"Starting batch run with config: {self.config_file}")
        
        # Load configuration
        if not self.load_configuration():
            return False
        
        # Load data files
        if not self.load_data_files():
            return False
        
        # Initialize plotters
        plotters = self.initialize_plotters()
        if not plotters:
            logger.warning("No active plotters, nothing to visualize")
            return False
        
        # Generate 3D visualization
        fig_3d = self.generate_3d_visualization(plotters)
        
        # Save visualization
        output_config = config.get_output_config()
        if not self.save_visualization(fig_3d, output_config):
            return False
        
        logger.info("Batch run completed successfully")
        return True

def run_batch(config_file: str) -> bool:
    """
    Run batch visualization from configuration file
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        True if successful
    """
    runner = BatchRunner(config_file)
    return runner.run()