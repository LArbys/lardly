#!/usr/bin/env python3
"""
Lardly - Liquid Argon TPC Data Viewer

This script is the main entry point for the Lardly application.
"""
import os
import sys
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(description='Lardly - Liquid Argon TPC Data Viewer')
    parser.add_argument('--config', type=str, default='lardly.yaml',
                        help='Path to configuration file')
    parser.add_argument('--port', type=int, default=None,
                        help='Port number for the web server')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode')
    parser.add_argument('--files', type=str, nargs='+',
                        help='Data files to load on startup')
    parser.add_argument('--tick-direction', type=str, default='TickForwards',
                        choices=['TickForwards', 'TickBackwards'],
                        help='Tick direction for data processing')
    parser.add_argument('--entry', type=int, default=None,
                        help='Entry number to load on startup')
    parser.add_argument('--log-level', 
                   choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                   default='INFO', 
                   help='Set the logging level')
    
    args = parser.parse_args()
    
    # set the log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # Add the project root to the Python path if needed
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Import lardly modules
    try:
        from lardly.ubdl.config.settings import config, load_config
        from lardly.ubdl.core.app import create_app, run_app
        #from lardly.ubdl.io.io_manager import io_manager, load_files, load_entry
    except ImportError as e:
        logger.error(f"Error importing lardly modules: {e}")
        logger.error("Make sure lardly is installed or in the Python path")
        sys.exit(1)
    
    # Load configuration
    config_path = args.config
    if os.path.exists(config_path):
        logger.info(f"Loading configuration from {config_path}")
        if not load_config(config_path):
            logger.warning(f"Failed to load configuration from {config_path}, using defaults")
    else:
        logger.warning(f"Configuration file {config_path} not found, using defaults")
    
    # Override configuration with command line arguments
    if args.port is not None:
        config.set(args.port, 'ui', 'default_port')
    
    if args.debug:
        config.set(True, 'ui', 'debug_mode')
        logging.getLogger().setLevel(logging.DEBUG)

    # Create the application
    app = create_app()
    
    # Load files if specified
    if args.files:
        logger.info(f"Loading files: {args.files}")
        
        # Register callback to load files after app is initialized
        @app.callback(
            output=None,  # No output, this is just to trigger the function
            inputs=[dash.dependencies.Input('_hidden-init-trigger', 'children')]
        )
        def _load_files_on_startup(_):
            # Load files
            load_files(args.files, args.tick_direction)
            
            # Load entry if specified
            if args.entry is not None:
                load_entry(args.entry)
        
        # Add hidden div to trigger the callback
        app.layout.children.append(html.Div(id='_hidden-init-trigger', style={'display': 'none'}))
    
    # Run the application
    port = args.port if args.port is not None else config.get('ui', 'default_port', default=8891)
    debug = args.debug if args.debug is not None else config.get('ui', 'debug_mode', default=True)
    
    logger.info(f"Starting Lardly application on port {port} (debug={debug})")
    run_app(app, port=port, debug=debug)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.exception(f"Error running Lardly: {e}")
        sys.exit(1)
