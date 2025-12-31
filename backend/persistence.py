"""
Simple file-based persistence for test server
Stores data in JSON files
"""

import json
import os
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class SimplePersistence:
    """Simple JSON file-based persistence"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
    def _get_file_path(self, name: str) -> Path:
        """Get file path for a data store"""
        return self.data_dir / f"{name}.json"
    
    def load(self, name: str) -> Dict[str, Any]:
        """Load data from file"""
        file_path = self._get_file_path(name)
        
        if not file_path.exists():
            logger.info(f"No existing data for {name}, starting fresh")
            return {}
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} items from {name}")
                return data
        except Exception as e:
            logger.error(f"Error loading {name}: {e}")
            return {}
    
    def save(self, name: str, data: Dict[str, Any]) -> bool:
        """Save data to file"""
        file_path = self._get_file_path(name)
        
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            logger.error(f"Error saving {name}: {e}")
            return False
    
    def save_all(self, stores: Dict[str, Dict[str, Any]]) -> bool:
        """Save multiple stores at once"""
        success = True
        for name, data in stores.items():
            if not self.save(name, data):
                success = False
        return success


# Global persistence instance
persistence = SimplePersistence()
