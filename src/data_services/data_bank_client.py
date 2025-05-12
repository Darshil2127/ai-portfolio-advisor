# src/data_services/data_bank_client.py
# STUBBED VERSION FOR DEPLOYMENT WITHOUT data_api

from flask import current_app

class DataBankClient:
    def __init__(self):
        # self.client = ApiClient() # Removed data_api dependency
        current_app.logger.info("[STUBBED] DataBankClient initialized (no actual API client)")

    def get_indicator_list(self, query_string=None, page=1, page_size=10):
        """Fetches a list of World Development Indicators - STUBBED."""
        current_app.logger.info(f"[STUBBED] get_indicator_list with query: {query_string}")
        return {
            "total": 1,
            "page": page,
            "pageSize": page_size,
            "items": [
                {"indicatorCode": "NY.GDP.MKTP.CD.STUB", "indicatorName": "[STUBBED] GDP (current US$)"}
            ]
        }

    def get_indicator_data(self, indicator_code, country_code):
        """Fetches data for a specific World Development Indicator and country - STUBBED."""
        current_app.logger.info(f"[STUBBED] get_indicator_data for {indicator_code} in {country_code}")
        # Return minimal valid-looking dummy data
        return {
            "countryCode": country_code,
            "countryName": "[STUBBED] United States",
            "indicatorCode": indicator_code,
            "indicatorName": "[STUBBED] GDP (current US$)",
            "data": {
                "2020": 20000000000000,
                "2021": 21000000000000,
                "2022": 22000000000000 
            }
        }

