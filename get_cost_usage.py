#!/usr/bin/python
# -*- coding: utf-8 -*-

from utils.log_util import logger
import json
from urllib import response
import boto3
import datetime

email_list = {}


def get_cost_per_user(event, context):
    logger.info(event)
    today = datetime.date.today()
    client = boto3.client('ce')
    
    response = client.get_cost_and_usage(TimePeriod={'Start': (today - datetime.timedelta(days=7)).strftime("%Y-%m-%d"),
                                                     'End': today.strftime("%Y-%m-%d")},
                                         Granularity='MONTHLY',
                                         Metrics=['UnblendedCost'],
                                         GroupBy=[{'Type': 'TAG',
                                                   'Key': 'created_by'}])
    logger.info(response)
    for item in response['ResultsByTime'][0]['Groups']:
        if len(item['Keys'][0].split(':')) > 2:
            if item['Keys'][0].split(':')[3] not in email_list.keys() and item['Keys'][0].split(':')[3].find('@presidio.com') != -1:
                email_list[item['Keys'][0].split(':')[3]] = float(
                    item['Metrics']['UnblendedCost']['Amount'])
            elif (item['Keys'][0].split(':')[3] in email_list.keys() and item['Keys'][0].split(':')[3].find('@presidio.com') != -1):
                email_list[item['Keys'][0].split(':')[3]] = float(email_list[item['Keys'][0].split(
                    ':')[3]]) + float(item['Metrics']['UnblendedCost']['Amount'])
    print(email_list)
    return email_list
