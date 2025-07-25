import requests
import json
import boto3
import os
from urllib.parse import quote_plus, urlencode
import lib.sanitize

def is_profile_admin(profile_name):
    session = boto3.Session(profile_name=profile_name)
    iam = session.client('iam')
    
    try:
        # Attempt to list IAM roles as a test of broad permissions
        iam.list_roles(MaxItems=1)
        print(f"The profile '{profile_name}' appears to have administrative privileges.")
        return True
    except Exception as error:
        if error.response['Error']['Code'] == 'AccessDenied':
            print(f"The profile '{profile_name}' does not have administrative privileges.")
        else:
            print(f"An error occurred: {error.response['Error']['Message']}")
        return False

def assume_role(access_key_id, secret_access_key, role_arn, session_name, exchange, logs, region=None):
    if region is None:
        region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
    print(f"Assuming role: Role ARN = {role_arn}, Session Name = {session_name}")
    try:
        # Create an STS client with the provided credentials
        sts_client = boto3.client(
            'sts',
            region_name=region,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key
        )
        response = sts_client.assume_role(RoleArn=role_arn, RoleSessionName=session_name)
        credentials = response['Credentials']
        sanitized_credentials = {
            "AccessKeyId": credentials['AccessKeyId'],
            "SecretAccessKey": credentials['SecretAccessKey'],
            "SessionToken": credentials['SessionToken'],
            "Expiration": credentials['Expiration'].isoformat() if 'Expiration' in credentials else None
        }
        exchange.append(sanitized_credentials)


        logs.append(f"Successfully assumed role")

        return {
            'AccessKeyId': credentials['AccessKeyId'],
            'SecretAccessKey': credentials['SecretAccessKey'],
            'SessionToken': credentials['SessionToken']
        }
    except Exception as e:
        logs.append(f"Error assuming role: {str(e)}")
        return None

def console_login(user_name, access_key_id, secret_access_key, exchange, logs, region=None):
    if region is None:
        region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
    sts_client = boto3.client(
            'sts',
            region_name=region,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key
        )
    
    sts_client.get_caller_identity()

    logs.append("Requesting federation token to access AWS console")
    federation_token_response = sts_client.get_federation_token(
        Name=user_name,
        Policy=json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": "*",
                "Resource": "*"
            }]
        }),
        DurationSeconds=3600  # 1 hour
    )
   

    sanitized_federation_response = {
        "Credentials": {
            "AccessKeyId": federation_token_response['Credentials']['AccessKeyId'],
            "SecretAccessKey": federation_token_response['Credentials']['SecretAccessKey'],
            "SessionToken": federation_token_response['Credentials']['SessionToken'],
            "Expiration": federation_token_response['Credentials']['Expiration'].isoformat()
        },
        "FederatedUser": {
            "FederatedUserId": federation_token_response['FederatedUser']['FederatedUserId'],
            "Arn": federation_token_response['FederatedUser']['Arn']
        }
    }
    exchange.append(sanitized_federation_response)

    temp_credentials = federation_token_response['Credentials']
    logs.append("Temporary security credentials obtained.")
   
    logs.append("Creating sign-in token for AWS console access")
    request_parameters = {
        "sessionId": temp_credentials['AccessKeyId'],
        "sessionKey": temp_credentials['SecretAccessKey'],
        "sessionToken": temp_credentials['SessionToken']
    }
    request_url = f"https://signin.aws.amazon.com/federation?Action=getSigninToken&Session={quote_plus(json.dumps(request_parameters))}"
    response = requests.get(request_url)
    signin_token = response.json().get('SigninToken')
    if signin_token:
        logs.append("Sign-in token created successfully.")
    else:
        logs.append("Failed to create sign-in token.")
        exit()
   
    console_url = "https://signin.aws.amazon.com/federation"
    console_destination = f"https://{region}.console.aws.amazon.com/" if region != 'us-east-1' else "https://console.aws.amazon.com/"
    console_parameters = {
        "Action": "login",
        "Issuer": "",
        "Destination": console_destination,
        "SigninToken": signin_token
    }

    final_url = f"{console_url}?{urlencode(console_parameters)}"
    logs.append(f"Login URL: {final_url}")

    response = requests.get(final_url)

    if response.status_code == 200:
        logs.append("URL invoked successfully.")
    else:
        logs.append(f"Failed to invoke URL. Status code: {response.status_code}")

