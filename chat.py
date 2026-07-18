
#control shift p to select interpretor 
#pip install python-dotenv
#pip install google-generativeai
#https://ai.google.dev/gemini-api/docs/migrate
# See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
import os
import requests
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv
from tavily import TavilyClient
from google.genai.errors import APIError

load_dotenv()

# gemini 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client() 
#tavily
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
#nasa
NASA_API_KEY = os.getenv("NASA_API_KEY")

# Fetch NASA Astronomy Picture of the Day (APOD)
def get_nasa_apod():
    NASA_API_KEY = os.getenv("NASA_API_KEY")
    url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}"
    try:
        print("Fetching today's astronomy picture from NASA...")
        response = requests.get(url, timeout=5) # Added timeout so it doesn't hang forever
        return response.json()
    except Exception as e:
        return {"error": f"Could not reach NASA servers: {e}"}


print("\n--- Initializing Tavily Search Loop ---")
print("Bot: Hello! Click a planet or type a space query to search live data.")
print()

while True:
    try:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit']:
            break
            
        print("\nSearching live space databases...")
        
        search_instruction = (
            f"""
            Provide exactly two unique mathematical facts about {user_input}, suitable for a website.
            Keep the response under 6 sentences make it sound exciting, and do not repeat basic info like size or position.
            
            CRITICAL RULES:
            1. The mathematical facts should be mathematically significant.
            2. You may also discuss theories surrounding {user_input} and mathematics.
            3. If {user_input} is unrelated to space, astronomy, or time physics, refuse to respond.
            4. Some mathematical concepts you can use in your output can include but not limited to: Fibonacci Sequence, the Golden Ratio, Set Theory
            5. You must explicitly cite the titles or domains of the resources used for these facts.
            """
        )
        
        # Pass the formatted instruction string straight to Tavily
        response = tavily_client.qna_search(
            query=search_instruction,
            search_depth="advanced"
        )

        print(f'Bot: {response}')
        print()
            
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"An error occurred: {e}\n")