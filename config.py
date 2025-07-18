# Gmail API Configuration
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent

# Gmail API settings - can be overridden by environment variables
CREDENTIALS_FILE = Path(os.getenv('GMAIL_CREDENTIALS_FILE', PROJECT_ROOT / "credentials.json"))
TOKEN_FILE = Path(os.getenv('GMAIL_TOKEN_FILE', PROJECT_ROOT / "token.json"))

# Gmail API scopes
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.labels'
]

# Default query parameters - can be overridden by environment variables
DEFAULT_MAX_RESULTS = int(os.getenv('GMAIL_MAX_RESULTS', 10))
DEFAULT_QUERY = os.getenv('GMAIL_DEFAULT_QUERY', "from:linkedin.com") 