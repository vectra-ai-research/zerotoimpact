from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
import lambda_privesc.controller
import policy_ransom_exploit.controller
import snapshot_exfil.controller
import os
import threading

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

profile = os.getenv("AWS_DEFAULT_PROFILE")
if profile is not None:
    print(f"The value of AWS_DEFAULT_PROFILE is: {profile}")
else:
    # Instead of printing, we raise an exception
    raise Exception(f"AWS_DEFAULT_PROFILE is not set.")

aws_region = 'us-east-1'

@app.route('/api/lambda_privesc_create/<id>')
@cross_origin()
def lambda_privesc_create(id):
    def run_async_create_task(id, profile, aws_region):
        lambda_privesc.controller.create(id, profile, aws_region)
    
    # Start the asynchronous task
    thread = threading.Thread(target=run_async_create_task, args=(id, profile, aws_region))
    thread.start()
    return jsonify({}), 200

@app.route('/api/lambda_privesc_status/<id>')
@cross_origin()
def lambda_privesc_status(id):
    response = lambda_privesc.controller.get_status(id)
    return jsonify({"response": response}), 200

@app.route('/api/lambda_privesc_attack/<id>')
@cross_origin()
def lambda_privesc_attack(id):
    def run_async_create_task(id, profile, aws_region):
        lambda_privesc.controller.attack(id, profile, aws_region)
    
    # Start the asynchronous task
    thread = threading.Thread(target=run_async_create_task, args=(id, profile, aws_region))
    thread.start()
    return jsonify({}), 200
    
@app.route('/api/lambda_privesc_start_destroy/<id>')
@cross_origin()
def lambda_privesc_start_destroy(id):
    def run_async_create_task(id, profile, aws_region):
        lambda_privesc.controller.destroy(id, profile, aws_region)
    
    # Start the asynchronous task
    thread = threading.Thread(target=run_async_create_task, args=(id, profile, aws_region))
    thread.start()
    return jsonify({}), 200

@app.route('/api/lambda_privesc_complete_destroy/<id>')
@cross_origin()
def lambda_privesc_complete_destroy(id):
    lambda_privesc.controller.destroy_instance(id)
    return jsonify({}), 200

@app.route('/api/policy_ransom_exploit_create/<id>')
@cross_origin()
def policy_ransom_exploit_create(id):
    def run_async_create_task(id, profile, aws_region):
        policy_ransom_exploit.controller.create(id, profile, aws_region)
    
    # Start the asynchronous task
    thread = threading.Thread(target=run_async_create_task, args=(id, profile, aws_region))
    thread.start()
    return jsonify({}), 200

@app.route('/api/policy_ransom_exploit_status/<id>')
@cross_origin()
def policy_ransom_exploit_status(id):
    response = policy_ransom_exploit.controller.get_status(id)
    return jsonify({"response": response}), 200

@app.route('/api/policy_ransom_exploit_attack/<id>')
@cross_origin()
def policy_ransom_exploit_attack(id):
    def run_async_create_task(id, profile, aws_region):
        policy_ransom_exploit.controller.attack(id, profile, aws_region)
    
    # Start the asynchronous task
    thread = threading.Thread(target=run_async_create_task, args=(id, profile, aws_region))
    thread.start()
    return jsonify({}), 200

@app.route('/api/policy_ransom_exploit_start_destroy/<id>')
@cross_origin()
def policy_ransom_exploit_start_destroy(id):
    def run_async_create_task(id, profile, aws_region):
        policy_ransom_exploit.controller.destroy(id, profile, aws_region)
    
    # Start the asynchronous task
    thread = threading.Thread(target=run_async_create_task, args=(id, profile, aws_region))
    thread.start()
    return jsonify({}), 200

@app.route('/api/policy_ransom_exploit_complete_destroy/<id>')
@cross_origin()
def policy_ransom_exploit_complete_destroy(id):
    policy_ransom_exploit.controller.destroy_instance(id)
    return jsonify({}), 200

@app.route('/api/snapshot_exfil_create/<id>')
@cross_origin()
def snapshot_exfil_create(id):
    def run_async_create_task(id, profile, aws_region):
        snapshot_exfil.controller.create(id, profile, aws_region)
    
    # Start the asynchronous task
    thread = threading.Thread(target=run_async_create_task, args=(id, profile, aws_region))
    thread.start()
    return jsonify({}), 200

@app.route('/api/snapshot_exfil_status/<id>')
@cross_origin()
def snapshot_exfil_status(id):
    response = snapshot_exfil.controller.get_status(id)
    return jsonify({"response": response}), 200

@app.route('/api/snapshot_exfil_attack/<id>')
@cross_origin()
def snapshot_exfil_attack(id):
    def run_async_create_task(id, profile, aws_region):
        snapshot_exfil.controller.attack(id, profile, aws_region)  
     
    thread = threading.Thread(target=run_async_create_task, args=(id, profile, aws_region))
    thread.start()
    
    return jsonify({}), 200

@app.route('/api/snapshot_exfil_start_destroy/<id>')
@cross_origin()
def snapshot_exfil_start_destroy(id):
    def run_async_create_task(id, profile, aws_region):
        snapshot_exfil.controller.destroy(id, profile, aws_region)  
     
    thread = threading.Thread(target=run_async_create_task, args=(id, profile, aws_region))
    thread.start()

    return jsonify({}), 200

@app.route('/api/snapshot_exfil_complete_destroy/<id>')
@cross_origin()
def snapshot_exfil_complete_destroy(id):
    snapshot_exfil.controller.destroy_instance(id)
    return jsonify({}), 200

if __name__ == '__main__':
    app.run(debug=True)

