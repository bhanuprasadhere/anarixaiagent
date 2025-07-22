import os
import pandas as pd
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
import matplotlib.pyplot as plt
import io
import base64
import json
import httpx

# -----------------------------------------------------------
# 0. Environment Variables and Project Setup
# -----------------------------------------------------------

# Load environment variables from .env file (if it exists, for local testing)
load_dotenv()

# --- Retrieve API Key and Configure Groq ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables. Please add it to Replit Secrets.")

try:
    # Create a custom httpx client without the 'proxies' argument
    # This is the workaround for the "unexpected keyword argument 'proxies'" error.
    custom_httpx_client = httpx.Client()
    groq_client = Groq(api_key=GROQ_API_KEY, http_client=custom_httpx_client)

    GROQ_MODEL_NAME = 'llama3-8b-8192'
    print(f"Groq client initialized successfully with model '{GROQ_MODEL_NAME}'.")
except Exception as e:
    print(f"Error initializing Groq client: {e}")
    raise

# Initialize FastAPI app
app = FastAPI(title="Anarix AI Agent")

# Mount static files (CSS, JS, images, etc.) from the root directory
app.mount("/static", StaticFiles(directory="."), name="static")

# Define the path for the SQLite database
DATABASE_FILE = "anarix_ecommerce.db"

# -----------------------------------------------------------
# 1. Database Setup: Convert CSVs to SQLite Tables
# -----------------------------------------------------------

def setup_database():
    """
    Connects to SQLite, loads CSVs into pandas DataFrames,
    and then writes them to SQL tables.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    print(f"Setting up database: {DATABASE_FILE}")

    # --- Product-Level Total Sales and Metrics ---
    try:
        total_sales_df = pd.read_csv("total_sales.csv")
        total_sales_df['date'] = pd.to_datetime(total_sales_df['date']).dt.strftime('%Y-%m-%d')
        total_sales_df.to_sql('total_sales', conn, if_exists='replace', index=False)
        print("Loaded total_sales.csv into 'total_sales' table.")
    except FileNotFoundError:
        print("Error: total_sales.csv not found. Please ensure it's uploaded and named 'total_sales.csv'.")
    except Exception as e:
        print(f"Error loading total_sales.csv: {e}")

    # --- Product-Level Ad Sales and Metrics ---
    try:
        ad_sales_df = pd.read_csv("ad_sales.csv")
        ad_sales_df['date'] = pd.to_datetime(ad_sales_df['date']).dt.strftime('%Y-%m-%d')
        ad_sales_df.to_sql('ad_sales', conn, if_exists='replace', index=False)
        print("Loaded ad_sales.csv into 'ad_sales' table.")
    except FileNotFoundError:
        print("Error: ad_sales.csv not found. Please ensure it's uploaded and named 'ad_sales.csv'.")
    except Exception as e:
        print(f"Error loading ad_sales.csv: {e}")

    # --- Product-Level Eligibility Table ---
    try:
        eligibility_df = pd.read_csv("eligibility.csv")
        eligibility_df['eligibility_datetime_utc'] = pd.to_datetime(eligibility_df['eligibility_datetime_utc']).dt.strftime('%Y-%m-%d %H:%M:%S')
        eligibility_df.to_sql('eligibility', conn, if_exists='replace', index=False)
        print("Loaded eligibility.csv into 'eligibility' table.")
    except FileNotFoundError:
        print("Error: eligibility.csv not found. Please ensure it's uploaded and named 'eligibility.csv'.")
    except Exception as e:
        print(f"Error loading eligibility.csv: {e}")

    conn.close()
    print("Database setup complete.")

# Call the database setup function when the application starts
setup_database()

# -----------------------------------------------------------
# 2. Database Query Execution Helper Function
# -----------------------------------------------------------

def execute_sql_query(query: str):
    """
    Connects to the SQLite database and executes the given SQL query.
    Returns column names and rows.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        return columns, rows
    except sqlite3.Error as e:
        conn.close()
        print(f"SQL Error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid SQL query: {e}")

# -----------------------------------------------------------
# 3. Database Schema for AI Model
# -----------------------------------------------------------

