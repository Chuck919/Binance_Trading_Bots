from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key and secret
api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')

print("API Key:", api_key)  # You can test if it's being loaded correctly
print("API Secret:", api_secret)  # You can test if it's being loaded correctly