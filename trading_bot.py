import time
import hmac
import hashlib
import requests
import logging
import numpy as np
import pandas as pd
from datetime import datetime
import sys
import pytz
import json
import os
from tensorflow.keras.models import load_model

class Formatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, timezone=None):
        super().__init__(fmt, datefmt)
        self.timezone = timezone

    def converter(self, timestamp):
        dt = datetime.fromtimestamp(timestamp, tz=self.timezone)
        return dt

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            return dt.strftime(datefmt)
        else:
            return dt.isoformat()

TIMEZONE = pytz.timezone("Asia/Kolkata")
formatter = Formatter(
    fmt='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    timezone=TIMEZONE
)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logging.basicConfig(
    level=logging.INFO,
    handlers=[handler],
    force=True
)

# CONFIGURATION
API_BASE_URL = "https://mock-api.roostoo.com/v3"
API_KEY = "sX8cRXeqEjaOktC4MX2R8ovMg7Hkq8PzEw2CgBTKu9lHScVryD4eaA0z7u5BQinN"
SECRET_KEY = "trocsegSyuxxkVnOE4sUxSndp09inv2DgqMvrrN7YbEiTyRpbg4qlLQoRWSSuJ0f"
RISK_FREE_RATE = 0.001
TRADING_INTERVAL = 20
INITIAL_BALANCE = 50000
RUN_DURATION = 86400

CRYPTOS = [
    {"symbol": "BTC/USD", "name": "Bitcoin", "weight": 0.90},
 ]

PROFIT_THRESHOLD = 0.02  
STOP_LOSS_THRESHOLD = -0.01  

STEP_SIZES = {
     "BTC/USD": 0.001,
}

TRADE_DATA_FILE = "trade_data.json"

# API Client
class RoostooAPIClient:
    def __init__(self, api_key, secret_key, base_url=API_BASE_URL):
        self.api_key = api_key
        self.secret_key = secret_key.encode()
        self.base_url = base_url

    def _get_timestamp(self):
        return str(int(time.time() * 1000))

    def _sign(self, params: dict):
        sorted_items = sorted(params.items())
        query_string = '&'.join([f"{key}={value}" for key, value in sorted_items])
        signature = hmac.new(self.secret_key, query_string.encode(), hashlib.sha256).hexdigest()
        return signature, query_string

    def _headers(self, params: dict, is_signed=False):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        if is_signed:
            signature, _ = self._sign(params)
            headers["RST-API-KEY"] = self.api_key
            headers["MSG-SIGNATURE"] = signature
        return headers

    def _handle_response(self, response):
        if response.status_code != 200:
            logging.error(f"HTTP Error: {response.status_code} {response.text}")
            logging.error(f"Request URL: {response.url}")
            return None
        try:
            data = response.json()
        except Exception as e:
            logging.error(f"JSON decode error: {e}")
            return None
        return data

    def get_ticker(self, pair=None):
        url = f"{self.base_url}/ticker"
        params = {
            "timestamp": self._get_timestamp()
        }
        if pair:
            params["pair"] = pair
        headers = self._headers(params, is_signed=False)
        response = requests.get(url, params=params, headers=headers)
        return self._handle_response(response)

    def place_order(self, symbol, quantity, order_type):
        url = f"{self.base_url}/place_order"
        params = {
            "pair": symbol,
            "quantity": quantity,
            "side": "BUY" if order_type == "buy" else "SELL",
            "type": "MARKET",
            "timestamp": self._get_timestamp()
        }
        headers = self._headers(params, is_signed=True)
        response = requests.post(url, data=params, headers=headers)
        logging.info(f"API Response: {response.text}")
        return self._handle_response(response)

    def get_balance(self):
        """Fetch current balance from the exchange."""
        url = f"{self.base_url}/balance"
        params = {
            "timestamp": self._get_timestamp()
        }
        headers = self._headers(params, is_signed=True)
        response = requests.get(url, params=params, headers=headers)
        return self._handle_response(response)

# Trading Strategy :- Mean Reversion with Momentum Filter
class MeanReversionStrategy:
    def __init__(self, window=20, rsi_window=14):
        self.window = window
        self.rsi_window = rsi_window
        self.prices = []
        self.rsi_values = []

    def update_price(self, price):
        self.prices.append(price)
        if len(self.prices) > self.window:
            self.prices.pop(0)

    def calculate_rsi(self):
        if len(self.prices) < self.rsi_window:
            return 50 
        gains = []
        losses = []
        for i in range(1, len(self.prices)):
            change = self.prices[i] - self.prices[i - 1]
            if change > 0:
                gains.append(change)
            else:
                losses.append(abs(change))
        avg_gain = np.mean(gains) if gains else 0
        avg_loss = np.mean(losses) if losses else 0
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def generate_signal(self):
        if len(self.prices) < self.window:
            return "HOLD"
        mean_price = np.mean(self.prices)
        current_price = self.prices[-1]
        rsi = self.calculate_rsi()
        if current_price < mean_price * 0.98 and rsi < 30: 
            return "BUY"
        elif current_price > mean_price * 1.02 and rsi > 70: 
            return "SELL"
        else:
            return "HOLD"

