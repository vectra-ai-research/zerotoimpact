from flask import jsonify
import os
from lib.instance_repo import read_from_desk
from .create import Create
from .destroy import Destroy
from .attack import Attack

instance_path = './api/snapshot_exfil/instances'

def create(id, profile, aws_region):
    instance = read_from_desk(id, instance_path)
    if instance:
        return {"id": instance['id'], "status": instance['status'], "step": instance['step']}

    create = Create(id, profile, aws_region, instance_path)
    create.create()
    return {"id": create.id, "status": create.status, "step": create.step}

def attack(id, profile, aws_region):
    instance = read_from_desk(id, instance_path)
    if instance['status'] == 'attack_finished':
        return {"id": instance['id'], "status": instance['status'], "step": instance['step']}
    
    attack = Attack(id, aws_region, instance, profile, instance_path)
    attack.attack()
    return {"id": attack.id, "status": attack.status, "step": attack.step}

def get_status(id):
    instance = read_from_desk(id,instance_path)
    if instance == None:
        return {"id": id, "status": "", "message": "ID not found"}

    exclude_keys = ['resources']
   
    for key in exclude_keys:
        instance.pop(key, None) 
     
    return instance

def destroy_instance(id):
    try:
        filename=f"{instance_path}/{id}.json"
        os.remove(filename)
            
        print(f"File {filename} has been successfully removed.")
    except FileNotFoundError:
        print(f"File {filename} does not exist, cannot remove.")
    except Exception as e:
        print(f"An error occurred: {e}")

def destroy(id, profile, aws_region):
    instance = read_from_desk(id, instance_path)
    if instance is None:
        return {"id": id, "status": "destroy_complete", "message": "ID not found"}
    
    destroy = Destroy(id, profile, aws_region, instance, instance_path)
    destroy.destroy()
    return {"id": destroy.id, "status": destroy.status, "message": destroy.logs}