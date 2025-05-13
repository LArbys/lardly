"""
Wire Plane Viewer Component

This module provides UI components and callbacks for visualizing wire plane data.
"""
import os
import traceback
from typing import List, Dict, Any, Optional, Tuple, Union

import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import numpy as np

from lardly.ubdl.io.io_manager import io_manager
from lardly.ubdl.core.state import state_manager

def make_wireplane_view_widget() -> html.Div:
    """
    Create the wire plane view widget
    
    Returns:
        Dash component for wire plane viewer
    """
    # Create empty figures
    empty_lo = go.Layout(
        title='Empty Wire Plane',
        autosize=True,
        hovermode='closest',
        showlegend=False
    )
    
    empty_plot = go.Heatmap(
        name="empty",
        z=np.zeros((101, 346)),
        x=np.linspace(0, 3460, 346),
        y=np.linspace(2400, 2400 + 101 * 60, 101)
    )
    
    empty_fig = go.Figure(data=[empty_plot], layout=empty_lo)
    
    return html.Div([
        html.H3('Wire Plane Viewer'),
        html.Label("Select Image Sources"),
        dcc.Dropdown(
            id='wireplane-viewer-dropdown',
            options=[],
            value=None
        ),
        
        # Three plane views
        html.Div([
            # U plane
            html.Div(
                dcc.Graph(
                    figure=empty_fig,
                    id='plane0-graph'
                ),
                style={'display': 'inline-block', 'padding': '0px', 'width': '32%'}
            ),
            
            # V plane
            html.Div(
                dcc.Graph(
                    figure=empty_fig,
                    id='plane1-graph'
                ),
                style={'display': 'inline-block', 'padding': '0px', 'width': '32%'}
            ),
            
            # Y plane
            html.Div(
                dcc.Graph(
                    figure=empty_fig,
                    id='plane2-graph'
                ),
                style={'display': 'inline-block', 'padding': '0px', 'width': '32%'}
            )
        ]),
        
        # Options for display
        html.Div([
            html.Label("Display Options:"),
            html.Div([
                html.Label("Color Scale:"),
                dcc.Dropdown(
                    id='wireplane-colorscale-dropdown',
                    options=[
                        {'label': 'Jet', 'value': 'Jet'},
                        {'label': 'Viridis', 'value': 'Viridis'},
                        {'label': 'Plasma', 'value': 'Plasma'},
                        {'label': 'Hot', 'value': 'Hot'},
                        {'label': 'Greys', 'value': 'Greys'}
                    ],
                    value='Jet'
                )
            ], style={'width': '20%', 'display': 'inline-block', 'margin': '10px'}),
            
            html.Div([
                html.Label("Min Value:"),
                dcc.Input(
                    id='wireplane-min-value',
                    type='number',
                    value=0,
                    step=1
                )
            ], style={'width': '15%', 'display': 'inline-block', 'margin': '10px'}),
            
            html.Div([
                html.Label("Max Value:"),
                dcc.Input(
                    id='wireplane-max-value',
                    type='number',
                    value=200,
                    step=10
                )
            ], style={'width': '15%', 'display': 'inline-block', 'margin': '10px'}),
            
            html.Div([
                html.Label("Reverse Ticks:"),
                dcc.Checklist(
                    id='wireplane-reverse-ticks',
                    options=[{'label': '', 'value': 'reverse'}],
                    value=[]
                )
            ], style={'width': '15%', 'display': 'inline-block', 'margin': '10px'}),
            
            html.Button(
                "Update Display",
                id='wireplane-update-button',
                style={'margin': '10px'}
            )
        ], style={'margin': '10px'})
    ], id='wireplane-viewer', style={'width': '99%', 'display': 'inline-block'})

def visualize_larcv_image2d(image2d, minz=0.0, maxz=200.0, reverse_ticks=False, colorscale="Jet"):
    """
    Create a heatmap visualization of a larcv::Image2D
    
    Args:
        image2d: larcv::Image2D object
        minz: Minimum value for color scale
        maxz: Maximum value for color scale
        reverse_ticks: Whether to reverse the tick axis
        colorscale: Colorscale to use
        
    Returns:
        Plotly heatmap trace
    """
    from larcv import larcv
    
    meta = image2d.meta()
    imgnp = np.transpose(larcv.as_ndarray(image2d), (1, 0))
    
    # Adjust x-axis for planes 0 and 1
    if meta.plane() in [0, 1]:
        imgnp = imgnp[:, 0:2400]
        maxx = 2400.0
    else:
        maxx = meta.max_x()
        
    # Create axis arrays
    xaxis = np.linspace(meta.min_x(), maxx, endpoint=False, num=int(maxx / meta.pixel_width()))
    yaxis = np.linspace(meta.min_y(), meta.max_y(), endpoint=False, num=meta.rows())
    
    # Apply limits to image data
    imgnp[imgnp < minz] = 0
    imgnp[imgnp > maxz] = maxz
    
    # Reverse ticks if requested
    if reverse_ticks:
        imgnp = np.flip(imgnp, axis=0)
    
    # Create heatmap
    heatmap = {
        "type": "heatmap",
        "z": imgnp,
        "x": xaxis,
        "y": yaxis,
        "colorscale": colorscale,
    }
    
    return heatmap

