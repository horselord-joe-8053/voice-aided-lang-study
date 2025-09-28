"""
Data Manager for Cost Monitoring

Handles JSON file creation, updates, and management for daily cost tracking.
"""

import json
import os
from datetime import datetime, date
from typing import Dict, Any, Optional
import threading

class DataManager:
    """
    Manages daily JSON files for cost tracking with incremental updates.
    """
    
    def __init__(self, base_dir: str = "cost_monitor"):
        self.base_dir = base_dir
        self.current_date = date.today()
        self.current_file = None
        self.data_lock = threading.Lock()
        self._ensure_base_dir()
    
    def _ensure_base_dir(self):
        """Ensure the base directory exists."""
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir, exist_ok=True)
    
    def _get_filename_for_date(self, target_date: date) -> str:
        """Generate filename for a specific date."""
        return f"token_cost_{target_date.strftime('%Y-%m-%d')}.json"
    
    def _get_filepath_for_date(self, target_date: date) -> str:
        """Get full filepath for a specific date."""
        filename = self._get_filename_for_date(target_date)
        return os.path.join(self.base_dir, filename)
    
    def _load_existing_data(self, filepath: str) -> Dict[str, Any]:
        """Load existing data from JSON file or create new structure."""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load existing data from {filepath}: {e}")
        
        # Create new data structure
        return {
            "metadata": {
                "date": date.today().isoformat(),
                "total_requests": 0,
                "total_cost_usd": 0.0,
                "providers": {}
            },
            "requests": {}
        }
    
    def _save_data(self, data: Dict[str, Any], filepath: str):
        """Save data to JSON file with proper formatting."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving data to {filepath}: {e}")
            raise
    
    def _update_metadata(self, data: Dict[str, Any], provider: str, cost: float):
        """Update metadata with new request information."""
        metadata = data["metadata"]
        metadata["total_requests"] += 1
        metadata["total_cost_usd"] += cost
        
        if provider not in metadata["providers"]:
            metadata["providers"][provider] = {"requests": 0, "cost": 0.0}
        
        metadata["providers"][provider]["requests"] += 1
        metadata["providers"][provider]["cost"] += cost
    
    def add_request(self, request_id: str, request_data: Dict[str, Any]) -> bool:
        """
        Add a new request to the daily cost file.
        
        Args:
            request_id: Unique request identifier (e.g., "request_001_openai")
            request_data: Dictionary containing request details
        
        Returns:
            bool: True if successful, False otherwise
        """
        with self.data_lock:
            try:
                # Check if we need to rotate to a new day
                today = date.today()
                if today != self.current_date:
                    self.current_date = today
                    self.current_file = None
                
                # Get current file path
                filepath = self._get_filepath_for_date(self.current_date)
                
                # Load existing data
                data = self._load_existing_data(filepath)
                
                # Add the new request
                data["requests"][request_id] = request_data
                
                # Update metadata
                provider = request_data.get("provider", "unknown")
                cost = request_data.get("cost_usd", 0.0)
                self._update_metadata(data, provider, cost)
                
                # Save updated data
                self._save_data(data, filepath)
                
                return True
                
            except Exception as e:
                print(f"Error adding request {request_id}: {e}")
                return False
    
    def get_daily_summary(self, target_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Get summary data for a specific date.
        
        Args:
            target_date: Date to get summary for (default: today)
        
        Returns:
            Dict containing daily summary
        """
        if target_date is None:
            target_date = date.today()
        
        filepath = self._get_filepath_for_date(target_date)
        data = self._load_existing_data(filepath)
        
        return data.get("metadata", {})
    
    def get_request_data(self, request_id: str, target_date: Optional[date] = None) -> Optional[Dict[str, Any]]:
        """
        Get data for a specific request.
        
        Args:
            request_id: The request identifier
            target_date: Date to search in (default: today)
        
        Returns:
            Request data if found, None otherwise
        """
        if target_date is None:
            target_date = date.today()
        
        filepath = self._get_filepath_for_date(target_date)
        data = self._load_existing_data(filepath)
        
        return data.get("requests", {}).get(request_id)
    
    def list_available_dates(self) -> list:
        """Get list of dates with available cost data."""
        dates = []
        for filename in os.listdir(self.base_dir):
            if filename.startswith("token_cost_") and filename.endswith(".json"):
                try:
                    date_str = filename.replace("token_cost_", "").replace(".json", "")
                    dates.append(datetime.strptime(date_str, "%Y-%m-%d").date())
                except ValueError:
                    continue
        
        return sorted(dates)
    
    def get_all_requests_for_date(self, target_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Get all requests for a specific date.
        
        Args:
            target_date: Date to get requests for (default: today)
        
        Returns:
            Dictionary of all requests for the date
        """
        if target_date is None:
            target_date = date.today()
        
        filepath = self._get_filepath_for_date(target_date)
        data = self._load_existing_data(filepath)
        
        return data.get("requests", {})
