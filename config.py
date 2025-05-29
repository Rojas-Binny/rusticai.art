from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configuration
INPUT_SVG_FILE = "input.svg"
OUTPUT_SVG_FILE = "output.svg"

# Get API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Please set GOOGLE_API_KEY in .env file")
    exit(1) 