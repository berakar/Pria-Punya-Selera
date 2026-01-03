"""
BPJS AUTOMATION - DATA VALIDATOR
Validates all input data and formats
"""

import re
from datetime import datetime
from config import (
    KPJ_MIN_LENGTH, KPJ_MAX_LENGTH, KPJ_ALLOWED_CHARS,
    MIN_NAME_LENGTH, MAX_NAME_LENGTH, MIN_NIK_LENGTH, MAX_NIK_LENGTH,
    validate_kpj as config_validate_kpj
)

class DataValidator:
    """Data validation and sanitization"""
    
    @staticmethod
    def validate_kpj(kpj):
        """
        Validate KPJ format
        Returns: (is_valid, message)
        """
        return config_validate_kpj(kpj)
    
    @staticmethod
    def validate_kpj_list(kpj_list):
        """
        Validate list of KPJs
        Returns: (valid_kpjs, invalid_kpjs)
        """
        valid = []
        invalid = []
        
        for kpj in kpj_list:
            is_valid, message = DataValidator.validate_kpj(kpj)
            if is_valid:
                valid.append(kpj)
            else:
                invalid.append({"kpj": kpj, "error": message})
        
        return valid, invalid
    
    @staticmethod
    def validate_nik(nik):
        """Validate NIK format"""
        if not nik:
            return False, "NIK cannot be empty"
        
        if len(nik) != MIN_NIK_LENGTH:
            return False, f"NIK must be {MIN_NIK_LENGTH} digits"
        
        if not nik.isdigit():
            return False, "NIK must contain only digits"
        
        # Basic NIK validation (province code 01-94)
        province_code = nik[:2]
        if not (1 <= int(province_code) <= 94):
            return False, "Invalid province code in NIK"
        
        return True, "Valid NIK"
    
    @staticmethod
    def validate_name(name):
        """Validate name format"""
        if not name:
            return False, "Name cannot be empty"
        
        if len(name) < MIN_NAME_LENGTH:
            return False, f"Name must be at least {MIN_NAME_LENGTH} characters"
        
        if len(name) > MAX_NAME_LENGTH:
            return False, f"Name cannot exceed {MAX_NAME_LENGTH} characters"
        
        # Allow letters, spaces, dots, and hyphens
        if not re.match(r'^[a-zA-Z\s\.\-]+$', name):
            return False, "Name contains invalid characters"
        
        return True, "Valid name"
    
    @staticmethod
    def validate_date(date_str, date_format="%d-%m-%Y"):
        """Validate date format"""
        if not date_str:
            return False, "Date cannot be empty"
        
        try:
            datetime.strptime(date_str, date_format)
            return True, "Valid date"
        except ValueError:
            return False, f"Date must be in format: {date_format}"
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        if not email:
            return True, "Email is optional"  # Email can be empty
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(email_pattern, email):
            return True, "Valid email"
        else:
            return False, "Invalid email format"
    
    @staticmethod
    def validate_address(address):
        """Validate address format"""
        if not address:
            return False, "Address cannot be empty"
        
        if len(address) < 10:
            return False, "Address is too short"
        
        if len(address) > 200:
            return False, "Address is too long"
        
        return True, "Valid address"
    
    @staticmethod
    def sanitize_text(text):
        """Sanitize text input"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s\-\.\,]', '', text)
        
        return text.strip()
    
    @staticmethod
    def sanitize_kpj(kpj):
        """Sanitize KPJ input"""
        if not kpj:
            return ""
        
        # Remove any non-digit characters
        kpj = re.sub(r'[^\d]', '', kpj)
        
        return kpj.strip()
    
    @staticmethod
    def format_date_for_display(date_str, input_format="%d-%m-%Y", output_format="%d %B %Y"):
        """Format date for display"""
        try:
            date_obj = datetime.strptime(date_str, input_format)
            return date_obj.strftime(output_format)
        except:
            return date_str  # Return original if formatting fails
    
    @staticmethod
    def format_name_for_display(name):
        """Format name with proper capitalization"""
        if not name:
            return ""
        
        # Capitalize each word
        return ' '.join(word.capitalize() for word in name.split())
    
    @staticmethod
    def extract_kpj_from_text(text):
        """Extract KPJs from text"""
        # Find all sequences of digits with length between min and max
        pattern = r'\b\d{%d,%d}\b' % (KPJ_MIN_LENGTH, KPJ_MAX_LENGTH)
        matches = re.findall(pattern, text)
        
        # Filter valid KPJs
        valid_kpjs = []
        for match in matches:
            is_valid, _ = DataValidator.validate_kpj(match)
            if is_valid:
                valid_kpjs.append(match)
        
        return valid_kpjs
    
    @staticmethod
    def validate_workflow_data(data):
        """Validate complete workflow data"""
        errors = []
        
        # Check required fields
        required_fields = ['kpj', 'nama', 'nik', 'ttl']
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        
        # Validate individual fields
        if 'kpj' in data:
            is_valid, message = DataValidator.validate_kpj(data['kpj'])
            if not is_valid:
                errors.append(f"KPJ: {message}")
        
        if 'nama' in data:
            is_valid, message = DataValidator.validate_name(data['nama'])
            if not is_valid:
                errors.append(f"Nama: {message}")
        
        if 'nik' in data:
            is_valid, message = DataValidator.validate_nik(data['nik'])
            if not is_valid:
                errors.append(f"NIK: {message}")
        
        if 'ttl' in data:
            is_valid, message = DataValidator.validate_date(data['ttl'])
            if not is_valid:
                errors.append(f"TTL: {message}")
        
        # Validate optional fields
        if 'email' in data and data['email']:
            is_valid, message = DataValidator.validate_email(data['email'])
            if not is_valid:
                errors.append(f"Email: {message}")
        
        if 'alamat' in data and data['alamat']:
            is_valid, message = DataValidator.validate_address(data['alamat'])
            if not is_valid:
                errors.append(f"Alamat: {message}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def generate_test_data(count=5):
        """Generate test data for development"""
        import random
        
        test_data = []
        for i in range(1, count + 1):
            kpj = str(random.randint(10**(KPJ_MIN_LENGTH-1), 10**KPJ_MIN_LENGTH - 1))
            nik = '32' + str(random.randint(10**13, 10**14 - 1))
            
            data = {
                'kpj': kpj,
                'nama': f'Test User {i}',
                'nik': nik,
                'ttl': f'{random.randint(1,28):02d}-{random.randint(1,12):02d}-19{random.randint(70,90)}',
                'alamat': f'Jl. Test No.{i}, Kota Test',
                'email': f'test{i}@example.com',
                'status': 'TEST_DATA'
            }
            test_data.append(data)
        
        return test_data

# Global validator instance
validator = DataValidator()

# Convenience functions
def validate_kpj(kpj):
    return validator.validate_kpj(kpj)

def validate_kpj_list(kpj_list):
    return validator.validate_kpj_list(kpj_list)

def sanitize_text(text):
    return validator.sanitize_text(text)

def extract_kpjs(text):
    return validator.extract_kpj_from_text(text)