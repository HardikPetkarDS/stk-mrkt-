import streamlit as st
import random
import time
import pandas as pd
from collections import defaultdict, deque

st.set_page_config(page_title="Advanced Stock Market Simulator", layout="wide")

# ------------------ SESSION STATE ------------------
if "balance" not in st.session_state:
    st.session_state.balance = 100000

if "portfolio" not in st.session_state:
    st.session_state.portfolio = defaultdict(int)

if "prices" not in st.session_state:
    st.session_state.prices = {"RELIANCE": 2500, "TCS": 3600, "HDFC": 1600, "INFY": 1500}

if "order_book" not in st.session_state:
    st.session_state.order_book = {
        s: {"buy": deque(), "sell": deque()} for s in st.session_state.prices
    }

if "trades" not in st.session_state:
    st.session_state.trades = []

if "price_history" not in st.session_state:
    st.session_state.price_history = {s: [] for s in st.session_state.prices}

if "last_update" not in st.session_state:
    st.session_state.last_update = time.time()

# ------------------ PRICE ENGINE ------------------
def update_prices():
    for s in st.session_state.prices:
        change = random.uniform(-3, 3)
        st.session_state.prices[s] = max(
            1, round(st.session_state.prices[s] + change, 2)
        )
        st.session_state.price_history[s].append(st.session_state.prices[s])

# auto update every second
if time.time() - st.session_state.last_update >= 1:
    update_prices()
    st.session_state.last_update = time.time()

# ------------------ MATCHING ENGINE ------------------
def match_orders(symbol):
    book = st.session_state.order_book[symbol]
    
    while book["buy"] and book["sell"]:
        buy = book["buy"][0]
        sell = book["sell"][0]

        if buy["price"] >= sell["price"]:
            trade_price = sell["price"]
            qty = min(buy["qty"], sell["qty"])

            # update quantities
            buy["qty"] -= qty
            sell["qty"] -= qty

            # portfolio adjustments
            st.session_state.portfolio[buy["user"]] += qty
            st.session_state.portfolio[sell["user"]] -= qty

            # balance adjustments
            st.session_state.balance -= qty * trade_price
            st.session_state.balance += qty * trade_price

            st.session_state.trades.append(
                {"symbol": symbol, "price": trade_price, "qty": qty}
            )

            if buy["qty"] == 0:
                book["buy"].popleft()
            if sell["qty"] == 0:
                book["sell"].popleft()
        else:
            break

# ------------------ UI ------------------
st.title("📈 Advanced Stock Market Prototype")

left, right = st.columns([2, 2])

# MARKET PANEL
with left:
    st.subheader("Live Market")
    for s, p in st.session_state.prices.items():
        st.metric(s, f"₹{p}")

    st.subheader("Price Chart")
    symbol = st.selectbox("Select stock", list(st.session_state.prices.keys()))
    if st.session_state.price_history[symbol]:
        st.line_chart(st.session_state.price_history[symbol])

# TRADING PANEL
with right:
    st.subheader("Trade")

    stock = st.selectbox("Stock", list(st.session_state.prices.keys()), key="trade_stock")
    order_kind = st.radio("Order Type", ["Market", "Limit"])
    side = st.radio("Side", ["Buy", "Sell"])
    qty = st.number_input("Quantity", min_value=1, step=1)

    price = None
    if order_kind == "Limit":
        price = st.number_input("Limit Price", min_value=1.0)

    if st.button("Place Order"):
        entry = {
            "user": "YOU",
            "qty": qty,
            "price": price if price else st.session_state.prices[stock],
        }

        if side == "Buy":
            st.session_state.order_book[stock]["buy"].append(entry)
        else:
            st.session_state.order_book[stock]["sell"].append(entry)

        match_orders(stock)
        st.success("Order placed!")

st.divider()

# ORDER BOOK
st.subheader("Order Book")
for s in st.session_state.order_book:
    st.write(f"### {s}")
    book = st.session_state.order_book[s]

    buys = [{"price": o["price"], "qty": o["qty"]} for o in book["buy"]]
    sells = [{"price": o["price"], "qty": o["qty"]} for o in book["sell"]]

    st.write("**Buy Orders**")
    st.dataframe(pd.DataFrame(buys) if buys else pd.DataFrame())

    st.write("**Sell Orders**")
    st.dataframe(pd.DataFrame(sells) if sells else pd.DataFrame())

st.divider()

# TRADE HISTORY
st.subheader("Trades")
if st.session_state.trades:
    st.table(pd.DataFrame(st.session_state.trades))
else:
    st.write("No trades yet.")
