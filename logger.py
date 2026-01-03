"""
BPJS AUTOMATION - LOGGING SYSTEM
Handles all logging operations
"""

import os
import sys
from datetime import datetime
from config import LOG_FOLDER, LOG_LEVEL_INFO, LOG_LEVEL_WARNING, LOG_LEVEL_ERROR

class Logger:
    """Logging system for BPJS Automation"""
    
    def __init__(self, log_to_file=True, log_to_console=True):
        self.log_to_file = log_to_file
        self.log_to_console = log_to_console
        self.log_entries = []
        
        # Create log folder if it doesn't exist
        if log_to_file:
            os.makedirs(LOG_FOLDER, exist_ok=True)
    
    def _get_timestamp(self):
        """Get current timestamp for logging"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _format_message(self, level, message):
        """Format log message with timestamp and level"""
        timestamp = self._get_timestamp()
        return f"[{timestamp}] [{level}] {message}"
    
    def _write_to_file(self, formatted_message):
        """Write log message to file"""
        try:
            # Daily log file
            date_str = datetime.now().strftime("%Y%m%d")
            log_file = os.path.join(LOG_FOLDER, f"bpjs_log_{date_str}.txt")
            
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(formatted_message + "\n")
        except Exception as e:
            # Fallback to console if file write fails
            print(f"Log file error: {e}")
    
    def log(self, message, level=LOG_LEVEL_INFO):
        """Main logging method"""
        formatted_message = self._format_message(level, message)
        
        # Store in memory
        self.log_entries.append({
            "timestamp": self._get_timestamp(),
            "level": level,
            "message": message,
            "formatted": formatted_message
        })
        
        # Write to console
        if self.log_to_console:
            if level == LOG_LEVEL_ERROR:
                print(f"\033[91m{formatted_message}\033[0m")  # Red for errors
            elif level == LOG_LEVEL_WARNING:
                print(f"\033[93m{formatted_message}\033[0m")  # Yellow for warnings
            else:
                print(formatted_message)
        
        # Write to file
        if self.log_to_file:
            self._write_to_file(formatted_message)
    
    def info(self, message):
        """Log info message"""
        self.log(message, LOG_LEVEL_INFO)
    
    def warning(self, message):
        """Log warning message"""
        self.log(message, LOG_LEVEL_WARNING)
    
    def error(self, message):
        """Log error message"""
        self.log(message, LOG_LEVEL_ERROR)
    
    def debug(self, message):
        """Log debug message"""
        self.log(message, "DEBUG")
    
    def log_process_start(self, kpj_list):
        """Log process start"""
        self.info(f"Starting batch processing of {len(kpj_list)} KPJs")
        self.info(f"KPJ List: {', '.join(kpj_list[:5])}" + 
                 ("..." if len(kpj_list) > 5 else ""))
    
    def log_kpj_processing(self, kpj, index, total):
        """Log KPJ processing start"""
        self.info(f"Processing KPJ {index}/{total}: {kpj}")
    
    def log_kpj_result(self, kpj, result):
        """Log KPJ processing result"""
        status = result.get("status", "UNKNOWN")
        if status == "SUCCESS":
            self.info(f"KPJ {kpj}: Success - {result.get('ref_number', 'No ref')}")
        elif status == "SKIPPED":
            self.warning(f"KPJ {kpj}: Skipped - {result.get('reason', 'No reason')}")
        else:
            self.error(f"KPJ {kpj}: Failed - {result.get('error', 'Unknown error')}")
    
    def log_batch_complete(self, stats):
        """Log batch completion"""
        self.info(f"Batch processing completed")
        self.info(f"Total processed: {stats.get('processed', 0)}")
        self.info(f"Total skipped: {stats.get('skipped', 0)}")
        self.info(f"Total failed: {stats.get('failed', 0)}")
    
    def log_csv_export(self, filename, record_count):
        """Log CSV export"""
        self.info(f"Exported {record_count} records to CSV: {filename}")
    
    def get_recent_logs(self, count=10):
        """Get recent log entries"""
        return self.log_entries[-count:] if self.log_entries else []
    
    def get_logs_by_level(self, level):
        """Get logs by specific level"""
        return [log for log in self.log_entries if log["level"] == level]
    
    def clear_logs(self):
        """Clear in-memory logs"""
        self.log_entries = []
        self.info("Logs cleared from memory")
    
    def export_logs(self, filename=None):
        """Export logs to file"""
        if not self.log_entries:
            return "No logs to export"
        
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"bpjs_logs_export_{timestamp}.txt"
            
            filepath = os.path.join(LOG_FOLDER, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                for log in self.log_entries:
                    f.write(log["formatted"] + "\n")
            
            return f"Logs exported to: {filepath}"
        
        except Exception as e:
            return f"Error exporting logs: {str(e)}"
    
    def get_stats(self):
        """Get logging statistics"""
        total = len(self.log_entries)
        info_count = len(self.get_logs_by_level(LOG_LEVEL_INFO))
        warning_count = len(self.get_logs_by_level(LOG_LEVEL_WARNING))
        error_count = len(self.get_logs_by_level(LOG_LEVEL_ERROR))
        
        return {
            "total_logs": total,
            "info_logs": info_count,
            "warning_logs": warning_count,
            "error_logs": error_count,
            "first_log": self.log_entries[0]["timestamp"] if self.log_entries else None,
            "last_log": self.log_entries[-1]["timestamp"] if self.log_entries else None,
        }

# Global logger instance
logger = Logger(log_to_file=True, log_to_console=True)

# Convenience functions
def log_info(message):
    logger.info(message)

def log_warning(message):
    logger.warning(message)

def log_error(message):
    logger.error(message)

def log_debug(message):
    logger.debug(message)