def register_dropdown_callback(app: dash.Dash) -> None:
    """
    Register callbacks for the wire plane viewer
    
    Args:
        app: Dash application
    """
    @app.callback(
        [Output('plane0-graph', 'figure'),
         Output('plane1-graph', 'figure'),
         Output('plane2-graph', 'figure')],
        [Input('wireplane-viewer-dropdown', 'value'),
         Input('wireplane-update-button', 'n_clicks')],
        [State('plane0-graph', 'figure'),
         State('plane1-graph', 'figure'),
         State('plane2-graph', 'figure'),
         State('wireplane-colorscale-dropdown', 'value'),
         State('wireplane-min-value', 'value'),
         State('wireplane-max-value', 'value'),
         State('wireplane-reverse-ticks', 'value')]
    )
    def update_wireplane_viewer(
        tree_value, n_clicks, fig_plane0, fig_plane1, fig_plane2, 
        colorscale, min_value, max_value, reverse_ticks
    ):
        """
        Update wire plane viewer based on selected tree and display options
        
        Args:
            tree_value: Selected tree
            n_clicks: Number of button clicks
            fig_plane0: Current U plane figure
            fig_plane1: Current V plane figure
            fig_plane2: Current Y plane figure
            colorscale: Selected color scale
            min_value: Minimum value for color scale
            max_value: Maximum value for color scale
            reverse_ticks: Whether to reverse ticks
            
        Returns:
            Updated figures for all three planes
        """
        # Get the context that triggered the callback
        ctx = dash.callback_context
        if not ctx.triggered:
            # No trigger, just return current figures
            return dash.no_update, dash.no_update, dash.no_update
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # If triggered by update button without a selected tree, do nothing
        if trigger_id == 'wireplane-update-button' and tree_value is None:
            return dash.no_update, dash.no_update, dash.no_update
        
        # If no tree is selected, return current figures
        if tree_value is None or tree_value == "none" or tree_value == "None":
            return dash.no_update, dash.no_update, dash.no_update
        
        try:
            # Get the IO manager
            iolarcv = io_manager._larcv_io
            if iolarcv is None:
                raise ValueError("larcv IO manager is not initialized")
                
            # Get the image product name from the tree name
            treename = str(tree_value).strip()
            prodname = treename.replace("image2d_", "").replace("_tree", "")
            
            # Get the image data
            ev_imgs = iolarcv.get_data("image2d", prodname)
            img_v = ev_imgs.as_vector()
            
            # Apply reverse ticks option
            do_reverse_ticks = 'reverse' in reverse_ticks
            
            # Ensure min/max values make sense
            if min_value is None:
                min_value = 0
            if max_value is None:
                max_value = 200
            if max_value <= min_value:
                max_value = min_value + 1
                
            # Create new figures for each plane
            figures = []
            for plane in range(3):
                # Create layout
                layout = go.Layout(
                    title=f'Plane[{plane}]',
                    autosize=True,
                    hovermode='closest',
                    showlegend=False
                )
                
                # Create trace if this plane exists in the data
                if plane < img_v.size():
                    trace = visualize_larcv_image2d(
                        img_v.at(plane),
                        minz=min_value,
                        maxz=max_value,
                        reverse_ticks=do_reverse_ticks,
                        colorscale=colorscale
                    )
                    figures.append(go.Figure(data=[trace], layout=layout))
                else:
                    # Use empty figure for missing planes
                    figures.append(dash.no_update)
                    
            # Return figures for all three planes
            return figures[0] if len(figures) > 0 else dash.no_update, \
                   figures[1] if len(figures) > 1 else dash.no_update, \
                   figures[2] if len(figures) > 2 else dash.no_update
                
        except Exception as e:
            print(f"Error updating wireplane viewer: {e}")
            print(traceback.format_exc())
            return dash.no_update, dash.no_update, dash.no_update