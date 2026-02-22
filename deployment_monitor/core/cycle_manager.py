import os
import math
import logging
from datetime import datetime, timedelta

logger = logging.getLogger("deployment_monitor.cycle_manager")


class CycleManager:
    def __init__(self, base_audit_path: str):
        try:
            self.base_audit_path = base_audit_path
            logger.debug(f"Initializing CycleManager - base: {base_audit_path}")
            logger.info("CycleManager initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing CycleManager: {e}")
            raise

    def _get_friday_anchor_date(self) -> datetime:
        """
        Anchor deployment cycle to Friday of the same weekend.
        Friday = 4, Saturday = 5, Sunday = 6
        """
        today = datetime.now()
        weekday = today.weekday()

        if weekday == 4:  # Friday
            return today
        elif weekday == 5:  # Saturday
            return today - timedelta(days=1)
        elif weekday == 6:  # Sunday
            return today - timedelta(days=2)
        else:
            # Fallback for unexpected run day (Mon-Thu)
            return today

    def _get_week_of_month(self, date_obj: datetime) -> int:
        """
        Calculate week of month using ceil(day / 7)
        """
        return math.ceil(date_obj.day / 7)

    def _get_base_cycle_name(self, anchor_date: datetime) -> str:
        """
        Example: Feb_week03_2026
        """
        month_str = anchor_date.strftime("%b")  # Feb
        year_str = anchor_date.strftime("%Y")   # 2026
        week_num = self._get_week_of_month(anchor_date)

        return f"{month_str}_week{week_num:02d}_{year_str}"

    def generate_cycle_name(self) -> str:
        """
        Public method to generate cycle name.
        Returns weekly cycle name (e.g., Feb_week03_2026).
        Reuses the same folder for the entire week.
        """
        try:
            anchor_date = self._get_friday_anchor_date()
            cycle_name = self._get_base_cycle_name(anchor_date)
            logger.info(f"Generated cycle name: {cycle_name}")
            return cycle_name
        except Exception as e:
            logger.error(f"Error generating cycle name: {e}", exc_info=True)
            raise

    def ensure_cycle_folder(self, cycle_name: str) -> str:
        """
        Create full cycle folder path if not exists.
        Returns full path.
        
        Raises:
            OSError: If folder creation fails
        """
        try:
            full_path = os.path.join(self.base_audit_path, cycle_name)
            logger.debug(f"Ensuring cycle folder exists: {full_path}")

            os.makedirs(full_path, exist_ok=True)
            logger.info(f"Cycle folder ready: {full_path}")
            
            return full_path
        
        except FileNotFoundError as e:
            logger.error(f"Base audit path not found: {e}")
            raise
        except PermissionError as e:
            logger.error(f"Permission denied creating cycle folder: {e}")
            raise
        except OSError as e:
            logger.error(f"Failed to create deployment cycle folder: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating cycle folder: {e}", exc_info=True)
            raise
