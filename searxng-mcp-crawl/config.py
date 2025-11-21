import os
from dotenv import load_dotenv

load_dotenv()

# SearXNG Configuration
SEARXNG_BASE_URL = os.getenv('SEARXNG_BASE_URL', 'http://localhost:32768')

# API Configuration
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '32769'))

# Crawler Configuration
CONTENT_MAX_LENGTH = int(os.getenv('CONTENT_MAX_LENGTH', '10000'))
SEARCH_RESULT_LIMIT = int(os.getenv('SEARCH_RESULT_LIMIT', '10'))

# User Agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
