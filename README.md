# Roostoo Trading Bot

A cryptocurrency trading bot leveraging Mean Reversion strategy, RSI momentum filtering, and LSTM neural networks for price prediction.

![Trading Bot](https://img.shields.io/badge/Trading-Bot-blue) ![Python](https://img.shields.io/badge/Python-3.7+-yellow) ![TensorFlow](https://img.shields.io/badge/TensorFlow-2.0+-orange) ![License](https://img.shields.io/badge/License-MIT-green)

## 📊 Overview

Roostoo Trading Bot combines technical analysis with machine learning to identify and execute potential trading opportunities in the cryptocurrency market. The system implements a hybrid approach using mean reversion principles alongside deep learning predictions to make informed trading decisions.

> **⚠️ DISCLAIMER:** This bot uses a mock API (Roostoo) for demonstration purposes only. It was trained on historical 2021 Bitcoin data and should not be used for actual trading without extensive further development and testing.

## ✨ Key Features

- **Hybrid Strategy Implementation**
  - Mean reversion with dynamic moving average bands
  - RSI momentum confirmation signals
  - Smart position sizing based on conviction metrics

- **Machine Learning Price Prediction**
  - LSTM neural network architecture for time series forecasting
  - Trained on historical BTC price action
  - Price movement probability distribution calculations

- **Comprehensive Risk Management**
  - Automatic 2% profit-taking threshold
  - 1% stop-loss protection mechanisms
  - Portfolio Sharpe ratio calculation and monitoring

- **Robust Technical Infrastructure**
  - REST API integration with authentication
  - JSON-based trade logging and history
  - Automated portfolio synchronization

## 🔧 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/roostoo_trading_bot_ml.git
cd roostoo_trading_bot_ml

# Install dependencies
pip install -r requirements.txt

# Configure your API keys in trading_bot.py
# Run the trading bot
python trading_bot.py
```

## 📂 Project Structure

```
roostoo_trading_bot_ml/
├── trading_bot.py            # Main trading bot implementation
├── train_model.py            # LSTM model training script
├── crypto_lstm_model.h5      # Pretrained LSTM model
├── predicted_prices.csv      # Sample price predictions
├── BTC-2021min.csv           # Sample training data
├── trade_data.json           # Trade history storage
└── README.md                 # This documentation
```

## ⚙️ Configuration

Edit these parameters in `trading_bot.py`:

```python
# API Configuration
API_BASE_URL = "https://mock-api.roostoo.com/v3"
API_KEY = "your_api_key_here"
SECRET_KEY = "your_secret_key_here"

# Trading Parameters
CRYPTOS = [{"symbol": "BTC/USD", "name": "Bitcoin", "weight": 0.5}]
TRADING_INTERVAL = 40  # seconds between checks
INITIAL_BALANCE = 10000  # starting virtual balance
```

## 📈 Trading Strategy

The bot implements a sophisticated hybrid strategy:

1. **Mean Reversion Detection**
   - Calculates moving average bands to identify price deviations
   - Looks for potential reversions to the mean

2. **RSI Momentum Filtering**
   - Uses RSI (Relative Strength Index) to confirm momentum direction
   - Filters out false signals with divergence detection

3. **LSTM Price Prediction**
   - Utilizes deep learning to forecast short-term price movements
   - Integrates predictions with technical signals for higher confidence trades

4. **Position Management**
   - Dynamically sizes positions based on conviction score
   - Implements take-profit and stop-loss mechanisms

## 🤖 Machine Learning Component

The LSTM neural network was designed to recognize patterns in cryptocurrency price movements:

- Trained on 2021 Bitcoin historical minute-level data
- Features engineered from price, volume, and technical indicators
- Optimized for short-term forecasting (5-15 minute horizon)

## ⚠️ Important Notes

- This bot uses mock API endpoints and will not execute real trades
- The LSTM model was trained on specific historical data only and requires retraining for current market conditions
- Extensive backtesting is recommended before considering live trading
- No guarantee of profitability; cryptocurrency markets are highly volatile

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

*Note: This project is for educational purposes only and should not be considered financial advice.*
