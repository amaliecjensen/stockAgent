import os
import mysql.connector
import yfinance as yf
from dotenv import load_dotenv
# from langchain_openai import OpenAIEmbeddings  # Bruges ikke pt.


load_dotenv() # Load environment variables from .env file

# Get environment variables
openai_api_key = os.environ.get("OPENAI_API_KEY")

# Create MySQL connection
conn = mysql.connector.connect(
    host=os.environ.get("DB_HOST"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD"),
    database=os.environ.get("DB_DATABASE")
)
cursor = conn.cursor()

# Get Apple stock data
ticker = yf.Ticker("AAPL")

from langchain_openai import ChatOpenAI

# Initialize ChatGPT
chat = ChatOpenAI(api_key=openai_api_key, model="gpt-3.5-turbo", temperature=0)

def generate_sql_query(question):
    """Generate SQL query based on natural language question"""
    prompt = f"""
    Convert this question to a SQL query for the stocks table:
    Question: {question}
    
    Table structure: symbol, name, current_price, start_price, market_cap, sector, growth_percent, fetched_at
    
    Important notes:
    - For "Apple" or "apple stock" use LIKE '%Apple%' or symbol = 'AAPL'
    - Use LIKE for partial name matches
    - Return only the SQL query without explanation
    
    Examples:
    "tell me about apple" -> SELECT * FROM stocks WHERE symbol = 'AAPL' OR name LIKE '%Apple%'
    "what stocks do we have" -> SELECT symbol, name FROM stocks
    
    SQL Query:
    """
    response = chat.invoke(prompt)
    return response.content.strip()

def format_answer(data, question):
    """Format database results into readable answer"""
    prompt = f"""
    Based on this data: {data}
    Answer the question: {question}
    
    Provide a short, readable answer in English.
    """
    response = chat.invoke(prompt)
    return response.content

def ask_stock_question(question):
    """Answer stock questions by searching database and using AI"""
    try:
        # Generate SQL query
        sql_query = generate_sql_query(question)
        # print(f"SQL Query: {sql_query}")  # Debug - enable if needed
        
        # Execute query
        cursor.execute(sql_query)
        results = cursor.fetchall()
        
        if not results:
            return "Sorry, I couldn't find relevant data for your question."
        
        # Format result into readable answer
        answer = format_answer(results, question)
        return answer
        
    except Exception as e:
        return f"Error processing question: {str(e)}"
history = ticker.history(period="3mo")
start_price = history["Close"].iloc[0]
current_price = history["Close"].iloc[-1]
growth_percent = ((current_price - start_price) / start_price) * 100


# Create database table for stock data
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

# Embeddings table (disabled for now)
# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS stock_embeddings (
#         id INT AUTO_INCREMENT PRIMARY KEY,
#         symbol VARCHAR(10),
#         embedding JSON
#     )
# """)
# conn.commit()

# Save function to database
def save_stock_to_db(symbol, name, current_price, start_price, market_cap, sector, growth_percent):
    cursor.execute("""
        INSERT INTO stocks (symbol, name, current_price, start_price, market_cap, sector, growth_percent)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (symbol, name, current_price, start_price, market_cap, sector, growth_percent))
    conn.commit()


# Save Apple data to database
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
print(f"Data saved for {info.get('symbol', 'N/A')}")

# Check what we have in the database
cursor.execute("SELECT symbol, name FROM stocks LIMIT 5")
db_stocks = cursor.fetchall()
print(f"\nStocks in database: {db_stocks}")

# Start RAG Chat System
print("\nStock Agent RAG System started!")
print("You can now ask questions about stock data in the database.")

# Chat loop
while True:
    question = input("\nAsk about stocks (or 'quit'): ")
    if question.lower() == 'quit':
        break
    answer = ask_stock_question(question)
    print(f"Answer: {answer}")

