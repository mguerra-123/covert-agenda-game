from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World! Covert Agenda will be back soon!'

@app.route('/test')
def test():
    return 'Test page is working!'

if __name__ == '__main__':
    app.run(port=4000) 