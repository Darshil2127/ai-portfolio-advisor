## Application Testing Plan: AI Portfolio Advisor

This document outlines the testing strategy for the AI Portfolio Advisor application, covering unit, integration, and end-to-end testing. This plan is based on the design documents for application requirements, portfolio upload, data integration, AI engine, and frontend.

### 1. Overall Testing Objectives

*   Ensure all core functionalities outlined in `application_requirements.md` are working as expected.
*   Verify the robustness and error handling capabilities of the application.
*   Confirm data integrity throughout the processing pipeline (upload -> data fetching -> AI analysis -> display).
*   Validate the accuracy and relevance of AI-generated recommendations (based on the defined rule-based system).
*   Ensure a smooth and intuitive user experience.

### 2. Testing Scope

*   **Backend Modules:** Portfolio CSV parsing, external API clients (YahooFinance, DataBank), data aggregation, AI feature engineering, AI rule engine, Flask routes and API endpoints.
*   **Frontend Components:** Portfolio upload form, dashboard display of recommendations, user feedback mechanisms.
*   **Data Flow:** From user CSV upload to the presentation of results on the dashboard.

### 3. Testing Levels

#### A. Unit Testing

*   **Objective:** To test individual components or modules in isolation.
*   **Tools:** Python's `unittest` or `pytest` framework for backend modules.
*   **Modules to Test & Key Scenarios:**
    1.  **Portfolio CSV Parser (`portfolio_upload_design.md` logic):**
        *   Test with valid CSV (all required columns, all optional columns, mix).
        *   Test with invalid CSV (missing required columns, incorrect data types for Quantity/PurchasePrice, malformed CSV).
        *   Test with empty CSV or CSV with only headers.
        *   Test with large CSV file (boundary check for size limits, if any).
        *   Test various delimiters or quote character issues if robust parsing is intended.
    2.  **YahooFinance API Client (`data_integration_design.md` - `yahoo_finance_client.py`):
        *   Mock API calls to test handling of successful responses (correct data extraction).
        *   Mock API calls to test handling of error responses (e.g., 404 for invalid symbol, 429 for rate limits, 500 server error).
        *   Test with different parameters for `get_stock_chart`, `get_stock_insights`, `get_stock_what_analyst_are_saying`.
    3.  **DataBank API Client (`data_integration_design.md` - `data_bank_client.py`):
        *   Similar to YahooFinance client: mock successful and error responses.
        *   Test `indicator_data` and `indicator_list` functionalities.
    4.  **Data Aggregator (`data_integration_design.md` - `data_aggregator.py`):
        *   Test with mock data from API clients.
        *   Verify correct aggregation and structuring of data for the AI engine.
        *   Test error handling if one of the data sources fails.
    5.  **AI Feature Engineering (`ai_recommendation_engine_design.md` - `feature_engineering.py`):
        *   Test calculation of each defined feature (SMAs, RSI, MACD, sentiment scores from mock inputs).
        *   Test handling of missing input data for feature calculation.
    6.  **AI Sentiment Analyzer (`ai_recommendation_engine_design.md` - `sentiment_analyzer.py`):
        *   Test with sample positive, negative, and neutral texts.
        *   Verify output score range.
    7.  **AI Rule Engine (`ai_recommendation_engine_design.md` - `rule_engine.py`):
        *   Test individual rules with mock feature sets that should trigger/not trigger them.
        *   Test rule priorities and conflict resolution (if applicable).
        *   Verify correct generation of recommendation, confidence, timeframe, and justification components.

#### B. Integration Testing

