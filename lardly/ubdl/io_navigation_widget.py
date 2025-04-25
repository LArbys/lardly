import os,traceback
import dash
from dash import html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go

import ROOT as rt
from larlite import larlite
from larcv import larcv
import lardly
from lardly.ubdl.det3d_plot_factory import make_applicable_det3d_plot_list, set_det3d_io

_ionav_iomanager = None
_ionav_storageman = None
_ionav_recotree = None
_ionav_eventTree = None
_the_core_tree = None
_the_core_treetype = None
_the_core_nentries = 0
_ionav_available_trees_list = []

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
        dcc.Textarea(
            id='file-path-input-dlmerged',
            placeholder='List input dlmerged file(s) ...',
            style={'width': '100%', 'marginBottom': '5px','height':'100px'}),
        dcc.RadioItems(id='tick-direction',
                       options=['TickForwards','TickBackwards'],
                       value='TickForwards'),
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

def set_ionav_storageman(io_storageman):
    global _ionav_storageman
    if io_storageman is not None:
        _ionav_storageman = iostrageman
        
def get_ionav_iomanager():
    global _ionav_iomanager
    return _ionav_iomanager

def set_ionav_recotree(recotree):
    global _ionav_recotree
    _ionav_recotree = recotree

def set_ionav_eventTree(evTree):
    global _ionav_eventTree
    _ionav_eventTree = evTree
    print("set _ionav_eventTree: ",_ionav_eventTree)

def get_ionav_recotree():
    global _ionav_recotree
    return _ionav_recotree

def get_ionav_eventTree():
    global _ionav_eventTree
    return _ionav_eventTree

