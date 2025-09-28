"""
Cost Tracker for TTS Providers

Core class for tracking token usage and costs across different TTS providers.
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional
from .pricing_config import PricingConfig
from .data_manager import DataManager

class CostTracker:
    """
    Tracks token usage and costs for TTS API calls.
    """
    
    def __init__(self, base_dir: str = "cost_monitor"):
        self.pricing_config = PricingConfig()
        self.data_manager = DataManager(base_dir)
        self.request_counter = self._get_next_request_number()
        self.active_requests = {}  # Track ongoing requests
    
    def _get_next_request_number(self) -> int:
        """Get the next request number based on existing requests for today."""
        try:
            requests = self.data_manager.get_all_requests_for_date()
            if not requests:
                return 0
            
            # Find the highest request number
            max_num = 0
            for request_id in requests.keys():
                if request_id.startswith("request_"):
                    try:
                        num_str = request_id.split("_")[1]
                        num = int(num_str)
                        max_num = max(max_num, num)
                    except (ValueError, IndexError):
                        continue
            
            return max_num
        except Exception:
            return 0
    
    def _generate_request_id(self, provider: str) -> str:
        """
        Generate a unique request ID in the format 'request_XXX_provider'.
        
        Args:
            provider: The TTS provider name
        
        Returns:
            str: Unique request identifier
        """
        self.request_counter += 1
        return f"request_{self.request_counter:03d}_{provider}"
    
    def start_request(self, provider: str, model: str, text: str) -> str:
        """
        Start tracking a new request.
        
        Args:
            provider: The TTS provider (e.g., 'openai', 'gemini')
            model: The model name (e.g., 'gpt-4o-mini-tts')
            text: The input text for TTS
        
        Returns:
            str: Unique request ID for this request
        """
        request_id = self._generate_request_id(provider)
        
        # Estimate input tokens (rough approximation: 1 token ≈ 4 characters)
        estimated_input_tokens = len(text) // 4
        
        # Store request start data
        self.active_requests[request_id] = {
            "provider": provider,
            "model": model,
            "text": text,
            "text_length": len(text),
            "estimated_input_tokens": estimated_input_tokens,
            "start_time": time.time(),
            "start_timestamp": datetime.now().isoformat()
        }
        
        print(f"Started tracking request: {request_id}")
        return request_id
    
    def end_request(self, request_id: str, success: bool = True, 
                   actual_input_tokens: Optional[int] = None,
                   actual_output_tokens: Optional[int] = None,
                   audio_duration: Optional[float] = None,
                   error: Optional[str] = None) -> bool:
        """
        End tracking for a request and save the data.
        
        Args:
            request_id: The request ID returned by start_request
            success: Whether the request was successful
            actual_input_tokens: Actual input tokens used (if known)
            actual_output_tokens: Actual output tokens used (if known)
            audio_duration: Duration of generated audio in seconds
            error: Error message if request failed
        
        Returns:
            bool: True if data was saved successfully
        """
        if request_id not in self.active_requests:
            print(f"Warning: Request {request_id} not found in active requests")
            return False
        
        # Get request data
        request_data = self.active_requests.pop(request_id)
        
        # Calculate actual tokens used
        input_tokens = actual_input_tokens or request_data["estimated_input_tokens"]
        output_tokens = actual_output_tokens or 0
        
        # Calculate cost
        cost = self.pricing_config.calculate_total_cost(
            request_data["provider"],
            request_data["model"],
            input_tokens,
            output_tokens
        )
        
        # Calculate duration
        duration = time.time() - request_data["start_time"]
        
        # Prepare final request data
        final_data = {
            "timestamp": request_data["start_timestamp"],
            "provider": request_data["provider"],
            "model": request_data["model"],
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": round(cost, 6),
            "text_length": request_data["text_length"],
            "audio_duration": audio_duration,
            "processing_time_seconds": round(duration, 3),
            "success": success,
            "error": error
        }
        
        # Save to daily JSON file
        success = self.data_manager.add_request(request_id, final_data)
        
        if success:
            print(f"Completed tracking request: {request_id} - Cost: ${cost:.6f}")
        else:
            print(f"Failed to save data for request: {request_id}")
        
        return success
    
    def get_daily_summary(self, target_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get summary of costs and usage for a specific date.
        
        Args:
            target_date: Date to get summary for (default: today)
        
        Returns:
            Dict containing daily summary
        """
        if target_date:
            target_date = target_date.date()
        
        return self.data_manager.get_daily_summary(target_date)
    
    def get_request_details(self, request_id: str, target_date: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific request.
        
        Args:
            request_id: The request identifier
            target_date: Date to search in (default: today)
        
        Returns:
            Request details if found, None otherwise
        """
        if target_date:
            target_date = target_date.date()
        
        return self.data_manager.get_request_data(request_id, target_date)
    
    def get_all_requests_for_date(self, target_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get all requests for a specific date.
        
        Args:
            target_date: Date to get requests for (default: today)
        
        Returns:
            Dictionary of all requests for the date
        """
        if target_date:
            target_date = target_date.date()
        
        return self.data_manager.get_all_requests_for_date(target_date)
    
    def list_available_dates(self) -> list:
        """Get list of dates with available cost data."""
        return self.data_manager.list_available_dates()
    
    def get_total_cost_today(self) -> float:
        """Get total cost for today."""
        summary = self.get_daily_summary()
        return summary.get("total_cost_usd", 0.0)
    
    def get_provider_costs_today(self) -> Dict[str, Dict[str, Any]]:
        """Get cost breakdown by provider for today."""
        summary = self.get_daily_summary()
        return summary.get("providers", {})
    
    def print_daily_report(self, target_date: Optional[datetime] = None):
        """
        Print a formatted daily report.
        
        Args:
            target_date: Date to report on (default: today)
        """
        summary = self.get_daily_summary(target_date)
        
        print(f"\n=== Daily Cost Report ===")
        print(f"Date: {summary.get('date', 'Unknown')}")
        print(f"Total Requests: {summary.get('total_requests', 0)}")
        print(f"Total Cost: ${summary.get('total_cost_usd', 0.0):.6f}")
        
        providers = summary.get('providers', {})
        if providers:
            print(f"\nBy Provider:")
            for provider, data in providers.items():
                print(f"  {provider}: {data.get('requests', 0)} requests, ${data.get('cost', 0.0):.6f}")
        
        print("=" * 30)