DATABASE_SCHEMA = """
The database has three tables:

1.  **total_sales**
    - `date` (TEXT, format YYYY-MM-DD): The date of the sales record.
    - `item_id` (INTEGER): Unique identifier for the product.
    - `total_sales` (REAL): Total sales amount for the item on that date.
    - `total_units_ordered` (INTEGER): Total units of the item ordered on that date.

2.  **ad_sales**
    - `date` (TEXT, format YYYY-MM-DD): The date of the ad sales record.
    - `item_id` (INTEGER): Unique identifier for the product.
    - `ad_sales` (REAL): Sales generated from ads for the item on that date.
    - `impressions` (INTEGER): Number of times ads for the item were shown.
    - `ad_spend` (REAL): Cost of advertising for the item on that date.
    - `clicks` (INTEGER): Number of clicks on ads for the item.
    - `units_sold` (INTEGER): Units sold through ads for the item on that date.

3.  **eligibility**
    - `eligibility_datetime_utc` (TEXT, format YYYY-MM-DD HH:MM:SS): Timestamp of the eligibility record in UTC.
    - `item_id` (INTEGER): Unique identifier for the product.
    - `eligibility` (TEXT, either 'TRUE' or 'FALSE'): Indicates if the product was eligible for advertising.
    - `message` (TEXT): A message related to the eligibility status (e.g., reason for ineligibility).

**Relationships / Important Notes:**
- `item_id` can be used to join tables (e.g., `total_sales` and `ad_sales`).
- When querying dates, use `strftime('%Y-%m-%d', date_column)` for comparison if needed.
- Always assume the current year for ambiguous date references if not specified.
- Calculations:
    - **RoAS (Return on Ad Spend)** = (ad_sales / ad_spend) * 100
    - **CPC (Cost Per Click)** = ad_spend / clicks
    - **CTR (Click-Through Rate)** = (clicks / impressions) * 100
    - **Conversion Rate** = (units_sold / clicks) * 100 (for ad-driven conversions)
"""

# -----------------------------------------------------------
# 4. FastAPI Endpoints (Updated /query endpoint for streaming!)
# -----------------------------------------------------------

# Basic root endpoint to serve the frontend HTML
@app.get("/", response_class=FileResponse)
async def read_root():
    return FileResponse('index.html')

# NEW: Endpoint to generate and return a simple plot as an HTML img tag
@app.get("/chart/total_sales_over_time", response_class=HTMLResponse)
async def get_total_sales_chart():
    try:
        # Query the database for total sales by date
        columns, rows = execute_sql_query("SELECT date, SUM(total_sales) FROM total_sales GROUP BY date ORDER BY date;")

        if not rows:
            return "<h1>No data available to generate chart.</h1>"

        dates = [row[0] for row in rows]
        sales = [row[1] for row in rows]

        # Convert dates to datetime objects for proper plotting
        dates_dt = pd.to_datetime(dates)

        # Generate the plot
        plt.figure(figsize=(10, 6))
        plt.plot(dates_dt, sales, marker='o', linestyle='-')
        plt.title('Total Sales Over Time')
        plt.xlabel('Date')
        plt.ylabel('Total Sales')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save plot to a BytesIO object
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close() # Close the plot to free memory

        # Encode image to base64
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')

        # Return as HTML img tag embedded in data URI
        return f'<img src="data:image/png;base64,{image_base64}" alt="Total Sales Chart">'

    except Exception as e:
        print(f"Error generating chart: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating chart: {e}")

