# src/ai_engine/sentiment_analyzer.py

from flask import current_app
# Ensure vaderSentiment is installed and in requirements.txt
# pip install vaderSentiment
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        current_app.logger.info("SentimentAnalyzer initialized with VADER.")

    def analyze_sentiment(self, texts):
        """
        Analyzes the sentiment of a given text or list of texts (e.g., news headlines, analyst opinions).
        Returns an aggregated sentiment score (e.g., average compound score).
        For stubbed data, this might receive an empty list or list of stubbed opinions.
        """
        if not texts:
            current_app.logger.info("No texts provided for sentiment analysis.")
            return 0.0  # Neutral sentiment if no text

        if isinstance(texts, str):
            texts = [texts] # Convert single string to list
        
        compound_scores = []
        try:
            for text_item in texts: # texts could be a list of strings or a list of dicts
                actual_text = ""
                if isinstance(text_item, dict):
                    # Try to extract text from common keys if it's a list of opinion dicts
                    actual_text = text_item.get("abstract", text_item.get("headline", text_item.get("title", "")))
                elif isinstance(text_item, str):
                    actual_text = text_item
                
                if actual_text and isinstance(actual_text, str):
                    vs = self.analyzer.polarity_scores(actual_text)
                    compound_scores.append(vs["compound"])
                else:
                    current_app.logger.debug(f"Skipping non-string or empty item in sentiment analysis: {text_item}")

        except Exception as e:
            # Ensure text_excerpt is well-defined for logging
            text_excerpt = "Error processing texts list" 
            if texts and isinstance(texts, list) and len(texts) > 0:
                 first_item_str = str(texts[0])
                 text_excerpt = first_item_str[:100] + ("..." if len(first_item_str) > 100 else "")
            elif isinstance(texts, str):
                 text_excerpt = texts[:100] + ("..." if len(texts) > 100 else "")
            
            current_app.logger.error(f"Error during sentiment analysis for input starting with: 	'{text_excerpt}	' - Error: {e}")
            return 0.0 # Neutral sentiment on error

        if not compound_scores:
            current_app.logger.info("No valid text found for sentiment scoring after processing.")
            return 0.0
        
        average_compound = sum(compound_scores) / len(compound_scores)
        current_app.logger.info(f"Aggregated sentiment score: {average_compound:.4f} from {len(compound_scores)} texts.")
        return average_compound

