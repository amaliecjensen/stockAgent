# Stock Agent

A Python application that fetches stock data and allows natural language queries using AI.

## What it does

- Fetches real-time stock data for major companies (Apple, Google, Microsoft, Tesla, Nvidia, Amazon)
- Stores stock information in a MySQL database
- Lets you ask questions about stocks in plain English
- Uses OpenAI GPT to understand your questions and provide answers

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your credentials:
   ```
   OPENAI_API_KEY=your_openai_api_key
   DB_HOST=localhost
   DB_USER=your_mysql_user
   DB_PASSWORD=your_mysql_password
   DB_DATABASE=your_database_name
   ```

3. Run the application:
   ```bash
   python stock.py
   ```

## Usage

You can ask questions like:
- "Tell me about Apple stock"
- "What stocks do we have?"
- "Show me the current price of Tesla"
- "Which stock has grown the most?"

## Requirements

- Python 3.7+
- MySQL database
- OpenAI API key