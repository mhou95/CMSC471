import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

# 1. Download stock data (last 1 year, hourly)
#ticker = "AAPL"
#df = yf.download(ticker, period="1y", interval="1h")
#df.dropna(inplace=True)
#
#price = df["Close"].values.flatten()
#dates = df.index

# Download 1 year of daily TSLA data
df = yf.download("TSLA", period="1y", interval="1d")

# Save to Excel
df.to_excel("TSLA_1yr_data.xlsx")

# 2. Detect large price jumps
returns = np.diff(price) / price[:-1]
event_indices = np.where(np.abs(returns) > 0.01)[0]

# Simulate high-intensity zones (top 10% of returns)
threshold = np.percentile(np.abs(returns), 90)
high_intensity_indices = np.where(np.abs(returns) > threshold)[0]

# 3. Train linear regression model
X, y = [], []
for idx in high_intensity_indices:
    if idx < 10 or idx + 1 >= len(price):
        continue
    window = price[idx-10:idx]
    future_change = price[idx+1] - price[idx]
    X.append(window)
    y.append(future_change)

X = np.array(X)
y = np.array(y)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

reg = LinearRegression()
reg.fit(X_scaled, y)

# 4. Predict next price movement
latest_window = price[-11:-1].reshape(1, -1)
latest_scaled = scaler.transform(latest_window)
prediction = reg.predict(latest_scaled)
next_price = price[-1] + prediction[0]

# 5. Plotting
plt.figure(figsize=(14, 6))
plt.plot(dates, price, label="Stock Price", color="black")
plt.scatter(dates[event_indices], price[event_indices], color="red", label="Events", s=20)
plt.scatter(dates[high_intensity_indices], price[high_intensity_indices], color="blue", label="High-Intensity", s=15)

plt.axvline(dates[-1], linestyle="--", color="gray")
plt.plot([dates[-1], dates[-1] + pd.Timedelta(hours=1)],
         [price[-1], next_price], color="green", linewidth=2, label="Prediction →")

plt.title(f"Price Prediction for {ticker}")
plt.xlabel("Time")
plt.ylabel("Price")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# 6. Console output
print(f"\n🔮 Predicted next price change: {prediction[0]:.4f}")
print(f"📈 From ${price[-1]:.2f} to ${next_price:.2f}")
