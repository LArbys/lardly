"""
Configuration management for Lardly 
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List

class Config:
    """
    Centralized configuration class for Lardly
    
    This class manages all configuration settings and provides methods
    to load configuration from files, environment variables, and defaults.
    """
    
    # Default configuration values
    DEFAULT_CONFIG = {
        # File paths
        "data_paths": {
            "default_daefile": "microboone_32pmts_nowires_cryostat.dae",
        },
        
        # Plot settings
        "plot": {
            "default_layout": {
                "height": 800,
                "aspect_ratio": {"x": 1, "y": 1, "z": 4},
            },
            "default_colorscale": [
                [0, "rgb(12,51,131)"],
                [0.25, "rgb(10,136,186)"],
                [0.5, "rgb(242,211,56)"],
                [0.75, "rgb(242,143,56)"],
                [1, "rgb(217,30,30)"],
            ],
        },
        
        # Tree names for different plotters
        "tree_names": {
            "intime_flash": "simpleFlashBeam",
            "boundary_cosmic": "boundarycosmicreduced",
            "contained_cosmic": "containedcosmicreduced",
            "proton_cosmic": "cosmicprotonreduced",
            "larmatch": "larmatch",
        },
        
        # UI settings
        "ui": {
            "default_port": 8891,
            "debug_mode": True,
        }
    }
    
    def __init__(self):
        """Initialize with default configuration"""
        self._config = self.DEFAULT_CONFIG.copy()
        self._config_file_path = None
        
    def load_from_file(self, file_path: str) -> bool:
        """
        Load configuration from a YAML file
        
        Args:
            file_path: Path to configuration file
            
        Returns:
            bool: True if configuration was loaded successfully, False otherwise
        """
        try:
            path = Path(file_path)
            if not path.exists():
                print(f"Configuration file {file_path} not found")
                return False
                
            with open(path, 'r') as f:
                config_from_file = yaml.safe_load(f)
                
            # Update configuration with values from file
            self._update_config(config_from_file)
            self._config_file_path = file_path
            return True
            
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return False
    
    def load_from_env(self, prefix: str = "LARDLY_") -> None:
        """
        Load configuration from environment variables
        
        Environment variables should be prefixed with 'LARDLY_' by default.
        Nested keys should be separated by double underscores.
        E.g., LARDLY_PLOT__DEFAULT_HEIGHT=800
        
        Args:
            prefix: Prefix for environment variables
        """
        env_vars = {k: v for k, v in os.environ.items() if k.startswith(prefix)}
        
        for key, value in env_vars.items():
            # Remove prefix and split by double underscore to get nested keys
            key_path = key[len(prefix):].lower().split('__')
            
            # Convert value to appropriate type
            if value.lower() in ('true', 'yes', '1'):
                value = True
            elif value.lower() in ('false', 'no', '0'):
                value = False
            elif value.isdigit():
                value = int(value)
            elif value.replace('.', '').isdigit() and value.count('.') == 1:
                value = float(value)
                
            # Update config with this value
            self._set_nested_value(self._config, key_path, value)
    
    def _set_nested_value(self, d: Dict[str, Any], key_path: list, value: Any) -> None:
        """
        Set a value in a nested dictionary given a path of keys
        
        Args:
            d: Dictionary to update
            key_path: List of keys defining the path
            value: Value to set
        """
        if len(key_path) == 1:
            d[key_path[0]] = value
        else:
            if key_path[0] not in d:
                d[key_path[0]] = {}
            self._set_nested_value(d[key_path[0]], key_path[1:], value)
    
    def _update_config(self, new_config: Dict[str, Any]) -> None:
        """
        Recursively update configuration dictionary
        
        Args:
            new_config: New configuration values
        """
        for key, value in new_config.items():
            if key in self._config and isinstance(self._config[key], dict) and isinstance(value, dict):
                self._update_config_dict(self._config[key], value)
            else:
                self._config[key] = value
    
    def _update_config_dict(self, d: Dict[str, Any], u: Dict[str, Any]) -> None:
        """
        Helper method to recursively update nested dictionaries
        
        Args:
            d: Dictionary to update
            u: Dictionary with update values
        """
        for key, value in u.items():
            if key in d and isinstance(d[key], dict) and isinstance(value, dict):
                self._update_config_dict(d[key], value)
            else:
                d[key] = value
    
    def get(self, *keys: str, default: Any = None) -> Any:
        """
        Get a configuration value by its key path
        
        Args:
            *keys: One or more keys defining the path in the configuration
            default: Default value to return if key not found
            
        Returns:
            The configuration value or default
        """
        result = self._config
        try:
            for key in keys:
                result = result[key]
            return result
        except (KeyError, TypeError):
            return default
    
    def set(self, value: Any, *keys: str) -> None:
        """
        Set a configuration value
        
        Args:
            value: Value to set
            *keys: One or more keys defining the path in the configuration
        """
        if not keys:
            return
            
        d = self._config
        for key in keys[:-1]:
            if key not in d:
                d[key] = {}
            d = d[key]
        
        d[keys[-1]] = value
    
    @property
    def config_file_path(self) -> Optional[str]:
        """Get the path to the currently loaded configuration file"""
        return self._config_file_path
    
    def get_plot_config(self) -> Optional[Dict[str, Any]]:
        """
        Get the plot configuration if available
        
        Returns:
            Plot configuration dictionary or None
        """
        return self.get('plot_config')
    
    def get_enabled_plots(self) -> List[Dict[str, Any]]:
        """
        Get list of enabled plots from configuration
        
        Returns:
            List of enabled plot configurations
        """
        plot_config = self.get_plot_config()
        if not plot_config or 'plots' not in plot_config:
            return []
        
        return [p for p in plot_config['plots'] if p.get('enabled', True)]
    
    def get_input_files(self) -> List[Dict[str, str]]:
        """
        Get input file configuration
        
        Returns:
            List of input file configurations
        """
        plot_config = self.get_plot_config()
        if not plot_config or 'input_files' not in plot_config:
            return []
        
        return plot_config['input_files']
    
    def get_output_config(self) -> Dict[str, Any]:
        """
        Get output configuration
        
        Returns:
            Output configuration dictionary
        """
        plot_config = self.get_plot_config()
        if not plot_config or 'output' not in plot_config:
            return {
                'html_file': 'output.html',
                'save_images': False,
                'image_format': 'png',
                'image_dir': './images/'
            }
        
        return plot_config['output']
    
    def get_viewer_3d_config(self) -> Dict[str, Any]:
        """
        Get 3D viewer configuration
        
        Returns:
            3D viewer configuration dictionary
        """
        plot_config = self.get_plot_config()
        if plot_config and 'viewer_3d' in plot_config:
            return plot_config['viewer_3d']
        
        return {
            'show_detector': True,
            'detector_opacity': 0.1,
            'detector_color': [100, 150, 200],  # Light blue RGB color
            'layout': {
                'width': 1200,
                'height': 800,
                'showlegend': True
            }
        }
    
    def get_viewer_2d_config(self) -> Dict[str, Any]:
        """
        Get 2D viewer configuration
        
        Returns:
            2D viewer configuration dictionary
        """
        plot_config = self.get_plot_config()
        if plot_config and 'viewer_2d' in plot_config:
            return plot_config['viewer_2d']
        
        return {
            'enabled': True,
            'planes': [
                {'plane': 0, 'show': True},
                {'plane': 1, 'show': True},
                {'plane': 2, 'show': True}
            ],
            'colorscale': 'Viridis',
            'contrast_range': [-50, 150]
        }

# Create a global instance for convenience
config = Config()

def load_config(file_path: str = "lardly.yaml") -> bool:
    """
    Load configuration from the specified file
    
    Args:
        file_path: Path to configuration file
        
    Returns:
        bool: True if configuration was loaded successfully
    """
    success = config.load_from_file(file_path)
    config.load_from_env()
    return success