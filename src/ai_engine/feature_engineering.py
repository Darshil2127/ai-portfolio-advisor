# src/ai_engine/feature_engineering.py

import pandas as pd
import numpy as np
from flask import current_app

class FeatureEngineer:
    def __init__(self):
        pass

    def calculate_sma(self, prices, window):
        """Calculates Simple Moving Average."""
        if len(prices) < window:
            return None
        return pd.Series(prices).rolling(window=window).mean().iloc[-1]

    def calculate_rsi(self, prices, window=14):
        """Calculates Relative Strength Index."""
        if len(prices) < window + 1:
            return None
        delta = pd.Series(prices).diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        if loss == 0: # Avoid division by zero if all losses are zero
            return 100 if gain > 0 else 50 # Or handle as per specific strategy
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if isinstance(rsi, pd.Series) else rsi # rsi can be a series or a float

    def calculate_macd(self, prices, short_window=12, long_window=26, signal_window=9):
        """Calculates MACD, MACD Signal, and MACD Histogram."""
        if len(prices) < long_window:
            return None, None, None
        
        prices_series = pd.Series(prices)
        short_ema = prices_series.ewm(span=short_window, adjust=False).mean()
        long_ema = prices_series.ewm(span=long_window, adjust=False).mean()
        
        macd_line = short_ema - long_ema
        signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
        macd_histogram = macd_line - signal_line
        
        return macd_line.iloc[-1], signal_line.iloc[-1], macd_histogram.iloc[-1]

    def extract_features(self, aggregated_stock_data):
        """
        Extracts and calculates features for a single stock from aggregated data.
        :param aggregated_stock_data: A dictionary containing data from DataAggregator for one stock.
        :return: A dictionary of features.
        """
        features = {
            "ticker": aggregated_stock_data.get("ticker"),
            "errors": []
        }
        current_app.logger.info(f"Starting feature engineering for {features['ticker']}")

        # A. Portfolio-Context Features (Example - can be expanded)
        # features["current_holding_percentage"] = ... (requires total portfolio value)
        # features["unrealized_pnl_percentage"] = ... (requires purchase_price and current_price)

        # B. Price & Volume Technical Indicators
        chart_data = aggregated_stock_data.get("yahoo_finance", {}).get("chart", {})
        if chart_data and chart_data.get("timestamp") and chart_data.get("indicators", {}).get("quote"):
            try:
                close_prices = chart_data["indicators"]["quote"][0].get("close", [])
                # Filter out None values which can break calculations
                close_prices = [p for p in close_prices if p is not None]

                if len(close_prices) > 0:
                    features["current_price"] = close_prices[-1]
                    features["sma_20_day"] = self.calculate_sma(close_prices, 20)
                    features["sma_50_day"] = self.calculate_sma(close_prices, 50)
                    features["sma_200_day"] = self.calculate_sma(close_prices, 200)
                    features["rsi_14_day"] = self.calculate_rsi(close_prices, 14)
                    macd, macd_signal, macd_hist = self.calculate_macd(close_prices)
                    features["macd_line"] = macd
                    features["macd_signal"] = macd_signal
                    features["macd_histogram"] = macd_hist
                else:
                    features["errors"].append("No close prices available for technical indicators.")
            except Exception as e:
                current_app.logger.error(f"Error calculating technical indicators for {features['ticker']}: {e}")
                features["errors"].append(f"Error in technical indicators: {str(e)}")
        else:
            features["errors"].append("Chart data missing or incomplete for technical indicators.")

        # C. Fundamental & Valuation Metrics (from YahooFinance Insights)
        insights = aggregated_stock_data.get("yahoo_finance", {}).get("insights", {})
        if insights:
            try:
                # Basic financial ratios (often in summaryDetail or defaultKeyStatistics)
                # The exact path depends on the API response structure which can be nested.
                # For now, we'll assume some direct paths or use .get() for safety.
                # This section needs to be robust to missing keys in the API response.
                summary_detail = insights.get("summaryDetail", {})
                features["pe_ratio_trailing"] = summary_detail.get("trailingPE", {}).get("raw")
                features["forward_pe_ratio"] = summary_detail.get("forwardPE", {}).get("raw")
                features["dividend_yield"] = summary_detail.get("dividendYield", {}).get("raw") 
                features["market_cap"] = summary_detail.get("marketCap", {}).get("raw")
                
                key_stats = insights.get("defaultKeyStatistics", {})
                features["price_to_book"] = key_stats.get("priceToBook", {}).get("raw")
                features["enterprise_value"] = key_stats.get("enterpriseValue", {}).get("raw")

                # Analyst recommendations
                recommendation = insights.get("recommendationTrend", {}).get("trend", [])
                if recommendation:
                    latest_rec = recommendation[0] # Assuming the first is the most recent or relevant
                    features["analyst_strong_buy"] = latest_rec.get("strongBuy")
                    features["analyst_buy"] = latest_rec.get("buy")
                    features["analyst_hold"] = latest_rec.get("hold")
                    features["analyst_sell"] = latest_rec.get("sell")
                    features["analyst_strong_sell"] = latest_rec.get("strongSell")
                
                # Valuation from insights
                valuation_info = insights.get("instrumentInfo", {}).get("valuation", {})
                features["valuation_description"] = valuation_info.get("description") # e.g., "Undervalued"
                features["valuation_discount"] = valuation_info.get("discount") # e.g., "-15%"

            except Exception as e:
                current_app.logger.error(f"Error extracting fundamental/valuation for {features['ticker']}: {e}")
                features["errors"].append(f"Error in fundamental/valuation: {str(e)}")
        else:
            features["errors"].append("YahooFinance insights data missing for fundamentals.")

        # D. News & Sentiment Indicators (Placeholder - Sentiment will be done by SentimentAnalyzer)
        # features["news_sentiment_score_stock"] = ... (This will come from SentimentAnalyzer)
        # features["news_volume_stock"] = ... (Count of sigDevs or analyst reports)
        sig_devs = insights.get("sigDevs", [])
        features["significant_developments_count"] = len(sig_devs) if sig_devs else 0

        analyst_reports = aggregated_stock_data.get("yahoo_finance", {}).get("analyst_opinions", [])
        features["analyst_reports_count"] = len(analyst_reports[0].get("hits",[])) if analyst_reports and analyst_reports[0].get("hits") else 0

        # E. Macroeconomic & World Event Indicators (from DataBank)
        databank_data = aggregated_stock_data.get("data_bank", {})
        if databank_data:
            try:
                gdp_us_data = databank_data.get("gdp_us", {}).get("data", {})
                if gdp_us_data:
                    # Get the most recent year's GDP value (assuming years are keys)
                    latest_year_gdp = max([int(y) for y in gdp_us_data.keys() if gdp_us_data[y] is not None and y.isdigit()], default=None)
                    if latest_year_gdp:
                        features["latest_gdp_us"] = gdp_us_data.get(str(latest_year_gdp))
                
                inflation_us_cpi_data = databank_data.get("inflation_us_cpi", {}).get("data", {})
                if inflation_us_cpi_data:
                    latest_year_inflation = max([int(y) for y in inflation_us_cpi_data.keys() if inflation_us_cpi_data[y] is not None and y.isdigit()], default=None)
                    if latest_year_inflation:
                        features["latest_inflation_us_cpi"] = inflation_us_cpi_data.get(str(latest_year_inflation))
            except Exception as e:
                current_app.logger.error(f"Error extracting macroeconomic data for {features['ticker']}: {e}")
                features["errors"].append(f"Error in macroeconomic data: {str(e)}")
        else:
            features["errors"].append("DataBank macroeconomic data missing.")
        
        current_app.logger.info(f"Finished feature engineering for {features['ticker']}. Features count: {len(features) - 2}, Errors: {len(features['errors'])}")
        return features

# Example usage (for testing - requires Flask app context for logger)
# if __name__ == "__main__":
#     # Mock aggregated_stock_data similar to what DataAggregator would produce
#     # Needs to be run within a Flask app context
#     pass

