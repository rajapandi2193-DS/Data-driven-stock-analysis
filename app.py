import streamlit as st
import pandas as pd
import yaml
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="Stock Dashboard", layout="wide")

# =========================
# LOAD DATA
# =========================
RAW_DATA_DIR = "data/raw"
all_stocks = []

for month in os.listdir(RAW_DATA_DIR):
    month_path = os.path.join(RAW_DATA_DIR, month)
    if os.path.isdir(month_path):
        for file in os.listdir(month_path):
            if file.endswith((".yaml", ".yml")):
                with open(os.path.join(month_path, file), "r") as f:
                    content = yaml.safe_load(f)
                    if isinstance(content, list):
                        all_stocks.extend(content)

df = pd.DataFrame(all_stocks)
# -----------------------
# STANDARDIZE COLUMNS
# -----------------------
df.columns = df.columns.str.strip().str.lower()

# auto-detect symbol column
if "symbol" not in df.columns:
    possible_symbol_cols = ["ticker", "stock", "stock_name", "name", "symbol_name"]
    for col in possible_symbol_cols:
        if col in df.columns:
            df = df.rename(columns={col: "symbol"})
            break

# safety check
if "symbol" not in df.columns:
    st.error("❌ No symbol column found in dataset")
    st.write("Available columns:", df.columns.tolist())
    st.stop()

df.columns = df.columns.str.strip().str.lower()
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["symbol", "date"])

# =========================
# CALCULATIONS
# =========================
returns = (
    df.groupby("symbol")["close"]
    .apply(lambda x: (x.iloc[-1] - x.iloc[0]) / x.iloc[0])
    .sort_values(ascending=False)
)

top_10_green = returns.head(10)
top_10_red = returns.tail(10)

df["daily_return"] = df.groupby("symbol")["close"].pct_change()
volatility = (
    df.groupby("symbol")["daily_return"]
    .std()
    .sort_values(ascending=False)
    .head(10)
)

# =========================
# HEADER
# =========================
st.title("📈 Stock Performance Dashboard")
st.caption("Nifty 50 – One Year Market Analysis")

# =========================
# KPI METRICS
# =========================
c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Stocks", returns.count())
c2.metric("Green Stocks", (returns > 0).sum())
c3.metric("Red Stocks", (returns < 0).sum())
c4.metric("Avg Price", round(df["close"].mean(), 2))

st.divider()

# =========================
# TOP 10 GREEN & RED
# =========================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🟢 Top 10 Gainers")
    st.dataframe(top_10_green.rename("Yearly Return"))

    fig, ax = plt.subplots()
    top_10_green.plot(kind="barh", ax=ax)
    ax.set_xlabel("Return")
    ax.set_ylabel("Stock")
    st.pyplot(fig)

with col2:
    st.subheader("🔴 Top 10 Losers")
    st.dataframe(top_10_red.rename("Yearly Return"))

    fig, ax = plt.subplots()
    top_10_red.plot(kind="barh", ax=ax)
    ax.set_xlabel("Return")
    ax.set_ylabel("Stock")
    st.pyplot(fig)

st.divider()

# =========================
# VOLATILITY
# =========================
st.subheader("📊 Top 10 Most Volatile Stocks")

fig, ax = plt.subplots(figsize=(8, 4))
volatility.plot(kind="bar", ax=ax)
ax.set_ylabel("Volatility (Std Dev)")
ax.set_xlabel("Stock")
st.pyplot(fig)

# =========================
# RAW DATA PREVIEW
# =========================
with st.expander("🔍 View Raw Data"):
    st.dataframe(df.head(100))
