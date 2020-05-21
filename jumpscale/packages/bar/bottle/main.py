from bottle import Bottle

app = Bottle()

@app.route('/')
def index():
    return 'bar bottle server'