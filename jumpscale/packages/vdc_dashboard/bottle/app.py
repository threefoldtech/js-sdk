import jumpscale.packages.vdc_dashboard.bottle.api.root
import jumpscale.packages.vdc_dashboard.bottle.api.backup
import jumpscale.packages.vdc_dashboard.bottle.api.deployments
import jumpscale.packages.vdc_dashboard.bottle.api.export

## now that we have loaded all of the submodules and registered more endpoints
## on top /vdc_dashboard/api, we define the app value that will get registered as subapp
## on jsmainapp for the 3bot, that runs on 31000
app = jumpscale.packages.vdc_dashboard.bottle.api.root.app
