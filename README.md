# anarix_ai_agent - E-commerce Data AI Agent

## Project Overview

This is a full-stack AI agent application designed to answer questions related to e-commerce data using a natural language interface. The project is built entirely on free online platforms (Replit for hosting) and leverages a Large Language Model (LLM) to translate user queries into SQL, execute them against a SQLite database, and provide human-readable answers. The frontend provides a chat-like interface for seamless interaction.

## Key Features

* **Natural Language to SQL:** Converts user questions into executable SQLite queries using a powerful LLM.
* **E-commerce Data Analysis:** Queries provided datasets (Product-Level Ad Sales, Total Sales, and Eligibility) stored in a local SQLite database.
* **FastAPI Backend:** Robust and scalable API for handling user requests and orchestrating AI and database interactions.
* **Dynamic Frontend:** Simple HTML/CSS/JS interface for intuitive user interaction.
* **Streamed Responses:** Provides a "typing" effect for AI answers, enhancing user experience.
* **Zero Local Execution:** Entire development, deployment, and execution environment is online.

## Technologies Used

* **Backend:** Python 3, FastAPI, Uvicorn, Pandas, SQLite3, Groq (for LLM inference)
* **Frontend:** HTML5, CSS3, JavaScript (ES6+)
* **Platform:** Replit (Development & Hosting)
* **Version Control:** Git, GitHub

## Project Setup and Running (on Replit)

1.  **Create Replit Account:** If you don't have one, sign up at [Replit.com](https://replit.com/).
2.  **Create a New Repl:**
    * Log in to Replit.
    * Click `+ Create Repl`.
    * Choose the `Python` template.
    * Name your Repl `anarix_ai_agent`.
    * Click `Create Repl`.
3.  **Upload Datasets:**
    * Upload your three `.csv` files:
        * `Product-Level Ad Sales and Metrics (mapped) - Product-Level Ad Sales and Metrics (mapped).csv`
        * `Product-Level Total Sales and Metrics (mapped) - Product-Level Total Sales and Metrics (mapped).csv`
        * `Product-Level Eligibility Table (mapped) - Product-Level Eligibility Table (mapped).csv`
    * **Rename them** for simplicity to `ad_sales.csv`, `total_sales.csv`, and `eligibility.csv` respectively.
4.  **Configure `.replit`:**
    * Ensure your `.replit` file contains:
        ```ini
        run = "uvicorn main:app --host 0.0.0.0 --port 8000"
        entrypoint = "main.py"
        # ... other default Replit config ...
        ```
5.  **Create `requirements.txt`:**
    * Create a file named `requirements.txt` in your project root.
    * Add the following package list:
        ```
        fastapi==0.111.0
        uvicorn==0.30.1
        pandas==2.2.2
        groq==0.8.0 # Or the latest compatible version
        python-dotenv==1.0.1
        ```
6.  **Set Groq API Key:**
    * Obtain a free API key from [GroqCloud](https://console.groq.com/keys).
    * In Replit, click the `🔒 Secrets` icon on the left sidebar.
    * Add a new secret with **Key:** `GROQ_API_KEY` and **Value:** (your Groq API key).
7.  **Create Frontend Files:**
    * Create `index.html`, `style.css`, and `script.js` in your project root.
    * Populate them with the respective code provided in the project guide.
8.  **Update `main.py`:**
    * Replace the entire content of your `main.py` with the complete code provided in the project guide (including Groq integration, database setup, static file serving, and streaming API endpoint).
9.  **Run the Repl:** Click the green "Run" button at the top of Replit. Replit will automatically install dependencies from `requirements.txt` and start your FastAPI app.

Your application will be accessible via the public URL provided by Replit (visible in the Webview pane).

## How to Use

1.  Open the public URL of your Replit app in a web browser.
2.  Type your questions about the e-commerce data into the input box.
3.  Click "Send" or press Enter.
4.  The AI agent will process your query, generate SQL, fetch results, and respond with a human-readable answer, displayed with a live typing effect.

## Example Questions

* "What is my total sales?"
* "Calculate the RoAS (Return on Ad Spend)."
* "Which product had the highest CPC (Cost Per Click)?"
* "How many units of item_id 21 were ordered on 2025-06-01?"
* "What is the eligibility status of product 262?"
* "Show me the ad sales and ad spend for item 3 on June 1, 2025."
* "Which product had the highest ad sales?"
* "What was the total ad spend across all products on 2025-06-01?"

---

*(This README will be automatically displayed on your GitHub repo. Remember to push this new file to GitHub as well!)*
