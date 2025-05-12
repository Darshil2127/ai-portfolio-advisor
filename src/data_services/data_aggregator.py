# src/data_services/data_aggregator.py

from flask import current_app
from .yahoo_finance_client import YahooFinanceClient
from .data_bank_client import DataBankClient
# from src.models.portfolio_holding import PortfolioHolding # Assuming this will be passed in

class DataAggregator:
    def __init__(self):
        self.yf_client = YahooFinanceClient()
        self.db_client = DataBankClient()

    def get_aggregated_data_for_holdings(self, portfolio_holdings):
        """
        Aggregates data from YahooFinance and DataBank for a list of portfolio holdings.
        :param portfolio_holdings: A list of PortfolioHolding model instances.
        :return: A list of dictionaries, each containing aggregated data for a stock.
        """
        aggregated_results = []

        for holding in portfolio_holdings:
            ticker = holding.ticker_symbol
            current_app.logger.info(f"Aggregating data for ticker: {ticker}")
            stock_data = {
                "ticker": ticker,
                "quantity": holding.quantity,
                "purchase_price": holding.purchase_price,
                "purchase_date": holding.purchase_date.isoformat() if holding.purchase_date else None,
                "yahoo_finance": {},
                "data_bank": {},
                "errors": []
            }

            # 1. Fetch Yahoo Finance Data
            chart_data = self.yf_client.get_stock_chart_data(symbol=ticker)
            if chart_data and not chart_data.get("error"):
                stock_data["yahoo_finance"]["chart"] = chart_data
            else:
                err_msg = f"Failed to fetch chart data for {ticker}: {chart_data.get('error', 'Unknown error') if chart_data else 'No response'}"
                current_app.logger.warning(err_msg)
                stock_data["errors"].append(err_msg)

            insights_data = self.yf_client.get_stock_insights_data(symbol=ticker)
            if insights_data and not insights_data.get("error"):
                stock_data["yahoo_finance"]["insights"] = insights_data
            else:
                err_msg = err_msg = f"Failed to fetch insights data for {ticker}: {insights_data.get('error', 'Unknown error') if insights_data else 'No response'}"
                current_app.logger.warning(err_msg)
                stock_data["errors"].append(err_msg)
            
            analyst_opinions = self.yf_client.get_analyst_opinions(symbol=ticker)
            if analyst_opinions and not analyst_opinions.get("error"):
                stock_data["yahoo_finance"]["analyst_opinions"] = analyst_opinions
            else:
                err_msg = f"Failed to fetch analyst opinions for {ticker}: {analyst_opinions.get('error', 'Unknown error') if analyst_opinions else 'No response'}"
                current_app.logger.warning(err_msg)
                stock_data["errors"].append(err_msg)

            # 2. Fetch DataBank Data (Example: GDP for USA - NY.GDP.MKTP.CD)
            # In a real app, country and indicators would be more dynamic or configurable
            # For V1, we can use a default or make assumptions.
            # This part needs more sophisticated logic to determine relevant country and indicators per stock.
            # For now, let's fetch a common indicator for a default region (e.g., USA)
            # This is a placeholder for more complex logic.
            country_code = "USA" # Default or derived from stock exchange/company info
            gdp_indicator_code = "NY.GDP.MKTP.CD" # Example: GDP (current US$)
            
            gdp_data = self.db_client.get_indicator_data(indicator_code=gdp_indicator_code, country_code=country_code)
            if gdp_data and not gdp_data.get("error"):
                stock_data["data_bank"]["gdp_us"] = gdp_data # Store under a descriptive key
            else:
                err_msg = f"Failed to fetch GDP data for {country_code}: {gdp_data.get('error', 'Unknown error') if gdp_data else 'No response'}"
                current_app.logger.warning(err_msg)
                stock_data["errors"].append(err_msg)
            
            # Add more DataBank indicators as needed (e.g., inflation, interest rates)
            # Example: Inflation (Consumer prices, annual %) - FP.CPI.TOTL.ZG
            inflation_indicator_code = "FP.CPI.TOTL.ZG"
            inflation_data = self.db_client.get_indicator_data(indicator_code=inflation_indicator_code, country_code=country_code)
            if inflation_data and not inflation_data.get("error"):
                stock_data["data_bank"]["inflation_us_cpi"] = inflation_data
            else:
                err_msg = f"Failed to fetch Inflation CPI data for {country_code}: {inflation_data.get('error', 'Unknown error') if inflation_data else 'No response'}"
                current_app.logger.warning(err_msg)
                stock_data["errors"].append(err_msg)

            aggregated_results.append(stock_data)
        
        current_app.logger.info(f"Finished aggregating data for {len(portfolio_holdings)} holdings.")
        return aggregated_results

# Example usage (for testing - requires Flask app context for logger and API clients)
# if __name__ == "__main__":
#     class MockHolding:
#         def __init__(self, ticker, quantity, purchase_price=None, purchase_date=None):
#             self.ticker_symbol = ticker
#             self.quantity = quantity
#             self.purchase_price = purchase_price
#             self.purchase_date = purchase_date
# 
#     # This would need to be run within a Flask app context
#     # from flask import Flask
#     # app = Flask(__name__)
#     # with app.app_context():
#     #     aggregator = DataAggregator()
#     #     mock_holdings = [MockHolding("AAPL", 10), MockHolding("MSFT", 5)]
#     #     results = aggregator.get_aggregated_data_for_holdings(mock_holdings)
#     #     import json
#     #     print(json.dumps(results, indent=4))

