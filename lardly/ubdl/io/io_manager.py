"""
IO Manager for Lardly

This module handles loading and managing data files.
"""
import os
from typing import Dict, Any, List, Optional, Tuple
import logging

import ROOT as rt
from larlite import larlite
from larcv import larcv

from lardly.ubdl.core.state import state_manager

logger = logging.getLogger(__name__)

class IOManager:
    """
    IO Manager for handling data files
    
    This class provides methods for loading data files and accessing their contents.
    """
    
    def __init__(self):
        """Initialize IO Manager"""
        self._larcv_io = None
        self._larcv_io_backward = None
        self._larlite_io = None
        self._recoTree = None
        self._eventTree = None
        self._the_core_tree = None
        self._the_core_treetype = None
        self._the_core_nentries = 0
        self._available_trees = []
        self._current_entry = -1
    
    def load_files(self, file_paths: List[str], tick_direction: str = 'TickForwards') -> bool:
        """
        Load data files
        
        Args:
            file_paths: List of file paths to load
            tick_direction: Tick direction ('TickForwards' or 'TickBackwards')
            
        Returns:
            True if files were loaded successfully
        """
        try:
            # Initialize IO managers
            if tick_direction == 'TickBackwards':
                self._larcv_io = larcv.IOManager(larcv.IOManager.kREAD, "larcv", larcv.IOManager.kTickBackward)
            else:
                self._larcv_io = larcv.IOManager(larcv.IOManager.kREAD, "larcv", larcv.IOManager.kTickForward)
            
            self._larlite_io = larlite.storage_manager(larlite.storage_manager.kREAD)
            self._recoTree = rt.TChain("KPSRecoManagerTree")
            self._eventTree = rt.TChain("EventTree")  # ntuple tree
            
            self._available_trees = []
            
            # Load each file
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    logger.error(f"File path does not exist: {file_path}")
                    return False
                
                # Add to IO managers
                self._larcv_io.add_in_file(file_path)
                self._larlite_io.add_in_filename(file_path)
                
                # Get list of trees in this root file
                tfile = rt.TFile(file_path)
                tlist = tfile.GetListOfKeys()
                for i in range(tlist.GetEntries()):
                    key = str(tlist.At(i))
                    
                    if 'KPSRecoManagerTree' in key:
                        self._recoTree.AddFile(file_path)
                        tree_name = key.strip().split()[1]
                        self._available_trees.append(tree_name)
                    if 'EventTree' in key:
                        self._eventTree.AddFile(file_path)
                        self._available_trees.append("EventTree")
                    elif "_tree" in key:
                        tree_name = key.strip().split()[1]
                        self._available_trees.append(tree_name)
                
                tfile.Close()
            
            # Initialize IO managers
            self._larcv_io.reverse_all_products()
            self._larcv_io.initialize()
            self._larlite_io.open()
            
            # Determine entry tree
            self._the_core_tree = None
            self._the_core_nentries = 0
            
            # Check entries in each tree
            nentries_dict = {}
            for name, tree in [("larcv", self._larcv_io), 
                              ("larlite", self._larlite_io), 
                              ("reco", self._recoTree), 
                              ("ntuple", self._eventTree)]:
                tree_nentries = 0
                
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
                    elif name in ["reco", "ntuple"]:
                        try:
                            tree_nentries = tree.GetEntries()
                        except:
                            tree_nentries = 0
                
                logger.info(f"{name}: {tree_nentries} entries")
                nentries_dict[name] = tree_nentries
                
                if tree_nentries != 0 and self._the_core_tree is None:
                    self._the_core_tree = tree
                    self._the_core_treetype = name
                    self._the_core_nentries = tree_nentries
            
            # Update state
            state_manager.set_state(nentries_dict, 'io', 'nentries')
            state_manager.set_state(self._available_trees, 'io', 'available_trees')
            state_manager.set_state(self._the_core_nentries, 'io', 'total_entries')
            
            return True
        
        except Exception as e:
            logger.error(f"Error loading files: {e}")
            # Clean up
            self._larcv_io = None
            self._larlite_io = None
            self._recoTree = None
            self._eventTree = None
            return False
    
    def load_entry(self, entry: int) -> bool:
        """
        Load a specific entry from the data files
        
        Args:
            entry: Entry number to load
            
        Returns:
            True if entry was loaded successfully
        """
        try:
            if entry < 0 or entry >= self._the_core_nentries:
                logger.error(f"Entry {entry} out of bounds (0-{self._the_core_nentries-1})")
                return False
            
            # Load entry in each IO manager
            if self._larcv_io is not None:
                try:
                    self._larcv_io.read_entry(entry)
                except Exception as e:
                    logger.error(f"Error reading larcv entry: {e}")
            
            if self._larlite_io is not None:
                try:
                    self._larlite_io.go_to(entry)
                except Exception as e:
                    logger.error(f"Error reading larlite entry: {e}")
            
            if self._recoTree is not None:
                try:
                    self._recoTree.GetEntry(entry)
                except Exception as e:
                    logger.error(f"Error reading recoTree entry: {e}")
            
            if self._eventTree is not None:
                try:
                    self._eventTree.GetEntry(entry)
                except Exception as e:
                    logger.error(f"Error reading eventTree entry: {e}")
            
            self._current_entry = entry
            state_manager.set_state(entry, 'io', 'current_entry')
            
            return True
        
        except Exception as e:
            logger.error(f"Error loading entry {entry}: {e}")
            return False
    
    def get_tree_dict(self) -> Dict[str, Any]:
        """
        Get a dictionary of available trees/data sources
        
        Returns:
            Dictionary with IO managers and trees
        """
        return {
            'iolarlite': self._larlite_io,
            'iolarcv': self._larcv_io,
            'recoTree': self._recoTree,
            'eventTree': self._eventTree
        }
    
    def get_available_trees(self) -> List[str]:
        """
        Get a list of available trees
        
        Returns:
            List of tree names
        """
        return self._available_trees
    
    def get_current_entry(self) -> int:
        """
        Get the current entry number
        
        Returns:
            Current entry number, -1 if no entry is loaded
        """
        return self._current_entry
    
    def get_total_entries(self) -> int:
        """
        Get the total number of entries
        
        Returns:
            Total number of entries
        """
        return self._the_core_nentries
    
    def is_loaded(self) -> bool:
        """
        Check if data is loaded
        
        Returns:
            True if data is loaded
        """
        return self._the_core_tree is not None

# Create a global instance
io_manager = IOManager()

def load_files(file_paths: List[str], tick_direction: str = 'TickForwards') -> bool:
    """
    Load data files using the global IO manager
    
    Args:
        file_paths: List of file paths to load
        tick_direction: Tick direction ('TickForwards' or 'TickBackwards')
        
    Returns:
        True if files were loaded successfully
    """
    return io_manager.load_files(file_paths, tick_direction)

def load_entry(entry: int) -> bool:
    """
    Load a specific entry using the global IO manager
    
    Args:
        entry: Entry number to load
        
    Returns:
        True if entry was loaded successfully
    """
    return io_manager.load_entry(entry)

def get_tree_dict() -> Dict[str, Any]:
    """
    Get a dictionary of available trees/data sources
    
    Returns:
        Dictionary with IO managers and trees
    """
    return io_manager.get_tree_dict()

def get_available_trees() -> List[str]:
    """
    Get a list of available trees
    
    Returns:
        List of tree names
    """
    return io_manager.get_available_trees()