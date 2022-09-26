import json
import boto3
from botocore.config import Config
from utils.log_util import logger
from utils.send_msg import send_weekly_report
from get_cost_usage import get_cost_per_user

def handler(event, context):
    logger.info("Entering into function **get_all_resources_weekly**")
    # generate json file to maintain user and resources they created using resource groups tagging api
    generate_resources_per_user()
    # get cost json (with dummy parameter )
    cost_payload = get_cost_per_user('','')

    # send report
    user_id = None
    if event:
            if event['body']['command'] == '/get_report':
                user_id = event['body']['user_id']
    send_weekly_report(cost_payload, user_id)
    return 'success'


def generate_resources_per_user():
    resource_list_json=[]
    # only for two regions since testing
    regions = ["us-east-1", "us-east-2"]
    # try:
    s3 = boto3.resource('s3')
    s3object = s3.Object('input-user-json', 'users.json')
    final_resource_list_per_user={}
    detail_resource_list_per_user={}
    for region in regions:
        myconfig = Config(region_name = region)
        client = boto3.client("resourcegroupstaggingapi",config=myconfig)
        resource_list_json = client.get_resources (
        )
        for each_resource in resource_list_json['ResourceTagMappingList']:
            arn = each_resource["ResourceARN"]
            for each_resource_tag in each_resource['Tags']:
                if each_resource_tag['Key'] == 'created_by':
                    if each_resource_tag['Value'] in detail_resource_list_per_user:
                        detail_resource_list_per_user[each_resource_tag['Value']].append({"ARN": arn, "Tag": each_resource['Tags'], "region":region})
                    else:
                        detail_resource_list_per_user[each_resource_tag['Value']] = [{"ARN": arn, "Tag": each_resource['Tags'],"region":region}]
        final_resource_list_per_user['users']=detail_resource_list_per_user
    # put the json 
    s3object.put(
        Body=(bytes(json.dumps(detail_resource_list_per_user).encode('UTF-8')))
    )