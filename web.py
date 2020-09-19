from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/hello', methods=['POST'])
def testpost():
    c = request.get_json()
    print(c)
    return jsonify(c)


if __name__ == "__main__":
    app.run()
