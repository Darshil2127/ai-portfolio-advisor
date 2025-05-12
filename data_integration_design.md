## News and Market Data Integration Design

This document outlines the design for integrating news and market data into the AI Portfolio Advisor application, primarily using the YahooFinance and DataBank APIs.

### 1. Data Requirements Recap

As per `application_requirements.md`, the application needs:

*   **Stock Market Data:** Historical prices, real-time quotes (if possible, or recent close), technical indicators, company fundamentals, analyst ratings, and significant company news/developments.
*   **World News & Economic Indicators:** Macroeconomic data (GDP, inflation, interest rates, etc.) and qualitative world news impacting markets (geopolitical events, tariffs).

### 2. API Endpoint Selection and Usage Strategy

#### A. YahooFinance API

1.  **`YahooFinance/get_stock_chart`**
    *   **Use Case:** Fetch historical price and volume data for individual stocks in the user's portfolio.
    *   **Parameters to Use:**
        *   `symbol`: Stock ticker from the user's portfolio.
        *   `interval`: Likely `1d` (daily) for trend analysis, possibly `1wk` or `1mo` for longer-term views.
        *   `range`: A suitable range like `1y`, `2y`, or `5y` to capture sufficient historical data for trend analysis and AI model input.
        *   `includeAdjustedClose`: `True` (default) is important for accurate historical performance.
    *   **Data to Extract:** Timestamps, open, high, low, close, volume, adjusted close prices.

2.  **`YahooFinance/get_stock_insights`**
    *   **Use Case:** Obtain comprehensive financial analysis, technical indicators, company metrics, valuation, research report summaries, significant developments, and SEC filings.
    *   **Parameters to Use:**
        *   `symbol`: Stock ticker.
    *   **Data to Extract:**
        *   `instrumentInfo.technicalEvents`: Short, intermediate, and long-term outlooks, support/resistance levels.
        *   `instrumentInfo.valuation`: Description, discount, relative value.
        *   `companySnapshot`: Sector info, company innovativeness, hiring, sustainability, insider sentiments, earnings reports, dividends.
        *   `recommendation`: Target price, provider, rating.
        *   `sigDevs`: Headlines and dates of significant developments (news).
        *   `secReports`: Information on SEC filings.

3.  **`YahooFinance/get_stock_what_analyst_are_saying`**
    *   **Use Case:** Get detailed analyst research reports, including titles, summaries, provider, and publication dates.
    *   **Parameters to Use:**
        *   `symbol`: Stock ticker.
    *   **Data to Extract:** Report titles, abstracts, provider, report date. (Note: `pdf_url` might be useful for users but not directly for AI processing unless content extraction is implemented).

#### B. DataBank API

1.  **`DataBank/indicator_list`**
    *   **Use Case:** (Primarily for initial setup or advanced configuration) To allow searching and selection of relevant World Development Indicators if the specific codes are not known beforehand.
    *   **Parameters to Use:** `q` for searching (e.g., "GDP", "inflation", "interest rate").

2.  **`DataBank/indicator_data`**
    *   **Use Case:** Fetch time-series data for specific macroeconomic indicators for relevant countries/regions.
    *   **Parameters to Use:**
        *   `indicator`: The specific indicator code (e.g., `NY.GDP.MKTP.CD` for GDP).
        *   `country`: ISO 3166 alpha-3 country codes (e.g., `USA`, `CHN`, `EUU` for Euro area). The application will need a mapping from stock exchange/company domicile to relevant country codes.
    *   **Data to Extract:** Yearly (or other frequency) data for the selected indicator.

#### C. General World News (Beyond YahooFinance `sigDevs`)

*   **Requirement:** The initial request mentioned "world news, like war, tariff". The YahooFinance API provides company-specific significant developments but might not cover broader geopolitical news or specific tariff announcements comprehensively.
*   **Strategy:**
    1.  **Initial Phase:** Rely on `YahooFinance/get_stock_insights` (sigDevs) and general market sentiment derived from financial news sources.
    2.  **Future Enhancement:** If more detailed world news is critical, integrate a dedicated news API (e.g., NewsAPI.org, GDELT project) or use web scraping (with caution due to reliability and maintenance). This would involve keyword-based searching for terms like "war", "tariff", specific country names, etc., followed by sentiment analysis.
    *   For now, this aspect will be noted as a potential area for future expansion, and the primary focus will be on the structured data from YahooFinance and DataBank.

### 3. Data Fetching and Processing Modules

Within the `portfolio_advisor_app/src/` directory, we will create a new subdirectory, e.g., `data_services`, to house the logic for interacting with these external APIs.

**Proposed Modules:**

*   `src/data_services/yahoo_finance_client.py`:
    *   Contains functions to call the various YahooFinance API endpoints.
    *   Each function will take necessary parameters (like `symbol`, `range`) and return the processed JSON data or a structured Python object/dictionary.
    *   Will use the `ApiClient` as shown in the datasource module examples.
    *   Error handling (API errors, network issues, unexpected response formats) will be implemented.
*   `src/data_services/data_bank_client.py`:
    *   Contains functions to call the DataBank API endpoints.
    *   Similar structure to `yahoo_finance_client.py`.
*   `src/data_services/data_aggregator.py` (or similar name):
    *   This module will be responsible for orchestrating calls to the client modules based on the user's portfolio.
    *   For each stock in the portfolio, it will fetch relevant data from YahooFinance.
    *   It will determine relevant macroeconomic indicators and countries (e.g., based on stock exchange or company HQ) and fetch data from DataBank.
    *   It will perform initial cleaning, transformation, and aggregation of data from different sources to prepare it for the AI engine.
    *   For example, it might align timestamps, calculate basic sentiment from news headlines (if feasible without advanced NLP initially), and structure data into a format suitable for AI model input.

### 4. Data Caching Strategy (Optional but Recommended for Performance)

*   **Rationale:** API calls, especially for a large portfolio or extensive historical data, can be slow and may be rate-limited.
*   **Simple Caching:**
    *   Implement a simple time-based cache (e.g., using Flask-Caching or a custom dictionary-based cache with timestamps).
    *   Store API responses for a certain period (e.g., stock price data for 15-60 minutes, daily indicators for 24 hours).
    *   Key for cache could be a hash of the API endpoint and parameters.
*   **Database Caching:** For more persistent caching, frequently accessed but slowly changing data (like historical prices for a specific range) could be stored in a dedicated database table.
*   **Initial Implementation:** Start without caching to simplify, but design modules to easily accommodate caching later.

### 5. Error Handling and Resilience

*   Each API client function must handle potential errors:
    *   Network errors (timeouts, connectivity issues).
    *   API-specific errors (invalid symbol, rate limits, authentication issues if any were required).
    *   Unexpected response formats.
*   The application should degrade gracefully. If a non-critical data source fails, it should attempt to proceed with available data and notify the user or log the issue.

### 6. Data for AI Model

The `data_aggregator.py` module will ultimately aim to produce a structured dataset for each stock that the AI recommendation engine can consume. This might be a dictionary or a Pandas DataFrame per stock, containing features like:

*   Historical price series (OHLCV, adjusted close).
*   Technical indicators (from YahooFinance or calculated).
*   Valuation metrics.
*   News sentiment scores (initially basic, potentially more advanced later).
*   Analyst ratings and target prices.
*   Relevant macroeconomic indicators.

This design provides a roadmap for integrating the necessary external data. The next step would be to start implementing the client modules for YahooFinance and DataBank.
