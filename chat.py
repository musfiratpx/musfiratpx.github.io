
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

# setup 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client() 
#tavily
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

#Set up tavily so that it can receive client request on front end (click on planet)
#tavily develops a query to send to gemini
#Ex. User clicks Jupiter --> JavaScript sends a message to flask "Hey user clicked on planet 5."
#Flask tells python (Tavily) --> Create a query with user input 5 -> Jupiter.
#Tavily creates a query "What are some mathematically significant facts about Jupiter", and provides sources to gemini. 
#gemini listens to instructions and sends an output that will display to front end as a pop-up. 
#Gemini's instructions: Mathematically significant facts about user input relating to astronomy, space, or time physics. Condensed in a paragraph. Cites the sources. 
