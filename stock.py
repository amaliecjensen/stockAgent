import os
import mysql.connector
from dotenv import load_dotenv

# Læs indholdet fra .env-filen
load_dotenv()

# Hent miljøvariable
openai_api_key = os.environ.get("OPENAI_API_KEY")
user_agent = os.environ.get("USER_AGENT")

# Opret MySQL-forbindelse
conn = mysql.connector.connect(
    host=os.environ.get("DB_HOST"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD"),
    database=os.environ.get("DB_DATABASE")
)
cursor = conn.cursor()

