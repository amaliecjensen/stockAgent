import os
import mysql.connector
import yfinance as yf
from dotenv import load_dotenv

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

# jeg bruger yfinance python pakken som wrapper yahoo finance data
ticker = yf.Ticker("AAPL")
print(ticker.history(period="1d"))  # hent den seneste kurs
print(ticker.info)

# Opret tabel til aktiedata
create_table_query = """
CREATE TABLE IF NOT EXISTS stocks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10),
    name VARCHAR(255),
    price DECIMAL(10,2),
    market_cap BIGINT,
    sector VARCHAR(255),
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

# Udfør SQL kommandoen
cursor.execute(create_table_query)
conn.commit()

# Funktion til at gemme aktiedata i database
def save_stock_to_db(symbol, price, market_cap, sector):
    cursor.execute("""
        INSERT INTO stocks (symbol, price, market_cap, sector)
        VALUES (%s, %s, %s, %s)
    """, (symbol, price, market_cap, sector))
    conn.commit()

# Test embeddings (kræver langchain_openai pakke)
try:
    from langchain_openai import OpenAIEmbeddings
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    
    text = "Apple Inc. er en amerikansk teknologivirksomhed med fokus på smartphones, pc'er og services." 
    vector = embeddings.embed_query(text)
    print(f"Vector length: {len(vector)}")
except ImportError:
    print("LangChain OpenAI pakke ikke installeret")

# Test ChatGPT integration (kræver langchain pakker)
try:
    from langchain.chains import RetrievalQA
    from langchain_openai import ChatOpenAI
    
    llm = ChatOpenAI(openai_api_key=openai_api_key, model="gpt-4o-mini")
    print("ChatGPT model loadet succesfuldt")
    
    # Note: Du skal oprette en retriever før du kan bruge RetrievalQA
    # qa_chain = RetrievalQA.from_chain_type(llm, retriever=my_retriever)
    # response = qa_chain.run("Hvilken teknologiaktie har haft størst vækst den seneste måned?")
    # print(response)
    
except ImportError:
    print("LangChain pakker ikke installeret")
