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
ticker.history(period="1mo")
# Info om aktien
print(ticker.info)

history = ticker.history(period="3mo")
start_price = history["Close"].iloc[0]
current_price = history["Close"].iloc[-1]
growth_percent = ((current_price - start_price) / start_price) * 100


#opret database tabel til aktiedata
cursor.execute("""
    CREATE TABLE IF NOT EXISTS stocks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        symbol VARCHAR(10),
        name VARCHAR(255),
        current_price DECIMAL(10,2),
        start_price DECIMAL(10,2),
        market_cap BIGINT,
        sector VARCHAR(255),
        growth_percent DECIMAL(5,2),
        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()

# Opret embeddings tabel
cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_embeddings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        symbol VARCHAR(10),
        embedding JSON
    )
""")
conn.commit()

#save funktion til databasen
def save_stock_to_db(symbol, name, current_price, start_price, market_cap, sector, growth_percent):
    cursor.execute("""
        INSERT INTO stocks (symbol, name, current_price, start_price, market_cap, sector, growth_percent)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (symbol, name, current_price, start_price, market_cap, sector, growth_percent))
    conn.commit()


info = ticker.info
#gem apple data til databasen
info = ticker.info
save_stock_to_db(
    symbol=info.get("symbol", "N/A"),
    name=info.get("longName", "N/A"),
    current_price=current_price,
    start_price=start_price,
    market_cap=info.get("marketCap", 0),
    sector=info.get("sector", "Unknown"),
    growth_percent=growth_percent
)


embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

text = "Apple Inc. er en amerikansk teknologivirksomhed med fokus på smartphones, pc'er og services."
vector = embeddings.embed_query(text)
print(len(vector))  # vektoren har 1536 tal der repræsenterer tekstens betydning
