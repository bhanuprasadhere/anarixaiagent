# anarix_ai_agent - E-commerce Data AI Agent

## Project Overview

This is a full-stack AI agent application designed to answer questions related to e-commerce data using a natural language interface. The project is built entirely on free online platforms (Replit for hosting) and leverages a Large Language Model (LLM) to translate user queries into SQL, execute them against a SQLite database, and provide human-readable answers. The frontend provides a chat-like interface for seamless interaction, including dynamic text streaming and an attempt at visual data representations.

## Key Features

* **Natural Language to SQL:** Converts user questions into executable SQLite queries using a powerful LLM (Groq).
* **E-commerce Data Analysis:** Queries provided datasets (Product-Level Ad Sales, Total Sales, and Eligibility) stored in a local SQLite database.
* **FastAPI Backend:** Robust and scalable API for handling user requests and orchestrating AI and database interactions.
* **Dynamic Frontend:** Simple HTML/CSS/JS interface for intuitive user interaction.
* **Streamed Responses:** Provides a "typing" effect for AI answers, enhancing user experience.
* **Data Visualization (Bonus Attempt):** Includes backend logic to generate charts and frontend attempt to display them (e.g., Total Sales over Time). *Note: The chart integration is functional on the backend endpoint, but full dynamic display within chat might require further refinement due to browser/streaming complexities.*
* **Zero Local Execution:** Entire development, deployment, and execution environment is online.

## Technologies Used

* **Backend:** Python 3 (3.10/3.11), FastAPI, Uvicorn, Pandas, SQLite3, Groq (for LLM inference), Matplotlib (for visualization)
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
    * Upload your three `.csv` files: `Product-Level Ad Sales and Metrics (mapped) - Product-Level Ad Sales and Metrics (mapped).csv`, `Product-Level Total Sales and Metrics (mapped) - Product-Level Total Sales and Metrics (mapped).csv`, `Product-Level Eligibility Table (mapped) - Product-Level Eligibility Table (mapped).csv`.
    * **Rename them** for simplicity to `ad_sales.csv`, `total_sales.csv`, and `eligibility.csv` respectively.
4.  **Configure `.replit`:**
    * Ensure your `.replit` file contains:
        ```ini
        entrypoint = "main.py"
        run = "uvicorn main:app --host 0.0.0.0 --port 8000"

        modules = ["python-3.11"] # Or python-3.10, based on your Repl

        [nix]
        channel = "stable-24_05" # Or stable-23_11
        packages = ["cairo", "ffmpeg-full", "freetype", "ghostscript", "glibcLocales", "gobject-introspection", "gtk3", "libxcrypt", "pkg-config", "qhull", "tcl", "tk"]

        [[ports]]
        localPort = 8000
        externalPort = 80
        ```
5.  **Create `replit.nix`:**
    * Create a file named `replit.nix` in your project root.
    * Paste the following:
        ```nix
        { pkgs }: {
          deps = [
            pkgs.python310
            pkgs.python310Packages.pip
            # Other packages for matplotlib
            pkgs.cairo
            pkgs.ffmpeg-full
            pkgs.freetype
            pkgs.ghostscript
            pkgs.glibcLocales
            pkgs.gobject-introspection
            pkgs.gtk3
            pkgs.libxcrypt
            pkgs.pkg-config
            pkgs.qhull
            pkgs.tcl
            pkgs.tk
          ];
          env = {
            PYTHON_BIN = "${pkgs.python310}/bin/python3.10";
            PIP_BIN = "${pkgs.python310Packages.pip}/bin/pip3.10";
          };
        }
        ```
6.  **Create `requirements.txt`:**
    * Create a file named `requirements.txt` in your project root.
    * Add the following package list:
        ```
        fastapi==0.111.0
        uvicorn==0.30.1
        pandas==2.2.2
        groq # Use latest version or specify a known good one like ==0.8.0
        python-dotenv==1.0.1
        matplotlib==3.8.4
        httpx # To ensure compatibility for internal calls if needed
        ```
7.  **Set Groq API Key:**
    * Obtain a free API key from [GroqCloud](https://console.groq.com/keys).
    * In Replit, click the `🔒 Secrets` icon on the left sidebar.
    * Add a new secret with **Key:** `GROQ_API_KEY` and **Value:** (your Groq API key).
8.  **Create Frontend Files:**
    * Create `index.html`, `style.css`, and `script.js` in your project root.
    * Populate them with the respective complete code blocks provided in this guide.
9.  **Update `main.py`:**
    * Replace the entire content of your `main.py` with the complete code block provided in this guide (latest version with Groq, database setup, static file serving, streaming, and chart endpoint).
10. **Perform Cleanup (if needed):** If you hit `command not found` or `proxies` errors, go to Shell and run:
    ```bash
    rm -rf .pythonlibs venv __pycache__ .cache
    pip3 cache purge
    pip3 install --no-cache-dir -r requirements.txt
    ```
11. **Run the Repl:** Click the green "Run" button at the top of Replit. Replit will automatically install dependencies from `requirements.txt` and start your FastAPI app.

    Your application will be accessible via the public URL provided by Replit (visible in the Webview pane).

## How to Use

1.  Open the public URL of your Replit app in a web browser.
2.  Type your questions about the e-commerce data into the input box.
3.  Click "Send" or press Enter.
4.  The AI agent will process your query, generate SQL, fetch results, and respond with a human-readable answer, displayed with a live typing effect.
5.  You can also directly access generated charts via specific endpoints (e.g., `/chart/total_sales_over_time`).

## Example Questions

* "What is my total sales?"
* "Calculate the RoAS (Return on Ad Spend)."
* "Which product had the highest CPC (Cost Per Click)?"
* "How many units of item_id 21 were ordered on 2025-06-01?"
* "What is the eligibility status of product 262?"
* "Show me the ad sales for item 3 on June 1, 2025."
* "What was the total ad spend across all products on 2025-06-01?"
* "Show me a chart of total sales over time." (This should trigger the chart display, check your console for debug output).

---
