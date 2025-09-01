"""
File Watcher for Hot Reload
===========================

Monitors the tools.yaml file for changes and triggers registry reload.
Simple implementation without external dependencies.
"""

import os
import time
import threading
from pathlib import Path
from typing import Callable, Optional
import logging

logger = logging.getLogger(__name__)

class FileWatcher:
    """Simple file watcher for tools.yaml hot reload."""
    
    def __init__(self, file_path: str, callback: Callable[[], None]):
        self.file_path = Path(file_path)
        self.callback = callback
        self.last_modified = 0
        self.watching = False
        self.watch_thread: Optional[threading.Thread] = None
        
        if self.file_path.exists():
            self.last_modified = self.file_path.stat().st_mtime
    
    def start_watching(self):
        """Start watching the file for changes."""
        if self.watching:
            return
        
        self.watching = True
        self.watch_thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.watch_thread.start()
        logger.info(f"Started watching {self.file_path}")
    
    def stop_watching(self):
        """Stop watching the file."""
        self.watching = False
        if self.watch_thread:
            self.watch_thread.join(timeout=1.0)
        logger.info(f"Stopped watching {self.file_path}")
    
    def _watch_loop(self):
        """Main watching loop."""
        while self.watching:
            try:
                if self.file_path.exists():
                    current_modified = self.file_path.stat().st_mtime
                    
                    if current_modified > self.last_modified:
                        logger.info(f"File changed: {self.file_path}")
                        self.last_modified = current_modified
                        
                        # Trigger callback
                        try:
                            self.callback()
                        except Exception as e:
                            logger.error(f"Error in file change callback: {e}")
                
                # Check every second
                time.sleep(1.0)
                
            except Exception as e:
                logger.error(f"Error in file watcher: {e}")
                time.sleep(1.0)  # Continue watching despite errors
