# Deployment Process

## Create Cluster

```bash
eksctl create cluster --name=JupyterES --nodes-min=2 --auto-kubeconfig --node-ami auto
```

## Create Tiller Account and Install Helm
```bash
kubectl --namespace kube-system create serviceaccount tiller
kubectl create clusterrolebinding tiller --clusterrole=cluster-admin --serviceaccount=kube-system:tiller

helm init --service-account tiller
```
