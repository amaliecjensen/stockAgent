import os
import mysql.connector
import yfinance as yf
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings


load_dotenv() # Læs indholdet fra .env-filen

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

# Hent data for Apple
ticker = yf.Ticker("AAPL")
# Seneste kurs
print(ticker.history(period="1d"))
# Info om aktien
print(ticker.info)

#opret database tabel til aktiedata
cursor.execute("""
    CREATE TABLE IF NOT EXISTS stocks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        symbol VARCHAR(10),
        name VARCHAR(255),
        price DECIMAL(10,2),
        market_cap BIGINT,
        sector VARCHAR(255),
        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()

#save funktion til databasen
def save_stock_to_db(symbol, price, market_cap, sector):
    cursor.execute("""
        INSERT INTO stocks (symbol, price, market_cap, sector)
        VALUES (%s, %s, %s, %s)
    """, (symbol, price, market_cap, sector))
    conn.commit()

info = ticker.info
#gem apple data til databasen
save_stock_to_db(
    symbol=info.get("symbol", "N/A"),
    price=info.get("currentPrice", 0),
    market_cap=info.get("marketCap", 0),
    sector=info.get("sector", "Unknown")
)


embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

text = "Apple Inc. er en amerikansk teknologivirksomhed med fokus på smartphones, pc'er og services."
vector = embeddings.embed_query(text)
print(len(vector))  # 1536 floats for ada-002
