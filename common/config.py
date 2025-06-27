"""
Конфигурация
"""

import os

from dotenv import load_dotenv

load_dotenv(override=True)

SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_MODEL = os.getenv("OPENAI_API_MODEL")
OPENAI_API_URL = os.getenv("OPENAI_API_URL")

DEBUG_SWARM = os.getenv("DEBUG_SWARM", "false").lower() == "true"
