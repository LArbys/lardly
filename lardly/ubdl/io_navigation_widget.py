import os,traceback
import dash
from dash import html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go

import ROOT as rt
from larcv import larcv
import lardly

_ionav_iomanager = None

def make_ionavigation_widget(app, iomanager=None ):

    if iomanager is None:
        nentries = 0
    else:
        try:
            nentries = iomanager.get_n_entries()
        except:
            nentries = 0
    
    widget = html.Div([
        html.H3("File Info"),
        html.Label("Enter dlmerged path (required):"),
        dcc.Input(
            id='file-path-input-dlmerged',
            type='text',
            placeholder='Choose input dlmerged file ...',
            style={'width': '100%', 'marginBottom': '5px'}),
        html.Button("Load file", id='button-load-dlmerged'),
        html.Hr(),
        html.Div([html.Label(f'Number of entries: {nentries}', id='io-nav-num-entries')],
                style={'width':'100%'}),
        html.Div([html.Label(f'Current Entry: Not loaded.', id='io-nav-current-entry')],
                style={'width':'100%'}),
        html.Div([ dcc.Input(
                    id='io-nav-entry-input',
                    type='text',
                    placeholder='Choose entry number ...',
                    style={'width': '300px', 'marginBottom': '5px'}),               
                  html.Button("Load Entry", id='io-nav-button-load-entry',style={'width':'100px'})]),
        html.Hr(),
        html.Div([html.H5("Error Messages")], id='error-message', style={'color': 'red'}),
    ],id='io-navigation')

    if iomanager is not None:
        _ionav_iomanager = iomanager

    return widget

def set_ionav_iomanager(iomanager):
    global _ionav_iomanager
    if iomanager is not None:
        _ionav_iomanager = iomanager

def get_ionav_iomanager():
    global _ionav_iomanager
    return _ionav_iomanager

def register_ionavigation_callbacks(app):

    # callback for loading the file
    @app.callback(
        [Output('io-nav-num-entries','children'),
        Output('wireplane-viewer-dropdown','options'),
        Output('error-message','children')],
        Input('button-load-dlmerged', 'n_clicks'),
        State('file-path-input-dlmerged', 'value')
    )
    def update_filepath(n_clicks, filename):

        global _ionav_iomanager

        if filename is None:
            return dash.no_update, dash.no_update, dash.no_update

        if not os.path.exists(filename):
            err_msgs = [
                html.H5("Error Messages"),
                html.Label('File path does not exist')
            ]
            return dash.no_update, dash.no_update, err_msgs

        # defaults
        app.larcv_io = larcv.IOManager(larcv.IOManager.kREAD,"larcv",larcv.IOManager.kTickBackward)
        app.larcv_io.add_in_file( filename )
        app.larcv_io.reverse_all_products()
        app.larcv_io.initialize()
        #set_ionav_iomanager(app.larcv_io)
        
        _ionav_iomanager = app.larcv_io

        nentries = _ionav_iomanager.get_n_entries()

        # set options for wireplane viewer
        tfile = rt.TFile(filename)
        'wireplane-viewer-dropdown'

        results = lardly.ubdl.dlmerged_parsing.parse_dlmerged_trees_and_make_widgets( app, tfile=tfile )
        tfile.Close()

        err_msgs = [
                html.H5("Error Messages",style={'width':'100%'}),
                html.Label('no errors')
            ]

        return  f'Number of Entries: {nentries}', results['wireplane_trees'], err_msgs


    # callback for entry loading
    @app.callback(
        [Output('io-nav-current-entry','children')],
        Input('io-nav-button-load-entry','n_clicks'),
        [State('io-nav-entry-input','value')]
    )
    def io_nav_load_entry(n_clicks, entry_text):


        global _ionav_iomanager

        print("ionav button press: ", entry_text, " ",_ionav_iomanager)

        try:
            ientry = int(entry_text.strip())
        except:
            ientry = -1
        
        if _ionav_iomanager is None:
            return ['Current Entry: IOManager=None.']

        nentries = _ionav_iomanager.get_n_entries()

        if ientry<0 or ientry>=nentries:
            return ['Current Entry: out of bounds.']
        

        try:
            _ionav_iomanager.read_entry(ientry)
            entry_info = f'Current Entry Loaded: {ientry}.'
        except Exception as e:
            entry_info = f'Current Entry: [Error loading entry] '+traceback.format_exc()
        
        return [entry_info]


