from flask import Flask, render_template, request, jsonify 
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv
#------------------------------code start-----------------------------------

app = Flask(__name__, template_folder='.')
CORS(app, origins=["https://theouterspace.io", "https://musfiratpx.github.io"])
load_dotenv()
tavily_key = os.getenv("TAVILY_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")
#-----------------helper functions---------------------
def generateInfo(planet): #logic to generate information for the planet 

    try:
        tavily_response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": tavily_key,
                "query": f"mathematical facts orbital mechanics mass radius density numbers about {planet}",
                "search_depth":"basic",
                 "max_results": 3
            },
            timeout=8
        )

        search = tavily_response.json()
        raw_snippets = " ".join([r.get('content', '') for r in search.get('results', [])])

        prompt = f"""
            You are a space science AI. Based on the following web snippets, write ONE fascinating, 
            concise mathematical or statistical fact about {planet}. 
            
            Rules:
            - Must include specific numbers, ratios, measurements, or mathematical properties.
            - Do NOT include web navigation, markdown links, URLs, or junk text.
            - Keep it strictly 1 to 3 sentences max.

            Web Snippets:
            {raw_snippets[:1500]}
            """

        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}"
        gemini_response = requests.post(
            gemini_url,
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            },
            timeout=10
        )
        gemini_data = gemini_response.json()

        fact_text = gemini_data['candidates'][0]['content']['parts'][0]['text']
        return fact_text.strip()
    except Exception as e:
        print(f"Error generating: {e}", flush=True)
        if(planet == "Universe"):
            return "The universe has many mathematical things to discover."
        return f"{planet} has fascinating orbital statistics and structural dimensions."


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
       facts = generateInfo(planet_name)
    else:
        facts = generateInfo("The universe")

    planetInfo ={
            "status": "success",
             "message": f"successfully recieved data for {planet_name}",
             "facts": facts
        }

    return jsonify(planetInfo), 200
#Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process if running multiple processes.

if __name__ == '__main__':
    app.run(debug=True)