# Pydantic model for incoming queries
class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def get_ai_response(request: QueryRequest):
    user_question = request.query
    print(f"Received user query: {user_question}")

    try:
        # Step 1: Ask LLM to convert natural language to SQL
        sql_generation_prompt = f"""
        You are an expert SQL analyst for an e-commerce database.
        Your task is to convert a user's natural language question into an SQLite SQL query.
        The database schema is provided below.
        Only respond with the SQL query itself, nothing else. Do NOT include any explanations or conversational text.
        If the question cannot be answered by the database, respond with 'N/A'.

        DATABASE SCHEMA:
        {DATABASE_SCHEMA}

        User Question: {user_question}

        SQL Query:
        """
        print("\n--- Sending SQL Generation Prompt to Groq ---")
        sql_completion = groq_client.chat.completions.create(
            model=GROQ_MODEL_NAME,
            messages=[
                {"role": "user", "content": sql_generation_prompt}
            ],
            temperature=0.0,
            max_tokens=200
        )
        generated_sql_query = sql_completion.choices[0].message.content.strip()
        print(f"Groq Generated SQL: {generated_sql_query}")

        if generated_sql_query.lower().strip() == 'n/a':
            async def generate_na_response():
                yield "I cannot answer that question based on the provided e-commerce data. Please ask a different question."
            return StreamingResponse(generate_na_response(), media_type="text/plain")

        # Step 2: Execute the generated SQL query
        print("\n--- Executing SQL Query ---")
        columns, rows = execute_sql_query(generated_sql_query)

        if not rows:
            async def generate_no_results_response():
                yield "The SQL query executed successfully, but returned no results. This might mean there's no data matching your criteria."
            print(f"SQL Results: No rows found for query.")
            return StreamingResponse(generate_no_results_response(), media_type="text/plain")

        # Format results for Groq
        results_str = f"Columns: {', '.join(columns)}\n"
        for row in rows:
            results_str += f"Row: {row}\n"

        # Limit the results string to avoid hitting token limits for very large results
        if len(results_str) > 3000:
            results_str = results_str[:3000] + "\n... (results truncated due to length)"

        print(f"SQL Results for Groq:\n{results_str}")

        # Step 3: Ask LLM to summarize/respond (WITH STREAMING AND CHART DETECTION!)
        summary_prompt = f"""
        You are an intelligent e-commerce data assistant.
        The user asked: "{user_question}"
        I executed the following SQL query: "{generated_sql_query}"
        The SQL query returned the following results from the database:
        {results_str}

        **Strict Instruction for Response Format:**
        If the user's question explicitly asks for a "chart" or "graph" related to "total sales over time" AND the results are suitable for such a chart,
        you MUST respond with ONLY this exact JSON string:
        ```json
        {{ "chart_url": "/chart/total_sales_over_time" }}
        ```
        Do NOT include any other text, explanation, or conversational content if you are providing the chart_url JSON.

        Otherwise (if not requesting a specific chart), provide a concise, human-readable answer based ONLY on these results. Do not include any SQL code.
        """
        print("\n--- Sending Summary Prompt to Groq (Streaming/Chart Detection) ---")

        async def generate_response_chunks():
            full_llm_raw_response = ""
            stream_chunks = [] # Store chunks to yield later if text

            try:
                # Accumulate the entire raw response from Groq first
                # This is necessary to reliably check for the JSON chart command
                stream = groq_client.chat.completions.create(
                    model=GROQ_MODEL_NAME,
                    messages=[
                        {"role": "user", "content": summary_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=500,
                    stream=True
                )
                for chunk in stream:
                    content = chunk.choices[0].delta.content or ""
                    full_llm_raw_response += content
                    stream_chunks.append(content) # Store chunks for later re-yielding if text

                print(f"Groq Raw Summary Response: {full_llm_raw_response}")

                # Attempt to parse the full response as JSON for chart command
                try:
                    parsed_response = json.loads(full_llm_raw_response)
                    if "chart_url" in parsed_response:
                        chart_url = parsed_response["chart_url"]
                        print(f"AI requested chart from URL: {chart_url}")

                        # Yield the JSON string directly for frontend to fetch
                        yield json.dumps({"chart_url": chart_url})
                        return # Important: Stop yielding after chart JSON is sent

                except json.JSONDecodeError:
                    # Not a JSON response, so treat as plain text
                    pass

                # If it's not a chart JSON, yield the text content chunk by chunk for typing effect
                for chunk_content in stream_chunks:
                    yield chunk_content

                print(f"Final AI Response (from stream): {full_llm_raw_response}") # This will show the text or the JSON

            except Exception as e:
                error_msg = f"Error during streaming AI response: {e}"
                print(error_msg)
                yield f"ERROR: {error_msg}"
                raise

        # Return a StreamingResponse
        return StreamingResponse(generate_response_chunks(), media_type="text/plain")

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")

# -----------------------------------------------------------
# 5. Running the FastAPI Application (Replit handles via .replit)
# -----------------------------------------------------------