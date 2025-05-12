## Frontend Design: AI Portfolio Advisor

This document outlines the design for the frontend user interface and user experience (UI/UX) of the AI Portfolio Advisor application. The frontend will be built using HTML, CSS, and JavaScript, interacting with the Flask backend.

### 1. Overall Structure and Navigation

The application will primarily consist of two main views/pages:

1.  **Upload Page (`/` or `/upload`):** The landing page where users can upload their portfolio CSV file.
2.  **Dashboard Page (`/dashboard`):** Displays the analysis and recommendations for the uploaded portfolio.

**Navigation Flow:**

*   User lands on the Upload Page.
*   User selects and uploads their CSV file.
*   Upon successful upload and initial validation by the backend, the backend processes the portfolio and performs the AI analysis.
*   Once analysis is complete, the user is redirected to the Dashboard Page, which displays the results for their portfolio.
*   A navigation bar (optional for V1, but good for future) could allow users to return to the upload page to analyze a new portfolio.

### 2. UI Design

#### A. Upload Page (`index.html` served by a Flask route, e.g., `/`)

*   **Layout:** Clean and simple.
    *   **Header:** Application Title (e.g., "AI Portfolio Advisor").
    *   **Main Content Area:**
        *   **Introduction:** A brief explanation of the application and its purpose (e.g., "Upload your stock portfolio in CSV format to get AI-powered buy, hold, or sell recommendations based on market data and news.").
        *   **CSV Format Instructions:** Clear instructions on the required CSV format:
            *   Required columns: `Ticker`, `Quantity`.
            *   Optional columns: `PurchasePrice`, `PurchaseDate`.
            *   Provide a small, clear example of the CSV structure.
            *   Link to a sample CSV file download (optional, but helpful).
        *   **File Upload Form:**
            *   HTML `<form>` element with `method="POST"` and `enctype="multipart/form-data"` targeting the backend upload endpoint (e.g., `/api/upload_portfolio`).
            *   A file input element: `<input type="file" name="portfolio_csv" accept=".csv" required>`.
            *   A submit button: `<button type="submit">Analyze Portfolio</button>`.
        *   **Loading/Feedback Area:** An area (e.g., a `<div>`) to display messages to the user:
            *   During upload/analysis: "Processing your portfolio, please wait..." (could include a simple spinner).
            *   Error messages: If CSV validation fails on the client-side (basic checks) or if the backend returns an error (e.g., invalid file format, server error).
    *   **Footer:** Copyright information or disclaimers (e.g., "For informational purposes only, not financial advice.").

**Client-side JavaScript (`upload_page.js`):**

*   Basic validation (e.g., check if a file is selected and if it appears to be a CSV by extension) before submitting the form.
*   Handle form submission using `fetch` API to allow for asynchronous processing and better feedback display without a full page reload (though a redirect to the dashboard will occur on success).
*   Display loading indicators and error messages from the backend.

#### B. Dashboard Page (`dashboard.html` served by a Flask route, e.g., `/dashboard`)

*   **Layout:** Clear, organized, and easy to read.
    *   **Header:** Application Title and perhaps a link back to the Upload Page ("Analyze New Portfolio").
    *   **Main Content Area:**
        *   **Portfolio Summary (Optional):** A small section showing the number of unique stocks analyzed.
        *   **Recommendations Table/Grid:** This is the core of the dashboard. For each stock in the analyzed portfolio, display:
            *   **Ticker Symbol:** (e.g., AAPL)
            *   **Current Price:** (Fetched by backend, e.g., $170.50)
            *   **AI Recommendation:** (BUY/HOLD/SELL) - Visually distinct (e.g., using color codes: Green for BUY, Orange for HOLD, Red for SELL).
            *   **Confidence:** (e.g., 75% or High/Medium/Low)
            *   **Timeframe:** (e.g., Short-Term, Medium-Term, Long-Term)
            *   **Justification/Key Drivers:** A concise explanation for the recommendation. This might be a short paragraph or a few bullet points. Could have a "Read More" toggle if the justification is long.
        *   **Data Presentation:** Use an HTML `<table>` for structured data or a series of `<div>` cards for a more modern look. Each row/card represents one stock.
        *   **Sorting/Filtering (Future Enhancement):** Allow users to sort the table by Ticker, Recommendation, etc.
    *   **Footer:** Disclaimers.

**Client-side JavaScript (`dashboard_page.js`):**

*   This page will primarily display data rendered by the Flask template engine when the user is redirected from the upload process. The backend will pass the analysis results to the `dashboard.html` template.
*   JavaScript might be used for interactive elements if added later (e.g., tooltips for more info, expanding/collapsing justification text, client-side sorting/filtering if not handled by backend).

### 3. Technology and Styling

*   **HTML5:** Semantic HTML for structure.
*   **CSS3:** For styling. Initially, use simple, clean CSS. The Flask template created by `create_flask_app` might include basic styling or a framework like Tailwind CSS. If not, custom CSS will be written in a `static/css/style.css` file.
    *   Focus on readability, clear visual hierarchy, and responsive design (so it works reasonably well on different screen sizes).
*   **JavaScript (ES6+):** For client-side interactions, form handling, and potentially dynamic updates if the application evolves.

### 4. Interaction with Backend (Flask API Endpoints)

*   **Portfolio Upload:**
    *   **Frontend Action:** User submits the CSV file via the form on the Upload Page.
    *   **API Endpoint (Backend):** e.g., `POST /api/upload_portfolio`
    *   **Request:** `multipart/form-data` containing the CSV file.
    *   **Backend Response (on success):** Redirect to `/dashboard` with analysis results passed to the template, or a JSON response with a success message and a URL to redirect to if handled purely by JS.
    *   **Backend Response (on error):** JSON response with an error message (e.g., `{"error": "Invalid CSV format"}`), which the frontend JS displays.
*   **Displaying Recommendations on Dashboard:**
    *   **Frontend Action:** The Dashboard Page is loaded after a successful analysis.
    *   **Data Source:** The Flask backend, when rendering `dashboard.html`, will query the results of the AI analysis (which might be stored temporarily in the session or a database associated with the session/upload) and pass this data to the Jinja2 template.
    *   The template will then iterate through the recommendation data and generate the HTML to display it.

### 5. File Structure (within `portfolio_advisor_app/src/static/` and `portfolio_advisor_app/src/templates/`)

*   `src/templates/index.html` (Upload Page)
*   `src/templates/dashboard.html` (Dashboard Page)
*   `src/templates/layout.html` (Base template with common header/footer, if used)
*   `src/static/css/style.css` (Custom stylesheets)
*   `src/static/js/upload_page.js` (JavaScript for the upload page)
*   `src/static/js/dashboard_page.js` (JavaScript for the dashboard page, if needed for interactivity)
*   `src/static/images/` (For any images like logos or spinners)

This frontend design aims for simplicity and clarity for the initial version, focusing on the core user flow of uploading a portfolio and viewing AI-driven recommendations.
