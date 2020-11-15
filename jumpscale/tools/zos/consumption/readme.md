# Example how to compute the cost of a workload for a period of time

``` python
zos = j.sals.zos.get()
# define your workload
container = zos.container.create('HT9yNvHRQs65dyRJeztAdEnXKweCX2bhgvD9i1WFPUNs', 'my_network', '172.26.10.40', 'https://hub.grid.tf/zaibon/zaibon-ubuntu-ssh-0.0.5.flist',2,entrypoint='/sbin/asdasd', cpu=2, memory=4096, disk_size=12040)

# use the zos tools to compute how much cloud units is comsumed
cloud_units = j.tools.zos.consumption.cloud_units(container)
print(f"compute units: {cloud_units.cu} storage units: {cloud_units.su}")

# compute the cost of the workload over a period of time
duration = 3600 * 24 * 30 # for 30 days
cost = j.tools.zos.consumption.cost(container, duration)
print(f"cost {cost} TFT")
```
