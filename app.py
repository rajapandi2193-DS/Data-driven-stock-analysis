import streamlit as st
import pandas as pd
import yaml
import os

st.title("📈 Stock Price Analysis Dashboard")

# -----------------------
# LOAD YAML DATA
# -----------------------
RAW_DATA_DIR = "data/raw"
all_stocks = []

for month_folder in os.listdir(RAW_DATA_DIR):
    month_path = os.path.join(RAW_DATA_DIR, month_folder)

    if os.path.isdir(month_path):
        for file in os.listdir(month_path):
            if file.endswith(".yaml") or file.endswith(".yml"):
                file_path = os.path.join(month_path, file)

                with open(file_path, "r") as f:
                    content = yaml.safe_load(f)

                    if isinstance(content, list):
                        all_stocks.extend(content)

df = pd.DataFrame(all_stocks)

df.columns = df.columns.str.strip().str.lower()
df = df.rename(columns={"ticker": "symbol"})  # <-- mapping

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["symbol", "date"])


# -----------------------
# YEARLY RETURNS
# -----------------------
returns = (
    df.groupby("symbol")["close"]
      .apply(lambda x: (x.iloc[-1] - x.iloc[0]) / x.iloc[0])
      .sort_values(ascending=False)
)

st.subheader("Yearly Returns (Sample)")
st.dataframe(returns.head(10))

# -----------------------
# TOP 10 GREEN & RED
# -----------------------
top_10_green = returns.head(10)
top_10_red = returns.tail(10)

st.subheader("Top 10 Green Stocks")
st.dataframe(top_10_green)

st.subheader("Top 10 Red Stocks")
st.dataframe(top_10_red)

# -----------------------
# MARKET SUMMARY
# -----------------------
market_summary = {
    "Total Stocks": int(returns.count()),
    "Green Stocks": int((returns > 0).sum()),
    "Red Stocks": int((returns < 0).sum()),
    "Average Price": round(df["close"].mean(), 2),
    "Average Volume": int(df["volume"].mean())
}

st.subheader("Market Summary")
st.json(market_summary)
