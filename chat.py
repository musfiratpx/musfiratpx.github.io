
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
#nasa
NASA_API_KEY = os.getenv("NASA_API_KEY")

