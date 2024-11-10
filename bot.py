from smartapi import SmartConnect
import os
from dotenv import load_dotenv
import time

load_dotenv()
api_key = os.getenv("API_KEY")
client_id = os.getenv("CLIENT_ID")
# Removed the password since you're using OTP and PIN
entry_price = float(os.getenv("ENTRY_PRICE"))
option_type = os.getenv("OPTION_TYPE")

class OptionTradingStrategy:
    def __init__(self, api_key, client_id, entry_price, option_type='call'):
        """
        Initialize the option trading strategy and connect to Angel One's SmartAPI.
        
        :param api_key: API key for Angel One
        :param client_id: Client ID for login
        :param entry_price: Entry price of the option
        :param option_type: Type of the option - 'call' or 'put'
        """
        # Connect to SmartAPI
        self.smart_connect = SmartConnect(api_key=api_key)

        # Manually handle OTP and PIN input
        print("Login step: Please provide OTP and PIN.")
        otp = input("Enter OTP sent to your registered mobile/email: ")
        pin = input("Enter your 4-digit PIN: ")

        # Generate session using OTP and PIN
        try:
            data = self.smart_connect.generateSession(client_id, otp=otp, pin=pin)
            self.access_token = data['data']['accessToken']
            print("Successfully logged in.")
        except Exception as e:
            print(f"Error during login: {e}")
            exit()

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
        
        try:
            order_id = self.smart_connect.placeOrder(order_params)
            print(f"Order placed. Order ID: {order_id}")
            return order_id
        except Exception as e:
            print(f"Error placing order: {e}")
            return None

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
            try:
                ltp_data = self.smart_connect.ltpData("NSE", tradingsymbol, "your_symbol_token")
                current_price = ltp_data["data"]["ltp"]
                print(f"Current Price: {current_price}")
                self.update_stop_loss(current_price)
                time.sleep(1)  # To avoid hitting rate limits
            except Exception as e:
                print(f"Error fetching data: {e}")
                break

# Example usage:
api_key = "your_api_key"
client_id = "your_client_id"

# Initialize the strategy with an entry price of 100 for a call option
strategy = OptionTradingStrategy(api_key, client_id, entry_price=100, option_type='call')

# Place the order
order_id = strategy.place_order(tradingsymbol="NIFTY23SEP18000CE", quantity=1)

# Start monitoring the price and adjusting the SL
if order_id:
    strategy.monitor_and_update(tradingsymbol="NIFTY23SEP18000CE")
else:
    print("Order not placed. Exiting...")
