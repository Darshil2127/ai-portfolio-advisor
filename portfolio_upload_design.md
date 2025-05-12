## Portfolio Upload Feature Design

This document outlines the design for the portfolio upload feature of the AI Portfolio Advisor application.

### 1. CSV File Structure

The application will expect users to upload a CSV (Comma Separated Values) file with the following structure:

*   **Required Columns:**
    *   `Ticker`: (Text/String) The stock ticker symbol (e.g., AAPL, MSFT, GOOGL).
    *   `Quantity`: (Integer) The number of shares owned.
*   **Optional Columns:**
    *   `PurchasePrice`: (Float/Decimal) The average purchase price per share. If not provided, some analyses (like profit/loss) might not be possible or will be based on current market price only.
    *   `PurchaseDate`: (Date, format: YYYY-MM-DD) The date when the shares were acquired. This can be useful for historical analysis or tax-lot accounting in future enhancements.

**Example CSV Content:**

```csv
Ticker,Quantity,PurchasePrice,PurchaseDate
AAPL,100,150.25,2023-01-15
MSFT,50,300.50,2022-11-20
GOOGL,75,120.00,
TSLA,20,,2024-03-01
NVDA,30,750.75
```

**Validation Rules for CSV Data:**

*   `Ticker` must not be empty and should ideally be validated against a list of known valid tickers (though this might be complex to maintain globally; initial validation might just check for non-emptiness and alphanumeric characters).
*   `Quantity` must be a positive integer.
*   `PurchasePrice` (if provided) must be a positive number.
*   `PurchaseDate` (if provided) must be a valid date, preferably not in the future.

### 2. Backend Logic for Portfolio Upload and Processing

**File Upload Endpoint:**

*   A Flask route (e.g., `/upload_portfolio`) will be created to handle `POST` requests with the CSV file.
*   The endpoint will accept `multipart/form-data` to receive the file.

**Processing Steps:**

1.  **Receive File:** Get the uploaded file from the request.
2.  **Basic Validation:**
    *   Check if a file was uploaded.
    *   Check if the file extension is `.csv`.
    *   Check file size (to prevent overly large uploads, e.g., max 5MB).
3.  **Parse CSV:**
    *   Use the `pandas` library to read the CSV data into a DataFrame for easy manipulation and validation.
    *   Attempt to read the header row to identify columns.
4.  **Data Validation (Row-level):**
    *   Iterate through each row of the DataFrame.
    *   Validate data types and constraints for each column as defined in the CSV structure section (Ticker, Quantity, PurchasePrice, PurchaseDate).
    *   Handle missing optional values gracefully.
    *   Collect valid rows and any rows with errors.
5.  **Error Handling & Feedback:**
    *   If critical errors occur (e.g., wrong file type, unparsable CSV), return an appropriate error message to the user.
    *   If row-level errors occur, provide feedback to the user about which rows/data points are problematic (e.g., "Row 3: Invalid quantity. Row 5: Ticker symbol missing.").
6.  **Data Storage (if validation passes for at least some data):**
    *   For valid portfolio items, store them in the database (see Database Schema section).
    *   Associate the portfolio data with the current user session or a user account if authentication is implemented later.
7.  **Response:**
    *   On successful upload and processing, redirect the user to the analysis/dashboard page or return a success message.
    *   On failure, display clear error messages and allow the user to try uploading again.

**Libraries to be used:**

*   Flask: For routing and request handling.
*   Pandas: For CSV parsing and data validation.

### 3. Database Schema for Storing User Portfolios

For the initial version, we will use a simple structure. If user accounts are implemented, a `user_id` would be a foreign key.

**Table: `PortfolioHolding`**

*   `id`: (Integer, Primary Key, Auto-increment) Unique identifier for each holding record.
*   `session_id`: (String) To associate holdings with a user's current session (if no user accounts). If user accounts are added, this would be `user_id` (Integer, Foreign Key to `User` table).
*   `ticker_symbol`: (String, Not Null) The stock ticker symbol.
*   `quantity`: (Integer, Not Null) Number of shares held.
*   `purchase_price`: (Float, Nullable) Average purchase price per share.
*   `purchase_date`: (Date, Nullable) Date of purchase.
*   `uploaded_at`: (DateTime, Not Null, Default: Current Timestamp) Timestamp of when the record was created/uploaded.

**Considerations for Database Setup (within Flask App):**

*   The Flask template `portfolio_advisor_app` has SQLAlchemy and PyMySQL pre-configured (though the database connection might be commented out in `src/main.py`).
*   We will need to:
    1.  Define the `PortfolioHolding` model in `src/models/portfolio_holding.py` (or a similar file).
    2.  Uncomment and configure the database URI in `src/main.py` if using MySQL. For initial development, SQLite might be simpler and can be configured directly in `SQLALCHEMY_DATABASE_URI`.
    3.  Create the database tables using Flask-Migrate or `db.create_all()`.

This design provides a solid foundation for the portfolio upload feature. Further refinements can be made as development progresses.
