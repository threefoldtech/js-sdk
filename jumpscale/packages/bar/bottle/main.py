from bottle import Bottle

app = Bottle()

@app.route('/')
def index():
    return 'bar bottle server'


@app.route('/test')
def test():
    return 'bar bottle server test'