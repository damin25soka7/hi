from plugin_base import MCPPlugin
from typing import Dict, Any
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import os
import logging

logger = logging.getLogger(__name__)


class DateTimePlugin(MCPPlugin):
    """
    Current Date and Time Plugin
    
    Returns the current date and time in a specified timezone.
    Useful for timestamping and date-aware operations.
    """
    
    def __init__(self):
        # Get timezone from environment or default to UTC
        self.timezone_str = os.getenv("DESIRED_TIMEZONE", "UTC")
        
        try:
            self.timezone = ZoneInfo(self.timezone_str)
            logger.info(f"🕐 DateTimePlugin: Timezone set to {self.timezone_str}")
        except Exception as e:
            logger.info(f"⚠️ Invalid timezone '{self.timezone_str}', falling back to UTC: {e}")
            self.timezone = timezone.utc
            self.timezone_str = "UTC"
    
    @property
    def name(self) -> str:
        return "get_current_datetime"
    
    @property
    def description(self) -> str:
        return f"Get the current date and time in {self.timezone_str} timezone. Returns formatted datetime string."
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def author(self) -> str:
        return "damin25soka7"
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get current date and time.
        
        Returns:
        {
            "success": true,
            "datetime": "2025-11-21T00:52:45+00:00",
            "formatted": "Thursday, November 21, 2025 at 12:52 AM (UTC)",
            "timezone": "UTC"
        }
        """
        try:
            now_utc = datetime.now(timezone.utc)
            now_local = now_utc.astimezone(self.timezone)
            
            formatted_datetime = now_local.strftime("%A, %B %d, %Y at %I:%M %p (%Z)")
            
            return {
                "success": True,
                "datetime": now_local.isoformat(),
                "formatted": formatted_datetime,
                "timezone": self.timezone_str,
                "utc_datetime": now_utc.isoformat()
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get datetime: {str(e)}"
            }
