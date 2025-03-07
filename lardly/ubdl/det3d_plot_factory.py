import os,sys

_det3d_plot_factory = {}
_det3d_plot_factory_ioll  = None
_det3d_plot_factory_iolcv = None
_det3d_plot_factor_recotree = None

def register_det3d_plotter( name, fn_add_plot_check, fn_make_options, fn_make_plot ):
    global _det3d_plot_factory
    _det3d_plot_factory[name] = {"addplot":fn_add_plot_check,
                                "options":fn_make_options,
                                "makeplot":fn_make_plot }

def set_det3d_io( ioll, iolcv, recotree ):

    global _det3d_plot_factory_ioll
    global _det3d_plot_factory_iolcv
    global _det3d_plot_factory_recotree

    _det3d_plot_factory_ioll = ioll
    _det3d_plot_factory_iolcv = iolcv
    _det3d_plot_factory_recotree = recotree


def make_applicable_det3d_plot_list( treelist ):

    
    plotter_list = []
    plotter_options = []
    print("check for applicable activies: ")
    print("det3d_plot_factory: ",_det3d_plot_factory.keys() )
    for name,fn_dict in _det3d_plot_factory.items():
        fn_check = fn_dict['addplot']
        fn_opts  = fn_dict['options']
        isapplicable = fn_check( treelist )
        print("is plotter[ name=",name,"] appicable? ",isapplicable)
        if isapplicable:
            plotter_list.append( name )
            plotter_options.append( fn_opts(treelist) )
    
    return plotter_list, plotter_options

def make_det3d_traces( selected_plots ):
    print("Make det3d plots: ",selected_plots)
    traces = []
    for plottype in selected_plots:
        if plottype in _det3d_plot_factory:
            plotter = _det3d_plot_factory[plottype]
            fn_make_traces = plotter['makeplot']
            plot_traces = fn_make_traces( _det3d_plot_factory_ioll, _det3d_plot_factory_iolcv, _det3d_plot_factory_recotree )
            print("number of traces from ",plottype,": ",len(plot_traces))
            if len(plot_traces)>0:
                traces += plot_traces
    return traces