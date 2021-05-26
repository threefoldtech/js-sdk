# ThreeFold Cloud v2.8.0 Spec
 
Next Release: JS-SDK v11.5 (Testnet)

## JS-SDK v11.5

### Component Upgrades
- [3Bot Deployer](https://github.com/threefoldtech/js-sdk/tree/master/jumpscale/packages/threebot_deployer)
- [Solution Marketplace](https://github.com/threefoldtech/js-sdk/tree/master/jumpscale/packages/marketplace)
- [Virtual Datacenter VDC](https://github.com/threefoldtech/js-sdk/tree/master/jumpscale/packages/vdc)
- [3Bot SDK](https://github.com/threefoldtech/js-sdk/tree/development/master/packages/tfgrid_solutions)

## Product Requirements

### VDC v2.8.0
- Generic VMs (SAL and admin dashboard integration)
- Add service to redeploy controller to prevent workload loss if node goes offline
- Auto fetch VDC workloads from TF Explorer when listing VDCs
- improve etcd cluster solution
- Update common component library files to avoid duplications (will get low prio because of the other things we have)
- Improve the speed of VDC deployment listing
- Improve the vdc deployer configuration 
- Safely drain kubernetes nodes before deletion 
- Add Support link in VDC deployer and in the VDC controller 
- Allow vdc controller to access kubernetes cluster via private IP 
- Add kubernetes CSI Plugin for 0-db storage (this is still experiment and by no means complete)
- Allow setting key to control VDC from the rest API (probably will move to 2.9) 
- New Marketplace Solution: Dash Blockchain Node Solution


### 3Bot SDK v2.8.0
- Improve the 3Bot Deployer configuration
