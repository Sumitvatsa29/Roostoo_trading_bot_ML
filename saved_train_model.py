# Save the trained model
model.save("crypto_lstm_model.h5")
print("Model saved as crypto_lstm_model.h5")

# Save the predicted prices to a CSV file
predicted_prices_df = pd.DataFrame(future_prices, columns=["Predicted Price"])
predicted_prices_df.to_csv("predicted_prices.csv", index=False)
print("Predicted prices saved as predicted_prices.csv")