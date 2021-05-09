from bottle import Bottle, HTTPResponse, request

from jumpscale.packages.vdc_dashboard.bottle.api.helpers import logger


app = Bottle()
app.install(logger)
