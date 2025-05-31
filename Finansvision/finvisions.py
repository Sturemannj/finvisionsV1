# Extended FinVisions with Local Login Authentication (no Courier)

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from PIL import Image
import plotly.graph_objects as go
import plotly.express as px
import datetime
from fpdf import FPDF
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import plotly.io as pio
import os

# === Streamlit Layout ===
st.set_page_config(layout="wide")

# === LOCAL LOGIN SYSTEM ===
def login():
    st.sidebar.header("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username == "Vebjorn.store" and password == "Jeglikerida123":
            st.session_state.logged_in = True
        else:
            st.error("Feil brukernavn eller passord.")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
    st.stop()

# === Sidebar: Logo + Input ===
logo_path = r"C:\\Users\\Tom Steinar\\Desktop\\koder\\bilder\\FinVisions.png"
logo = Image.open(logo_path)
with st.sidebar:
    st.image(logo, width=160)
    st.header("Stock Analysis Settings")
    tickerSymbol = st.text_input("Enter Stock Symbol", 'GOOGL')
    start_date = st.date_input("Start Date", datetime.date(2010, 1, 1))
    end_date = st.date_input("End Date", datetime.date.today())

# === HEADER ===
st.title("FinVisions: Total Market Domination™")
st.markdown("### Advanced Financial Analysis and Visualization Hub for Power Traders")

# === DATA ===
tickerData = yf.Ticker(tickerSymbol)
tickerDf = tickerData.history(period='1d', start=start_date, end=end_date)
st.header(f"Data Preview for {tickerSymbol}")
st.dataframe(tickerDf.head())

# === FUNDAMENTALS ===
st.header(f"Company Fundamentals: {tickerSymbol}")
info = tickerData.info
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"**Sector:** {info.get('sector', 'N/A')}")
    st.markdown(f"**Industry:** {info.get('industry', 'N/A')}")
    st.markdown(f"**Market Cap:** ${info.get('marketCap', 0):,}")
with col2:
    st.markdown(f"**P/E Ratio:** {info.get('trailingPE', 'N/A')}")
    st.markdown(f"**P/B Ratio:** {info.get('priceToBook', 'N/A')}")
    st.markdown(f"**PEG Ratio:** {info.get('pegRatio', 'N/A')}")
with col3:
    st.markdown(f"**Debt/Equity:** {info.get('debtToEquity', 'N/A')}")
    st.markdown(f"**ROE:** {info.get('returnOnEquity', 'N/A')}")
    st.markdown(f"**Dividend Yield:** {info.get('dividendYield', 'N/A')}")

# === Charts ===
st.header("Closing Price")
fig_close = px.line(tickerDf, x=tickerDf.index, y="Close")
st.plotly_chart(fig_close, use_container_width=True)

st.header("Trading Volume")
fig_volume = px.bar(tickerDf, x=tickerDf.index, y="Volume")
st.plotly_chart(fig_volume, use_container_width=True)

# === Moving Averages ===
st.header("Moving Averages")
short_window = st.sidebar.slider('Short MA (Days)', 10, 100, 50)
long_window = st.sidebar.slider('Long MA (Days)', 100, 300, 200)
tickerDf['Short_MA'] = tickerDf['Close'].rolling(window=short_window).mean()
tickerDf['Long_MA'] = tickerDf['Close'].rolling(window=long_window).mean()
fig_ma = go.Figure()
fig_ma.add_trace(go.Scatter(x=tickerDf.index, y=tickerDf['Close'], name='Close'))
fig_ma.add_trace(go.Scatter(x=tickerDf.index, y=tickerDf['Short_MA'], name=f'{short_window}-Day MA'))
fig_ma.add_trace(go.Scatter(x=tickerDf.index, y=tickerDf['Long_MA'], name=f'{long_window}-Day MA'))
fig_ma.update_layout(xaxis_title="Date", yaxis_title="Price")
st.plotly_chart(fig_ma, use_container_width=True)

# === Bollinger Bands ===
st.header("Bollinger Bands")
boll_window = st.sidebar.slider('Bollinger Window', 10, 100, 20)
std_dev = st.sidebar.slider('Std Dev', 1, 3, 2)
tickerDf['MA20'] = tickerDf['Close'].rolling(window=boll_window).mean()
tickerDf['Upper_Band'] = tickerDf['MA20'] + tickerDf['Close'].rolling(window=boll_window).std() * std_dev
tickerDf['Lower_Band'] = tickerDf['MA20'] - tickerDf['Close'].rolling(window=boll_window).std() * std_dev
fig_boll = go.Figure()
fig_boll.add_trace(go.Scatter(x=tickerDf.index, y=tickerDf['Close'], name='Close'))
fig_boll.add_trace(go.Scatter(x=tickerDf.index, y=tickerDf['Upper_Band'], name='Upper Band', line=dict(dash='dot')))
fig_boll.add_trace(go.Scatter(x=tickerDf.index, y=tickerDf['Lower_Band'], name='Lower Band', line=dict(dash='dot')))
fig_boll.add_trace(go.Scatter(x=tickerDf.index, y=tickerDf['MA20'], name='20-Day MA'))
fig_boll.update_layout(xaxis_title="Date", yaxis_title="Price")
st.plotly_chart(fig_boll, use_container_width=True)

