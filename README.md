# k8s-eks-deploy
k8s on EKS deployment

# On Boarding

## Accounts and Roles

- Root Account
  - email for root account
  - Disable Key Access
- Admins: (administrator access)
  - Brian
  - Zach
  - Dwight

## EKS

- Deploy VPC
  ```bash
  aws cloudformation create-stack --stack-name eksTest --template-body file://cluster.yml --capabilities CAPABILITY_NAMED_IAM
  ```
- Deploy NodeGroup
- 