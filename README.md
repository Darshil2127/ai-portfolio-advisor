# AI Portfolio Advisor Flask Application

This application allows users to upload their stock portfolio in CSV format and receive AI-powered buy, hold, or sell recommendations.

## Project Structure

```
portfolio_advisor_app/
├── venv/                   # Virtual environment (not in Git)
├── src/
│   ├── ai_engine/          # AI recommendation engine modules
│   │   ├── __init__.py
│   │   ├── feature_engineering.py
│   │   ├── main_analyzer.py
│   │   ├── rule_engine.py
│   │   └── sentiment_analyzer.py
│   ├── data_services/      # API client modules
│   │   ├── __init__.py
│   │   ├── data_aggregator.py
│   │   ├── data_bank_client.py
│   │   └── yahoo_finance_client.py
│   ├── models/             # Database models
│   │   ├── __init__.py
│   │   └── portfolio_holding.py
│   ├── routes/             # Flask blueprints for routes
│   │   ├── __init__.py
│   │   ├── upload_routes.py
│   │   └── view_routes.py
│   ├── static/             # Static files (CSS, JS, images)
│   │   ├── css/style.css
│   │   └── js/upload_page.js
│   ├── templates/          # HTML templates
│   │   ├── dashboard.html
│   │   └── index.html
│   └── main.py             # Main Flask application entry point
├── .gitignore              # Specifies intentionally untracked files that Git should ignore
├── Procfile                # Specifies the commands that are executed by the app on startup (for Render)
├── requirements.txt        # Lists Python package dependencies
└── README.md               # This file
```

## Setup and Local Development

1.  **Clone the Repository (or Unpack the Code):**
    ```bash
    # If from Git
    # git clone <repository_url>
    # cd portfolio_advisor_app
    ```

2.  **Create and Activate a Virtual Environment:**
    It is highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    (On Windows, use `venv\Scripts\activate`)

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Environment Variables (Optional but Recommended):**
    The application uses a default `SECRET_KEY` and an SQLite database (`portfolio_app.db`) by default. For production, you should set these via environment variables.
    *   `SECRET_KEY`: A strong, random string for Flask session security.
    *   `DATABASE_URL`: If you want to use a different database (e.g., PostgreSQL for production on Render). For SQLite, no change is needed for local run.

    You can create a `.env` file (and add it to `.gitignore`) for local development:
    ```
    SECRET_KEY=\'your_strong_random_secret_key_here\'
    # DATABASE_URL=\'your_production_database_url_here\'
    ```
    The application will pick these up if you use a library like `python-dotenv` (not included by default in this setup, `os.environ.get` is used).

5.  **Run the Application Locally:**
    ```bash
    python src/main.py
    ```
    The application should be accessible at `http://localhost:5000` or `http://0.0.0.0:5000`.

## Deployment to Render (Using GitHub)

Render is a platform that can deploy web applications directly from a GitHub repository.

1.  **Push to GitHub:**
    *   Ensure your `portfolio_advisor_app` directory is a Git repository.
    *   Commit all your application files (including `Procfile`, `requirements.txt`, and the `src` directory).
    *   Push your repository to GitHub.

2.  **Create a New Web Service on Render:**
    *   Log in to your Render dashboard.
    *   Click "New +" and select "Web Service".
    *   Connect your GitHub account and select the repository for the `portfolio_advisor_app`.

3.  **Configure the Web Service on Render:**
    *   **Name:** Give your service a name (e.g., `ai-portfolio-advisor`).
    *   **Region:** Choose a region closest to your users.
    *   **Branch:** Select the branch you want to deploy (e.g., `main` or `master`).
    *   **Root Directory:** Leave this blank if your `Procfile` and `requirements.txt` are in the root of the repository. If they are inside the `portfolio_advisor_app` folder within your repo, set this to `portfolio_advisor_app`.
    *   **Runtime:** Render should auto-detect Python.
    *   **Build Command:** Render typically uses `pip install -r requirements.txt`. This should be sufficient.
    *   **Start Command:** Render will use the `web` process type from your `Procfile`. So, `gunicorn src.main:app --log-file=-` will be used.
    *   **Instance Type:** Choose an appropriate instance type (e.g., Free or Starter plan).

4.  **Add Environment Variables on Render:**
    *   Go to the "Environment" tab for your service on Render.
    *   Add a `SECRET_KEY` with a strong, random value.
    *   **Python Version:** You might need to set a `PYTHON_VERSION` environment variable if Render's default Python version is not compatible (e.g., `PYTHON_VERSION` to `3.11.0`). Check `requirements.txt` for any version-specific packages.
    *   **Database (Optional - for Production):**
        *   If you want to use a production database like PostgreSQL on Render:
            1.  Create a new PostgreSQL instance on Render.
            2.  Render will provide a `DATABASE_URL` (Internal Connection String).
            3.  Add this `DATABASE_URL` as an environment variable to your Web Service.
            4.  Ensure your `requirements.txt` includes `psycopg2-binary` if using PostgreSQL.
        *   If you continue using SQLite (default in `main.py`), be aware that on Render's free tier, the filesystem is ephemeral. This means your SQLite database will be reset on every deploy or restart. For persistent data, a managed database like PostgreSQL is recommended.

5.  **Deploy:**
    *   Click "Create Web Service".
    *   Render will pull your code from GitHub, build the application, and deploy it.
    *   You can monitor the deployment logs on Render.
    *   Once deployed, Render will provide you with a public URL (e.g., `your-app-name.onrender.com`).

6.  **Automatic Deploys (Optional):**
    Render can automatically redeploy your application whenever you push changes to the connected GitHub branch.

## Important Notes

*   **API Usage:** This application uses external APIs (YahooFinance, DataBank) which are called via a sandboxed `ApiClient`. Ensure these APIs are accessible from Render's environment. No explicit API keys are configured in the current codebase for these specific APIs as they were provided as available datasources.
*   **Error Handling & Logging:** The application includes basic logging to the console. For production, you might want to configure more robust logging (e.g., to a logging service).
*   **Security:** Always use strong, unique secret keys. Be mindful of any sensitive data.
*   **Scaling:** For higher traffic, you may need to upgrade your Render instance type or consider more advanced scaling strategies.

This README provides the essential steps to get the AI Portfolio Advisor application running locally and deployed to Render. Refer to the official Render documentation for more detailed information on their platform features and configurations.

