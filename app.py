import streamlit as st
import random
import time

st.set_page_config(page_title="Stock Market Prototype", layout="wide")

# ------------ INITIALIZE SESSION STATE ------------
if "balance" not in st.session_state:
    st.session_state.balance = 100000   # virtual money
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {}     # stock -> qty
if "prices" not in st.session_state:
    st.session_state.prices = {
        "RELIANCE": 2500,
        "TCS": 3600,
        "HDFC": 1600,
        "INFY": 1500,
    }
if "history" not in st.session_state:
    st.session_state.history = []
if "last_update" not in st.session_state:
    st.session_state.last_update = time.time()


# ------------ PRICE ENGINE (SIMULATED MARKET) ------------
def update_prices():
    for stock in st.session_state.prices:
        change = random.uniform(-5, 5)
        st.session_state.prices[stock] = max(
            1, round(st.session_state.prices[stock] + change, 2)
        )


# auto update every second
if time.time() - st.session_state.last_update >= 1:
    update_prices()
    st.session_state.last_update = time.time()


# ------------ LAYOUT ------------
st.title("📈 Stock Market Prototype (Live Simulation)")

col1, col2 = st.columns(2)

# ------------ MARKET DASHBOARD ------------
with col1:
    st.subheader("Live Market Prices")
    for stock, price in st.session_state.prices.items():
        st.metric(stock, f"₹{price}")

# ------------ PORTFOLIO ------------
with col2:
    st.subheader("Your Portfolio")
    st.write(f"💰 Balance: **₹{round(st.session_state.balance,2)}**")

    if st.session_state.portfolio:
        for stock, qty in st.session_state.portfolio.items():
            price = st.session_state.prices[stock]
            st.write(f"{stock}: {qty} shares  (₹{round(qty * price,2)})")
    else:
        st.write("No stocks yet.")


st.divider()

# ------------ TRADING PANEL ------------
st.subheader("Place Trade")

stock = st.selectbox("Select Stock", list(st.session_state.prices.keys()))
order_type = st.radio("Order Type", ["BUY", "SELL"])
qty = st.number_input("Quantity", min_value=1, step=1)

current_price = st.session_state.prices[stock]
st.info(f"Current Price: ₹{current_price}")

if st.button("Confirm Order"):
    total_cost = qty * current_price

    # BUY LOGIC
    if order_type == "BUY":
        if st.session_state.balance >= total_cost:
            st.session_state.balance -= total_cost
            st.session_state.portfolio[stock] = (
                st.session_state.portfolio.get(stock, 0) + qty
            )
            st.success(f"Bought {qty} {stock} at ₹{current_price}")
            st.session_state.history.append(
                ("BUY", stock, qty, current_price)
            )
        else:
            st.error("Not enough balance!")

    # SELL LOGIC
    else:
        if st.session_state.portfolio.get(stock, 0) >= qty:
            st.session_state.portfolio[stock] -= qty
            st.session_state.balance += total_cost
            st.success(f"Sold {qty} {stock} at ₹{current_price}")
            st.session_state.history.append(
                ("SELL", stock, qty, current_price)
            )
        else:
            st.error("You don't own enough shares!")

st.divider()

# ------------ TRADE HISTORY ------------
st.subheader("Trade History")
if st.session_state.history:
    for h in st.session_state.history[::-1]:
        st.write(f"{h[0]} — {h[1]} — {h[2]} shares @ ₹{h[3]}")
else:
    st.write("No trades yet.")
