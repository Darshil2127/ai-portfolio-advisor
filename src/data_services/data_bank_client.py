# src/data_services/data_bank_client.py

import sys
from flask import current_app

# Ensure the data_api module can be found
sys.path.append("/opt/.manus/.sandbox-runtime")
from data_api import ApiClient

class DataBankClient:
    def __init__(self):
        self.client = ApiClient()

    def get_indicator_list(self, query_string=None, page=1, page_size=10):
        """Fetches a list of World Development Indicators."""
        try:
            params = {
                "page": page,
                "pageSize": page_size
            }
            if query_string:
                params["q"] = query_string
            
            current_app.logger.info(f"Fetching DataBank indicator list with params: {params}")
            response = self.client.call_api("DataBank/indicator_list", query=params)
            # Basic validation of response structure
            if response and "items" in response and "total" in response:
                current_app.logger.info(f"Successfully fetched DataBank indicator list. Total items: {response["total"]}")
                return response
            else:
                current_app.logger.error(f"Unexpected response structure for DataBank/indicator_list: {response}")
                return {"error": "Invalid data structure from API for DataBank/indicator_list", "details": response}
        except Exception as e:
            current_app.logger.error(f"Error fetching DataBank indicator list: {e}")
            return {"error": str(e)}

    def get_indicator_data(self, indicator_code, country_code):
        """Fetches data for a specific World Development Indicator and country."""
        try:
            params = {
                "indicator": indicator_code,
                "country": country_code
            }
            current_app.logger.info(f"Fetching DataBank indicator data for {indicator_code} in {country_code} with params: {params}")
            response = self.client.call_api("DataBank/indicator_data", query=params)
            # Basic validation of response structure
            if response and "indicatorCode" in response and "data" in response:
                current_app.logger.info(f"Successfully fetched DataBank indicator data for {indicator_code} in {country_code}")
                return response
            else:
                current_app.logger.error(f"Unexpected response structure for DataBank/indicator_data ({indicator_code}, {country_code}): {response}")
                return {"error": "Invalid data structure from API for DataBank/indicator_data", "details": response}
        except Exception as e:
            current_app.logger.error(f"Error fetching DataBank indicator data for {indicator_code} in {country_code}: {e}")
            return {"error": str(e)}

# Example usage (for testing purposes, not part of the Flask app directly here):
# if __name__ == "__main__":
#     # This part needs a Flask app context to run current_app.logger
#     # For standalone testing, you might replace current_app.logger with print()
#     # and instantiate ApiClient directly without Flask context.
#     pass

