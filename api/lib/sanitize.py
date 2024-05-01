import re

def sanitize_bucket_name(name):
    # Convert to lowercase
    sanitized_name = name.lower()
    
    # Remove unwanted characters
    sanitized_name = re.sub(r'[^a-z0-9.-]', '', sanitized_name)
    
    # Ensure the name does not start or end with dash or period
    sanitized_name = sanitized_name.strip('.-')
    
    # Ensure the length is within limits
    if len(sanitized_name) < 3:
        raise ValueError("Bucket name must be at least 3 characters after sanitizing")
    if len(sanitized_name) > 63:
        raise ValueError("Bucket name must be no more than 63 characters after sanitizing")
    
    return sanitized_name
