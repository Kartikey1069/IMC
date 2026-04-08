# Algorithmic Trading Step-by-Step Study Guide

Welcome! If you have no prior experience with trading, statistics, or building trading bots, this guide is completely tailored for you. We will go through everything you need to know about what your trading bot (`trader.py`) is doing, why it's making those decisions, and the basic stats behind it.

---

## 1. The Core Concepts (No Math Required!)

Before we look at code, let's understand how a market works using a simple analogy: **The Grocery Store**.

### The Order Book
Imagine you are at an open-air market buying and selling Tomatoes.
Some people are constantly shouting prices they are willing to *pay* to buy a tomato.
Other people are shouting prices they are willing to *accept* to sell a tomato.

The **Order Book** is simply a digital list recording all of these shouts.

### Best Bid vs. Best Ask
- **Bid**: An offer to *buy*. The highest price among all buyers is called the **Best Bid**. It’s the highest someone is currently willing to pay. 
- **Ask**: An offer to *sell*. The lowest price among all sellers is called the **Best Ask**. It’s the cheapest you can currently buy a tomato for.
- **Spread**: The difference between the Best Bid and the Best Ask. If the highest buyer is bidding $9 and the lowest seller is asking $11, the spread is $2.

---

## 2. The Data Metrics Used (Features)

The Python script uses certain pieces of historical and real-time data to make its decisions. Knowing what these components represent is critical for optimization later on:

### The "Mid-Price" (Fair Value Estimate)
If the highest someone is willing to pay is $9, and the lowest someone is willing to sell is $11... what is the tomato *actually* worth? 

In statistics and algorithmic trading, a common and highly effective way to estimate value is to take the absolute average of these two numbers.
*(Best Bid + Best Ask) / 2 = Mid-Price*.
*(9 + 11) / 2 = 10*.

Your script uses the **Mid-Price** as its **"Fair Value" or "Acceptable Price"**. It assumes that the item is statistically worth exactly the middle of the best available prices.

### Position Limits (Inventory)
Exchanges usually don't let you buy an infinite amount of an item to protect against market manipulation or reckless borrowing. You have a **Position Limit** (e.g. 20).
- You cannot own more than 20 tomatoes simultaneously (**Long** position limit).
- You cannot owe more than 20 items simultaneously (**Short** position limit).

Your algorithm checks your `current_position` before ordering to calculate exactly how many items to buy/sell without triggering a penalty.

---

Searching for prices_round_0_day_-1.csv...
✅ Successfully read 20000 rows from prices_round_0_day_-1.csv
============================================================
📊 DATA METRICS FOR: TOMATOES
  - Average Mid-Price : 4977.57
  - Minimum Price     : 4946.50
  - Maximum Price     : 5011.00
  - Average Spread    : 12.98 (gap between buyers and sellers)
  - Overall Imbalance : -0.01 (Positive = High demand / Negative = Over-supply)
  💡 CONCLUSION: This asset is VOLATILE. Use Moving Averages to track it!
------------------------------------------------------------
📊 DATA METRICS FOR: EMERALDS
  - Average Mid-Price : 10000.00
  - Minimum Price     : 9996.00
  - Maximum Price     : 10004.00
  - Average Spread    : 15.74 (gap between buyers and sellers)
  - Overall Imbalance : -0.01 (Positive = High demand / Negative = Over-supply)
  💡 CONCLUSION: This asset is VOLATILE. Use Moving Averages to track it!
------------------------------------------------------------

Searching for prices_round_0_day_-2.csv...
✅ Successfully read 20000 rows from prices_round_0_day_-2.csv
============================================================
📊 DATA METRICS FOR: EMERALDS
  - Average Mid-Price : 10000.00
  - Minimum Price     : 9996.00
  - Maximum Price     : 10004.00
📊 DATA METRICS FOR: TOMATOES
  - Average Mid-Price : 5007.95
  - Minimum Price     : 4988.00
  - Maximum Price     : 5036.00
  - Average Spread    : 13.07 (gap between buyers and sellers)
  - Overall Imbalance : 0.00 (Positive = High demand / Negative = Over-supply)
  💡 CONCLUSION: This asset is VOLATILE. Use Moving Averages to track it!
------------------------------------------------------------






## 3. The Strategy (Dual Market Approach)

One of the most dangerous things you can do in algorithmic trading is treat two different assets the exact same way. Based on our data analysis, we learned:
- **EMERALDS** are a **Mean-Reverting** (stable) asset perfectly pegged to `10000`.
- **TOMATOES** are a **Trending** (volatile) asset whose value heavily shifts over the day.

We cannot use the same math! Therefore, our `run()` method uses a "Dual-Strategy".

### Strategy 1: The Mean-Reversion Anchor (EMERALDS)
Since we know Emeralds literally never stray far from `10000`, we abandon complex math. 
If the price ever dips to `9998` or lower, we aggressively buy them, because it's guaranteed to rubber-band back! If they ever spike to `10002`, we aggressively short-sell them.

### Strategy 2: Moving Average Crossovers (TOMATOES)
Because Tomatoes rapidly shift their value, we must calculate the "Trend". 
We calculate the **Short Moving Average (10 ticks)** and the **Long Moving Average (50 ticks)**.
- **Buying Condition:** If the short-term trend violently crosses *above* the long-term trend, momentum is swinging up! This is a buy signal.
- **Selling Condition:** If the short-term trend dives *underneath* the long-term trend, the market is panicking down! This is a sell signal to exit your positions.

---

