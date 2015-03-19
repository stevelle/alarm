from flask import Flask

app = Flask(__name__)

@app.route('/scale_up/1', methods=['POST'])
def scale_up():
    return "Scaling Up"

@app.route('/scale_down/1', methods=['POST'])
def scale_down():
    return "Scaling Down"

if __name__ == '__main__':
    app.run(debug=True, port=5001)
