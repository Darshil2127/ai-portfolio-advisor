# src/ai_engine/rule_engine.py

from flask import current_app

class RuleEngine:
    def __init__(self):
        current_app.logger.info("RuleEngine initialized.")
        # Define thresholds or more complex rule configurations here if needed
        self.thresholds = {
            "rsi_oversold": 30,
            "rsi_overbought": 70,
            "sentiment_positive_strong": 0.5,
            "sentiment_negative_strong": -0.5,
            "pe_ratio_low_threshold": 15, # Example: Lower P/E might indicate undervaluation
            "pe_ratio_high_threshold": 25, # Example: Higher P/E might indicate overvaluation
            "moving_avg_short_vs_long_buy_signal_margin": 1.02, # e.g. short term MA is 2% above long term MA
            "moving_avg_short_vs_long_sell_signal_margin": 0.98 # e.g. short term MA is 2% below long term MA
        }

    def generate_advice(self, ticker, engineered_features, sentiment_score, market_data):
        """
        Applies a set of rules to the engineered features and sentiment score 
        to generate buy/sell/hold advice for a given stock.
        `market_data` is the aggregated data which might include price, P/E, etc.
        `engineered_features` might include RSI, moving averages, etc.
        """
        advice = "Hold"
        reason = "Default recommendation; no strong signals detected."
        confidence_score = 0.5 # Neutral confidence

        # --- Basic Price & Volume checks (from market_data if available) ---
        # Example: Check for unusual volume spikes if volume data is present
        # current_price = market_data.get("chart", {}).get("meta", {}).get("regularMarketPrice")
        # current_volume = market_data.get("chart", {}).get("meta", {}).get("regularMarketVolume")
        # historical_avg_volume = engineered_features.get("average_volume_30d") # Assuming this feature exists
        # if current_volume and historical_avg_volume and current_volume > historical_avg_volume * 2:
        #     reason += " Significant volume spike detected."
        #     confidence_score = min(1.0, confidence_score + 0.1)

        # --- Sentiment-based rules ---
        if sentiment_score > self.thresholds["sentiment_positive_strong"]:
            advice = "Consider Buy"
            reason = "Strong positive sentiment detected from news and analyst opinions."
            confidence_score = 0.7
        elif sentiment_score < self.thresholds["sentiment_negative_strong"]:
            advice = "Consider Sell"
            reason = "Strong negative sentiment detected from news and analyst opinions."
            confidence_score = 0.7

        # --- Technical Indicator-based rules (from engineered_features) ---
        rsi = engineered_features.get("rsi_14d")
        if rsi is not None:
            if rsi < self.thresholds["rsi_oversold"]:
                if advice == "Consider Sell": # Conflicting signals
                    advice = "Hold"
                    reason = f"Conflicting signals: RSI ({rsi:.2f}) indicates oversold, but sentiment is negative. Recommending Hold."
                    confidence_score = 0.4
                else:
                    advice = "Buy"
                    reason = f"RSI ({rsi:.2f}) indicates the stock may be oversold."
                    confidence_score = max(confidence_score, 0.75)
            elif rsi > self.thresholds["rsi_overbought"]:
                if advice == "Consider Buy": # Conflicting signals
                    advice = "Hold"
                    reason = f"Conflicting signals: RSI ({rsi:.2f}) indicates overbought, but sentiment is positive. Recommending Hold."
                    confidence_score = 0.4
                else:
                    advice = "Sell"
                    reason = f"RSI ({rsi:.2f}) indicates the stock may be overbought."
                    confidence_score = max(confidence_score, 0.75)
        
        # --- Moving Average Crossover (from engineered_features) ---
        # sma_short = engineered_features.get("sma_20d")
        # sma_long = engineered_features.get("sma_50d")
        # if sma_short and sma_long:
        #     if sma_short > sma_long * self.thresholds["moving_avg_short_vs_long_buy_signal_margin"]:
        #         # Golden Cross (simplified)
        #         if advice == "Sell" or advice == "Consider Sell":
        #             advice = "Hold"
        #             reason = f"Conflicting signals: SMA crossover suggests bullish, but other indicators bearish. Hold."
        #             confidence_score = 0.4
        #         else:
        #             advice = "Buy"
        #             reason += " Short-term moving average crossed above long-term, potential bullish signal."
        #             confidence_score = min(1.0, confidence_score + 0.15)
        #     elif sma_short < sma_long * self.thresholds["moving_avg_short_vs_long_sell_signal_margin"]:
        #         # Death Cross (simplified)
        #         if advice == "Buy" or advice == "Consider Buy":
        #             advice = "Hold"
        #             reason = f"Conflicting signals: SMA crossover suggests bearish, but other indicators bullish. Hold."
        #             confidence_score = 0.4
        #         else:
        #             advice = "Sell"
        #             reason += " Short-term moving average crossed below long-term, potential bearish signal."
        #             confidence_score = min(1.0, confidence_score + 0.15)

        # --- Fundamental data based rules (example, if P/E ratio is available in market_data -> insights) ---
        # pe_ratio = market_data.get("insights", {}).get("valuation", {}).get("peRatio") # Path might vary
        # if pe_ratio:
        #     if pe_ratio < self.thresholds["pe_ratio_low_threshold"] and sentiment_score > 0:
        #         reason += f" Potentially undervalued with P/E of {pe_ratio:.2f} and positive sentiment."
        #         if advice == "Hold" or advice == "Consider Buy": advice = "Buy"
        #         confidence_score = min(1.0, confidence_score + 0.1)
        #     elif pe_ratio > self.thresholds["pe_ratio_high_threshold"] and sentiment_score < 0:
        #         reason += f" Potentially overvalued with P/E of {pe_ratio:.2f} and negative sentiment."
        #         if advice == "Hold" or advice == "Consider Sell": advice = "Sell"
        #         confidence_score = min(1.0, confidence_score + 0.1)

        result = {
            "symbol": ticker,
            "recommendation": advice,
            "reason": reason.strip(),
            "confidence_score": round(confidence_score, 2),
            "details": {
                "rsi_14d": f"{rsi:.2f}" if rsi is not None else "N/A",
                "sentiment_score": f"{sentiment_score:.4f}",
                # Add other relevant features/data points used in decision making
            }
        }
        current_app.logger.info(f"Generated recommendation for {ticker}: {result['recommendation']} with confidence {result['confidence_score']}")
        return result

