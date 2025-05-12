# src/ai_engine/main_analyzer.py

from flask import current_app
from .feature_engineering import FeatureEngineer
from .sentiment_analyzer import SentimentAnalyzer
from .rule_engine import RuleEngine

class MainAnalyzer:
    def __init__(self):
        self.feature_engineer = FeatureEngineer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.rule_engine = RuleEngine()
        current_app.logger.info("MainAnalyzer initialized with all sub-modules.")

    def analyze_portfolio_holdings(self, aggregated_data_list):
        """
        Analyzes a list of aggregated stock data and generates recommendations.
        :param aggregated_data_list: A list of dictionaries, where each dictionary 
                                     is the output from DataAggregator for one stock.
        :return: A list of recommendation dictionaries.
        """
        all_recommendations = []
        if not aggregated_data_list:
            current_app.logger.warning("MainAnalyzer received empty aggregated_data_list.")
            return []

        current_app.logger.info(f"MainAnalyzer starting analysis for {len(aggregated_data_list)} holdings.")

        for stock_data in aggregated_data_list:
            ticker = stock_data.get("ticker", "Unknown Ticker")
            current_app.logger.info(f"Processing analysis for ticker: {ticker}")

            if not stock_data or stock_data.get("errors"): # Check if data aggregator had issues
                # If data aggregator already reported errors, we might not proceed or return a default error recommendation
                # For now, we log and try to proceed if some data is present, but feature engineering might fail.
                current_app.logger.warning(f"Aggregated data for {ticker} has errors or is incomplete: {stock_data.get("errors")}")
                # Decide if we should skip or attempt partial analysis
                # For now, let's create a default error recommendation if critical data is missing
                if not stock_data.get("yahoo_finance", {}).get("chart") and not stock_data.get("yahoo_finance", {}).get("insights"):
                    all_recommendations.append({
                        "ticker": ticker,
                        "recommendation": "ERROR",
                        "confidence_score": 0.0,
                        "timeframe": "N/A",
                        "justification": f"Could not retrieve essential market data for {ticker}. Analysis cannot proceed. Errors: {stock_data.get("errors")}"
                    })
                    current_app.logger.error(f"Skipping analysis for {ticker} due to missing critical data.")
                    continue

            # 1. Feature Engineering
            try:
                features = self.feature_engineer.extract_features(stock_data)
                if features.get("errors"):
                    current_app.logger.warning(f"Feature engineering for {ticker} resulted in errors: {features["errors"]}")
                    # Depending on severity, we might still proceed or create an error recommendation
            except Exception as e:
                current_app.logger.error(f"Critical error during feature engineering for {ticker}: {e}")
                all_recommendations.append({
                    "ticker": ticker,
                    "recommendation": "ERROR",
                    "confidence_score": 0.0,
                    "timeframe": "N/A",
                    "justification": f"Critical error during feature engineering for {ticker}: {str(e)}"
                })
                continue # Skip to next stock
            
            # 2. Sentiment Analysis
            try:
                sentiments = self.sentiment_analyzer.analyze_stock_news_sentiment(stock_data)
                if sentiments.get("errors"):
                     current_app.logger.warning(f"Sentiment analysis for {ticker} resulted in errors: {sentiments["errors"]}")
            except Exception as e:
                current_app.logger.error(f"Critical error during sentiment analysis for {ticker}: {e}")
                # We might proceed with default sentiment or create an error recommendation
                # For now, let rule engine handle potentially missing sentiment
                sentiments = {} # Default to empty if error

            # 3. Rule-Based Recommendation
            try:
                recommendation_result = self.rule_engine.generate_recommendation(features, sentiments)
                all_recommendations.append(recommendation_result)
            except Exception as e:
                current_app.logger.error(f"Critical error during rule engine processing for {ticker}: {e}")
                all_recommendations.append({
                    "ticker": ticker,
                    "recommendation": "ERROR",
                    "confidence_score": 0.0,
                    "timeframe": "N/A",
                    "justification": f"Critical error during recommendation generation for {ticker}: {str(e)}"
                })
                continue # Skip to next stock

        current_app.logger.info(f"MainAnalyzer finished analysis. Generated {len(all_recommendations)} recommendations.")
        return all_recommendations

# Example usage (for testing - requires Flask app context for logger and sub-modules)
# if __name__ == "__main__":
#     # Mock aggregated_data_list
#     # Needs to be run within a Flask app context
#     pass

