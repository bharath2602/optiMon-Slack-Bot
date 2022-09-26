"""
Serverles Slack Bot Lambda handler.
"""
import os

from utils.log_util import logger
import json
import urllib3
import boto3

# Get Bot User OAuth Access token from environment
BOT_TOKEN = os.environ["BOT_TOKEN"]

# Slack URL to send bot replies
SLACK_URL = "https://slack.com/api/chat.postMessage"

http = urllib3.PoolManager()

def send_response(response_url, msg):
    # channel_id = "U0439HAF9RV"
    # bot_reply = "hello"
    try:
        payload =  {
        "response_type": "ephemeral",
        "replace_original": True,
        "text": msg
        }
        print(response_url, payload)
        # response = requests.post(response_url, json=payload, headers=headers)
        response = http.request(
            "POST",
            response_url,
            body=json.dumps(payload),
            headers={
                "Content-type": "application/json",
                "Authorization": f'Bearer {os.environ["BOT_TOKEN"]}',
            },
        )
        # data = urllib.parse.urlencode(
        #     (
        #         ("token", bot_token),
        #         ("channel", channel_id),
        #         ("text", bot_response)
        #     )
        # )
        # data = data.encode("ascii")

        # # Construct the HTTP request that will be sent to the Slack API.
        # request = urllib.request.Request(
        #     SLACK_URL,
        #     data=data,
        #     method="POST"
        # )

        # # Add a header mentioning that the text is URL-encoded.
        # request.add_header(
        #     "Content-Type",
        #     "application/x-www-form-urlencoded"
        # )

        # # Fire the request
        # bot_response_status = urllib.request.urlopen(request).read()
        # bot_response_status = bot_response_status.decode('utf-8').replace("'", '"')
        # bot_response_status = json.loads(bot_response_status)
        # is_sent = bot_response_status.get("ok")
        # return is_sent
    except Exception as ex:
        logger.error("*** Error while sending message from bot ***", str(ex))
    return 'success'



def send_weekly_report(cost_payload, user_id):
    s3 = boto3.resource("s3")
    content_object = s3.Object("input-user-json", "users.json")
    file_content = content_object.get()["Body"].read().decode("utf-8")
    json_content = json.loads(file_content)
    # if user_id:
    post_data = {}

    for data in json_content:
        for value in json_content[data]:
            resource_type = value["ARN"].split(":")[2]
            region = value["ARN"].split(":")[3]
            # print("Resource ID:", value["ARN"])

            # for rds
            resource_id = value["ARN"].split(":")[-1]

            #for ec2
            resource_id = resource_id.split('/')[-1]

            res1 = http.request(
                "GET",
                "https://slack.com/api/users.list",
                headers={"Authorization": f'Bearer {os.environ["BOT_TOKEN"]}'},
            )
            for user in json.loads(res1.data.decode("utf-8"))["members"]:
                try:
                    if user_id:
                        if data == user["profile"]["email"] and user["id"] == user_id:
                            post_data = {
                                "channel": user["id"],
                                "blocks":  [
                                    {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": f"*Type :* {resource_type}\n *ID:* {resource_id}\n *Region:* {region}",
                                    },
                                    "accessory": {
                                        "type": "button",
                                        "text": {
                                            "type": "plain_text",
                                            "emoji": True,
                                            "text": "Destroy",
                                        },
                                        "style": "danger",
                                        "value": resource_id,
                                    },
                                }
                                ]
                            }
                            logger.info(post_data)
                            res = http.request(
                                "POST",
                                "https://slack.com/api/chat.postMessage",
                                body=json.dumps(post_data),
                                headers={
                                    "Content-type": "application/json",
                                    "Authorization": f'Bearer {os.environ["BOT_TOKEN"]}',
                                },
                            )
                    else:
                        if data == user["profile"]["email"]:
                            post_data = {
                                "channel": user["id"],
                                "blocks":  [
                                    {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": f"*Type :* {resource_type}\n *ID:* {resource_id}\n *Region:* {region}",
                                    },
                                    "accessory": {
                                        "type": "button",
                                        "text": {
                                            "type": "plain_text",
                                            "emoji": True,
                                            "text": "Destroy",
                                        },
                                        "style": "danger",
                                        "value": resource_id,
                                    },
                                }
                                ]
                            }
                            logger.info(post_data)
                            res = http.request(
                                "POST",
                                "https://slack.com/api/chat.postMessage",
                                body=json.dumps(post_data),
                                headers={
                                    "Content-type": "application/json",
                                    "Authorization": f'Bearer {os.environ["BOT_TOKEN"]}',
                                },
                            )
                except:
                    # print(user["profile"]["email"], data)
                    logger.info("error not an user ")
    cost_data = {
        "channel": post_data['channel'],
        "text": "*Bill Amount(USD):* "+cost_payload.get(data, '0')
    }
    http.request(
        "POST",
        "https://slack.com/api/chat.postMessage",
        body=json.dumps(cost_data),
        headers={
            "Content-type": "application/json",
            "Authorization": f'Bearer {os.environ["BOT_TOKEN"]}',
        },
    )
        
    logger.info("Successfully sent report to user")
    return 'success'


