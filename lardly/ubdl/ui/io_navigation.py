"""
IO Navigation UI Component

This module provides UI components and callbacks for navigating through data files.
"""
import os
from typing import List, Dict, Any
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State

from lardly.ubdl.io.io_manager import io_manager, load_files, load_entry
from lardly.ubdl.core.state import state_manager
from lardly.ubdl.plotters.registry import get_applicable_plotters

def make_io_navigation_widget() -> html.Div:
    """
    Create the IO navigation widget
    
    Returns:
        Dash component for IO navigation
    """
    return html.Div([
        html.H3("File Info"),
        html.Label("Enter dlmerged path (required):"),
        dcc.Textarea(
            id='file-path-input-dlmerged',
            placeholder='List input dlmerged file(s) ...',
            style={'width': '100%', 'marginBottom': '5px', 'height': '100px'}
        ),
        dcc.RadioItems(
            id='tick-direction',
            options=[
                {'label': 'Tick Forwards', 'value': 'TickForwards'},
                {'label': 'Tick Backwards', 'value': 'TickBackwards'}
            ],
            value='TickForwards'
        ),
        html.Button("Load file", id='button-load-dlmerged'),
        html.Hr(),
        html.Div(
            [html.Label('Number of entries: 0', id='io-nav-num-entries')],
            style={'width': '100%'}
        ),
        html.Div(
            [html.Label('Current Entry: Not loaded.', id='io-nav-current-entry')],
            style={'width': '100%'}
        ),
        html.Div([
            dcc.Input(
                id='io-nav-entry-input',
                type='text',
                placeholder='Choose entry number ...',
                style={'width': '300px', 'marginBottom': '5px'}
            ),
            html.Button(
                "Load Entry",
                id='io-nav-button-load-entry',
                style={'width': '100px'}
            )
        ]),
        html.Hr(),
        html.Div(
            [html.H5("Error Messages")],
            id='error-message',
            style={'color': 'red'}
        ),
    ], id='io-navigation')

def register_io_navigation_callbacks(app: dash.Dash) -> None:
    """
    Register callbacks for the IO navigation widget
    
    Args:
        app: Dash application
    """
    @app.callback(
        [Output('io-nav-num-entries', 'children'),
         Output('wireplane-viewer-dropdown', 'options'),
         Output('det3d-viewer-checklist-plotchoices', 'options'),
         Output('error-message', 'children')],
        Input('button-load-dlmerged', 'n_clicks'),
        [State('file-path-input-dlmerged', 'value'),
         State('tick-direction', 'value')]
    )
    def update_filepath(n_clicks, textbox_input, tick_direction):
        """
        Update file path and load files
        
        Args:
            n_clicks: Number of button clicks
            textbox_input: File paths from textbox
            tick_direction: Tick direction selection
            
        Returns:
            Updated UI components
        """
        if n_clicks is None or textbox_input is None:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        # Parse file paths
        file_paths = textbox_input.strip().split()
        
        # Check if all files exist
        for file_path in file_paths:
            if not os.path.exists(file_path):
                err_msgs = [
                    html.H5("Error Messages"),
                    html.Label(f'File path does not exist: {file_path}')
                ]
                return dash.no_update, dash.no_update, dash.no_update, err_msgs
        
        # Load files
        if not load_files(file_paths, tick_direction):
            err_msgs = [
                html.H5("Error Messages"),
                html.Label('Failed to load files')
            ]
            return dash.no_update, dash.no_update, dash.no_update, err_msgs
        
        # Get available trees
        available_trees = io_manager.get_available_trees()
        total_entries = io_manager.get_total_entries()
        
        # Get available plotter options
        plotter_options = []
        plotters = get_applicable_plotters(available_trees)
        for name, description in plotters:
            plotter_options.append({'label': description, 'value': name})
        
        # Get wire plane options
        wire_plane_options = []
        for tree in available_trees:
            if "image2d_" in tree:
                wire_plane_options.append({'label': tree, 'value': tree})
        
        err_msgs = [
            html.H5("Error Messages", style={'width': '100%'}),
            html.Label('No errors')
        ]
        
        return f'Number of Entries: {total_entries}', wire_plane_options, plotter_options, err_msgs
    
    @app.callback(
        [Output('io-nav-current-entry', 'children')],
        Input('io-nav-button-load-entry', 'n_clicks'),
        [State('io-nav-entry-input', 'value')]
    )
    def io_nav_load_entry(n_clicks, entry_text):
        """
        Load a specific entry
        
        Args:
            n_clicks: Number of button clicks
            entry_text: Entry number input
            
        Returns:
            Updated current entry label
        """
        if n_clicks is None or entry_text is None:
            return dash.no_update
        
        try:
            entry = int(entry_text.strip())
        except ValueError:
            return ['Current Entry: Invalid entry number']
        
        if not io_manager.is_loaded():
            return ['Current Entry: No files loaded']
        
        if load_entry(entry):
            return [f'Current Entry Loaded: {entry}']
        else:
            total_entries = io_manager.get_total_entries()
            return [f'Current Entry: Failed to load entry {entry}. Valid range: 0-{total_entries-1}']