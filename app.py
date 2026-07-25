from flask import Flask, render_template, request, jsonify 
from flask_cors import CORS
app = Flask(__name__, template_folder='.')
CORS(app, origins=["https://theouterspace.io", "https://musfiratpx.github.io"])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/selected-planet', methods=['POST'])
def selected_planet():
    data = request.get_json()
    if not data:
        return jsonify(
            {
                "status":"error",
                "message":"didn't recieve any data"
            }
        ), 400



    planet_name = data.get('planet_name')
    print(f"User clicked on: {planet_name}")
    return jsonify(
        {
            "status":"success",
            "message":f"successfully recieved data for {planet_name}"
        }
    ), 200


if __name__ == '__main__':
    app.run(debug=True)