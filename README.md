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
- You cannot owe more than 20 tomatoes simultaneously (**Short** position limit).

Your algorithm tracks your `current_position` as a feature to securely calculate exactly how many items to buy/sell without triggering a penalty.

---

## 3. The Strategy: "Statistical Market Taking"

Your script follows one primary psychological principle: **It looks for deals where others mispriced their items.**

Here’s the step-by-step logic your `run()` function performs 1,000 times a second:

1. **Calculate the True Value:** It scans the Order Book, finds the Best Bid and Best Ask, and calculates the `acceptable_price` (the Mid-Price).
2. **Scan for Cheap Assets (Buy Logic):** It looks at the Best Ask. If a seller is asking for less money than the `acceptable_price`, the script immediately snaps it up! It buys the cheap item because it believes it's worth more.
3. **Scan for Overpaying Buyers (Sell Logic):** It looks at the Best Bid. If a buyer is willing to pay *more* than the `acceptable_price`, your script will immediately drop what it's holding and sell to them at this premium markup.
4. **Enforce Rules**: Before every trade, it mathematically ensures you have enough "Position Limit" capacity left.

This is fundamentally how your algorithm ensures you slowly chip away a profit! It buys underpriced assets and sells overpriced ones.

---

## 4. Code Walkthrough (`trader.py`)

If you want to edit or tune the script yourself, here is a line-by-line explanation of the most important block!

```python
# 1. We grab the cheapest sale price (best_ask) and the highest purchase price (best_bid).
best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]

# 2. We calculate our Fair Value (Mid-Price).
acceptable_price = (best_ask + best_bid) / 2

# 3. We check if the cheapest item being sold is CHEAPER than its True Fair Value.
if int(best_ask) < acceptable_price:

    # 4. We calculate how many we're allowed to buy based on our limit constraint (e.g., Limit 20)
    available_to_buy_capacity = position_limit - current_position
    
    if available_to_buy_capacity > 0:
        # 5. Determine the precise quantity to buy and submit the Order
        # We buy the amount the seller is selling (-best_ask_amount), OR whatever capacity we have left.
        buy_quantity = min(-best_ask_amount, available_to_buy_capacity)
        orders.append(Order(product, best_ask, buy_quantity))
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

## Next Testing Steps

- **Try adjusting the `acceptable_price` formula!** For example, what happens if you make the formula `((best_ask * 0.4) + (best_bid * 0.6))`? 
- Try tracking **Moving Averages**, which is taking the value of `acceptable_price` over the past 5 iterations and generating an average. This gives your formula "historical memory" rather than just looking at the exact second it executes!

