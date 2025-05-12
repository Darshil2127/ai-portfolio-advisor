# src/ai_engine/sentiment_analyzer.py

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from flask import current_app

class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def get_sentiment_score(self, text):
        """
        Calculates the compound sentiment score for a given text.
        Score ranges from -1 (most negative) to +1 (most positive).
        """
        if not text or not isinstance(text, str):
            return 0.0 # Neutral for empty or invalid input
        
        try:
            vs = self.analyzer.polarity_scores(text)
            # The compound score is a normalized, weighted composite score.
            return vs["compound"]
        except Exception as e:
            current_app.logger.error(f"Error during sentiment analysis for text 
{text[:100]}...
: {e}")
            return 0.0 # Return neutral on error

    def analyze_stock_news_sentiment(self, aggregated_stock_data):
        """
        Analyzes sentiment for news related to a single stock from aggregated data.
        :param aggregated_stock_data: A dictionary from DataAggregator for one stock.
        :return: A dictionary with average sentiment scores for different news types.
        """
        sentiments = {
            "overall_avg_sentiment": 0.0,
            "significant_developments_avg_sentiment": 0.0,
            "analyst_abstracts_avg_sentiment": 0.0,
            "errors": []
        }
        all_scores = []
        
        current_app.logger.info(f"Starting sentiment analysis for {aggregated_stock_data.get("ticker")}")

        # 1. Sentiment from Significant Developments (YahooFinance Insights sigDevs)
        sig_devs_scores = []
        sig_devs = aggregated_stock_data.get("yahoo_finance", {}).get("insights", {}).get("sigDevs", [])
        if sig_devs:
            for dev in sig_devs:
                headline = dev.get("headline")
                if headline:
                    score = self.get_sentiment_score(headline)
                    sig_devs_scores.append(score)
                    all_scores.append(score)
            if sig_devs_scores:
                sentiments["significant_developments_avg_sentiment"] = sum(sig_devs_scores) / len(sig_devs_scores)
        else:
            current_app.logger.info(f"No significant developments found for sentiment analysis for {aggregated_stock_data.get("ticker")}")

        # 2. Sentiment from Analyst Opinion Abstracts (YahooFinance get_stock_what_analyst_are_saying)
        analyst_abstract_scores = []
        analyst_reports_data = aggregated_stock_data.get("yahoo_finance", {}).get("analyst_opinions", [])
        # The response is a list, usually with one item containing "hits"
        if analyst_reports_data and isinstance(analyst_reports_data, list) and len(analyst_reports_data) > 0:
            hits = analyst_reports_data[0].get("hits", [])
            if hits:
                for report in hits:
                    abstract = report.get("abstract")
                    if abstract:
                        score = self.get_sentiment_score(abstract)
                        analyst_abstract_scores.append(score)
                        all_scores.append(score)
                if analyst_abstract_scores:
                    sentiments["analyst_abstracts_avg_sentiment"] = sum(analyst_abstract_scores) / len(analyst_abstract_scores)
            else:
                current_app.logger.info(f"No analyst report hits found for sentiment analysis for {aggregated_stock_data.get("ticker")}")
        else:
            current_app.logger.info(f"No analyst reports data found for sentiment analysis for {aggregated_stock_data.get("ticker")}")

        if all_scores:
            sentiments["overall_avg_sentiment"] = sum(all_scores) / len(all_scores)
        
        current_app.logger.info(f"Finished sentiment analysis for {aggregated_stock_data.get("ticker")}. Overall: {sentiments["overall_avg_sentiment"]}")
        return sentiments

# Example usage (for testing - requires Flask app context for logger)
# if __name__ == "__main__":
#     # Mock aggregated_stock_data
#     # Needs to be run within a Flask app context
#     pass

