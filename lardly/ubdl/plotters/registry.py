"""
Plotter registry for Lardly

This module provides a registry for plotters and functions to work with them.
"""
from typing import Dict, List, Any, Optional, Type, Set, Tuple
import logging
from lardly.ubdl.plotters.base import BasePlotter

logger = logging.getLogger(__name__)

class PlotterRegistry:
    """
    Registry for plotters
    
    This class maintains a registry of available plotters and provides methods
    to register, discover, and use them.
    """
    
    def __init__(self):
        """Initialize with an empty registry"""
        self._plotters: Dict[str, BasePlotter] = {}
    
    def register(self, plotter: BasePlotter) -> None:
        """
        Register a plotter
        
        Args:
            plotter: Plotter instance to register
        """
        if plotter.name in self._plotters:
            logger.warning(f"Plotter '{plotter.name}' already registered, overwriting")
        
        self._plotters[plotter.name] = plotter
        plotter.initialize_options()
        logger.info(f"Registered plotter: {plotter.name}")
    
    def get_plotter(self, name: str) -> Optional[BasePlotter]:
        """
        Get a registered plotter by name
        
        Args:
            name: Name of the plotter
            
        Returns:
            Plotter instance or None if not found
        """
        return self._plotters.get(name)
    
    def get_all_plotters(self) -> List[BasePlotter]:
        """
        Get all registered plotters
        
        Returns:
            List of all registered plotter instances
        """
        return list(self._plotters.values())
    
    def get_applicable_plotters(self, tree_keys: List[str]) -> List[BasePlotter]:
        """
        Get plotters applicable for the given data
        
        Args:
            tree_keys: List of tree keys available in the data
            
        Returns:
            List of applicable plotter instances
        """
        return [
            plotter for plotter in self._plotters.values()
            if plotter.is_applicable(tree_keys)
        ]
    
    def make_traces(self, plotter_names: List[str], tree_dict: Dict[str, Any], 
                    options: Optional[Dict[str, Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Create traces for the given plotters
        
        Args:
            plotter_names: Names of plotters to use
            tree_dict: Dictionary of trees (data sources)
            options: Optional dictionary of options by plotter name
            
        Returns:
            List of plotly trace dictionaries
        """
        all_traces = []
        
        for name in plotter_names:
            plotter = self.get_plotter(name)
            if plotter is None:
                logger.warning(f"Plotter '{name}' not found")
                continue
            
            plotter_options = None
            if options and name in options:
                plotter_options = options[name]
            
            try:
                traces = plotter.make_traces(tree_dict, plotter_options)
                logger.info(f"Plotter '{name}' created {len(traces)} traces")
                all_traces.extend(traces)
            except Exception as e:
                logger.error(f"Error creating traces for plotter '{name}': {e}")
        
        return all_traces

    def register_callbacks(self, app):
        """
        Register callbacks for all plotters
        
        Args:
            app: Dash application
        """
        for plotter in self._plotters.values():
            try:
                plotter.register_callbacks(app)
            except Exception as e:
                logger.error(f"Error registering callbacks for plotter '{plotter.name}': {e}")


# Create a global registry instance
registry = PlotterRegistry()

def register_plotter(plotter: BasePlotter) -> None:
    """
    Register a plotter in the global registry
    
    Args:
        plotter: Plotter instance to register
    """
    registry.register(plotter)

def register_callbacks(app):
    """Register callbacks for all plotters"""
    registry.register_callbacks(app)

def get_applicable_plotters(tree_keys: List[str]) -> List[Tuple[str, str]]:
    """
    Get names and descriptions of applicable plotters
    
    Args:
        tree_keys: List of tree keys available in the data
        
    Returns:
        List of (name, description) tuples for applicable plotters
    """
    plotters = registry.get_applicable_plotters(tree_keys)
    return [(p.name, p.description) for p in plotters]

def make_traces(selected_plotters: List[str], tree_dict: Dict[str, Any], 
                options: Optional[Dict[str, Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """
    Create traces for the selected plotters
    
    Args:
        selected_plotters: Names of selected plotters
        tree_dict: Dictionary of trees (data sources)
        options: Optional dictionary of options by plotter name
        
    Returns:
        List of plotly trace dictionaries
    """
    return registry.make_traces(selected_plotters, tree_dict, options)