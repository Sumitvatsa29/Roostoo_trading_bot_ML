# Roostoo_trading_bot_ML
📌 Overview

This project implements an automated cryptocurrency trading bot that combines:

A Mean Reversion strategy with RSI momentum filtering
LSTM neural networks for price prediction
Risk management with position sizing and stop-loss mechanisms
Important Note: This bot was trained on 2021 Bitcoin price data and is configured to use a mock API (Roostoo) for demonstration purposes only.

✨ Features

Hybrid Trading Strategy:
Mean reversion with moving average bands
RSI momentum confirmation
Dynamic position sizing
Machine Learning Component:
LSTM model for price prediction
Trained on 2021 BTC historical data
Price forecasting capability
Risk Management:
2% profit-taking threshold
1% stop-loss protection
Portfolio Sharpe ratio calculation
Technical Implementation:
REST API integration
Persistent trade logging
Portfolio synchronization


📂 Project Structure

crypto-trading-bot/
├── trading_bot.py            # Main trading bot implementation
├── train_model.py            # LSTM model training script
├── crypto_lstm_model.h5      # Pretrained LSTM model
├── predicted_prices.csv      # Sample price predictions
├── BTC-2021min.csv           # Sample training data
├── trade_data.json           # Trade history storage
└── README.md

⚙️ Configuration

Edit these parameters in trading_bot.py:

python
# API Configuration
API_BASE_URL = "https://mock-api.roostoo.com/v3"
API_KEY = "your_api_key_here"
SECRET_KEY = "your_secret_key_here"

# Trading Parameters
CRYPTOS = [{"symbol": "BTC/USD", "name": "Bitcoin", "weight": 0.5}]
TRADING_INTERVAL = 40  # seconds between checks
INITIAL_BALANCE = 10000  # starting virtual balance

⚠️ Important Notes

This bot uses mock API endpoints and will not execute real trades
The LSTM model was trained on 2021 data only and may not predict current market conditions accurately
Backtest thoroughly before considering live trading

