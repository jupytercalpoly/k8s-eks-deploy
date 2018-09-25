# Troubleshooting JupyterHub Deployments

## Useful `kubectl` commands:

```bash
$ # Shows all notebook server pods on the cluster
$ kubectl get pod --all-namespaces | grep jupyter-
stat218       jupyter-townsenddw                               1/1       Running   0          7m
stat331       jupyter-skhillon                                 1/1       Running   0          1h
```
