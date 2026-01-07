import streamlit as st
import random
import time
import pandas as pd
from collections import defaultdict, deque

st.set_page_config(page_title="Advanced Stock Market Simulator", layout="wide")

placeholder = st.empty()
time.sleep(1)




# ------------------ SESSION STATE ------------------
if "balance" not in st.session_state:
    st.session_state.balance = 100000

if "portfolio" not in st.session_state:
    st.session_state.portfolio = defaultdict(int)

if "prices" not in st.session_state:
    st.session_state.prices = {"RELIANCE": 2500, "TCS": 3600, "HDFC": 1600, "INFY": 1500}

if "order_book" not in st.session_state:
    st.session_state.order_book = {s: {"buy": deque(), "sell": deque()} 
                                   for s in st.session_state.prices}

if "trades" not in st.session_state:
    st.session_state.trades = []

if "price_history" not in st.session_state:
    st.session_state.price_history = {s: [] for s in st.session_state.prices}

if "last_update" not in st.session_state:
    st.session_state.last_update = time.time()

# ------------------ PRICE ENGINE ------------------
def update_prices():
    for s in st.session_state.prices:
        change = random.uniform(-4, 4)
        st.session_state.prices[s] = max(1, round(st.session_state.prices[s] + change, 2))
        st.session_state.price_history[s].append(st.session_state.prices[s])

if time.time() - st.session_state.last_update >= 1:
    update_prices()
    st.session_state.last_update = time.time()

# ------------------ MATCHING ENGINE ------------------
def match_orders(symbol):
    book = st.session_state.order_book[symbol]

    # sort buy high→low, sell low→high
    book["buy"] = deque(sorted(book["buy"], key=lambda x: -x["price"]))
    book["sell"] = deque(sorted(book["sell"], key=lambda x: x["price"]))

    while book["buy"] and book["sell"]:
        buy = book["buy"][0]
        sell = book["sell"][0]

        if buy["price"] >= sell["price"]:
            trade_price = sell["price"]
            qty = min(buy["qty"], sell["qty"])

            buy["qty"] -= qty
            sell["qty"] -= qty

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
st.title("📈 Advanced Stock Market Simulator (Live)")

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
    st.subheader("Place Order")

    stock = st.selectbox("Stock", list(st.session_state.prices.keys()))
    side = st.radio("Side", ["Buy", "Sell"])
    order_type = st.radio("Order Type", ["Market", "Limit"])
    qty = st.number_input("Quantity", min_value=1)

    price = st.session_state.prices[stock] if order_type == "Market" \
            else st.number_input("Limit Price", min_value=1.0)

    if st.button("Submit Order"):
        entry = {"price": price, "qty": qty}

        if side == "Buy":
            st.session_state.order_book[stock]["buy"].append(entry)
        else:
            st.session_state.order_book[stock]["sell"].append(entry)

        match_orders(stock)
        st.success("Order submitted!")

st.divider()

# ORDER BOOK
st.subheader("Order Book (Live)")
for s in st.session_state.order_book:
    st.write(f"### {s}")

    buys = [{"price": o["price"], "qty": o["qty"]} for o in st.session_state.order_book[s]["buy"]]
    sells = [{"price": o["price"], "qty": o["qty"]} for o in st.session_state.order_book[s]["sell"]]

    st.write("**Buy Orders**")
    st.dataframe(pd.DataFrame(buys))

    st.write("**Sell Orders**")
    st.dataframe(pd.DataFrame(sells))

st.divider()

# TRADE HISTORY
st.subheader("Trades")
if st.session_state.trades:
    st.table(pd.DataFrame(st.session_state.trades))
else:
    st.write("No trades yet.")