# === RSI ===
st.header("Relative Strength Index (RSI)")
rsi_period = st.sidebar.slider('RSI Period', 10, 50, 14)
delta = tickerDf['Close'].diff()
gain = delta.where(delta > 0, 0).rolling(window=rsi_period).mean()
loss = -delta.where(delta < 0, 0).rolling(window=rsi_period).mean()
rs = gain / loss
rsi = 100 - (100 / (1 + rs))
fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=tickerDf.index, y=rsi, name='RSI'))
fig_rsi.update_layout(xaxis_title="Date", yaxis_title="RSI")
st.plotly_chart(fig_rsi, use_container_width=True)

# === Dividend History ===
st.header("Dividend History")
dividends = tickerData.dividends
if dividends is not None and not dividends.empty:
    fig_div = px.bar(dividends, x=dividends.index, y=dividends.values)
    st.plotly_chart(fig_div, use_container_width=True)
else:
    st.info("No dividend data available.")

# === Earnings History ===
st.header("Earnings Over Time")
earnings = tickerData.earnings
if earnings is not None and not earnings.empty:
    st.bar_chart(earnings['Revenue'], use_container_width=True)
else:
    st.info("No earnings data available.")

# === Compare Stocks ===
st.header("Compare Multiple Stocks")
compare_symbols = st.sidebar.text_area("Multiple Symbols (comma-separated)", "AAPL,AMZN,MSFT,NVDA")
symbols = [s.strip().upper() for s in compare_symbols.split(",")]
compare_data = {}
for sym in symbols:
    try:
        df = yf.Ticker(sym).history(start=start_date, end=end_date)
        compare_data[sym] = df['Close']
    except:
        continue
compare_df = pd.DataFrame(compare_data)
st.line_chart(compare_df, use_container_width=True)

# === Forecasting ===
st.header("Price Forecasting (Linear Regression)")
forecast_days = st.slider("Days to Forecast", 1, 60, 30)
df = tickerDf[['Close']].dropna()
df['Prediction'] = df['Close'].shift(-forecast_days)
X = np.array(df.drop(['Prediction'], axis=1))[:-forecast_days]
y = np.array(df['Prediction'])[:-forecast_days]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = LinearRegression()
model.fit(X_train, y_train)
future = df.drop(['Prediction'], axis=1)[-forecast_days:]
forecast = model.predict(future)
st.line_chart(pd.DataFrame({'Forecast': forecast}, index=pd.date_range(start=tickerDf.index[-1], periods=forecast_days + 1, freq='B')[1:]))

# === Export CSV ===
st.header("Download Data")
csv = tickerDf.to_csv().encode('utf-8')
st.download_button("Download CSV", data=csv, file_name=f'{tickerSymbol}_data.csv', mime='text/csv')

# === Export PDF ===
def generate_plot_images(figures, names):
    paths = []
    for fig, name in zip(figures, names):
        path = f"{name}.png"
        pio.write_image(fig, path, format="png", width=900, height=500)
        paths.append(path)
    return paths

def generate_pdf_report(df, symbol, images):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Stock Report: {symbol}", ln=True, align='C')
    for idx, row in df.head(10).iterrows():
        pdf.cell(200, 10, txt=f"{idx.date()} | Close: {row['Close']:.2f} | Volume: {row['Volume']}", ln=True)
    for img in images:
        pdf.add_page()
        pdf.image(img, x=10, y=25, w=180)
    file = f"{symbol}_report.pdf"
    pdf.output(file)
    return file

if st.button("Generate Full PDF Report"):
    figs = [fig_close, fig_volume, fig_ma, fig_boll, fig_rsi]
    names = ['close', 'volume', 'ma', 'boll', 'rsi']
    images = generate_plot_images(figs, names)
    file = generate_pdf_report(tickerDf, tickerSymbol, images)
    with open(file, "rb") as f:
        st.download_button("Download PDF Report", f, file_name=file)
    for img in images:
        os.remove(img)

st.markdown("**FinVisions © 2025 – Built by Dominance.**")
