# Deployment Notes


## TODO:
 - Helm Installs:
    - utils/efs-provisioner:
    `helm install --name efs-provisioner --namespace utils stable/efs-provisioner -f deployments/config-efs-provisioner.yaml`
        - If chart isn't working:   
        `kubectl create clusterrolebinding utils-admin --clusterrole cluster-admin --serviceaccount=utils:default`
    - utils/nginx-ingress
    `helm install stable/nginx-ingress --name nginx-ingress --namespace utils`
    - utils/kube-lego
    `helm install --name kube-lego --namespace utils stable/kube-lego -f deployments/config-kube-lego.yaml`
    - Install Fall Deployments
        - stat331
        - stat218
        - stat350
        - data301
    - utils/kuberenetes-dashboard
    `kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/master/src/deploy/recommended/kubernetes-dashboard.yaml`
    - utils/cluster-autoscaler
    - utils/overprovisioning
    - utils/heapster
    - utils/grafana

 - Optimize image pulls somehow to speed up the node launch time