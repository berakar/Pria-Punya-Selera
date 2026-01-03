"""
BPJS AUTOMATION - CSV HANDLER
Handles all CSV file operations
"""

import csv
import os
import json
from datetime import datetime
from config import (
    CSV_ENCODING, CSV_DELIMITER, CSV_QUOTING,
    DOWNLOAD_FOLDER, CSV_PREFIX, get_csv_path
)
from logger import log_info, log_error, log_warning

class CSVHandler:
    """Handles CSV file operations"""
    
    def __init__(self):
        self.data = []
        self.fields = set()
        self.current_file = None
        
    def add_record(self, record):
        """Add a record to the data collection"""
        if not isinstance(record, dict):
            log_warning(f"Invalid record type: {type(record)}")
            return False
        
        # Add timestamp if not present
        if 'timestamp' not in record:
            record['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Add processing time if not present
        if 'processing_time' not in record:
            record['processing_time'] = datetime.now().strftime('%H:%M:%S')
        
        self.data.append(record)
        
        # Update fields set
        self.fields.update(record.keys())
        
        log_info(f"Record added: KPJ {record.get('kpj', 'Unknown')}")
        return True
    
    def add_batch(self, records):
        """Add multiple records at once"""
        success_count = 0
        for record in records:
            if self.add_record(record):
                success_count += 1
        
        log_info(f"Added {success_count} of {len(records)} records")
        return success_count
    
    def clear_data(self):
        """Clear all stored data"""
        count = len(self.data)
        self.data = []
        self.fields = set()
        log_info(f"Cleared {count} records from memory")
        return count
    
    def get_record_count(self):
        """Get total number of records"""
        return len(self.data)
    
    def get_fields(self):
        """Get all field names"""
        return sorted(list(self.fields))
    
    def save_to_csv(self, filename=None, include_all_fields=True):
        """
        Save data to CSV file
        Returns: (success, filepath or error_message)
        """
        if not self.data:
            log_error("No data to save to CSV")
            return False, "No data available"
        
        try:
            # Generate filename if not provided
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{CSV_PREFIX}{timestamp}.csv"
            
            # Get full filepath
            filepath = get_csv_path(filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Determine fields to include
            if include_all_fields:
                fields_to_write = self.get_fields()
            else:
                # Use fields from first record
                fields_to_write = list(self.data[0].keys())
            
            # Write CSV file
            with open(filepath, 'w', newline='', encoding=CSV_ENCODING) as csvfile:
                # Configure CSV writer
                writer = csv.DictWriter(
                    csvfile,
                    fieldnames=fields_to_write,
                    delimiter=CSV_DELIMITER,
                    quoting=eval(CSV_QUOTING)
                )
                
                # Write header and data
                writer.writeheader()
                
                for record in self.data:
                    # Ensure all fields are present in each record
                    row = {field: record.get(field, '') for field in fields_to_write}
                    writer.writerow(row)
            
            self.current_file = filepath
            record_count = len(self.data)
            
            log_info(f"Saved {record_count} records to CSV: {filepath}")
            return True, filepath
            
        except Exception as e:
            error_msg = f"Error saving CSV: {str(e)}"
            log_error(error_msg)
            return False, error_msg
    
    def load_from_csv(self, filepath):
        """
        Load data from CSV file
        Returns: (success, loaded_count or error_message)
        """
        if not os.path.exists(filepath):
            log_error(f"CSV file not found: {filepath}")
            return False, "File not found"
        
        try:
            with open(filepath, 'r', encoding=CSV_ENCODING) as csvfile:
                reader = csv.DictReader(csvfile, delimiter=CSV_DELIMITER)
                
                loaded_data = []
                for row in reader:
                    loaded_data.append(dict(row))
                
                # Replace current data with loaded data
                self.data = loaded_data
                self.fields = set()
                for record in self.data:
                    self.fields.update(record.keys())
                
                count = len(self.data)
                self.current_file = filepath
                
                log_info(f"Loaded {count} records from CSV: {filepath}")
                return True, count
                
        except Exception as e:
            error_msg = f"Error loading CSV: {str(e)}"
            log_error(error_msg)
            return False, error_msg
    
    def export_to_json(self, filepath=None):
        """Export data to JSON file"""
        if not self.data:
            return False, "No data to export"
        
        try:
            if filepath is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = os.path.join(DOWNLOAD_FOLDER, f"{CSV_PREFIX}{timestamp}.json")
            
            with open(filepath, 'w', encoding=CSV_ENCODING) as jsonfile:
                json.dump(self.data, jsonfile, indent=2, ensure_ascii=False)
            
            log_info(f"Exported {len(self.data)} records to JSON: {filepath}")
            return True, filepath
            
        except Exception as e:
            error_msg = f"Error exporting JSON: {str(e)}"
            log_error(error_msg)
            return False, error_msg
    
    def get_statistics(self):
        """Get statistics about the data"""
        if not self.data:
            return {"total_records": 0}
        
        stats = {
            "total_records": len(self.data),
            "fields_count": len(self.fields),
            "field_names": self.get_fields(),
            "first_record_time": self.data[0].get('timestamp', 'Unknown') if self.data else 'Unknown',
            "last_record_time": self.data[-1].get('timestamp', 'Unknown') if self.data else 'Unknown',
        }
        
        # Count by status
        status_counts = {}
        for record in self.data:
            status = record.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        stats["status_counts"] = status_counts
        
        # Count by date
        date_counts = {}
        for record in self.data:
            timestamp = record.get('timestamp', '')
            if timestamp:
                date = timestamp.split()[0] if ' ' in timestamp else timestamp[:10]
                date_counts[date] = date_counts.get(date, 0) + 1
        
        stats["date_counts"] = date_counts
        
        return stats
    
    def filter_by_status(self, status):
        """Filter records by status"""
        filtered = [record for record in self.data if record.get('status') == status]
        return filtered
    
    def filter_by_date(self, date_str):
        """Filter records by date"""
        filtered = []
        for record in self.data:
            timestamp = record.get('timestamp', '')
            if timestamp and timestamp.startswith(date_str):
                filtered.append(record)
        return filtered
    
    def find_by_kpj(self, kpj):
        """Find records by KPJ"""
        found = [record for record in self.data if record.get('kpj') == kpj]
        return found
    
    def remove_duplicates(self, key_field='kpj'):
        """Remove duplicate records based on key field"""
        if not self.data:
            return 0
        
        unique_records = {}
        duplicates_removed = 0
        
        for record in self.data:
            key = record.get(key_field)
            if key not in unique_records:
                unique_records[key] = record
            else:
                duplicates_removed += 1
        
        self.data = list(unique_records.values())
        log_info(f"Removed {duplicates_removed} duplicate records")
        return duplicates_removed
    
    def sort_by_field(self, field, reverse=False):
        """Sort records by field"""
        if not self.data or field not in self.data[0]:
            return False
        
        try:
            self.data.sort(key=lambda x: x.get(field, ''), reverse=reverse)
            log_info(f"Sorted {len(self.data)} records by {field}")
            return True
        except Exception as e:
            log_error(f"Error sorting records: {str(e)}")
            return False
    
    def backup_current_file(self):
        """Create backup of current CSV file"""
        if not self.current_file or not os.path.exists(self.current_file):
            return False, "No current file to backup"
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(DOWNLOAD_FOLDER, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            filename = os.path.basename(self.current_file)
            backup_file = os.path.join(backup_dir, f"backup_{timestamp}_{filename}")
            
            import shutil
            shutil.copy2(self.current_file, backup_file)
            
            log_info(f"Created backup: {backup_file}")
            return True, backup_file
            
        except Exception as e:
            error_msg = f"Error creating backup: {str(e)}"
            log_error(error_msg)
            return False, error_msg

# Global CSV handler instance
csv_handler = CSVHandler()

# Convenience functions
def save_csv(data, filename=None):
    """Quick save data to CSV"""
    handler = CSVHandler()
    handler.add_batch(data)
    return handler.save_to_csv(filename)

def load_csv(filepath):
    """Quick load data from CSV"""
    handler = CSVHandler()
    return handler.load_from_csv(filepath)

def get_csv_stats(filepath):
    """Get statistics from CSV file"""
    handler = CSVHandler()
    success, result = handler.load_from_csv(filepath)
    if success:
        return handler.get_statistics()
    return {"error": result}