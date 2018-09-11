

# AWS EKS tl;dr

*Amazon Elastic Container Serivce for Kubernetes* 

No need to stand up or maintain your own Kubenetes control plane. Simply launch EKS instance any Kubernetes is ready out of the box.

## Prerequisite

#### 0. Setup AWS CLI

EKS is only available on two AWS regions: `us-west-2` or `us-east-1`. Point your user profile to one of these two regions.

**IMPORTANT**: If your using a profile (which I suggest for sandboxing), finish every `aws` command with `--profile <profile-name>` .

#### 1. Create EKS Service Role

We'll first create a EKS role on the AWS Console (webpage).

1. Open the IAM console at <https://console.aws.amazon.com/iam/>.
2. Choose **Roles**, then **Create role**.
3. Choose **EKS** from the list of services, then **Allows Amazon EKS to manage your clusters on your behalf** for your use case, then **Next: Permissions**.
4. Choose **Next: Review**.
5. For **Role name**, enter a unique name for your role, then choose **Create role**.

#### 2. Create Cluster VPC

We'll do this using AWS's CLI. 

Downlaod the sample VCP configuration YAML file [here](https://amazon-eks.s3-us-west-2.amazonaws.com/cloudformation/2018-08-30/amazon-eks-vpc-sample.yaml). You can edit different fields in this file. Then, use AWS `cloudformation`  to create an EKS cluster on AWS:

```
aws cloudformation create-stack \
	--stack-name devel \
	--template-body file://<VPC-configuration>.yaml
```

#### 3. Create EC2 key pair



## Launching EKS Instance

### 1. Create Amazon EKS Cluster

Use AWS CLI to create your EKS cluster. 

```
aws eks create-cluster \
	--name devel \
	--role-arn arn:aws:iam::111122223333:role/eks-service-role-AWSServiceRoleForAmazonEKS-EXAMPLEBKZRQR \
	--resources-vpc-config subnetIds=subnet-a9189fe2,subnet-50432629,securityGroupIds=sg-f5c54184 \
```

If you get the following error,

```
An error occurred (UnsupportedAvailabilityZoneException) when calling the CreateCluster operation: Cannot create cluster 'sandbox-zrs' because us-east-1b, the targeted availability zone, does not currently have sufficient capacity to support the cluster. Retry and choose from these availability zones: us-east-1a, us-east-1c, us-east-1d
```

try removing one of the subnetIds from the `--resource-vpc-config` option.

When JSON appears in your console, your cluster launched successfully. Wait for it to complete, checking the status using the AWS CLI:

 ```
aws eks describe-cluster --name devel --query cluster.status
 ```

Once your query replies "ACTIVE", grab a two things to configure your k8s interaction:

**Endpoint** 

```
aws eks describe-cluster --name devel  --query cluster.endpoint --output text
```

**Certificate authority data**

```
aws eks describe-cluster --name devel  --query cluster.certificateAuthority.data --output text
```

### 2. Configure `kubectl` for Amazon EKS

Add a new `kubeconfig` to your `~/.kube` directory (if this directory doesn't exist on your machine, create it). Paste this code into you the config file.

```yaml
apiVersion: v1
clusters:
- cluster:
    server: <endpoint-url>
    certificate-authority-data: <base64-encoded-ca-cert>
  name: kubernetes
contexts:
- context:
    cluster: kubernetes
    user: aws
  name: aws
current-context: aws
kind: Config
preferences: {}
users:
- name: aws
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1alpha1
      command: aws-iam-authenticator
      args:
        - "token"
        - "-i"
        - "<cluster-name>"
        # - "-r"
        # - "<role-arn>"
      # env:
        # - name: AWS_PROFILE
        #   value: "<aws-profile>"
```

Changes you'll need to make:

* `endpoint-url` can be found using the commands in the previous section
* `base64-encoded-ca-cert` can be found using the commands in the previous section
* `cluster-name` should be the name of your cluster.

Check that your cluster is working:

```
kubectl get svc
```

### 3. Launch and Configure EKS worker nodes

Launch your worker nodes using `cloudformation`:

```
aws cloudformation create-stack \
	--stack-name devel \
	--template-body https://amazon-eks.s3-us-west-2.amazonaws.com/cloudformation/2018-08-30/amazon-eks-nodegroup.yaml \
	--capabilities CAPABILITY_NAMED_IAM \
	--parameters \
		ParameterKey=ClusterName,ParameterValue="devel" \
		ParameterKey=ClusterControlPlaneSecurityGroup,\
		ParameterValue="sg-085366fa2e921b4a3" \
		ParameterKey=NodeGroupName,\
		ParameterValue="devel" \
		ParameterKey=NodeImageId,\
		ParameterValue="ami-0b2ae3c6bda8b5c06" \
		ParameterKey=KeyName,\
		ParameterValue="devel" \
		ParameterKey=VpcId,\
		ParameterValue="vpc-0b1e662c43f912c7e" \
		ParameterKey=Subnets,\
		ParameterValue="'subnet-0bd524d82518869c9,subnet-065ccf344b0762522'"
```

*Notice the `Subnets` parameter. If you are using multiple subnets, you'll need to use double quotes and single quote to encapsulate a list*

Enable your worker nodes to join the cluster:

```
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: arn:aws:iam::822466877299:role/CalpolyDataScience-nodeGroup-NodeInstanceRole-G7C4WIB81Q4V
      username: system:node:{{EC2PrivateDNSName}}
      groups:
        - system:bootstrappers
        - system:nodes
```

## Terms

- **VPC (Virtual private cloud)**: launch AWS resources in a virtual network environment. Select IP addresses, create subnets, and configure route tables and network gatesways. 

- **IAM Role**: IAM role is similar to a user (but different). This is your identity with permissions that determine what the identity can/can't do in AWS. 

  A role does not have standard long-term credentials (password or access keys). Instead, if a user assumes a role, temporary security credentials are created dynamically and provided to the user.

  Roles are used to delegate access to users. 