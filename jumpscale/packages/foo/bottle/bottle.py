from bottle import Bottle

app = Bottle()

@app.route('/')
def index():
    return 'foo bottle server'