*   **Objective:** To test the interaction between different integrated modules.
*   **Strategy:** Test key data flows and API interactions.
*   **Key Integrations to Test:**
    1.  **Portfolio Upload to Data Storage:**
        *   Upload a CSV -> Backend parsing -> Validation -> Data written to database (mocked or actual test DB).
        *   Verify correct data transformation and storage.
    2.  **Data Retrieval Pipeline (Portfolio -> API Clients -> Data Aggregator):
        *   Trigger analysis for a sample portfolio.
        *   Verify that the Data Aggregator correctly calls YahooFinance and DataBank clients with appropriate parameters (e.g., stock tickers from portfolio).
        *   Verify that data from different sources is correctly combined.
    3.  **Full Backend Analysis Pipeline (Portfolio -> Data Aggregation -> AI Engine -> Recommendation Output):
        *   Input a sample portfolio.
        *   Trace data flow through data aggregation, feature engineering, and the AI rule engine.
        *   Verify that the final recommendation objects (JSON) are structured as designed.
    4.  **Frontend to Backend API Endpoints:**
        *   Test `/api/upload_portfolio` endpoint: Send valid and invalid CSV files from a test client (e.g., Postman or Python `requests`) and check responses (success redirect/JSON, error JSONs).
        *   Test any other API endpoints defined for fetching dashboard data (if not purely server-rendered on redirect).

#### C. End-to-End (E2E) Testing / UI Testing

*   **Objective:** To test the entire application flow from the user's perspective, simulating real user scenarios.
*   **Strategy:** Manual testing based on user stories. Automated E2E testing using tools like Selenium or Playwright could be a future enhancement.
*   **Key User Scenarios to Test:**
    1.  **Successful Portfolio Analysis:**
        *   User navigates to the upload page.
        *   User sees instructions for CSV format.
        *   User uploads a valid CSV file with a few diverse stocks (some with all optional fields, some without).
        *   User sees a loading indicator.
        *   User is redirected to the dashboard page.
        *   Dashboard correctly displays each stock from the CSV with its AI recommendation, confidence, timeframe, and justification.
        *   Data displayed (e.g., current price - if shown) is plausible.
    2.  **Invalid CSV Upload - File Format:**
        *   User attempts to upload a non-CSV file (e.g., .txt, .jpg).
        *   Application shows an appropriate error message on the upload page.
    3.  **Invalid CSV Upload - Data Issues:**
        *   User uploads a CSV with missing required columns (e.g., no 'Ticker').
        *   User uploads a CSV with invalid data types (e.g., text in 'Quantity').
        *   Application shows clear error messages, ideally indicating problematic rows/columns.
    4.  **Empty CSV Upload:**
        *   User uploads an empty CSV or a CSV with only headers.
        *   Application handles this gracefully (e.g., error message or message indicating no data to analyze).
    5.  **API Data Fetching Issues (Simulated if possible, or observed during testing):
        *   If the backend fails to fetch data for a specific stock (e.g., invalid ticker not caught earlier, or API temporarily down for that stock), how is this presented? (e.g., stock shown with an error, or omitted with a notice).
    6.  **UI Responsiveness (Basic Check):**
        *   View the upload and dashboard pages on different screen sizes (desktop, tablet-like width) to ensure basic readability and usability.

### 4. Test Data Requirements

*   **Sample CSV Files:** Various valid and invalid CSVs covering different scenarios.
    *   `valid_portfolio_full.csv` (all fields, multiple stocks)
    *   `valid_portfolio_minimal.csv` (only required fields)
    *   `invalid_portfolio_missing_ticker.csv`
    *   `invalid_portfolio_bad_quantity.csv`
    *   `empty_portfolio.csv`
    *   `header_only_portfolio.csv`
*   **Mock API Responses:** JSON files representing successful and error responses from YahooFinance and DataBank APIs for unit testing API clients.
*   **Expected AI Outputs:** For specific input feature sets, define the expected recommendation from the rule-based system to validate AI logic.

### 5. Defect Management

*   Any bugs or issues found will be documented with steps to reproduce, actual vs. expected results, and severity.
*   (For a larger project, a bug tracking system would be used. For this, a simple list or section in a document might suffice initially).

### 6. Test Environment

*   **Backend:** Local development environment with the Flask application running.
*   **Database:** SQLite for initial testing, or the configured MySQL if used.
*   **Frontend:** Web browser (e.g., Chrome, Firefox).

This testing plan provides a comprehensive approach to validating the AI Portfolio Advisor application. The actual execution of these tests will occur after the implementation of the respective modules and frontend pages.
