from pydoc import cli, resolve
from tracemalloc import start
import boto3
import pandas as pd
from datetime import datetime, timedelta, timezone

def get_average_cpu_utilization(instance_id,region):
    session = boto3.Session(profile_name="508414721836_AWSAdministratorAccess",region_name= region)
    client = session.client('cloudwatch')
    #metric = client.Metric('AWS/EC2','CPUUtilization')
    ec2 = session.resource('ec2')
    instance = ec2.Instance(instance_id)

    instance_type = instance.instance_type
    start_time = instance.launch_time
    current_time = datetime.now(timezone.utc)
    total_sec = start_time - current_time

    total_sec = total_sec.seconds - total_sec.seconds%60

    response = client.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': instance_id
            },
        ],
        StartTime=start_time,
        EndTime=current_time,
        Period=total_sec,
        Statistics=[
            'Average',
        ],
        Unit='Percent'
    )
    response["instance_type"] = instance_type
    return response

def get_instance_type_suggestion(instance_type,region,is_low):
    session = boto3.Session(profile_name="508414721836_AWSAdministratorAccess",region_name= region)
    ec2 = session.client('ec2')
    instance_type_details = ec2.describe_instance_types(
        InstanceTypes = [instance_type]
    )
    vcpu = instance_type_details['InstanceTypes'][0]['VCpuInfo']['DefaultVCpus']
    args={}
    if is_low:
        #under
        args = {'VCpuCount': {
            'Min': 0,
            'Max': vcpu
        },
        'MemoryMiB': {
            'Min': 0,
            'Max': instance_type_details['InstanceTypes'][0]["MemoryInfo"]["SizeInMiB"]
        }}
    else:
        args = {'VCpuCount': {
            'Min': vcpu,
            'Max': vcpu+2
        },
        'MemoryMiB': {
            'Min': instance_type_details['InstanceTypes'][0]["MemoryInfo"]["SizeInMiB"],
            'Max': instance_type_details['InstanceTypes'][0]["MemoryInfo"]["SizeInMiB"]+2024
        }}

    suggestion = ec2.get_instance_types_from_instance_requirements(
        ArchitectureTypes = instance_type_details['InstanceTypes'][0]["ProcessorInfo"]['SupportedArchitectures'],
        VirtualizationTypes = instance_type_details['InstanceTypes'][0]['SupportedVirtualizationTypes'],
        InstanceRequirements= args,
        MaxResults=3        
    )

    return suggestion


def get_suggestion_by_utilization(instance_id,region): 
    utilization = get_average_cpu_utilization(instance_id,region)
    avg_utilization = utilization["Datapoints"]
    if len(avg_utilization) > 0:    
        avg_utilization = avg_utilization[0]["Average"]
    else:    
        utilization["suggestion"] = ["No data"]
        return utilization
    
    if avg_utilization <= 30:
        #less utilization
        suggestion = get_instance_type_suggestion(utilization["instance_type"],region,True)
        utilization["need_modification"] = True 
        utilization["suggestion"] = suggestion["InstanceTypes"]
    elif avg_utilization > 30 and avg_utilization < 90:
        #normal 
        utilization["need_modification"] = False
        utilization["suggestion"] = ["No need"]
    else:
        #high
        suggestion = get_instance_type_suggestion(utilization["instance_type"],region,False)
        utilization["suggestion"] = suggestion["InstanceTypes"]
        utilization["need_modification"] = True
    return utilization                    
#print(get_average_cpu_utilization("i-09e8177cba5692f2d","us-east-1"))
#print(get_instance_type_suggestion("t2.micro","us-east-1",False))
print(get_suggestion_by_utilization("i-0d7e22f29d0b8ecfd","us-east-1"))