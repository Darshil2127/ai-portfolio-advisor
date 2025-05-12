# src/ai_engine/main_analyzer.py

from flask import current_app
from .feature_engineering import FeatureEngineer
from .sentiment_analyzer import SentimentAnalyzer
from .rule_engine import RuleEngine
from src.data_services.data_aggregator import DataAggregator # Assuming this is correctly placed

class MainAnalyzer:
    def __init__(self):
        self.feature_engineer = FeatureEngineer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.rule_engine = RuleEngine()
        self.data_aggregator = DataAggregator() # Instantiate the aggregator
        current_app.logger.info("MainAnalyzer initialized.")

    def analyze_portfolio_and_generate_advice(self, portfolio_data):
        """
        Main analysis pipeline.
        1. Fetches market data for each stock in the portfolio.
        2. Performs feature engineering.
        3. Analyzes sentiment from news/opinions.
        4. Applies rule engine to generate advice.
        """
        advice_for_portfolio = []
        if not portfolio_data:
            current_app.logger.warning("Portfolio data is empty. Cannot generate advice.")
            return {"error": "Portfolio data is empty."}

        for holding in portfolio_data:
            ticker = holding.get("symbol")
            if not ticker:
                current_app.logger.warning(f"Skipping holding due to missing symbol: {holding}")
                continue
            
            current_app.logger.info(f"Analyzing ticker: {ticker}")
            
            # 1. Fetch aggregated market data
            # Assuming country_code is available or can be defaulted (e.g., from user profile or stock exchange)
            country_code_for_gdp = holding.get("country_code", "USA") # Example default
            stock_data = self.data_aggregator.get_all_data_for_stock(ticker, country_code_for_gdp)

            if not stock_data or stock_data.get("errors"): # Check if stock_data itself is None or has an error key
                current_app.logger.warning(f"Aggregated data for {ticker} has errors or is incomplete: {stock_data.get('errors') if stock_data else 'No data returned'}")
                advice_for_portfolio.append({"symbol": ticker, "error": "Failed to retrieve complete market data."})
                continue

            # 2. Feature Engineering (using fetched data)
            # This part would need actual data to work on; for now, it might receive stubbed data
            engineered_features = self.feature_engineer.generate_features(stock_data)
            
            # 3. Sentiment Analysis (using fetched news/opinions)
            # This part also needs actual data; for now, it might receive stubbed data
            sentiment_score = self.sentiment_analyzer.analyze_sentiment(stock_data.get("analyst_opinions", []))
            
            # 4. Rule Engine
            advice_details = self.rule_engine.generate_advice(ticker, engineered_features, sentiment_score, stock_data)
            current_app.logger.info(f"Generated advice for {ticker}: {advice_details.get('action', 'N/A')}")
            advice_for_portfolio.append(advice_details)

        return advice_for_portfolio

