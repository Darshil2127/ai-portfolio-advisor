# src/data_services/yahoo_finance_client.py
# STUBBED VERSION FOR DEPLOYMENT WITHOUT data_api

from flask import current_app

class YahooFinanceClient:
    def __init__(self):
        # self.client = ApiClient() # Removed data_api dependency
        current_app.logger.info("[STUBBED] YahooFinanceClient initialized (no actual API client)")

    def get_stock_chart_data(self, symbol, interval="1d", range="1y", region="US", include_adjusted_close=True):
        """Fetches historical stock chart data - STUBBED."""
        current_app.logger.info(f"[STUBBED] get_stock_chart_data for {symbol}")
        # Return minimal valid-looking dummy data
        return {
            "meta": {"symbol": symbol, "currency": "USD", "exchangeName": "NMS", "instrumentType": "EQUITY", "firstTradeDate": 1588000000, "regularMarketTime": 1688000000, "gmtoffset": -14400, "timezone": "EDT", "exchangeTimezoneName": "America/New_York", "regularMarketPrice": 150.0, "chartPreviousClose": 149.0, "priceHint": 2, "currentTradingPeriod": {"pre": {}, "regular": {}, "post": {}}, "dataGranularity": "1d", "range": "1y", "validRanges": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]},
            "timestamp": [1687000000, 1687100000], 
            "indicators": {
                "quote": [{
                    "open": [149.5, 150.1],
                    "close": [150.0, 150.5],
                    "high": [150.5, 150.8],
                    "low": [149.0, 150.0],
                    "volume": [1000000, 1200000]
                }], 
                "adjclose": [{ 
                    "adjclose": [150.0, 150.5]
                }]
            }
        }

    def get_stock_insights_data(self, symbol, region="US"): 
        """Fetches stock insights data - STUBBED."""
        current_app.logger.info(f"[STUBBED] get_stock_insights_data for {symbol}")
        return {
            "symbol": symbol,
            "instrumentInfo": {
                "technicalEvents": {"provider": "StubProvider", "shortTermOutlook": {"stateDescription": "Neutral"}, "intermediateTermOutlook": {"stateDescription": "Neutral"}, "longTermOutlook": {"stateDescription": "Neutral"}},
                "keyTechnicals": {"provider": "StubProvider", "support": 140.0, "resistance": 160.0, "stopLoss": 135.0},
                "valuation": {"description": "Fairly Valued", "provider": "StubProvider"}
            },
            "companySnapshot": {"company": {"innovativeness": 0.5}, "sector": {"innovativeness": 0.5}},
            "recommendation": {"targetPrice": 155.0, "provider": "StubProvider", "rating": "Hold"},
            "sigDevs": [
                {"headline": "[STUBBED] Company announces new product", "date": "2023-10-26"}
            ],
            "secReports": []
        }

    def get_analyst_opinions(self, symbol, region="US", lang="en-US"):
        """Fetches what analysts are saying about a stock - STUBBED."""
        current_app.logger.info(f"[STUBBED] get_analyst_opinions for {symbol}")
        return [
            {
                "hits": [
                    {"report_title": "[STUBBED] Analyst Report on XYZ", "provider": "StubBank", "abstract": "[STUBBED] Neutral outlook for XYZ stock."}
                ]
            }
        ]

