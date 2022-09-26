#!/usr/bin/python
# -*- coding: utf-8 -*-

import boto3
from datetime import date, timedelta

email_list = {}


def lambda_handler(event, context):
    currentDay = date.today()
    requestedDay = currentDay - timedelta(days=7)
    client = boto3.client('ce')
    response = client.get_cost_and_usage(TimePeriod={'Start': requestedDay.strftime("%Y-%m-%d"),
                                                     'End': currentDay.strftime("%Y-%m-%d")},
                                         Granularity='MONTHLY',
                                         Metrics=['UnblendedCost'],
                                         GroupBy=[{'Type': 'TAG',
                                                   'Key': 'aws:createdBy'}])

    for item in response['ResultsByTime'][0]['Groups']:
        if len(item['Keys'][0].split(':')) > 2:
            if item['Keys'][0].split(':')[3] not in email_list.keys() and item['Keys'][0].split(':')[3].find('@presidio.com') != -1:
                email_list[item['Keys'][0].split(':')[3]] = float(
                    item['Metrics']['UnblendedCost']['Amount'])
            elif (item['Keys'][0].split(':')[3] in email_list.keys() and item['Keys'][0].split(':')[3].find('@presidio.com') != -1):
                email_list[item['Keys'][0].split(':')[3]] = float(email_list[item['Keys'][0].split(
                    ':')[3]]) + float(item['Metrics']['UnblendedCost']['Amount'])

    return {'statusCode': 200, 'body': email_list}
