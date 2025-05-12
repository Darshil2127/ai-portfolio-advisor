# src/ai_engine/rule_engine.py

from flask import current_app

class RuleEngine:
    def __init__(self):
        # In a more advanced system, rules could be loaded from a config file or database
        pass

    def generate_recommendation(self, stock_features, stock_sentiments):
        """
        Generates a recommendation based on a set of rules applied to stock features and sentiments.
        :param stock_features: Dictionary of engineered features for a stock.
        :param stock_sentiments: Dictionary of sentiment scores for the stock.
        :return: A dictionary containing the recommendation, confidence, timeframe, and justification.
        """
        ticker = stock_features.get("ticker", "Unknown")
        current_app.logger.info(f"Starting rule-based recommendation for {ticker}")

        recommendation = "HOLD"  # Default recommendation
        confidence = 0.5  # Default confidence (neutral)
        timeframe = "Medium-Term" # Default timeframe
        justification_points = []

        # --- Rule Evaluation --- 
        # These rules are examples and should be expanded and refined based on financial expertise and testing.

        # Rule 1: Strong Buy Signal (RSI Oversold + Positive Sentiment + Good Fundamentals)
        try:
            rsi = stock_features.get("rsi_14_day")
            overall_sentiment = stock_sentiments.get("overall_avg_sentiment", 0.0)
            # Assuming analyst ratings are converted to a numerical score or simple category
            # For simplicity, let's use valuation description for now
            valuation = stock_features.get("valuation_description", "").lower()
            sma_20 = stock_features.get("sma_20_day")
            sma_50 = stock_features.get("sma_50_day")
            current_price = stock_features.get("current_price")

            # Basic BUY rules
            if rsi is not None and rsi < 35 and overall_sentiment > 0.1:
                if valuation in ["undervalued", "significantly undervalued"]:
                    recommendation = "BUY"
                    confidence = 0.75
                    justification_points.append("RSI indicates oversold conditions (<35).")
                    justification_points.append(f"Positive overall news sentiment ({overall_sentiment:.2f}).")
                    justification_points.append(f"Valuation appears attractive ({valuation}).")
                    timeframe = "Medium-Term"
            
            elif current_price and sma_20 and sma_50 and current_price > sma_20 and sma_20 > sma_50 and overall_sentiment > 0.05:
                recommendation = "BUY"
                confidence = 0.70
                justification_points.append("Positive short-term price trend (Price > SMA20 > SMA50).")
                justification_points.append(f"Slightly positive news sentiment ({overall_sentiment:.2f}).")
                timeframe = "Short-Term"

            # Basic SELL rules
            if rsi is not None and rsi > 65 and overall_sentiment < -0.1:
                if valuation in ["overvalued", "significantly overvalued"]:
                    recommendation = "SELL"
                    confidence = 0.75
                    justification_points.append("RSI indicates overbought conditions (>65).")
                    justification_points.append(f"Negative overall news sentiment ({overall_sentiment:.2f}).")
                    justification_points.append(f"Valuation appears stretched ({valuation}).")
                    timeframe = "Medium-Term"

            elif current_price and sma_20 and sma_50 and current_price < sma_20 and sma_20 < sma_50 and overall_sentiment < -0.05:
                recommendation = "SELL"
                confidence = 0.70
                justification_points.append("Negative short-term price trend (Price < SMA20 < SMA50).")
                justification_points.append(f"Slightly negative news sentiment ({overall_sentiment:.2f}).")
                timeframe = "Short-Term"

            # Hold conditions (if no strong buy/sell, or conflicting signals)
            if not justification_points: # If no strong signals fired
                justification_points.append("Market conditions and indicators appear neutral or mixed for this stock currently.")
                confidence = 0.5 # Reset confidence for HOLD if it wasn't changed by a rule
                if recommendation != "HOLD": # If a weak rule changed it, but no justification points, revert to HOLD
                    recommendation = "HOLD"

        except Exception as e:
            current_app.logger.error(f"Error during rule evaluation for {ticker}: {e}")
            justification_points.append(f"Error in rule engine: {str(e)}")
            recommendation = "HOLD" # Default to HOLD on error
            confidence = 0.3 # Lower confidence due to error

        final_justification = " ".join(justification_points)
        if not final_justification:
            final_justification = "No specific strong signals identified; current recommendation is based on a neutral outlook."

        result = {
            "ticker": ticker,
            "recommendation": recommendation,
            "confidence_score": round(confidence, 2),
            "timeframe": timeframe,
            "justification": final_justification,
            "raw_features_considered": { # For debugging or advanced display
                "rsi_14_day": stock_features.get("rsi_14_day"),
                "overall_sentiment": stock_sentiments.get("overall_avg_sentiment", 0.0),
                "valuation_description": stock_features.get("valuation_description")
            }
        }
        current_app.logger.info(f"Generated recommendation for {ticker}: {result["recommendation"]} with confidence {result["confidence_score"]}")
        return result

# Example usage (for testing - requires Flask app context for logger)
# if __name__ == "__main__":
#     # Mock stock_features and stock_sentiments
#     # Needs to be run within a Flask app context
#     pass

