"""
BPJS AUTOMATION - CONFIGURATION FILE
Edit URLs and settings according to your needs
"""

# ============================================
# URL CONFIGURATION - EDIT THESE URLs
# ============================================

# SIPP System URL - Edit this if needed
SIPP_URL = "https://sipp.bpjsketenagakerjaan.go.id/"

# DPT System URL - Edit this if needed  
DPT_URL = "https://cekdptonline.kpu.go.id/"

# LAPAK System URL - Edit this if needed
LAPAK_URL = "https://lapakasik.bpjsketenagakerjaan.go.id/?source=e419a6aed6c50fefd9182774c25450b333de8d5e29169de6018bd1abb1c8f89b"

# ============================================
# APPLICATION SETTINGS
# ============================================

APP_NAME = "BPJS Workflow Automation"
APP_VERSION = "2.0.0"
APP_AUTHOR = "BPJS Automation Team"

# File paths
DOWNLOAD_FOLDER = "/storage/emulated/0/Download/"
LOG_FOLDER = "/storage/emulated/0/Download/bpjs_logs/"
CSV_PREFIX = "bpjs_result_"

# Processing settings
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
REQUEST_TIMEOUT = 30  # seconds

# UI Settings
UI_REFRESH_RATE = 0.5  # seconds
PROGRESS_UPDATE_INTERVAL = 0.2  # seconds

# CSV Export settings
CSV_ENCODING = "utf-8"
CSV_DELIMITER = ","
CSV_QUOTING = "csv.QUOTE_MINIMAL"

# Logging levels
LOG_LEVEL_INFO = "INFO"
LOG_LEVEL_WARNING = "WARNING"
LOG_LEVEL_ERROR = "ERROR"
LOG_LEVEL_DEBUG = "DEBUG"

# ============================================
# VALIDATION SETTINGS
# ============================================

# KPJ validation
KPJ_MIN_LENGTH = 10
KPJ_MAX_LENGTH = 15
KPJ_ALLOWED_CHARS = "0123456789"

# Data validation
MIN_NAME_LENGTH = 3
MAX_NAME_LENGTH = 100
MIN_NIK_LENGTH = 16
MAX_NIK_LENGTH = 16

# ============================================
# SIMULATION SETTINGS (For testing)
# ============================================

SIMULATE_DELAYS = True
MIN_PROCESS_DELAY = 0.5  # seconds
MAX_PROCESS_DELAY = 2.0  # seconds
SUCCESS_RATE = 0.85  # 85% success rate

# ============================================
# COLOR SCHEME (UI Colors)
# ============================================

COLOR_PRIMARY = (0.2, 0.6, 1, 1)      # Blue
COLOR_SUCCESS = (0.2, 0.8, 0.2, 1)    # Green
COLOR_WARNING = (1, 0.8, 0.2, 1)      # Yellow
COLOR_ERROR = (0.9, 0.2, 0.2, 1)      # Red
COLOR_DISABLED = (0.7, 0.7, 0.7, 1)   # Gray

# ============================================
# TEXT MESSAGES
# ============================================

MESSAGES = {
    "ready": "Ready to process. Enter KPJ list below.",
    "processing": "Processing KPJ: {kpj} ({current}/{total})",
    "completed": "Processing completed! {processed} successful, {skipped} skipped.",
    "error_no_kpj": "Please enter at least one KPJ.",
    "error_invalid_kpj": "Invalid KPJ format: {kpj}",
    "saving_csv": "Saving results to CSV...",
    "csv_saved": "CSV saved successfully: {filename}",
    "csv_error": "Error saving CSV: {error}",
    "login_required": "Please login to the system first.",
    "network_error": "Network error. Please check connection.",
    "timeout_error": "Request timeout. Please try again.",
}

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_all_urls():
    """Return all configured URLs"""
    return {
        "sipp": SIPP_URL,
        "dpt": DPT_URL,
        "lapak": LAPAK_URL,
    }

def get_csv_path(filename=None):
    """Get full path for CSV file"""
    import os
    from datetime import datetime
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{CSV_PREFIX}{timestamp}.csv"
    
    # Ensure download folder exists
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    
    return os.path.join(DOWNLOAD_FOLDER, filename)

def validate_kpj(kpj):
    """Validate KPJ format"""
    if not kpj:
        return False, "KPJ cannot be empty"
    
    if len(kpj) < KPJ_MIN_LENGTH or len(kpj) > KPJ_MAX_LENGTH:
        return False, f"KPJ must be {KPJ_MIN_LENGTH}-{KPJ_MAX_LENGTH} digits"
    
    if not all(char in KPJ_ALLOWED_CHARS for char in kpj):
        return False, "KPJ must contain only digits"
    
    return True, "Valid KPJ"

# ============================================
# END OF CONFIGURATION
# ============================================