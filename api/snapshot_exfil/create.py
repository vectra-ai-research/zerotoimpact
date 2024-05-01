import boto3
import time
import json
import os
from lib.iam_operations import create_client_profile
from lib.instance_repo import add_to_disk
 
class Create:
    def __init__(self, id, profile, region, pathToDisk):
        self.api_logs = []
        self.important_logs = []
        self.resources = {
            'iam_role': '',
            'instance_profile': '',
            'ec2_instance': '',
            'rds_snapshot': '',
            'rds_instance': '',
            'rds_snapshot_id': ''
        }
        self.id = id
        self.profile = profile
        self.region = region
        self.step = 0
        self.status = None
        self.filename = os.path.abspath(f"{pathToDisk}/{self.id}.json")

    def create(self):
        self.status = "create_started"
        try:
            self.step = 1
            role_name = f"EC2RDSFullAccessRole-{self.id}"
            policy_arn = "arn:aws:iam::aws:policy/AmazonRDSFullAccess"
            role_name = f"EC2RDSFullAccessRole-{self.id}"
            db_instance_identifier = f"zti-db-instance-id-{self.id}"  
            snapshot_identifier = f"zti-db-snapshot-id-{self.id}"
            self.resources['rds_snapshot_id'] = snapshot_identifier
            db_instance_class = "db.t3.micro"
            db_engine = "mysql"
            master_username = "ztiadmin"
            master_user_password = f"admin-zti-{self.id}" 
            self.create_iam_role_and_profile(role_name, policy_arn)
            self._add_to_disk()

            self.step = 2
            self.launch_ec2_instance('ami-0f403e3180720dd7e',"t2.micro", role_name)
            self._add_to_disk()

            self.step = 3
            self.create_rds_instance(db_instance_identifier, db_instance_class, db_engine, master_username, master_user_password)
            self._add_to_disk()

            self.step = 4
            self.create_rds_snapshot(db_instance_identifier,snapshot_identifier)
            self.status = "create_complete"
            self._add_to_disk()
        except Exception as e:
            self.status = "create_failed"
            self.log_important(f"Error in create {e}")
            print(f"Create failed {e}")
            self._add_to_disk()

    def _add_to_disk(self):
        add_to_disk(self.filename, self.id, self.status, self.step, self.api_logs, self.important_logs, self.resources)
   
    def log_api_call(self, operation, response):
        self.api_logs.append({'operation': operation, 'response': response})

    def log_important(self, message):
        self.important_logs.append(message)

    def create_rds_snapshot(self, db_instance_identifier, snapshot_identifier):        
        rds_client = create_client_profile('rds', self.region, self.profile)
        response = rds_client.create_db_snapshot(
            DBSnapshotIdentifier=snapshot_identifier,
            DBInstanceIdentifier=db_instance_identifier
        )
        snapshot_arn = response['DBSnapshot']['DBSnapshotArn']
        self.resources['rds_snapshot'] = snapshot_arn
        self.log_important(f"RDS snapshot {snapshot_identifier} created for instance {db_instance_identifier}.")
         
    def create_iam_role_and_profile(self, role_name, policy_arn):
        client = create_client_profile('iam', self.region, self.profile)
        iam_role = client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps({
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "ec2.amazonaws.com"},
                    "Action": "sts:AssumeRole"}]
            })
        )
        self.log_api_call('create_role', iam_role) 
        attach_policy_response = client.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
        client.attach_role_policy(
            RoleName=role_name,
            PolicyArn="arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
        )
        self.log_api_call('attach_role_policy (AmazonRDSFullAccess)', attach_policy_response)   

        instance_profile_response = client.create_instance_profile(InstanceProfileName=role_name)
        self.log_api_call('create_instance_profile', instance_profile_response)   

        add_role_response = client.add_role_to_instance_profile(InstanceProfileName=role_name, RoleName=role_name)
        self.log_api_call('add_role_to_instance_profile', add_role_response)  # Log API call

        self.resources['iam_role'] = iam_role['Role']['Arn']
        self.resources['instance_profile'] = role_name
        
        self.log_important(f"IAM role {role_name} and instance profile created.")
        time.sleep(10)
       
    def launch_ec2_instance(self, image_id, instance_type, instance_profile_name):
        user_data_script = """#!/bin/bash
                cd /tmp
                sudo yum install -y https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/linux_amd64/amazon-ssm-agent.rpm
                sudo systemctl enable amazon-ssm-agent
                sudo systemctl start amazon-ssm-agent
            """
         
        ec2_client = create_client_profile('ec2', self.region, self.profile)
        ec2_response = ec2_client.run_instances(
            ImageId=image_id,
            InstanceType=instance_type,
            IamInstanceProfile={'Name': instance_profile_name},
            MinCount=1,
            MaxCount=1,
            UserData=user_data_script,
            MetadataOptions={'HttpTokens': 'optional'}
        )
        instance_id = ec2_response['Instances'][0]['InstanceId']
        self.log_api_call('run_instances', ec2_response)  # Log API call

        self.resources['ec2_instance'] = instance_id
        self.log_important(f"EC2 instance {instance_id} launched with profile {instance_profile_name}.")
         
    def create_rds_instance(self, db_instance_identifier, db_instance_class, db_engine, master_username, master_user_password):
        rds_client = create_client_profile('rds', self.region, self.profile)
        db_response = rds_client.create_db_instance(
            DBInstanceIdentifier=db_instance_identifier,
            AllocatedStorage=20,   
            DBInstanceClass=db_instance_class,
            Engine=db_engine,
            MasterUsername=master_username,
            MasterUserPassword=master_user_password,
            BackupRetentionPeriod=7,   
        )
        self.resources['rds_instance'] = db_instance_identifier
        self.log_api_call('create_db_instance', db_response)
        self.log_important(f"RDS instance creation initiated: {db_instance_identifier}")

        waiter = rds_client.get_waiter('db_instance_available')
        waiter.wait(DBInstanceIdentifier=db_instance_identifier)
        self.log_important("RDS instance is now available.")
         
            