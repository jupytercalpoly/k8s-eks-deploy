# Deployment Notes


## TODO:
 - Helm Installs:
    - utilities/efs-provisioner\
        - If chart isn't working:   
        `kubectl create clusterrolebinding utilities-admin --clusterrole cluster-admin --serviceaccount=utilities:default`
    - utilities/cluster-autoscaler
    - Install Fall Deployments
    - utilities/overprovisioning

 - Optimize image pulls somehow to speed up the node launch time