class RiskManager:
    def __init__(self):
        self.portfolio_values = []

    def update_portfolio(self, value):
        self.portfolio_values.append(value)

    def calculate_sharpe_ratio(self):
        if len(self.portfolio_values) < 2:
            return 0
        returns = np.diff(self.portfolio_values) / self.portfolio_values[:-1]
        excess_returns = returns - RISK_FREE_RATE
        mean_return = np.mean(excess_returns)
        std_return = np.std(excess_returns)
        if std_return == 0:
            return 0
        sharpe_ratio = mean_return / std_return
        return sharpe_ratio

class TradingBot:
    def __init__(self, api_client, initial_cash=INITIAL_BALANCE):
        self.api_client = api_client
        self.cash = initial_cash
        self.holdings = {crypto["symbol"]: 0.0 for crypto in CRYPTOS}
        self.trade_log = []
        self.strategies = {crypto["symbol"]: MeanReversionStrategy() for crypto in CRYPTOS}
        self.risk_manager = RiskManager()
        self.entry_prices = {crypto["symbol"]: 0.0 for crypto in CRYPTOS}
        self.model = load_model("crypto_lstm_model.h5")
        self.predicted_prices = pd.read_csv("predicted_prices.csv")["Predicted Price"].values
        self.sync_holdings()  
        self.load_trade_data()

    def sync_holdings(self):
        """Sync the bot's holdings with the actual balance on the exchange."""
        balance_data = self.api_client.get_balance()

        logging.info(f"Balance API Response: {json.dumps(balance_data, indent=2)}")

        if balance_data and balance_data.get("Success"):
            if "SpotWallet" in balance_data:
                for crypto in CRYPTOS:
                    symbol = crypto["symbol"]
                    coin = symbol.split("/")[0]  
                    if coin in balance_data["SpotWallet"]:
                        exchange_balance = float(balance_data["SpotWallet"][coin]["Free"])
                        if self.holdings[symbol] != exchange_balance:
                            logging.warning(f"Discrepancy detected for {symbol}. Bot's holdings: {self.holdings[symbol]:.4f}, Exchange balance: {exchange_balance:.4f}")
                            self.holdings[symbol] = exchange_balance 
                        logging.info(f"Synced holdings for {symbol}: {self.holdings[symbol]:.4f}")
                    else:
                        logging.warning(f"Coin {coin} not found in SpotWallet. Setting holdings to 0.")
                        self.holdings[symbol] = 0.0
            else:
                logging.error("'SpotWallet' key not found in balance API response.")
        else:
            logging.error("Failed to fetch balance from the exchange.")

    def load_trade_data(self):
        if os.path.exists(TRADE_DATA_FILE):
            with open(TRADE_DATA_FILE, "r") as file:
                data = json.load(file)
                self.cash = data.get("cash", INITIAL_BALANCE)
                self.holdings = data.get("holdings", {crypto["symbol"]: 0.0 for crypto in CRYPTOS})
                self.trade_log = data.get("trade_log", [])
                self.entry_prices = data.get("entry_prices", {crypto["symbol"]: 0.0 for crypto in CRYPTOS})
                logging.info("Loaded previous trade data.")

    def save_trade_data(self):
        data = {
            "cash": self.cash,
            "holdings": self.holdings,
            "trade_log": self.trade_log,
            "entry_prices": self.entry_prices
        }
        with open(TRADE_DATA_FILE, "w") as file:
            json.dump(data, file)
        logging.info("Saved trade data.")

    def update_portfolio_value(self, prices):
        portfolio_value = self.cash
        for crypto in CRYPTOS:
            portfolio_value += self.holdings[crypto["symbol"]] * prices[crypto["symbol"]]
        self.risk_manager.update_portfolio(portfolio_value)
        return portfolio_value

    def execute_trade(self, symbol, signal, price):
        trade_amount = (self.cash * CRYPTOS[next(i for i, c in enumerate(CRYPTOS) if c["symbol"] == symbol)]["weight"]) / price

        step_size = STEP_SIZES.get(symbol, 0.01)
        trade_amount = (trade_amount // step_size) * step_size

        min_order_size = step_size
        if trade_amount < min_order_size:
            trade_amount = min_order_size 

        logging.info(f"Trade amount for {symbol}: {trade_amount:.4f} | Current holdings: {self.holdings[symbol]:.4f}")

        if signal == "BUY" and self.cash >= trade_amount * price:
            order = self.api_client.place_order(symbol, trade_amount, 'buy')
            if order and order.get("Success"):
                self.holdings[symbol] += trade_amount
                self.cash -= trade_amount * price
                self.entry_prices[symbol] = price  
                self.trade_log.append({"timestamp": datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S'), "action": "BUY", "symbol": symbol, "price": price, "amount": trade_amount})
                logging.info(f"Executed BUY: {trade_amount} {symbol} at {price}")
            else:
                logging.error(f"Failed to execute BUY order for {symbol}. Error: {order.get('ErrMsg', 'Unknown error')}")
        elif signal == "SELL":
            if self.holdings[symbol] >= trade_amount:
                entry_price = self.entry_prices[symbol]
                if entry_price > 0:
                    profit_loss = (price - entry_price) / entry_price
                    logging.info(f"Profit/Loss for {symbol}: {profit_loss:.2%} | Entry Price: {entry_price} | Current Price: {price}")
                else:
                    logging.warning(f"Cannot calculate profit/loss for {symbol} because entry price is 0.")
                    profit_loss = 0.0  
                balance_data = self.api_client.get_balance()
                if balance_data and balance_data.get("Success") and "SpotWallet" in balance_data:
                    coin = symbol.split("/")[0] 
                    if coin in balance_data["SpotWallet"]:
                        available_balance = float(balance_data["SpotWallet"][coin]["Free"])
                        if available_balance >= self.holdings[symbol]:
                            logging.info(f"Executing SELL for {symbol} (SELL signal received).")
                            order = self.api_client.place_order(symbol, self.holdings[symbol], 'sell')
                            if order and order.get("Success"):
                                self.cash += self.holdings[symbol] * price
                                self.trade_log.append({"timestamp": datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S'), "action": "SELL", "symbol": symbol, "price": price, "amount": self.holdings[symbol]})
                                logging.info(f"Executed SELL: {self.holdings[symbol]} {symbol} at {price} (Profit/Loss: {profit_loss:.2%})")
                                self.holdings[symbol] = 0.0 
                            else:
                                logging.error(f"Failed to execute SELL order for {symbol}. Error: {order.get('ErrMsg', 'Unknown error')}")
                        else:
                            logging.warning(f"Insufficient available balance to sell {symbol}. Available: {available_balance:.4f}, Required: {self.holdings[symbol]:.4f}")
                    else:
                        logging.warning(f"Coin {coin} not found in SpotWallet. Cannot execute SELL order.")
                else:
                    logging.error("Failed to fetch balance or 'SpotWallet' key not found in API response.")
            else:
                logging.warning(f"Insufficient holdings to sell {symbol}. Current holdings: {self.holdings[symbol]:.4f}, Required: {trade_amount:.4f}")
        else:
            logging.info(f"No trade executed for {symbol} (either HOLD signal or insufficient funds/holdings).")

    def run(self, duration_sec=None):
        logging.info("Starting trading bot...")
        start_time = time.time()
        while True:
            try:
                if duration_sec and time.time() - start_time >= duration_sec:
                    logging.info("Trading bot stopped after the specified duration.")
                    break

                prices = {}
                for crypto in CRYPTOS:
                    ticker_data = self.api_client.get_ticker(pair=crypto["symbol"])
                    if ticker_data and ticker_data.get("Success"):
                        price = float(ticker_data["Data"][crypto["symbol"]]["LastPrice"])
                        prices[crypto["symbol"]] = price
                        self.strategies[crypto["symbol"]].update_price(price)
                        signal = self.strategies[crypto["symbol"]].generate_signal()
                        current_time = datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')
                        logging.info(f"Time: {current_time} | {crypto['name']} | Price: {price} | Signal: {signal}")

                        logging.info(f"Current holdings for {crypto['symbol']}: {self.holdings[crypto['symbol']]:.4f}")
                        logging.info(f"Current cash: {self.cash:.2f}")

                        self.execute_trade(crypto["symbol"], signal, price)

                portfolio_value = self.update_portfolio_value(prices)
                sharpe_ratio = self.risk_manager.calculate_sharpe_ratio()
                logging.info(f"Portfolio Value: {portfolio_value:.2f}")
                logging.info(f"Sharpe Ratio: {sharpe_ratio:.4f}")

                time.sleep(TRADING_INTERVAL)
            except Exception as e:
                logging.error(f"An error occurred: {e}")
                time.sleep(TRADING_INTERVAL)

        self.save_trade_data()
        self.print_summary()

    def print_summary(self):
        logging.info("--- TRADING BOT SUMMARY ---")
        logging.info(f"Initial Balance: ${INITIAL_BALANCE:.2f}")
        logging.info(f"Final Cash: ${self.cash:.2f}")
        for crypto in CRYPTOS:
            logging.info(f"Final Holdings {crypto['name']}: {self.holdings[crypto['symbol']]:.4f}")
        final_portfolio_value = self.cash + sum(self.holdings[crypto["symbol"]] * self.trade_log[-1]["price"] for crypto in CRYPTOS if self.trade_log)
        logging.info(f"Final Portfolio Value: ${final_portfolio_value:.2f}")
        logging.info(f"Total Trades Executed: {len(self.trade_log)}")
        logging.info(f"Sharpe Ratio: {self.risk_manager.calculate_sharpe_ratio():.4f}")

def main():
    api_client = RoostooAPIClient(API_KEY, SECRET_KEY)
    trading_bot = TradingBot(api_client, initial_cash=INITIAL_BALANCE)
    trading_bot.run(duration_sec=RUN_DURATION)

if __name__ == "__main__":
    main()