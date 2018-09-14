#!/bin/python3
'''
Only run this after deploying cloud formation templates
'''


# PreReqs
import boto3
import jinja2
import subprocess

## Using minimal input this script should bootsrap an EKS cluster on AWS

## Check for existing kubeconfig(s)

## Check for existing awscli credentials

## Check for aws-iam-authenticator


# Deploy VPC

# Deploy Management Plane

## Add IAM admin users

# Deploy Worker Nodes (minions)
# with open('worker-nodes.yaml', 'r') as stream:
#     template_body = yaml.load(stream)

# client = boto3.client('cloudformation')
# response = client.create_stack(
#     StackName='prod-worker-nodes',
#     TemplateURL=template_body,
#     Capabilities=['CAPABILITY_NAMED_IAM']
# )
# print(response)

## Get ARN of instance role of worker nodes and apply to cluster
# This is just a hack now, but it works assuming your awscli 
# and kubectl are configureed correctly
# Also, this section is idempotent
cloudformation = boto3.resource('cloudformation')
stack = cloudformation.Stack('prod-worker-nodes')
worker_node_arn = stack.outputs[0]['OutputValue']
print(worker_node_arn)

def kubectl(*args, **kwargs):
    #logging.info("Executing kubectl", ' '.join(args))
    return subprocess.check_call(['kubectl'] + list(args), **kwargs)

templateLoader = jinja2.FileSystemLoader(searchpath="./templates")
templateEnv = jinja2.Environment(loader=templateLoader)
TEMPLATE_FILE = "aws-auth-cm.yaml.template"
template = templateEnv.get_template(TEMPLATE_FILE)
outputText = template.render(arn=worker_node_arn)

with open('aws-auth-cm.yaml', 'w') as ofile:
    ofile.writelines(outputText)

kubectl('apply', '-f', 'aws-auth-cm.yaml')

## Storage Class
kubectl('apply', '-f', 'storageclass.yaml')

## Install Helm/Tiller
# NOT idempotent
# kubectl('--namespace', 'kube-system', 'create', 'serviceaccount', 'tiller')
# kubectl('create', 'clusterrolebinding', 'tiller', '--clusterrole=cluster-admin', '--serviceaccount=kube-system:tiller')

def helm(*args, **kwargs):
    # logging.info("Executing helm", ' '.join(args))
    return subprocess.check_call(['helm'] + list(args), **kwargs)

helm('init', '--service-account', 'tiller')


## Congfigure Clients

# Add kubeconfig file

# If needed adjust aws config


