from smartapi import SmartConnect
import os
from dotenv import load_dotenv
import time

load_dotenv()
api_key = os.getenv("API_KEY")
client_id = os.getenv("CLIENT_ID")
password = os.getenv("PASSWORD")
entry_price = float(os.getenv("ENTRY_PRICE"))
option_type = os.getenv("OPTION_TYPE")

class OptionTradingStrategy:
    def __init__(self, api_key, client_id, password, entry_price, option_type='call'):
        """
        Initialize the option trading strategy and connect to Angel One's SmartAPI.
        
        :param api_key: API key for Angel One
        :param client_id: Client ID for login
        :param password: Password for login
        :param entry_price: Entry price of the option
        :param option_type: Type of the option - 'call' or 'put'
        """
        # Connect to SmartAPI
        self.smart_connect = SmartConnect(api_key=api_key)
        data = self.smart_connect.generateSession(client_id, password)
        self.access_token = data['data']['accessToken']
        
        self.entry_price = entry_price
        self.option_type = option_type.lower()
        self.stop_loss = entry_price - 20  # Initial SL set 20 points below entry
        self.trailing_interval = 20  # Points to trail SL

    def place_order(self, tradingsymbol, quantity):
        """
        Place a buy order for the option.
        
        :param tradingsymbol: The option's trading symbol
        :param quantity: Quantity to buy
        """
        order_params = {
            "variety": "NORMAL",
            "tradingsymbol": tradingsymbol,
            "symboltoken": "your_symbol_token",  # Obtain this from Angel One
            "transactiontype": "BUY",
            "exchange": "NSE",
            "ordertype": "MARKET",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "quantity": quantity
        }
        
        order_id = self.smart_connect.placeOrder(order_params)
        print(f"Order placed. Order ID: {order_id}")
        return order_id

    def update_stop_loss(self, current_price):
        """
        Update the trailing stop loss based on the current price.
        
        :param current_price: The latest price of the option
        """
        if current_price >= self.entry_price + self.trailing_interval:
            self.stop_loss = max(self.stop_loss, current_price - self.trailing_interval)
            print(f"Trailing Stop Loss updated to: {self.stop_loss}")

    def monitor_and_update(self, tradingsymbol):
        """
        Continuously monitor the price and update SL as needed.
        
        :param tradingsymbol: The option's trading symbol to monitor
        """
        while True:
            ltp_data = self.smart_connect.ltpData("NSE", tradingsymbol, "your_symbol_token")
            current_price = ltp_data["data"]["ltp"]
            print(f"Current Price: {current_price}")
            self.update_stop_loss(current_price)
            time.sleep(1)  # To avoid hitting rate limits

# Example usage:
api_key = "your_api_key"
client_id = "your_client_id"
password = "your_password"

# Initialize the strategy with an entry price of 100 for a call option
strategy = OptionTradingStrategy(api_key, client_id, password, entry_price=100, option_type='call')

# Place the order
strategy.place_order(tradingsymbol="NIFTY23SEP18000CE", quantity=1)

# Start monitoring the price and adjusting the SL
strategy.monitor_and_update(tradingsymbol="NIFTY23SEP18000CE")
