### test01_ubuntu

Test case for deploying Ubuntu.

**Test Scenario**

- Deploy Ubuntu.
- Check that Ubuntu is reachable.
- Check that Ubuntu has been deployed with the same version.

### test02_kubernetes

Test case for Deploying a kubernetes.

**Test Scenario**

- Deploy kubernetes.
- Check that kubernetes is reachable.
- Check that kubernetes has been deployed with the same number of workers.

### test03_minio

Test case for deploying Minio.

**Test Scenario**

- Deploy Minio.
- Check that Minio is reachable.

### test04_monitoring

Test case for deploying a monitoring solution.

**Test Scenario**

- Deploy a monitoring solution.
- Check that Prometheus UI is reachable.
- Check that Grafana UI is reachable.
- Check that Redis is reachable.

### test05_generic_flist

Test case for deploying a container with a generic flist.

**Test Scenario**

- Deploy a container with a flist.
- Check that the container coreX is reachable.

### test06_exposed_flist

Test case for exposing a container with generic flist.

**Test Scenario**

- Deploy a container with a flist.
- Expose this container's coreX endpoint to a subdomain.
- Check that the container coreX is reachable through the subdomain.