def create_client_with_credentials(service, region, access_key, secret_key):
    client = boto3.client(
        service,
        region_name=region,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key)
    return client
    
def create_client_with_sts_credentials(service, region, access_key, secret_key, session_token):
    client = boto3.client(
        service,
        region_name=region,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        aws_session_token=session_token)
    return client

def create_client_profile(service, region, profile):
    session = boto3.Session(profile_name=profile)
    client = session.client(service, region_name = region)
    return client

def create_user(client, user_name, exchange, logs, resources):
    try:
        response = client.create_user(UserName=user_name)
        sanitized_user_response = {
            "User": {
                "UserName": response['User']['UserName'],
                "UserId": response['User']['UserId'],
                "Arn": response['User']['Arn'],
                "Path": response['User']['Path']
            },
            "ResponseMetadata": {
                "HTTPStatusCode": response["ResponseMetadata"]["HTTPStatusCode"]
            }
        }
        exchange.append({"operation" : "create iam user", "response": sanitized_user_response})
        resources['users'].append(user_name)
        logs.append(f"User {user_name} created successfully.")
        return response['User']
    except Exception as e:
        print(f"Error creating user {user_name}: {e}")

def create_access_key(client, user_name, exchange, logs, resources):
    try:
        response = client.create_access_key(UserName=user_name)

        logs.append(f"Access key created for user {user_name}.")
        resources['iam_credentials'].append({"userAccessKey": user_name, 
                                             "accessKeyId" : response['AccessKey']['AccessKeyId'], 
                                             "secretAccessKey": response['AccessKey']['SecretAccessKey']})
        
        obfuscated_response = lib.sanitize.obfuscate_access_key(response)
        
        exchange.append({"operation" : "create iam user credentials", "response": obfuscated_response})


        return response
    except Exception as e:
        print(f"Error creating access key for user {user_name}: {e}")

def attach_policy_to_user(client, user_name, policy_arn, exchange, logs, resources): 
    try:
        response = client.attach_user_policy(
            UserName=user_name,
            PolicyArn=policy_arn
        )
        sanitized_attach_response = {
            "ResponseMetadata": {
                "HTTPStatusCode": response["ResponseMetadata"]["HTTPStatusCode"]
            }
        }
        exchange.append({"operation" : f"attach_user_policy for user: {user_name}", "response": sanitized_attach_response})

        logs.append(f"Policy {policy_arn} attached to user {user_name} successfully.")
    except Exception as e:
        logs.append(f"Error attaching policy: {e}")

def get_profile_account_id(profile, region=None):
    if region is None:
        region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
    client = create_client_profile('sts', region, profile)
    caller_identity = client.get_caller_identity()
    account_number = caller_identity['Account']
    return account_number

def create_iam_policy(client, policy_name, policy_document, exchange, logs, resources):
    response = client.create_policy(
        PolicyName=policy_name,
        PolicyDocument=json.dumps(policy_document),
    )
    resources['policies'].append(response['Policy']['Arn'])
    sanitized_policy_response = {
        "Policy": {
            "PolicyName": response['Policy']['PolicyName'],
            "Arn": response['Policy']['Arn'],
            "PolicyId": response['Policy']['PolicyId']
        },
        "ResponseMetadata": {
            "HTTPStatusCode": response["ResponseMetadata"]["HTTPStatusCode"]
        }
    }
    exchange.append({"operation": "create custom policy", "response": sanitized_policy_response})


    return response['Policy']['Arn']
