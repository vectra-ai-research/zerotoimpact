from lib.iam_operations import create_client_profile
from lib.instance_repo import add_to_disk
import os

class Destroy:
    def __init__(self, id, profile, aws_region, instance,pathToDisk):
        self.id = id
        self.logs =  []
        self.instance = instance
        self.resources = instance['resources']
        self.profile = profile
        self.region = aws_region
        self.filename = os.path.abspath(f"{pathToDisk}/{self.id}.json")
        self.step = 0

    def destroy(self):
        self.status = 'destroy_started'
        try:
            if 'ec2_instance' in self.resources and self.resources['ec2_instance']:
                ec2_client = self._client('ec2')
                print(f"Terminating EC2 instance: {self.resources['ec2_instance']}")
                ec2_client.terminate_instances(InstanceIds=[self.resources['ec2_instance']])
                ec2_client.get_waiter('instance_terminated').wait(InstanceIds=[self.resources['ec2_instance']])
                self.logs.append(f"EC2 instance {self.resources['ec2_instance']} terminated.")
            self._add_to_disk()

            if 'rds_instance' in self.resources and self.resources['rds_instance']:
                rds_client = self._client('rds')
                print(f"Deleting RDS instance: {self.resources['rds_instance']}")
                rds_client.delete_db_instance(DBInstanceIdentifier=self.resources['rds_instance'], SkipFinalSnapshot=True)
                print("Waiting for RDS instance to be deleted...")
                rds_client.get_waiter('db_instance_deleted').wait(DBInstanceIdentifier=self.resources['rds_instance'])
                self.logs.append(f"RDS instance {self.resources['rds_instance']} deleted.")
            self._add_to_disk()

            if 'rds_snapshot' in self.resources and self.resources['rds_snapshot']:
                rds_client = self._client('rds')
                self.logs.append(f"Deleting RDS snapshot: {self.resources['rds_snapshot']}")
                rds_client.delete_db_snapshot(DBSnapshotIdentifier=self.resources['rds_snapshot_id'])
                self.logs.append(f"RDS snapshot {self.resources['rds_snapshot']} deleted.")
            self._add_to_disk()

            if 'iam_role' in self.resources and self.resources['iam_role']:
                iam_client = self._client('iam')
                role_name = self.resources['iam_role'].split('/')[1]
            
                policies = iam_client.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']
                for policy in policies:
                    iam_client.detach_role_policy(RoleName=role_name, PolicyArn=policy['PolicyArn'])
                    self.logs.append(f"Detached policy {policy['PolicyArn']} from role {role_name}.")
                
                if 'instance_profile' in self.resources and self.resources['instance_profile']:
                    iam_client.remove_role_from_instance_profile(InstanceProfileName=self.resources['instance_profile'], RoleName=role_name)
                    iam_client.delete_instance_profile(InstanceProfileName=self.resources['instance_profile'])
                    self.logs.append(f"Deleted instance profile {self.resources['instance_profile']}.")
                
                iam_client.delete_role(RoleName=role_name)
                self.logs.append(f"IAM role {role_name} deleted.")

            self.status = 'destroy_complete'
            self._add_to_disk()
        except Exception as e:
            self.status = 'destroy_failed'
            self.logs.append(f"Error destroy process failed: {e}")
            self._add_to_disk()

    def _client(self, service):
        return create_client_profile(service, self.region, self.profile)
    
    def _add_to_disk(self):
        add_to_disk(self.filename, self.id, self.status, self.step, self.instance["exchange"],self.instance["logs"],self.instance["resources"])
