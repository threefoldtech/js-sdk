from bottle import Bottle, HTTPResponse, request
from jumpscale.packages.vdc_dashboard.bottle.api.helpers import logger

# Here we define the root app for the VDC dashboard package, and to be imported by
# all of the submodules in bottle/api when needed to register more API endpoints
# on top of /vdc_dashboard/api

app = Bottle()
app.install(logger)
