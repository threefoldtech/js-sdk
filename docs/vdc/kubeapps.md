Kubeapps is a web-based UI for deploying and managing applications in Kubernetes clusters.

### Step 1: Install Kubeapps

##### you can use our chatflow from VDC market place  

or 

Use the Helm chart to install the latest version of Kubeapps:



```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
kubectl create namespace kubeapps
helm install kubeapps --namespace kubeapps bitnami/kubeapps
```




### Step 2: Create a demo credential with which to access Kubeapps and Kubernetes
For any user-facing installation you should configure an OAuth2/OIDC provider to enable secure user authentication with Kubeapps and the cluster, but this is quite an overhead to simply try out Kubeapps. Instead, for a simpler way to try out Kubeapps for personal learning, we can create a Kubernetes service account and use that API token to authenticate with the Kubernetes API server via Kubeapps:

```bash
kubectl create serviceaccount kubeapps-operator
kubectl create clusterrolebinding kubeapps-operator --clusterrole=cluster-admin --serviceaccount=default:kubeapps-operator
```

To retrieve the token,

#### On Linux/macOS:

```bash
kubectl get secret $(kubectl get serviceaccount kubeapps-operator -o jsonpath='{range .secrets[*]}{.name}{"\n"}{end}' | grep kubeapps-operator-token) -o jsonpath='{.data.token}' -o go-template='{{.data.token | base64decode}}' && echo
```

Note

we are using the latest version of `kubernetes` so it is not totally compatible with all the charts in the `kubeapps`