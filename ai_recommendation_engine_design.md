## AI Recommendation Engine Design

This document outlines the design for the AI Recommendation Engine component of the AI Portfolio Advisor application.

### 1. Overview

The AI Recommendation Engine will analyze the processed data (portfolio, stock market data, news, economic indicators) to generate BUY, HOLD, or SELL recommendations for each stock, along with a suggested timeframe and justification.

Given the complexity and the need for explainability, an initial version might employ a hybrid approach, combining rule-based logic with machine learning components. For a purely ML-driven approach, significant historical data and robust backtesting would be required, which is a more advanced stage.

### 2. Feature Engineering and Selection

Input features will be derived from the data collected and processed by the `data_aggregator.py` module (as designed in `data_integration_design.md`). For each stock, the following features will be considered:

*   **A. Portfolio-Context Features:**
    *   `current_holding_percentage`: Percentage of this stock in the user's current portfolio (if portfolio context is used for diversification advice - future enhancement).
    *   `unrealized_pnl_percentage`: (PurchasePrice - CurrentPrice) / PurchasePrice (if PurchasePrice is available).

*   **B. Price & Volume Technical Indicators:**
    *   `price_trend_short_term`: e.g., 20-day Simple Moving Average (SMA) slope, or relative position to 20-day SMA.
    *   `price_trend_medium_term`: e.g., 50-day SMA slope, or relative position to 50-day SMA.
    *   `price_trend_long_term`: e.g., 200-day SMA slope, or relative position to 200-day SMA.
    *   `volatility_short_term`: e.g., Standard deviation of returns over the last 20 days or Average True Range (ATR).
    *   `volume_trend`: e.g., Ratio of 20-day average volume to 50-day average volume.
    *   `rsi_14_day`: Relative Strength Index (14-day).
    *   `macd_12_26_9`: Moving Average Convergence Divergence signal and histogram values.
    *   `support_level`: From `YahooFinance/get_stock_insights` (keyTechnicals).
    *   `resistance_level`: From `YahooFinance/get_stock_insights` (keyTechnicals).

*   **C. Fundamental & Valuation Metrics:**
    *   `pe_ratio`: Price-to-Earnings ratio (from `YahooFinance/get_stock_insights` or calculated).
    *   `ps_ratio`: Price-to-Sales ratio.
    *   `pb_ratio`: Price-to-Book ratio.
    *   `dividend_yield`: (from `YahooFinance/get_stock_insights`).
    *   `analyst_target_price_mean`: Mean target price from analysts.
    *   `analyst_rating_consensus`: e.g., BUY, HOLD, SELL, Strong BUY (converted to numerical scale).
    *   `valuation_description`: e.g., Undervalued, Overvalued, Fairly Valued (from `YahooFinance/get_stock_insights.instrumentInfo.valuation`, converted to numerical/categorical).

*   **D. News & Sentiment Indicators:**
    *   `news_sentiment_score_stock`: Sentiment score derived from company-specific news (`YahooFinance/get_stock_insights.sigDevs` and `YahooFinance/get_stock_what_analyst_are_saying.abstracts`). This will require an NLP component (see Data Preprocessing).
    *   `news_volume_stock`: Number of significant news items/reports in the last N days.

*   **E. Macroeconomic & World Event Indicators:**
    *   `gdp_growth_rate_country`: GDP growth for the stock's primary market country (from DataBank).
    *   `inflation_rate_country`: Inflation rate for the stock's primary market country (from DataBank).
    *   `interest_rate_country`: Central bank interest rate for the stock's primary market country (from DataBank).
    *   `geopolitical_risk_factor_sector_country`: A qualitative or derived quantitative score representing impact of major world events (e.g., wars, tariffs) on the stock's sector/country. (Initially, this might be a manually curated input or a simplified rule, e.g., if a major conflict impacts a region where the company has significant operations).

### 3. Data Preprocessing

1.  **Handling Missing Values:**
    *   For numerical features: Impute with mean, median, or a constant (e.g., 0 if appropriate). For time-series, forward-fill or backward-fill might be used.
    *   For categorical features: Impute with mode or a special 'missing' category.
2.  **Scaling Numerical Features:**
    *   StandardScaler (Z-score normalization) or MinMaxScaler (to [0,1] range) to ensure features with larger values don't dominate the model.
3.  **Encoding Categorical Features:**
    *   One-Hot Encoding for nominal categories (e.g., sector, analyst rating description).
    *   Ordinal Encoding for ordinal categories (e.g., short/medium/long term outlook if ranked).
4.  **News Sentiment Analysis:**
    *   **Initial Approach:** Use a pre-trained sentiment analysis model (e.g., VADER, or a transformer-based model like FinBERT if resources allow and can be installed/accessed) to score headlines/abstracts from -1 (very negative) to +1 (very positive).
    *   Aggregate scores for a stock over a recent period (e.g., weighted average).
5.  **Date/Time Features:**
    *   Extract relevant parts if needed (e.g., day of week, month), though less critical for daily/weekly stock analysis directly in the model unless looking for seasonality.

### 4. Model Selection and Architecture

**Option 1: Rule-Based System (Initial Version - Prioritized for Simplicity & Explainability)**

