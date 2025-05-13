"""
Base plotter class for Lardly

This module defines the base plotter class that all plotters should inherit from.
"""
from typing import Dict, Any, List, Optional, Tuple
import dash
from dash import html, dcc
import plotly.graph_objects as go
import abc
import logging

from lardly.ubdl.core.state import state_manager

logger = logging.getLogger(__name__)

class BasePlotter(abc.ABC):
    """
    Base class for all 3D plotters in Lardly
    
    This class defines the interface that all plotters should implement.
    It provides methods for checking applicability, creating traces, and
    generating UI widgets for options.
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize the plotter with a name and optional description
        
        Args:
            name: Name of the plotter, used as identifier
            description: Optional description of the plotter
        """
        self.name = name
        self.description = description or name
    
    @abc.abstractmethod
    def is_applicable(self, tree_keys: List[str]) -> bool:
        """
        Check if this plotter is applicable for the given data
        
        Args:
            tree_keys: List of tree keys available in the data
            
        Returns:
            True if the plotter can be used with this data, False otherwise
        """
        pass
    
    def make_option_widgets(self) -> List[dash.development.base_component.Component]:
        """
        Create option widgets for this plotter
        
        Returns:
            List of Dash components for options, empty list if no options
        """
        return [html.Label(f'{self.name}: no options')]
    
    @abc.abstractmethod
    def make_traces(self, tree_dict: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Create plotly traces for this plotter
        
        Args:
            tree_dict: Dictionary of trees (data sources)
            options: Optional dictionary of options for this plotter
            
        Returns:
            List of plotly trace dictionaries
        """
        pass
    
    def initialize_options(self) -> None:
        """
        Initialize plotter options in the state manager
        
        This method should be called when the plotter is registered. It sets up
        default values for any options the plotter uses.
        """
        pass
    
    def get_option_value(self, option_name: str, default: Any = None) -> Any:
        """
        Get the current value of an option from the state manager
        
        Args:
            option_name: Name of the option
            default: Default value if option not set
            
        Returns:
            Current value of the option
        """
        return state_manager.get_state('plotters', self.name, 'options', option_name, default=default)
    
    def set_option_value(self, option_name: str, value: Any) -> None:
        """
        Set an option value in the state manager
        
        Args:
            option_name: Name of the option
            value: New value for the option
        """
        state_manager.set_state(value, 'plotters', self.name, 'options', option_name)
    
    def log_info(self, message: str) -> None:
        """
        Log an info message for this plotter
        
        Args:
            message: Message to log
        """
        logger.info(f"[{self.name}] {message}")
    
    def log_error(self, message: str) -> None:
        """
        Log an error message for this plotter
        
        Args:
            message: Message to log
        """
        logger.error(f"[{self.name}] {message}")