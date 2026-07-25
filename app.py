from flask import Flask, render_template, request, jsonify 
from flask_cors import CORS
from tavily import TavilyClient
import os
from dotenv import load_dotenv
from google import genai
#------------------------------code start-----------------------------------

app = Flask(__name__, template_folder='.')
CORS(app, origins=["https://theouterspace.io", "https://musfiratpx.github.io"])
load_dotenv()
tavily_key = os.getenv("TAVILY_API_KEY")
#-----------------helper functions---------------------
def generateInfo(planet): #logic to generate information for the planet 

    try:
        tavily_client = TavilyClient(api_key=f"{tavily_key}")
        gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        search = tavily_client.search(
                query=f"mathematical facts orbital mechanics mass radius density numbers about {planet}", 
                search_depth="basic",
                max_results=3
            )
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

        result = gemini_client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
        )
        return result.text.strip()
    except Exception as e:
        print(f"Error generating: {e}", flush=True)
        if(planet == "Puddle"):
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