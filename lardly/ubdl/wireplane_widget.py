import os,traceback
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import numpy as np

from .io_navigation_widget import get_ionav_iomanager
from lardly.data.larcv_image2d import visualize_larcv_image2d

_stored_figures = {}
_io_manager = None

def make_imageplane_view_widget( app, image_v=[], tree_list=[] ):

    plot_v = []
    if len(image_v)==0:
        name = f'empty_image_full'
        if name not in _stored_figures:
            empty_lo = go.Layout(
                title='empty wire plane',
                autosize=True,
                hovermode='closest',
                showlegend=False)
            plot = go.Heatmap(name="empty",
                            z=np.random.random(101*346).reshape((101,346)),
                            x=np.linspace(0,3460,346),
                            y=np.linspace(2400,2400+101*60,101))
            empty = go.Figure( data=[plot], layout=empty_lo )
            _stored_figures[name] = empty
        empty_fig = _stored_figures[name]

        for p in range(3):
            plot_v.append(empty_fig)
    

    if len(tree_list)==0:
        trees = ["none"]
    else:
        trees = tree_list
    
    layout = html.Div([
        html.Label("Select Image Sources"),
        dcc.Dropdown(options=trees, value=trees[0], id='wireplane-viewer-dropdown'),
        # uplane
        html.Div(
            dcc.Graph(figure=plot_v[0], id='plane0-graph'), 
            style={'display':'inline-block','padding': '0px 0px 0px 0px','width':'32%'}),
        # vplane
        html.Div(
            dcc.Graph(figure=plot_v[1], id='plane1-graph'),
            style={'display':'inline-block','padding': '0px 0px 0px 0px','width':'32%'}),
        # yplane
        html.Div(
            dcc.Graph(figure=plot_v[2], id='plane2-graph'),
            style={'display':'inline-block','padding': '0px 0px 0px 0px','width':'32%'})],
        id='wireplane-viewer',
        style={'width': '99%', 'display': 'inline-block','float':'right'})

    return layout
   
def register_dropdown_callback(app):
    # define the callback
    @app.callback(
        [Output('plane0-graph', 'figure'),
        Output('plane1-graph', 'figure'),
        Output('plane2-graph', 'figure')],
        Input('wireplane-viewer-dropdown', 'value'),
        [State('plane0-graph','figure'),
        State('plane1-graph','figure'),
        State('plane2-graph','figure')])
    def update_wireplane_viewer_tree(value,fig_plane0,fig_plane1,fig_plane2):
        print("update_wireplane_viewer_tree: set value to ",value)

        if value is None or value=="none" or value=="None":
            return dash.no_update, dash.no_update, dash.no_update

        ioman = get_ionav_iomanager()
        info = str(value).strip().split()
        treename = info[1]

        prodname = treename.replace("image2d_","").replace("_tree","")
        ev_imgs = ioman.get_data("image2d",prodname)

        try:
            img_v = ev_imgs.as_vector()
        except Exception:
            print(traceback.format_exc())

        print("Number of images: ",img_v.size())

        out = []

        for i in range(img_v.size()):
            layout = go.Layout(
                title=f'Plane[{i}]',
                autosize=True,
                hovermode='closest',
                showlegend=False)
            out.append( go.Figure(data=visualize_larcv_image2d(img_v.at(i)), layout=layout) )

        for i in range(len(out),3):
            out.append( dash.no_update )

        return out[0], out[1], out[2]

    return True