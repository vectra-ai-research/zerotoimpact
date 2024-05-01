import boto3
import json
import os
import time
from lib.instance_repo import add_to_disk
from lib.iam_operations import create_client_profile

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

lambdaManager_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "lambdaManager",
            "Effect": "Allow",
            "Action": [
                "lambda:*",
                "iam:PassRole"
            ],
            "Resource": "*"
        }
    ]
}

debug_role_document = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}

class CreateLambdaPriEsc:
    def __init__(self, id, profile, pathToDisk):
        self.id = id
        self.aws_region = 'us-east-1'
        self.profile = profile 
        session = boto3.Session(profile_name=profile)
        self.client = session.client('iam')
        self.logs =  []
        self.exchange = []
        self.resources = []
        self.resources_v2 = {
            "ssm_params": []
        }
        self.status = None
        self.step = 0
        self.filename= os.path.abspath(f"{pathToDisk}/{self.id}.json")

    def create(self):
        self.status = 'create_started'
        
        try:
            self.step = 1
            user_name = f"sean-{self.id}"
            policy_arn = self.create_policy(f"sean-policy-{self.id}", iam_policy)
            self._add_to_disk()
            
            user = self.create_user(user_name)
            self._add_to_disk()

            self.create_access_key(user_name)
            self._add_to_disk()

            self.attach_user_policy(user_name, policy_arn)
            self._add_to_disk()

            lambdaManager_policy_document = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                    "Action": "sts:AssumeRole",
                    "Principal": {
                        "AWS": f"{user['Arn']}"
                    },
                    "Effect": "Allow",
                    "Sid": ""
                    }
                ]
            }

            policy_arn = self.create_policy(f"lambdaManager-policy-{user_name}", lambdaManager_policy)
            self._add_to_disk()

            time.sleep(15)
            
            self.step = 2
            role = self.create_role(f"lambdaManager-role-{self.id}", lambdaManager_policy_document, policy_arn)
            self._add_to_disk()

            self.step = 3
            role = self.create_role(f"debug-role-{self.id}", debug_role_document, "arn:aws:iam::aws:policy/AdministratorAccess")
            self._add_to_disk() 

            self.step = 4
            self.create_ssm_parameters()
            self.status = 'create_complete'
            self._add_to_disk()
        except Exception as e:
            self.status = 'create_failed'
            self.logs.append(f"Create failed: {e}")
            print(f"Create failed: {e}")
            self._add_to_disk()    

    def create_role(self, role_name, policy_document, permissions):
        response = self.client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(policy_document)
        )

        self.exchange.append(response)
        self.logs.append(f"Role {role_name} created successfully.")
        self.resources.append({f"role": role_name, "arn": response['Role']})  

        self.client.attach_role_policy(
            RoleName=role_name,
            PolicyArn=permissions
        )
        self.logs.append(f"Attached {permissions} policy to '{role_name}' role.")
        
    def create_policy(self, policy_name, policy_document):
        response = self.client.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document)
        )
        policy_arn = response['Policy']['Arn']

        self.exchange.append(response)
        self.logs.append(f"Policy created successfully: {policy_arn}")
        self.resources.append({"policy_name": policy_name, "arn": response['Policy']['Arn']})            
        return policy_arn
       
    def create_user(self, user_name):
        user = self.client.create_user(UserName=user_name)
        self.exchange.append(user)
        self.logs.append(f"User {user_name} created successfully.")
        self.resources.append({"user": user['User']['UserName'], "details": user['User']})

        return user['User']
         
    def attach_user_policy(self, user_name, policy_arn):
        response = self.client.attach_user_policy(UserName=user_name, PolicyArn=policy_arn)
        self.exchange.append(response)
        self.logs.append(f"Policy {policy_arn} attached to user {user_name} successfully.")
       
    def create_access_key(self, user_name):
        response = self.client.create_access_key(UserName=user_name)

        self.exchange.append(response)
        self.logs.append(f"Access key created for user {user_name}.")
        self.resources.append({"userAccessKey": user_name, 
                                        "accessKeyId" : response['AccessKey']['AccessKeyId'], 
                                        "secretAccessKey": response['AccessKey']['SecretAccessKey']})
        return response['AccessKey']
         
    def create_ssm_parameters(self):
        client = create_client_profile('ssm', self.aws_region, self.profile)
            
        for i in range(1, 11):
            param_name = f"/zerotoimpact-{self.id}/{i}"
            param_value = f"Value{i}"
            
            try:
                response = client.put_parameter(
                    Name=param_name,
                    Value=param_value,
                    Type='String', 
                    Overwrite=True  
                )
                self.resources_v2['ssm_params'].append(param_name)
                self.exchange.append({"operation":"put_parameter", "response":response})
            except Exception as e:
                print(f"Error creating parameter {param_name}: {e}")

        self.logs.append(f"Created ssm parameters")

    def _add_to_disk(self):
        add_to_disk(self.filename, self.id, self.status, self.step, self.exchange, self.logs, self.resources, self.resources_v2)
   