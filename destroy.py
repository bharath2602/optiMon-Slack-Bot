import os


from utils.log_util import logger
from utils.send_msg import send_response
import boto3
import json

# Get Bot User OAuth Access token from environment
BOT_TOKEN = os.environ["BOT_TOKEN"]

# Slack URL to send bot replies
SLACK_URL = "https://slack.com/api/chat.postMessage"


def handler(event, context):
    logger.info("Request Event: {}".format(event))
    # try:
    # Default empty response
    request_body_json = event['body']['payload']
    request_body_json = json.loads(request_body_json)
    request_block_list = request_body_json.get('message')
    user_id = request_body_json['user'].get('id')
    text_msg = request_block_list['text']
    split_msg = text_msg.split('\n')
    service_type = split_msg[0].split(' ')[-1]
    logger.info("Service Type {}".format(service_type))
    id = split_msg[1].split(' ')[-1]
    region = split_msg[2].split(' ')[-1]
    msg = f"<@{user_id}> {service_type} - {id}"
    response_status_code = None
    if service_type.lower() == 'ec2':
        response_status_code = destroy_ec2(id)
    elif service_type.lower() == 'rds':
        response_status_code = destroy_rds(id)
    if response_status_code == 200:
        msg += f" - Deleted Successfully"
    else:
        msg += f" - Error terminating the Service "

    # send response to user
    response_url = request_body_json['response_url']
    send_response(response_url, msg)


def destroy_ec2(instance_id):
    status_code = 0
    client = boto3.client('ec2')
    try:
        response = client.terminate_instances(
            InstanceIds = [
                instance_id
            ]
        )
        status_code = 200
    except Exception as exp:
        logger.error(exp)
    return status_code
    
def destroy_rds(id):
    status_code = 0
    client = boto3.client('rds')
    try:
        response = client.delete_db_instance(
            DBInstanceIdentifier = id
        )
        status_code = 200
    except Exception as exp:
        logger.error(exp)
    return status_code
    