def register_ionavigation_callbacks(app):

    # callback for loading the file
    @app.callback(
        [Output('io-nav-num-entries','children'),
        Output('wireplane-viewer-dropdown','options'),
        Output('det3d-viewer-checklist-plotchoices','options'),
        Output('error-message','children')],
        Input('button-load-dlmerged', 'n_clicks'),
        State('file-path-input-dlmerged', 'value'),
        State('tick-direction','value')
    )
    def update_filepath(n_clicks, textbox_input, tick_direction):
        """
        Runs when we click the button that loads the files.

        When we do, we update the options for plots available to the 
        wireplane and det3d viewer.
        """

        global _ionav_iomanager
        global _ionav_storageman
        global _ionav_recotree
        global _ionav_eventTree
        global _ionav_available_trees_list
        global _the_core_tree
        global _the_core_treetype
        global _the_core_nentries

        set_ionav_recotree( None )
        set_ionav_eventTree( None )
        set_ionav_iomanager( None )
        set_ionav_storageman( None )

        #print("textbox input: ",textbox_input)

        if textbox_input is None:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update

        if tick_direction=='TickBackwards':
            larcv_io = larcv.IOManager(larcv.IOManager.kREAD,"larcv",larcv.IOManager.kTickBackward)
        else:
            larcv_io = larcv.IOManager(larcv.IOManager.kREAD,"larcv",larcv.IOManager.kTickForward)
        larlite_io = larlite.storage_manager(larlite.storage_manager.kREAD)
        recoTree = rt.TChain("KPSRecoManagerTree")
        eventTree = rt.TChain("EventTree") # ntuple tree

        # parse the text box: list of files
        filelist = textbox_input.split()
        for filename in filelist:

            if not os.path.exists(filename):
                err_msgs = [
                    html.H5("Error Messages"),
                    html.Label('File path does not exist')
                ]
                return dash.no_update, dash.no_update, dash.no_update, err_msgs

            # defaults
            larcv_io.add_in_file( filename )
            larlite_io.add_in_filename( filename )

            # get list of trees in this root file
            tfile = rt.TFile(filename)
            tlist = tfile.GetListOfKeys()
            for i in range(tlist.GetEntries()):
                key = str(tlist.At(i))

                if 'KPSRecoManagerTree' in key:
                    recoTree.AddFile( filename )
                    tree_name = key.strip().split()[1]
                    _ionav_available_trees_list.append(tree_name)
                if 'EventTree' in key:
                    eventTree.AddFile(filename)
                    _ionav_available_trees_list.append("EventTree")
                #print(key.GetName())
                elif "_tree" in key:
                    tree_name = key.strip().split()[1]
                    _ionav_available_trees_list.append(tree_name)
            tfile.Close()
            # end of tree key loop

        larcv_io.reverse_all_products()
        larcv_io.initialize()
        larlite_io.open()
        
        _ionav_iomanager  = larcv_io
        _ionav_storageman = larlite_io

        # determine entry tree
        # these trees need an interface wrapper
        _the_core_tree = None
        nentries = 0
        nentries_dict = {}
        for (name,tree) in [("larcv",_ionav_iomanager),("larlite",_ionav_storageman),("reco",recoTree),("ntuple",eventTree)]:
            if tree is not None:
                if name in ["larcv"]:
                    try:
                        tree_nentries = tree.get_n_entries()
                    except:
                        tree_nentries = 0
                elif name in ["larlite"]:
                    try:
                        tree_nentries = tree.get_nentries()
                    except:
                        tree_nentries = 0
                elif name in ["reco","ntuple"]:
                    try:
                        tree_nentries = tree.GetEntries()
                    except:
                        tree_nentries = 0
            print(name,": ",tree_nentries," entries")
            nentries_dict[name] = tree_nentries
            if tree_nentries!=0 and _the_core_tree is None:
                _the_core_tree = tree
                _the_core_treetype = name
                _the_core_nentries = tree_nentries
                nentries = tree_nentries

        if nentries_dict['reco']>0:
            set_ionav_recotree( recoTree )
        else:
            set_ionav_recotree( None )

        if nentries_dict['ntuple']>0:
            set_ionav_eventTree( eventTree )
        else:
            set_ionav_eventTree( None )

        if nentries_dict['larcv']==0:
            set_ionav_iomanager( None )

        if nentries_dict['larlite']==0:
            set_ionav_storageman( None )

        # with the list of trees set. we want to pass available plotters.
        wire_plane_trees = []
        for key in _ionav_available_trees_list:
            if "image2d_" in key:
                wire_plane_trees.append(key)

        set_det3d_io( _ionav_storageman, _ionav_iomanager, _ionav_recotree, _ionav_eventTree ) # give pointers to iomanagers to det3d modules
        det3d_plotters, det3d_options = make_applicable_det3d_plot_list( _ionav_available_trees_list ) # activate certain plots based on available trees

        err_msgs = [
                html.H5("Error Messages",style={'width':'100%'}),
                html.Label('no errors')
            ]

        return  f'Number of Entries: {nentries}', wire_plane_trees, det3d_plotters, err_msgs


    # callback for entry loading
    @app.callback(
        [Output('io-nav-current-entry','children')],
        Input('io-nav-button-load-entry','n_clicks'),
        [State('io-nav-entry-input','value')]
    )
    def io_nav_load_entry(n_clicks, entry_text):


        global _ionav_iomanager
        global _ionav_recotree
        global _ionav_eventTree
        global _ionav_storageman
        global _the_core_tree

        print("ionav button press: ", entry_text, " ",_the_core_tree)

        try:
            ientry = int(entry_text.strip())
        except:
            ientry = -1

        
        if _the_core_tree is None:
            return ['Current Entry: IOManager=None.']

        if ientry<0 or ientry>=_the_core_nentries:
            return [f'Current Entry: out of bounds. NENTRIES={_the_core_nentries}']

        if _ionav_iomanager is not None:
            try:
                _ionav_iomanager.read_entry(ientry)
            except:
                pass
            
        if _ionav_storageman is not None:
            try:
                _ionav_storageman.go_to(ientry)
            except:
                pass

        if _ionav_recotree is not None:
            try:
                _ionav_recotree.GetEntry(ientry)
            except:
                pass

        if _ionav_eventTree is not None:
            try:
                _ionav_eventTree.GetEntry(ientry)
            except:
                pass
        
        entry_info = f'Current Entry Loaded: {ientry}.'
        
        return [entry_info]


