# Deployment Process

## Create Cluster

```bash
eksctl create cluster --name=JupyterES --nodes-min=2 --auto-kubeconfig --node-ami auto
```

## Create Worker Nodes
aws cloudformation create-stack --stack-name prod-nodes \
 --template-body file://amazon-eks-nodegroup.yaml \
 --capabilities CAPABILITY_IAM \
 --parameters file://params/worker-node-param.json


## Create Tiller Account and Install Helm
```bash
kubectl --namespace kube-system create serviceaccount tiller
kubectl create clusterrolebinding tiller --clusterrole=cluster-admin --serviceaccount=kube-system:tiller

helm init --service-account tiller
```
