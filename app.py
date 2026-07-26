from flask import Flask, render_template, request, jsonify 
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv
#------------------------------code start-----------------------------------

app = Flask(__name__, template_folder='.')
CORS(
    app,
    resources={r"/api/*": {"origins": "*"}},
    methods=["GET", "POST", "OPTIONS"],
)
load_dotenv()
tavily_key = os.getenv("TAVILY_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")
#-----------------helper functions---------------------
fallback = {
    "Mercury": "There are strangle hollows on Mercury's surface, thousands of weird depressions at a variety of longitudes and latitudes. Could be 60 feet to miles...and a depth of 80+ feet. No one knows how they got there, and there's nothing like it anywhere else.",
    "Venus": "Earth and Venus are called 'twins separated at birth' they have similar everything, but some say Venus' atmosphere is due to carbon dioxide making the planet 870 degrees fahrenheit. Maybe Earth will become the next Venus at a certain point?",
    "Earth": "We still don't know how to accurately predict earthquakes or why seismic waves happen..",
    "Mars": "Mars used to be known to move in perfect circles (thanks to ancient Greek metaphysics). In the early 17th century, Johannes Kepler showed that Mars (& all planets) orbit the Sun in ellipses using mathematical discoveries derived from Tycho Brahe's observational data",
    "Jupiter": "The Grand tack hypothesis proposes that Jupiter formed near the ice line (~3.5 AU) and then migrated inward to ~1.5 AU before being captured in a 2:3 orbital resonance with Saturn, which reversed its migration",
    "Saturn": "In 2004, scientists estimated that the core must be 9 to 22 times the mass of Earth, which is about a diameter of 12,000 miles",
    "Uranus": "Uranus has a ring system, a magnetosphere, and many natural satellites. The extremely dark ring system reflects only 2/100 of the incoming light. ",
    "Neptune": "Neptune's axis of rotation is tilted 28 degrees with respect to the plane of its orbit around the Sun, similar to the axial tilts of Mars & Earth. Neptune experiences seasons just like we do on Earth! But it has a long year, so each season lasts 40 Earth years.",
    "Universe":"The universe is a Fibonacci structure. It also appears in nature. Check out spiral galaxy arms and the golden spiral!"
}



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
        return fallback.get(planet, f"{planet} has many amazing mathematical attributes.")


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/selected-planet', methods=['POST', 'OPTIONS'])
@app.route('/api/selected-planet/', methods=['POST', 'OPTIONS'])
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
        facts = generateInfo("Universe")

    planetInfo ={
            "status": "success",
             "message": f"successfully recieved data for {planet_name}",
             "facts": facts
        }

    return jsonify(planetInfo), 200
#Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process if running multiple processes.

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)