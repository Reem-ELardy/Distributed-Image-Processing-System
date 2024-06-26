import time

import boto3
import paramiko

# AWS configuration (better to set in environment variables or use IAM roles)
region_name = 'eu-west-2'  # Ensure this is the correct region

# List of instance IDs
instance_ids = ['i-0df8310af7e44104f', 'i-0292bca7e7ad04153', 'i-0a26050d82519ca18', 'i-09536d7b0d812c9e3']
# instance_ids = ['i-09536d7b0d812c9e3']

target_group_arn = "arn:aws:elasticloadbalancing:eu-west-2:654654207475:targetgroup/Distributed-Target/53b2bcc68c9b87f6"

ec2_client = boto3.client('ec2', region_name=region_name)
elbv2_client = boto3.client('elbv2', region_name=region_name)

# Parameters for launching instances
user_data_script = [
    "cd Phase3 && python3 cmd.py"
]


# Function to start EC2 instances
def start_instance(instance_id,):
    try:
        response = ec2_client.start_instances(InstanceIds=[instance_id])
        print(f"Starting instance: {instance_id}")
        waiter = ec2_client.get_waiter('instance_running')
        waiter.wait(InstanceIds=[instance_id])
        print(f"Instance {instance_id} is now running")
    except Exception as e:
        print(f"Error starting instance {instance_id}: {e}")


# Function to stop EC2 instances
def stop_instance(instance_id):
    try:
        response = ec2_client.stop_instances(InstanceIds=[instance_id])
        print(f"Stopping instance: {instance_id}")
        waiter = ec2_client.get_waiter('instance_stopped')
        waiter.wait(InstanceIds=[instance_id])
        print(f"Instance {instance_id} is now stopped")
    except Exception as e:
        print(f"Error stopping instance {instance_id}: {e}")


# Function to send commands to an instance
def wait_for_status(instance_id):
    try:
        # Check instance status
        while True:
            # Check instance status
            instance_status = ec2_client.describe_instance_status(InstanceIds=[instance_id])
            if not instance_status['InstanceStatuses']:
                print(f"Instance {instance_id} is not in a valid state.")
                return
            if instance_status['InstanceStatuses'][0]['InstanceStatus']['Status'] == 'ok':
                break
            print(f"Waiting for instance {instance_id} to be in a valid state...")
            time.sleep(20)  # Wait for 5 seconds before checking again
        print(f"Commands sent to instance {instance_id}")
    except Exception as e:
        print(f"Error sending commands to instance {instance_id}: {e}")


# Function to send commands to an instance
def send_commands(instance_id, commands, region_name):
    ssm_client = boto3.client('ssm', region_name=region_name)
    try:
        # Check instance status
        wait_for_status(instance_id)

        # Send commands
        response = ssm_client.send_command(
            InstanceIds=[instance_id],
            DocumentName="AWS-RunShellScript",
            Parameters={'commands': commands}
        )
        print(f"Commands sent to instance {instance_id}")
    except Exception as e:
        print(f"Error sending commands to instance {instance_id}: {e}")



def register_instances(target_group_arn, instance_ids):
    try:
        response = elbv2_client.register_targets(
            TargetGroupArn=target_group_arn,
            Targets=[{'Id': instance_id, 'Port': 8080} for instance_id in instance_ids]
        )
        print(f"Instances {instance_ids} registered with target group {target_group_arn}")
    except Exception as e:
        print(f"Error registering instances {instance_ids}: {e}")


# Function to deregister instances from a target group
def deregister_instances(target_group_arn, instance_ids):
    try:
        response = elbv2_client.deregister_targets(
            TargetGroupArn=target_group_arn,
            Targets=[{'Id': instance_id, 'Port': 8080} for instance_id in instance_ids]
        )
        print(f"Instances {instance_ids} deregistered from target group {target_group_arn}")
    except Exception as e:
        print(f"Error deregistering instances {instance_ids}: {e}")


def wait_for_registration(target_group_arn, instance_ids):
    try:
        while True:
            response = elbv2_client.describe_target_health(TargetGroupArn=target_group_arn)
            target_states = {target['Target']['Id']: target['TargetHealth']['State'] for target in response['TargetHealthDescriptions']}
            if all(target_states.get(instance_id) == 'healthy' for instance_id in instance_ids):
                print("All instances are healthy.")
                break
            print("Waiting for instances to be healthy...")
            time.sleep(20)
    except Exception as e:
        print(f"Error waiting for registration of instances {instance_ids}: {e}")


# Main function to start instances and send commands
def main1(num):
    instance_id_used = []
    try:
        for i in range(num):
            start_instance(instance_ids[i])
            send_commands(instance_ids[i], user_data_script, region_name)
            instance_id_used.append(instance_ids[i])
        register_instances(target_group_arn, instance_id_used)
        wait_for_registration(target_group_arn, instance_id_used)
        print("Register")
        return instance_id_used
    except Exception as e:
        print(f"Error in main1: {e}")
        return instance_id_used


# Main function to stop instances
def main2(instance_id_used):
    try:
        deregister_instances(target_group_arn, instance_id_used)
        for instance_id in instance_id_used:
            stop_instance(instance_id)
    except Exception as e:
        print(f"Error in main2: {e}")
