import boto3
from lib.iam_operations import create_client_with_sts_credentials

class IAMEnum:
    def __init__(self, user_name, access_key, secret_key, region, token = ''):
        self.exchange = []
        self.log = []
        self.aws_region = region
        self.access_key = access_key
        self.secret_key = secret_key
        self.user_name = user_name
        self.token = token

    def _client(self, client_name):
        if self.token:
            client = boto3.client(
            client_name,
            region_name=self.aws_region,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            aws_session_token=self.token)
        else:
            client = boto3.client(
            client_name,
            region_name=self.aws_region,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key)
            
        return client

    def noise_enum(self, exchange, logs):

        try:
            response = self._client('cloudtrail').list_trails()
            exchange.append({"operation": "list trails", "response": response})     
        except Exception as e:
            exchange.append(f"Error: {e}")

        try:
            response = self._client('s3').list_buckets()
            exchange.append({"operation": "list_buckets", "response": response}) 
        except Exception as e:
            exchange.append(f"Error: {e}")

        try:
            # Call to retrieve a list of RDS instances
            response = response = self._client('rds').describe_db_instances()
            exchange.append({"operation": "describe_db_instances", "response": response}) 
        except Exception as e:
            exchange.append(f"Error listing RDS instances: {e}")

        # try:
        #     response = self._client('iam').get_account_authorization_details()
        #     print(response)
        # except Exception as e:
        #     print(f"Error: {e}")

        try:
            response = self._client('iam').get_user(UserName=self.user_name)
            exchange.append({"operation": "get_user", "response": response})   
        except Exception as e:
            exchange.append(f"Error: {e}")

        try:
            response = self._client('iam').list_users()
            exchange.append({"operation": "list_users", "response": response})   
        except Exception as e:
            exchange.append(f"Error listing users: {e}")

        try:
            response = self._client('iam').list_groups()
            exchange.append({"operation": "list_groups", "response": response})   
        except Exception as e:
            exchange.append(f"Error listing groups: {e}")
    
        try:
            response = self._client('iam').list_groups_for_user(UserName=self.user_name)
            exchange.append({"operation": "list_groups_for_user", "response": response})   
        except Exception as e:
            exchange.append(f"Error: {e}")

        try:
            response = self._client('iam').attach_user_policy(
                PolicyArn='arn:aws:iam::aws:policy/AdministratorAccess',
                UserName=self.user_name
            )
            exchange.append({"operation": "attach_user_policy", "response": response})  
        except Exception as e:
            exchange.append(f"Error: {e}")

        try:
            response = self._client('iam').list_attached_user_policies(UserName=self.user_name)
            exchange.append({"operation": "list_attached_user_policies", "response": response}) 
        except Exception as e:
            exchange.append(f"Error: {e}")

        try:
            response = self._client('iam').list_user_policies(UserName=self.user_name)
            exchange.append({"operation": "list_user_policies", "response": response}) 
            for policy_name in response['PolicyNames']:
                policy_document = self._client('iam').get_user_policy(UserName=self.user_name, PolicyName=policy_name)
                exchange.append({"operation": "get_user_policy", "response": policy_document}) 
        except Exception as e:
            exchange.append(f"Error: {e}")

        try:
            response = self._client('iam').list_roles()
            exchange.append({"operation": "list_roles", "response": response}) 
        except Exception as e:
            exchange.append(f"Error: {e}")
        
    def get_iam_policy(self, policy_arn, exchange, logs):
        logs.append(f"Attempting to retrieve policy versions for: {policy_arn}")
        try:
            # List all policy versions
            response = self._client('iam').list_policy_versions(PolicyArn=policy_arn)
            logs.append("Policy versions listed successfully.")

            # Determine the default version ID directly from the list
            default_version_id = None
            for version in response['Versions']:
                if version['IsDefaultVersion']:
                    default_version_id = version['VersionId']
                    break

            if default_version_id:
                logs.append(f"Retrieving default policy version: {default_version_id}")
                response = self._client('iam').get_policy_version(PolicyArn=policy_arn, VersionId=default_version_id)
                exchange.append( response['PolicyVersion']['Document'])
                logs.append(f"Default policy version {default_version_id} retrieved successfully.")
                return response
            else:
                exchange.append("No default policy version found.")
                return None

        except Exception as e:
            logs.append(f"Error retrieving policy versions for {policy_arn}: {e}")
            return None

    def iam_role_enum(self, role_name, exchange, logs):
        iam = self._client('iam')

        try:
            logs.append(f"Getting details for role: {role_name}")
            role_details = iam.get_role(RoleName=role_name)
            exchange.append(f"Role Details: {role_details['Role']}")

            logs.append("\nListing inline role policies:")
            inline_policies = iam.list_role_policies(RoleName=role_name)
            for policy_name in inline_policies.get('PolicyNames', []):
                policy_details = iam.get_role_policy(RoleName=role_name, PolicyName=policy_name)
                exchange.append(f"  Policy Details: {policy_details}")

            logs.append("\nListing attached role policies:")
            attached_policies = iam.list_attached_role_policies(RoleName=role_name)
            for policy in attached_policies.get('AttachedPolicies', []):
                exchange.append(f"Policy ARN: {policy['PolicyArn']}\n")

        except Exception as e:
            exchange.append(f"Error: {e}")

    def list_attached_user_policies(self, user_name, exchange, logs):
        client = self._client('iam')

        try:
            response = client.list_attached_user_policies(
                UserName=user_name,
            )
            exchange.append(f"Policies attached to {user_name}: {response['AttachedPolicies']}")
            logs.append(f"List policies attached to {user_name}")
        except Exception as e:
            exchange.append(f"Error listing attached user policies: {e}")


def role_recon_sts_token(access_key, secret_key,  token, region, exchange_logs):

    try:
        client = create_client_with_sts_credentials('iam', region, access_key, secret_key, token)
        response = client.get_account_authorization_details()
        exchange_logs.append({"operation": "get_account_authorization_details", "response": response})   
    except Exception as e:
        exchange_logs.append(f"Error: {e}")

    try:
        client = create_client_with_sts_credentials('cloudtrail', region, access_key, secret_key, token)
        response = client.list_trails()
        exchange_logs.append({"operation": "list_trails", "response": response})     
    except Exception as e:
        exchange_logs.append(f"Error: {e}")

    try:
        client = create_client_with_sts_credentials('s3', region, access_key, secret_key, token)
        response = client.list_buckets()
        exchange_logs.append({"operation": "list_buckets", "response": response}) 
    except Exception as e:
        exchange_logs.append(f"Error: {e}")

    try:
        client = create_client_with_sts_credentials('rds', region, access_key, secret_key, token)
        response = client.describe_db_instances()
        exchange_logs.append({"operation": "describe_db_instances", "response": response}) 
    except Exception as e:
        exchange_logs.append(f"Error listing RDS instances: {e}")
