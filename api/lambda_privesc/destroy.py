import boto3
import os
from lib.iam_operations import create_client_profile
from lib.instance_repo import add_to_disk

class DestroyLambdaPriEsc:
    def __init__(self, id, profile, instance, pathToDisk):
        self.id = id
        self.profile = profile
        self.logs =  []
        self.aws_region = 'us-east-1'
        self.instance = instance
        self.resources = instance['resources']
        self.resources_v2 = instance['resourcesV2']
        self.status = None
        self.filename = os.path.abspath(f"{pathToDisk}/{self.id}.json")
        self.step = 0
    
    def destroy(self):
        self.status = 'destroy_started'
        try:
            if self.has_index(self.resources, 1):
                self.delete_iam_user(self.resources[1]['user'])
            self._add_to_disk()
            if self.has_index(self.resources, 0):
                self.delete_policy(self.resources[0]['arn'])
            self._add_to_disk()
            if self.has_index(self.resources, 4):
                self.delete_role(self.resources[4]['arn']['RoleName'], self.resources[3]['arn'])
            self._add_to_disk()
            if self.has_index(self.resources, 3):
                self.delete_policy(self.resources[3]['arn'])
            self._add_to_disk()
            if self.has_index(self.resources, 5):
                self.delete_role(self.resources[5]['arn']['RoleName'], "arn:aws:iam::aws:policy/AdministratorAccess")
            self._add_to_disk()
            if self.has_index(self.resources, 6):
                self.delete_function(self.resources[6]['function'])
            self._add_to_disk()
            if getattr(self, 'resources_v2', {}).get('ssm_params'):
                self.delete_ssm_params(self.resources_v2['ssm_params'])
            self.delete_zipfile()
            self.status = 'destroy_complete'
            self._add_to_disk()
        except Exception as e:
            self.status = 'destroy_failed'
            self.logs.append(f"Error destroy process failed: {e}")  
            print(f"Error destroy process failed: {e}")
            self._add_to_disk()
        
    def delete_iam_user(self, user_name):
        client = create_client_profile('iam', self.aws_region,self.profile)
        policies = client.list_attached_user_policies(UserName=user_name)['AttachedPolicies']
        for policy in policies:
            client.detach_user_policy(UserName=user_name, PolicyArn=policy['PolicyArn'])
        
        # Delete all access keys
        access_keys = client.list_access_keys(UserName=user_name)['AccessKeyMetadata']
        for key in access_keys:
            client.delete_access_key(UserName=user_name, AccessKeyId=key['AccessKeyId'])
        
        # Finally, delete the user
        client.delete_user(UserName=user_name)
        self.logs.append(f"User {user_name} deleted successfully.")
        print(f"User {user_name} deleted successfully.")

    def delete_policy(self, policy_arn):
        client = create_client_profile('iam', self.aws_region,self.profile)
        client.delete_policy(PolicyArn=policy_arn)
        self.logs.append(f"Policy {policy_arn} deleted successfully.")

    def delete_role(self, role_name, policy_arn):
        client = create_client_profile('iam', self.aws_region,self.profile)
        client.detach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
        client.delete_role(RoleName=role_name)
        self.logs.append(f"Role {role_name} deleted successfully.")

    def delete_function(self, function_name):
        client = create_client_profile('lambda', self.aws_region,self.profile)
        
        client.delete_function(
            FunctionName=function_name
        )
        self.logs.append(f"Lambda function '{function_name}' deleted successfully.")

    def delete_zipfile(self):
        file_path = "./api/lambda_privesc/lambda_function.py.zip"
        if os.path.exists(file_path):
            os.remove(file_path)
    
    def has_index(self, lst, index):
        try:
            _ = lst[index]
            return True      
        except IndexError:
            return False  
   
    def delete_ssm_params(self, ssm_params):
        client = create_client_profile('ssm', self.aws_region,self.profile)
        
        for param_name in ssm_params:
            client.delete_parameter(Name=param_name)
               
        self.logs.append(f"SSM Parameters deleted successfully")

    def _add_to_disk(self):
        add_to_disk(self.filename, self.id,self.status,self.step,self.instance["exchange"],self.instance["logs"],self.instance["resources"], self.instance["resourcesV2"])
