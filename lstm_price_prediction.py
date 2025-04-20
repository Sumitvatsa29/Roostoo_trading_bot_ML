import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# Load data
data = pd.read_csv("BTC-2021min.csv")  # Columns : Date, Open, High, Low ,volume

# Normalize data
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_prices = scaler.fit_transform(prices)

# Prepare training data
def create_dataset(data, time_step=60):
    X, y = [], []
    for i in range(len(data) - time_step - 1):
        X.append(data[i:(i + time_step), 0])
        y.append(data[i + time_step, 0])
    return np.array(X), np.array(y)

time_step = 60
X, y = create_dataset(scaled_prices, time_step)
X = X.reshape(X.shape[0], X.shape[1], 1)

model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape=(time_step, 1)))
model.add(LSTM(50, return_sequences=False))
model.add(Dense(25))
model.add(Dense(1))

model.compile(optimizer="adam", loss="mean_squared_error")
model.fit(X, y, batch_size=64, epochs=20)

# Predict future prices
def predict_future_prices(model, data, time_step, future_steps=10):
    predictions = []
    last_sequence = data[-time_step:]
    for _ in range(future_steps):
        pred = model.predict(last_sequence.reshape(1, time_step, 1))
        predictions.append(pred[0, 0])
        last_sequence = np.append(last_sequence[1:], pred)
    return scaler.inverse_transform(np.array(predictions).reshape(-1, 1))

future_prices = predict_future_prices(model, scaled_prices, time_step)
print("Predicted Prices:", future_prices)
