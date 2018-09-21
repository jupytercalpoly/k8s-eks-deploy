#!/bin/python
'''
Only run this after deploying cloud formation templates
Using minimal input this script should bootsrap an EKS cluster on AWS
'''

# Imports
import boto3
import jinja2
import json
import subprocess
from pathlib import Path

# Exceptions
# from botocore.errorfactory import AlreadyExistsException

# TODO: "Arguments"
CLUSTER_NAME='JupyterES'

# Constants
ROLE_TEMPLATE_URL = "https://amazon-eks.s3-us-west-2.amazonaws.com/cloudformation/2018-08-30/amazon-eks-service-role.yaml"
VPC_TEMPLATE_URL = "https://amazon-eks.s3-us-west-2.amazonaws.com/cloudformation/2018-08-30/amazon-eks-vpc-sample.yaml"
NODE_TEMPLATE_URL = "https://amazon-eks.s3-us-west-2.amazonaws.com/cloudformation/2018-08-30/amazon-eks-nodegroup.yaml"
SPOT_TEMPLATE_URL = "https://raw.githubusercontent.com/townsenddw/k8s-eks-deploy/master/spot-nodes.yaml"

# Utilities

client = boto3.client('cloudformation')
waiter = client.get_waiter('stack_create_complete')
cf = boto3.resource('cloudformation')

def writeKubeconfig():
    """Creates kubeconfig file in users home with CLUSTER_NAME appended"""
    templateLoader = jinja2.FileSystemLoader(searchpath="./templates")
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "kubeconfig.yaml.template"
    template = templateEnv.get_template(TEMPLATE_FILE)
    outputText = template.render(
        endpoint_url=ENDPOINT_URL,
        ca_cert=CA_CERT,
        cluster_name=CLUSTER_NAME)
    with open(f'{Path.home()}/.kube/kubeconfig-{CLUSTER_NAME}', 'w') as ofile:
        ofile.writelines(outputText)

def kubectl(*args, **kwargs):
    #logging.info("Executing kubectl", ' '.join(args))
    return subprocess.check_call(['kubectl'] + list(args), **kwargs)

def helm(*args, **kwargs):
    # logging.info("Executing helm", ' '.join(args))
    return subprocess.check_call(['helm'] + list(args), **kwargs)

def YAML(file_name):
    with open(file_name, 'r') as stream:
        template_body = yaml.load(stream)
    return template_body

def getOutput(stack, outputKey):
    for output in stack.outputs:
        if output['OutputKey'] == outputKey:
            return output['OutputValue']

# TODO: Check for existing kubeconfig(s)

# TODO: Check for aws-cli, aws-iam-authenticator, 

# TODO: Download current CloudFormation templates

# Deploy Role
try:
    stack = cf.create_stack(
        StackName=f'{CLUSTER_NAME}-role',
        TemplateURL=ROLE_TEMPLATE_URL,
        Capabilities=[
            'CAPABILITY_NAMED_IAM',
        ]
    )
    waiter.wait(StackName=stack.name)
except:
    stack = cf.Stack(f'{CLUSTER_NAME}-role')
finally:
    CLUSTER_ROLE = getOutput(stack, 'RoleArn')

# Deploy VPC
try:
    stack = cf.create_stack(
        StackName=f'{CLUSTER_NAME}-vpc',
        TemplateURL=VPC_TEMPLATE_URL,
        Parameters=json.loads(open('params/vpc.json', 'rb').read())
    )
    waiter.wait(StackName=stack.name)
except:
    stack = cf.Stack(f'{CLUSTER_NAME}-vpc')
finally:
    SECURITY_GROUPS = getOutput(stack, 'SecurityGroups')
    SUBNET_IDS = getOutput(stack, 'SubnetIds')
    VPC_ID = getOutput(stack, 'VpcId')

# Deploy Cluster
try:
    stack = cf.create_stack(
        StackName=f'{CLUSTER_NAME}-cluster',
        TemplateBody=open('cluster.yml').read(),
        Parameters=[
            {
                "ParameterKey": "ClusterName",
                "ParameterValue": CLUSTER_NAME
            },
            {
                "ParameterKey": "ControlPlaneSecurityGroup",
                "ParameterValue": SECURITY_GROUPS
            },
            {
                "ParameterKey": "Subnets",
                "ParameterValue": SUBNET_IDS
            },
        ]
    )
    waiter.wait(StackName=stack.name)
except:
    stack = cf.Stack(f'{CLUSTER_NAME}-cluster')
    waiter.wait(StackName=stack.name)
