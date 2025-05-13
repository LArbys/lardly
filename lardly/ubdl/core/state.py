"""
State management for Lardly

This module provides a centralized state management system for the application.
"""
from typing import Dict, Any, Optional, List, Callable, Set
import threading
import logging

logger = logging.getLogger(__name__)

class StateManager:
    """
    Centralized state management for the application
    
    This class manages the application state and provides methods for components
    to read, update, and subscribe to state changes.
    """
    
    def __init__(self):
        """Initialize state manager with empty state"""
        self._state = {}
        self._subscribers = {}
        self._lock = threading.RLock()
    
    def get_state(self, *keys: str, default: Any = None) -> Any:
        """
        Get a value from the state by its key path
        
        Args:
            *keys: One or more keys defining the path in the state
            default: Default value to return if key not found
            
        Returns:
            The state value or default
        """
        with self._lock:
            result = self._state
            try:
                for key in keys:
                    result = result[key]
                return result
            except (KeyError, TypeError):
                return default
    
    def set_state(self, value: Any, *keys: str) -> None:
        """
        Set a value in the state
        
        Args:
            value: Value to set
            *keys: One or more keys defining the path in the state
        """
        if not keys:
            return
            
        with self._lock:
            # Build the path to the value
            d = self._state
            for key in keys[:-1]:
                if key not in d:
                    d[key] = {}
                d = d[key]
            
            # Set the value
            old_value = d.get(keys[-1])
            d[keys[-1]] = value
            
            # Notify subscribers if value changed
            if old_value != value:
                self._notify_subscribers(keys, value)
    
    def update_state(self, updates: Dict[str, Any], *prefix_keys: str) -> None:
        """
        Update multiple state values at once
        
        Args:
            updates: Dictionary of updates
            *prefix_keys: Optional prefix keys for the updates
        """
        with self._lock:
            for key, value in updates.items():
                if prefix_keys:
                    self.set_state(value, *prefix_keys, key)
                else:
                    self.set_state(value, key)
    
    def subscribe(self, callback: Callable[[List[str], Any], None], *keys: str) -> Callable[[], None]:
        """
        Subscribe to state changes
        
        Args:
            callback: Function to call when state changes, receives key path and new value
            *keys: One or more keys defining the path to watch
            
        Returns:
            Unsubscribe function
        """
        if not keys:
            return lambda: None
            
        key_path = tuple(keys)
        
        with self._lock:
            if key_path not in self._subscribers:
                self._subscribers[key_path] = set()
            
            self._subscribers[key_path].add(callback)
        
        # Return unsubscribe function
        def unsubscribe():
            with self._lock:
                if key_path in self._subscribers and callback in self._subscribers[key_path]:
                    self._subscribers[key_path].remove(callback)
                    if not self._subscribers[key_path]:
                        del self._subscribers[key_path]
        
        return unsubscribe
    
    def _notify_subscribers(self, keys: List[str], value: Any) -> None:
        """
        Notify subscribers of a state change
        
        Args:
            keys: Key path that changed
            value: New value
        """
        # Find all subscribers that should be notified
        to_notify = set()
        
        # Check for subscribers at each level of the key path
        for i in range(len(keys) + 1):
            prefix = tuple(keys[:i])
            if prefix in self._subscribers:
                for callback in self._subscribers[prefix]:
                    to_notify.add(callback)
        
        # Notify each subscriber
        for callback in to_notify:
            try:
                callback(keys, value)
            except Exception as e:
                logger.error(f"Error in state subscriber callback: {e}")

# Create a global instance for convenience
state_manager = StateManager()