## 4. Code Walkthrough (`trader.py`)

To calculate a 50-tick moving average, our bot needs a "Memory". 
The IMC container normally wipes all memory clean every time it calls your bot.
**The Secret:** The system provides you a string variable called `traderData`. By using Python's `json` dictionary converter, we can secretly store 50 prices in a python list, convert it to a string, hand it back to the system, and ask for it back on the next tick!

```python
# 1. LOAD OUR MEMORY: Convert the system-provided string back into a Python Dictionary
try:
    trader_data_dict = json.loads(state.traderData)
except json.JSONDecodeError:
    trader_data_dict = {"tomato_prices": []} # Fresh start!

# 2. Add our new data to Memory!
trader_data_dict["tomato_prices"].append(mid_price)

# 3. Calculate out the 50-tick and 10-tick Averages!
short_ma = sum(trader_data_dict["tomato_prices"][-10:]) / 10
long_ma = sum(trader_data_dict["tomato_prices"]) / 50

# 4. Momentum Detect! Buy when short jumps over long.
if short_ma > long_ma:
    buy_quantity = min(-best_ask_amount, available_to_buy)
    orders.append(Order(product, best_ask, buy_quantity))

# 5. SAVE OUR MEMORY: Lock our memory back into a raw string to give back to the IMC framework!
new_trader_data_string = json.dumps(trader_data_dict)
return result, conversions, new_trader_data_string
```

## 5. Local Testing using `datamodel.py`

To test your `trader.py` algorithm on your own machine without waiting for the competition servers, you need a way to **mock the market simulator**. That's exactly what `datamodel.py` is for!

`datamodel.py` contains all the blueprints (Classes like `OrderDepth`, `Trade`, `TradingState`, etc.) that the competition server normally uses. 

Because we have this blueprint file saved locally, you can create a simple local test script that builds a fake `TradingState` and feeds it into your `Trader` class just like the server would, like so:

```python
from trader import Trader
from datamodel import TradingState, OrderDepth

# 1. Create a fake market state
fake_order_depths = {
    "TOMATOES": OrderDepth() 
    # (In a real test, you would add fake buy/sell orders here to trick your bot into making a trade!)
}

# 2. Package it into a State identical to what the engine provides
state = TradingState(
    traderData="", 
    timestamp=1000, 
    listings={}, 
    order_depths=fake_order_depths, 
    own_trades={}, 
    market_trades={}, 
    position={"TOMATOES": 5}, 
    observations={}
)

# 3. Run your bot locally!
trader = Trader()
orders, conversions, traderData = trader.run(state)

print("Orders placed by bot:", orders)
```

By tweaking the simulated `best_ask` and `best_bid` values in your mock code, you can easily ensure your bot buys and sells exactly when it's supposed to.

---

## 6. How to Use the Historical "Order Book" and "Trades" Data

If you've been given historical data (like a spreadsheet of past Order Books and Trades), it is arguably your most powerful tool. You shouldn't just guess your `acceptable_price` formula—you should prove it using this data!

Here are the specific patterns and analyses you need to perform on your historical data files:

### A. Is the Price "Pegged" or "Volatile"? (Price Discovery)
The very first thing you need to do is calculate the Mid-Price for every row in your historical Order Book data and plot it on a line graph.
- **The Flatline Pattern (Pegged):** If you plot `EMERALDS` and notice the mid-price is *always* perfectly hovering around 10,000 all day long, you have discovered a massive pattern. Instead of calculating `acceptable_price = (best_bid + best_ask)/2`, you can hardcode `acceptable_price = 10000`. This means you will aggressively buy anytime it drops to 9,998 and sell when it hits 10,002.
- **The Wavy Pattern (Mean Reverting):** `TOMATOES` might look like a rollercoaster. If it goes up and down but always returns to the center, you need to calculate a **Simple Moving Average (SMA)** over the last 10 minutes of data to serve as your `acceptable_price`.

### B. Order Book Imbalance (Predicting the Future)
Look at the *amounts* in your historical order book, not just the prices. 
- **The Pattern:** If the Order Book currently has 100 people wanting to buy tomatoes, but only 2 people wanting to sell tomatoes... what will happen to the price in the next few seconds? It will shoot up!
- **How to use it:** You can do math on historical data to prove this. If you calculate `Imbalance = (Total Buy Amount) - (Total Sell Amount)`, you might discover a pattern where extreme buy imbalances *always* precede a price spike. You can code your bot to buy heavily when it spots this imbalance!

### C. Analyzing the "Trades" Data
The Trades data shows you trades that *actually happened* (the matches).
- **Finding Resistance:** Look at the trade data to see the maximum price `TOMATOES` ever reached. Let's say tomatoes never sold above $150. If the price reaches $148, you know a drop is coming, so you immediately sell your whole inventory.
- **Competitor Bots:** The market trades let you see where the *other* bots are willing to trade. If you see a lot of trades constantly executing at a specific price bracket, that tells you the parameters your competitors are using.

**Your Action Item:** Open your historical data in Python using a library like `pandas` (or just load it in Excel!) and create a simple line chart of the prices. Look at `EMERALDS` vs `TOMATOES` and immediately you will see what their fundamental behavior is!

- **Try adjusting the `acceptable_price` formula!** For example, what happens if you make the formula `((best_ask * 0.4) + (best_bid * 0.6))`? 
- Try tracking **Moving Averages**, which is taking the value of `acceptable_price` over the past 5 iterations and generating an average. This gives your formula "historical memory" rather than just looking at the exact second it executes!