*   **Description:** A system of `IF-THEN-ELSE` rules based on the engineered features. Rules would be crafted based on common financial heuristics and technical analysis principles.
*   **Example Rules:**
    *   `IF (rsi_14_day < 30 AND news_sentiment_score_stock > 0.2 AND analyst_rating_consensus == 'BUY') THEN Recommendation = BUY`
    *   `IF (price_above_200_day_sma AND 50_day_sma_slope > 0 AND news_sentiment_score_stock > 0) THEN Recommendation = BUY (Timeframe: Medium-Term)`
    *   `IF (rsi_14_day > 70 AND valuation_description == 'Overvalued') THEN Recommendation = SELL`
    *   `IF (geopolitical_risk_factor_sector_country == 'HIGH' AND stock_exposure_to_region > 0.5) THEN Recommendation = HOLD/SELL (pending further analysis)`
*   **Pros:** Highly explainable (justification is the rule that fired), easier to implement and debug initially.
*   **Cons:** Can become complex to manage as rules grow, may not capture subtle patterns, requires domain expertise to define effective rules.

**Option 2: Classical Machine Learning Model (Future Enhancement or Parallel Track)**

*   **Model Type:** Classification model (e.g., Random Forest, Gradient Boosting Machines like XGBoost/LightGBM, Support Vector Machines).
    *   **Target Variable:** BUY (1), HOLD (0), SELL (-1). Or, predict future price movement direction/magnitude which is then translated to a recommendation.
*   **Training Data:** This is the most challenging part. Would require labeling historical data (e.g., if a stock price increased by X% in Y days after a certain set of features, label it as BUY). This often involves defining a forward-looking window and a success criterion.
*   **Pros:** Can learn complex patterns from data, potentially higher accuracy if well-trained.
*   **Cons:** Requires significant labeled historical data, less directly explainable (though techniques like SHAP values can help), prone to overfitting, needs careful backtesting.

**Hybrid Approach (Recommended Long-Term):**

*   Use ML models to generate initial scores or probabilities for BUY/HOLD/SELL.
*   Use a rule-based layer on top to refine these suggestions, incorporate non-modelable factors (e.g., very recent critical news not yet in sentiment scores), and generate justifications.

**Initial Focus:** Implement a **Rule-Based System (Option 1)**. This allows for quicker development and provides inherent explainability for the justifications.

### 5. Recommendation Logic and Output Generation

1.  **Input:** For each stock, the AI engine receives the preprocessed feature set.
2.  **Rule Evaluation (for Rule-Based System):**
    *   The feature set is passed through the defined rules.
    *   A scoring system might be needed if multiple rules fire, or a priority system for rules.
3.  **Determining Recommendation (BUY/HOLD/SELL):**
    *   Based on the outcome of the rule evaluation.
4.  **Determining Confidence Score:**
    *   For a rule-based system, this could be based on the strength/number of rules supporting the decision, or a predefined confidence for each rule.
    *   E.g., if multiple strong buy signals align, confidence is high.
5.  **Determining Timeframe:**
    *   Some rules might inherently suggest a timeframe (e.g., short-term indicators vs. long-term fundamentals).
    *   Default to medium-term if not specified by rules.
6.  **Generating Justification:**
    *   The primary rule(s) that triggered the recommendation will form the basis of the justification.
    *   E.g., "Recommendation: BUY. Justification: Strong positive momentum (RSI < 30, above 50-day SMA) and positive recent news sentiment."

### 6. Output Format (per stock)

The AI engine will output a structured response for each stock, for example, a JSON object:

```json
{
  "ticker": "AAPL",
  "recommendation": "BUY", // BUY, HOLD, SELL
  "confidence_score": 0.75, // 0.0 to 1.0
  "timeframe": "Medium-Term", // Short-Term, Medium-Term, Long-Term
  "justification": "Stock shows strong upward momentum (RSI: 65, MACD crossover positive) and recent analyst upgrades. Valuation appears reasonable compared to sector peers.",
  "contributing_factors": [
    {"feature": "RSI_14_day", "value": 65, "impact": "Positive"},
    {"feature": "MACD_signal", "value": "Positive Crossover", "impact": "Positive"},
    {"feature": "Analyst_Rating_Consensus", "value": "BUY", "impact": "Positive"},
    {"feature": "Valuation_Description", "value": "Fairly Valued", "impact": "Neutral"}
  ]
}
```

(The `contributing_factors` part is an enhancement for more detailed explainability).

### 7. Implementation Plan

1.  **Develop Feature Engineering Functions:** In `src/ai_engine/feature_engineering.py`.
2.  **Implement Sentiment Analysis Module:** In `src/ai_engine/sentiment_analyzer.py` (initially simple, e.g., VADER).
3.  **Define and Implement Rule-Based Logic:** In `src/ai_engine/rule_engine.py`.
4.  **Create Main AI Engine Orchestrator:** In `src/ai_engine/main_analyzer.py` that takes data from `data_aggregator.py`, preprocesses it, runs it through the rule engine, and formats the output.
5.  **Directory Structure:** Create `src/ai_engine/`.

This design focuses on a pragmatic, explainable initial version while laying the groundwork for more sophisticated ML models in the future.
