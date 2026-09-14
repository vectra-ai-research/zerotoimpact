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

def obfuscate_access_key(response):
    access_key_id = response['AccessKey']['AccessKeyId']
    secret_access_key = response['AccessKey']['SecretAccessKey']
    
    obfuscated_access_key_id = access_key_id[:4] + '*' * (len(access_key_id) - 4)
    obfuscated_secret_access_key = secret_access_key[:4] + '*' * (len(secret_access_key) - 4)
    
    response['AccessKey']['AccessKeyId'] = obfuscated_access_key_id
    response['AccessKey']['SecretAccessKey'] = obfuscated_secret_access_key
    
    return response