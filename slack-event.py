from utils.log_util import logger
import json
import urllib3
import os
import boto3


def lambda_handler(event, context):
    http = urllib3.PoolManager()
    s3 = boto3.resource("s3")
    content_object = s3.Object("input-user-json", "users.json")
    file_content = content_object.get()["Body"].read().decode("utf-8")
    json_content = json.loads(file_content)

    logger.info(file_content)
    for data in json_content:
        post_data = {}
        for value in json_content[data]:
            res1 = http.request(
                "GET",
                "https://slack.com/api/users.list",
                headers={"Authorization": f'Bearer {os.environ["SLACK_TOKEN"]}'},
            )
            resource_type = value["ARN"].split(":")[2]
            region = value["ARN"].split(":")[3]
            resource_id = value["ARN"].split("/")[1]
            for user in json.loads(res1.data.decode("utf-8"))["members"]:
                try:
                    if data == user["profile"]["email"]:
                        post_data = construct_data(
                            user["id"], resource_type, resource_id, region, post_data
                        )
                except:
                    logger.info("error not an user")
        logger.info(post_data)
        res = http.request(
            "POST",
            "https://slack.com/api/chat.postMessage",
            body=json.dumps(post_data),
            headers={
                "Content-type": "application/json",
                "Authorization": f'Bearer {os.environ["SLACK_TOKEN"]}',
            },
        )
    return {"statusCode": 200, "body": "Hello Slack from Lambda"}


def construct_data(user_id, type, id, region, data):
    if "blocks" in data:
        logger.info("inside if block")
        data["channel"] = user_id
        data["blocks"].append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Type :* {type}\n *ID:* {id}\n *Region:* {region}",
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "Destroy",
                    },
                    "style": "danger",
                    "value": {"region": region, "resource_id": id, "resource": type},
                },
            }
        )
    else:
        logger.info("inside else block")
        data["channel"] = user_id
        data["blocks"] = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Type :* {type}\n *ID:* {id}\n *Region:* {region}",
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "Destroy",
                    },
                    "style": "danger",
                    "value": "click_me_123",
                },
            }
        ]
    return data
