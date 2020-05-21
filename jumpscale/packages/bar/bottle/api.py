from bottle import Bottle

app = Bottle()

@app.route('/endpoint1')
def endpoint1():
    return 'bar api endporint 1'

@app.route('/endpoint2')
def endpoint2():
    return 'bar api endporint 2'