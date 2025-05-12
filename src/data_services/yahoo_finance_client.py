# src/data_services/yahoo_finance_client.py

import sys
from flask import current_app

# Ensure the data_api module can be found
sys.path.append("/opt/.manus/.sandbox-runtime")
from data_api import ApiClient

class YahooFinanceClient:
    def __init__(self):
        self.client = ApiClient()

    def get_stock_chart_data(self, symbol, interval="1d", range="1y", region="US", include_adjusted_close=True):
        """Fetches historical stock chart data."""
        try:
            params = {
                "symbol": symbol,
                "interval": interval,
                "range": range,
                "region": region,
                "includeAdjustedClose": include_adjusted_close
            }
            current_app.logger.info(f"Fetching stock chart data for {symbol} with params: {params}")
            response = self.client.call_api("YahooFinance/get_stock_chart", query=params)
            # Basic validation of response structure
            if response and response.get("chart") and response["chart"].get("result") and response["chart"]["result"][0]:
                current_app.logger.info(f"Successfully fetched stock chart data for {symbol}")
                return response["chart"]["result"][0]
            else:
                current_app.logger.error(f"Unexpected response structure for get_stock_chart {symbol}: {response}")
                return {"error": "Invalid data structure from API for get_stock_chart", "details": response}
        except Exception as e:
            current_app.logger.error(f"Error fetching stock chart data for {symbol}: {e}")
            return {"error": str(e)}

    def get_stock_insights_data(self, symbol, region="US"): # region is not in API spec for insights, but good to keep consistent if other YF APIs use it
        """Fetches stock insights data."""
        try:
            params = {
                "symbol": symbol
                # "region": region # Not a parameter for get_stock_insights based on provided API docs
            }
            current_app.logger.info(f"Fetching stock insights for {symbol} with params: {params}")
            response = self.client.call_api("YahooFinance/get_stock_insights", query=params)
            if response and response.get("finance") and response["finance"].get("result"):
                current_app.logger.info(f"Successfully fetched stock insights for {symbol}")
                return response["finance"]["result"]
            else:
                current_app.logger.error(f"Unexpected response structure for get_stock_insights {symbol}: {response}")
                return {"error": "Invalid data structure from API for get_stock_insights", "details": response}
        except Exception as e:
            current_app.logger.error(f"Error fetching stock insights for {symbol}: {e}")
            return {"error": str(e)}

    def get_analyst_opinions(self, symbol, region="US", lang="en-US"):
        """Fetches what analysts are saying about a stock."""
        try:
            params = {
                "symbol": symbol,
                "region": region,
                "lang": lang
            }
            current_app.logger.info(f"Fetching analyst opinions for {symbol} with params: {params}")
            response = self.client.call_api("YahooFinance/get_stock_what_analyst_are_saying", query=params)
            if response and response.get("result"):
                current_app.logger.info(f"Successfully fetched analyst opinions for {symbol}")
                return response["result"]
            else:
                current_app.logger.error(f"Unexpected response structure for get_stock_what_analyst_are_saying {symbol}: {response}")
                return {"error": "Invalid data structure from API for get_stock_what_analyst_are_saying", "details": response}
        except Exception as e:
            current_app.logger.error(f"Error fetching analyst opinions for {symbol}: {e}")
            return {"error": str(e)}

# Example usage (for testing purposes, not part of the Flask app directly here):
# if __name__ == "__main__":
#     # This part needs a Flask app context to run current_app.logger
#     # For standalone testing, you might replace current_app.logger with print()
#     # and instantiate ApiClient directly without Flask context.
#     pass

