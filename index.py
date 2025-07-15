from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'message': 'Covert Agenda is running!',
        'status': 'success',
        'version': '1.0.0'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/test')
def test():
    return jsonify({'message': 'Test endpoint working!'})

if __name__ == '__main__':
    app.run(debug=True) 