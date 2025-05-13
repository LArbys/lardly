"""
Main application module for Lardly

This module initializes and runs the Dash application.
"""
import os
import argparse
from typing import List, Dict, Any, Optional

import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State

from lardly.ubdl.config.settings import config, load_config
from lardly.ubdl.core.state import state_manager
from lardly.ubdl.ui.io_navigation import make_io_navigation_widget, register_io_navigation_callbacks
from lardly.ubdl.ui.det3d_viewer import make_det3d_viewer, register_det3d_callbacks
from lardly.ubdl.io.io_manager import io_manager

# Import plotter implementations
from lardly.ubdl.plotters.implementations.reconu import RecoNuPlotter
from lardly.ubdl.plotters.registry import register_plotter

# Import wireplane viewer module
import lardly.ubdl.ui.wireplane_viewer as wireplane_viewer

def init_plotters() -> None:
    """
    Initialize and register all plotters
    """
    # Register all plotters
    register_plotter(RecoNuPlotter())
    
    # Add more plotters here as needed
    # register_plotter(CRTHitPlotter())
    # register_plotter(MCTruthPlotter())
    # etc.

def create_layout() -> html.Div:
    """
    Create the main application layout
    
    Returns:
        Dash HTML layout
    """
    return html.Div([
        # Navigation bar / header
        html.Div([
            html.H1("Lardly - Liquid Argon TPC Data Viewer", 
                   style={'textAlign': 'center'})
        ], style={
            'backgroundColor': '#f8f9fa',
            'padding': '10px',
            'marginBottom': '20px',
            'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)'
        }),
        
        # Main content
        html.Div([
            # Left panel - file navigation
            html.Div([
                make_io_navigation_widget(),
            ], style={
                'width': '30%', 
                'float': 'left',
                'padding': '10px',
                'backgroundColor': '#f8f9fa',
                'borderRadius': '5px',
                'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
                'marginRight': '20px'
            }),
            
            # Right panel - visualization
            html.Div([
                html.Hr(),
                # Wire plane viewer
                wireplane_viewer.make_wireplane_view_widget(),
                html.Hr(),
                # 3D detector viewer
                make_det3d_viewer(),
                html.Hr(),
            ], style={
                'width': '65%',
                'float': 'left',
                'padding': '10px',
                'backgroundColor': '#f8f9fa',
                'borderRadius': '5px',
                'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)'
            }),
        ], style={
            'display': 'flex',
            'flexWrap': 'wrap'
        }),
        
        # Footer
        html.Div([
            html.Hr(),
            html.P("Lardly - Liquid Argon TPC Data Viewer", 
                  style={'textAlign': 'center', 'fontStyle': 'italic'}),
        ], style={
            'clear': 'both',
            'padding': '10px',
            'marginTop': '20px',
            'backgroundColor': '#f8f9fa',
            'textAlign': 'center'
        }),
    ])

def register_callbacks(app):
    """Register all callbacks for the application"""
    # Register IO navigation callbacks
    register_io_navigation_callbacks(app)
    
    # Register wireplane viewer callbacks
    wireplane_viewer.register_dropdown_callback(app)
    
    # Register det3d callbacks
    register_det3d_callbacks(app)
    
    # Register plotter-specific callbacks
    from lardly.ubdl.plotters.registry import register_callbacks as register_plotter_callbacks
    register_plotter_callbacks(app)

def create_app():
    """Create and configure the Dash application"""
    app = dash.Dash(
        __name__,
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
        suppress_callback_exceptions=True,  # Allow for dynamic callbacks
    )
    
    # Initialize plotters
    init_plotters()
    
    # Set up the layout
    app.layout = create_layout()
    
    # Register callbacks
    register_callbacks(app)
    
    return app

def run_app(app: dash.Dash, port: Optional[int] = None, debug: Optional[bool] = None) -> None:
    """
    Run the Dash application
    
    Args:
        app: Dash application
        port: Optional port number, defaults to config value
        debug: Optional debug mode, defaults to config value
    """
    # Use provided values or defaults from config
    if port is None:
        port = config.get('ui', 'default_port', default=8891)
    
    if debug is None:
        debug = config.get('ui', 'debug_mode', default=True)
    
    # Run the app
    app.run_server(port=port, debug=debug)

def main() -> None:
    """
    Main entry point for the application
    """
    parser = argparse.ArgumentParser(description='Lardly - Liquid Argon TPC Data Viewer')
    parser.add_argument('--config', type=str, default='lardly.yaml',
                        help='Path to configuration file')
    parser.add_argument('--port', type=int, default=None,
                        help='Port number for the web server')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Load configuration
    load_config(args.config)
    
    # Create and run app
    app = create_app()
    run_app(app, port=args.port, debug=args.debug)

if __name__ == '__main__':
    main()