finally:
    client = boto3.client('eks')
    response = client.describe_cluster(
        name=CLUSTER_NAME
    )
    ENDPOINT_URL = response['cluster']['endpoint']
    CA_CERT = response['cluster']['certificateAuthority']['data']

# Deploy AWS Default Worker Nodes (OnDemand minions)
    # TODO: add system reserved specification
    # {
    #   "ParameterKey": "BootstrapArguments",
    #   "ParameterValue": "--kubelet-extra-args --system-reserved cpu=500m,memory=500Mi"
    # },
try:
    stack = cf.create_stack(
        StackName=f'{CLUSTER_NAME}-ondemand-nodes',
        TemplateURL=NODE_TEMPLATE_URL,
        Parameters=[
            {
                "ParameterKey": "ClusterName",
                "ParameterValue": CLUSTER_NAME
            },
            {
                "ParameterKey": "ClusterControlPlaneSecurityGroup",
                "ParameterValue": SECURITY_GROUPS
            },
            {
                "ParameterKey": "Subnets",
                "ParameterValue": SUBNET_IDS
            },
            {
                "ParameterKey": "VpcId",
                "ParameterValue": VPC_ID
            },
        ] + json.loads(open('params/ondemand-nodes.json', 'rb').read()),
        Capabilities=[
            'CAPABILITY_IAM'
        ]
    )
    waiter.wait(StackName=stack.name)
except:
    stack = cf.Stack(f'{CLUSTER_NAME}-ondemand-nodes')
    waiter.wait(StackName=stack.name)
finally:
    NODE_ARN = getOutput(stack, 'NodeInstanceRole')
    NODE_INSTANCE_PROFILE = stack.Resource('NodeInstanceProfile').physical_resource_id
    NODE_INSTANCE_ROLE = stack.Resource('NodeInstanceRole').physical_resource_id
    NODE_SECURITY_GROUP = stack.Resource('NodeSecurityGroup').physical_resource_id

# Deploy spot instances
try:
    stack = cf.create_stack(
        StackName=f'{CLUSTER_NAME}-spot-nodes',
        TemplateBody=open('spot-nodes.yaml').read(),
        Parameters=[
            {
                "ParameterKey": "ClusterName",
                "ParameterValue": CLUSTER_NAME
            },
            {
                "ParameterKey": "Subnets",
                "ParameterValue": SUBNET_IDS
            },
            {
                "ParameterKey": "NodeInstanceProfile",
                "ParameterValue": NODE_INSTANCE_PROFILE
            },
            {
                "ParameterKey": "NodeInstanceRole",
                "ParameterValue": NODE_INSTANCE_ROLE
            },
            {
                "ParameterKey": "NodeSecurityGroup",
                "ParameterValue": NODE_SECURITY_GROUP
            },
        ],
    )
    waiter.wait(StackName=stack.name)
except:
    stack = cf.Stack(f'{CLUSTER_NAME}-spot-nodes')
    waiter.wait(StackName=stack.name)

writeKubeconfig()

## Apply ARN of instance role of worker nodes and apply to cluster
templateLoader = jinja2.FileSystemLoader(searchpath="./templates")
templateEnv = jinja2.Environment(loader=templateLoader)
TEMPLATE_FILE = "aws-auth-cm.yaml.template"
template = templateEnv.get_template(TEMPLATE_FILE)
outputText = template.render(arn=NODE_ARN)

# TODO: Add all IAM admin users

with open('aws-auth-cm.yaml', 'w') as ofile:
    ofile.writelines(outputText)

kubectl('apply', '-f', 'aws-auth-cm.yaml')

## Storage Class
try:
  kubectl('delete', 'storageclass', 'gp2')
except:
    pass
finally:
  kubectl('apply', '-f', 'storageclass.yaml')

## Install Tiller serviceaccount and clusterrolbinding - Idempotent
# Tiller ServiceAccount Creation
try:
    kubectl('-n','kube-system','get','serviceaccount','tiller')
except:
    kubectl('--namespace', 'kube-system', 'create', 'serviceaccount', 'tiller')

# ClusterRoleBinding
try:
    kubectl('get', 'clusterrolebinding', 'tiller')
except:
    kubectl('create', 'clusterrolebinding', 'tiller', '--clusterrole=cluster-admin', '--serviceaccount=kube-system:tiller')

# Inititalize Helm/Tiller for the cluster
helm('init', '--service-account', 'tiller')

# # TODO: Set KUBECONFIG env variable
# # perhaps append to .bash_profile?



