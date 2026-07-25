from flask import Flask, render_template, request, jsonify 
from flask_cors import CORS
from tavily import TavilyClient
import os
from dotenv import load_dotenv
#------------------------------code start-----------------------------------

app = Flask(__name__, template_folder='.')
CORS(app, origins=["https://theouterspace.io", "https://musfiratpx.github.io"])
load_dotenv()
tavily_key = os.getenv("TAVILY_API_KEY")
#-----------------helper functions---------------------
def generateInfo(planet): #logic to generate information for the planet 
    tavily_client = TavilyClient(api_key=f"{tavily_key}")
    research = tavily_client.research(f"What are some mathematical facts about {planet}?")
    response = tavily_client.get_research(research["request_id"])
    print(response) #https://docs.tavily.com/documentation/api-reference/endpoint/research


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
    planet_name = data.get("planet_name")
    print(f"User clicked on: {planet_name}", flush=True)
    planets = {"Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"}
    if planet_name in planets:
        generateInfo(planet_name)
    else:
        generateInfo("the milky-way or the universe")
    return jsonify(
        { 
            "status":"success", 
            "message":f"successfully recieved data for {planet_name}"
        }
        ), 200
#Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process if running multiple processes.

if __name__ == '__main__':
    app.run(debug=True)