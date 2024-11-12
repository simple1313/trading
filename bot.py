# from Smartapi import SmartConnect
import os
from dotenv import load_dotenv
import time
import requests

load_dotenv()
api_key = os.getenv("API_KEY")
client_id = os.getenv("CLIENT_ID")

class OptionTradingStrategy:
    def __init__(self, api_key, client_id, entry_price, option_type):
        # self.smart_connect = SmartConnect(api_key=api_key)

        print("Login step: Please provide OTP and PIN.")
        otp = input("Enter OTP sent to your registered mobile/email: ")
        pin = input("Enter your 4-digit PIN: ")

        try:
            # data = self.smart_connect.generateSession(client_id, otp=otp, pin=pin)
            self.access_token = data['data']['accessToken']
            self.refresh_token = data['data']['refreshToken']
            print("Successfully logged in.")
        except Exception as e:
            print(f"Error during login: {e}")
            exit()

        self.entry_price = entry_price
        self.option_type = option_type.lower()
        self.stop_loss = entry_price - 20  # Initial SL set 20 points below entry
        self.trailing_interval = 20  # Points to trail SL

    def generate_new_token(self):
        """
        Generate a new JWT token using the refresh token.
        """
        url = "https://apiconnect.angelone.in/rest/auth/angelbroking/jwt/v1/generateTokens"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-UserType": "USER",
            "X-SourceID": "WEB",
            "X-ClientLocalIP": "CLIENT_LOCAL_IP",
            "X-ClientPublicIP": "CLIENT_PUBLIC_IP",
            "X-MACAddress": "MAC_ADDRESS",
            "X-PrivateKey": api_key,
        }

        data = {
            "refreshToken": self.refresh_token
        }

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            if response_data['status']:
                print("JWT Token generated successfully.")
                return response_data['data']['jwtToken']
            else:
                print(f"Error generating JWT Token: {response_data['message']}")
        else:
            print(f"Error in token generation: {response.status_code}")
        return None

    def get_profile(self):
        """
        Fetch the profile details of the user.
        """
        url = "https://apiconnect.angelone.in/rest/secure/angelbroking/user/v1/getProfile"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-UserType": "USER",
            "X-SourceID": "WEB",
            "X-ClientLocalIP": "CLIENT_LOCAL_IP",
            "X-ClientPublicIP": "CLIENT_PUBLIC_IP",
            "X-MACAddress": "MAC_ADDRESS",
            "X-PrivateKey": api_key,
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            if response_data['status']:
                print("Profile fetched successfully.")
                return response_data['data']
            else:
                print(f"Error fetching profile: {response_data['message']}")
        else:
            print(f"Error fetching profile: {response.status_code}")
        return None

    def get_symbol_token(self, tradingsymbol):
        """
        Retrieve the symbol token for the provided trading symbol.
        
        :param tradingsymbol: The trading symbol like "NIFTY23SEP18000CE"
        :return: The symbol token for the given tradingsymbol
        """
        try:
            # symbol_info = self.smart_connect.getSymbolInfo(tradingsymbol)
            return symbol_info['data'][0]['symboltoken']
        except Exception as e:
            print(f"Error fetching symbol token: {e}")
            return None

    def place_order(self, tradingsymbol, quantity):
        """
        Place a buy order for the option.
        
        :param tradingsymbol: The option's trading symbol
        :param quantity: Quantity to buy
        """
        symbol_token = self.get_symbol_token(tradingsymbol)
        if not symbol_token:
            print(f"Error: Unable to fetch symbol token for {tradingsymbol}")
            return None

        order_params = {
            "variety": "NORMAL",
            "tradingsymbol": tradingsymbol,
            "symboltoken": symbol_token,  # Use the fetched symbol token
            "transactiontype": "BUY",
            "exchange": "NSE",
            "ordertype": "MARKET",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "quantity": quantity
        }

        try:
            # order_id = self.smart_connect.placeOrder(order_params)
            print(f"Order placed. Order ID: {order_id}")
            return order_id
        except Exception as e:
            print(f"Error placing order: {e}")
            return None

    def update_stop_loss(self, current_price):
        if current_price >= self.entry_price + self.trailing_interval:
            new_stop_loss = current_price - self.trailing_interval
            if new_stop_loss > self.stop_loss:
                self.stop_loss = new_stop_loss
                print(f"Trailing Stop Loss updated to: {self.stop_loss}")

    def monitor_and_update(self, tradingsymbol):
        while True:
            try:
                # ltp_data = self.smart_connect.ltpData("NSE", tradingsymbol)
                current_price = ltp_data["data"]["ltp"]
                print(f"Current Price: {current_price}")
                self.update_stop_loss(current_price)
                time.sleep(1)
            except Exception as e:
                print(f"Error fetching data: {e}")
                time.sleep(5)  # Retry after delay

# Example usage
api_key = "your_api_key"
client_id = "your_client_id"
strategy = OptionTradingStrategy(api_key, client_id, entry_price=100, option_type='call')

# Step 1: Generate new JWT token using refresh token
new_jwt_token = strategy.generate_new_token()

if new_jwt_token:
    print("New JWT Token: ", new_jwt_token)

# Step 2: Get user profile
profile = strategy.get_profile()

if profile:
    print("User Profile:", profile)

# Step 3: Place the order
order_id = strategy.place_order(tradingsymbol="NIFTY23SEP18000CE", quantity=1)

if order_id:
    # Step 4: Monitor and update the stop loss
    strategy.monitor_and_update(tradingsymbol="NIFTY23SEP18000CE")
else:
    print("Order not placed. Exiting...")
