# Deployment Process

## Create Cluster

```bash
eksctl create cluster --name=JupyterES --nodes-min=2 --auto-kubeconfig --node-ami auto
```

## Create Worker Nodes
aws cloudformation create-stack --stack-name prod-nodes \
 --template-body file://amazon-eks-nodegroup.yaml \
 --capabilities CAPABILITY_IAM \
 --parameters ParameterKey=KeyName,ParameterValue=townsenddw \
 ParameterKey=NodeImageId,ParameterValue=ami-0a54c984b9f908c81 \
 ParameterKey=ClusterName,ParameterValue=JupyterHubES \
 ParameterKey=NodeGroupName,ParameterValue=test \
 ParameterKey=ClusterControlPlaneSecurityGroup,ParameterValue=sg-0125f62764a2fbbc0 \
 ParameterKey=VpcId,ParameterValue=vpc-0fd882d3e2a6d96de \
 ParameterKey=Subnets,ParameterValue=\"subnet-0d76e9bb3c5ab141d,subnet-091399585eb7d0e87\"


## Create Tiller Account and Install Helm
```bash
kubectl --namespace kube-system create serviceaccount tiller
kubectl create clusterrolebinding tiller --clusterrole=cluster-admin --serviceaccount=kube-system:tiller

helm init --service-account tiller
```
