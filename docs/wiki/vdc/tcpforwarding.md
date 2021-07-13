The following creates
1- endpoint to www.python.org ip address 151.101.112.223 `pyorg`
2- service `pyorg`
3- tcp route for requests with SNI of www.python.org to go to the service `pyorg`

```
echo -e '
apiVersion: v1
kind: Service
metadata:
  name: pyorg
spec:
  ports:
    - protocol: TCP
      port: 443
      targetPort: 443

---

apiVersion: v1
kind: Endpoints
metadata:
  name: pyorg
subsets:
  - addresses:
      - ip: 151.101.112.223
    ports:
      - port: 443

---

kind: IngressRouteTCP
apiVersion: traefik.containo.us/v1alpha1
metadata:
  name: pyorg
spec:
  entryPoints:
    - websecure
  routes:
    - match: HostSNI(`www.python.org`)
      services:
        - name: pyorg
          port: 443
  tls:
    passthrough: true
' | kubectl apply -f -
```


## checking

edit /etc/hosts and add entry for `$CLUSTER_IP   www.python.org`
curl https://www.python.org # after editing /etc/hosts to make www.python.org point to the cluster
