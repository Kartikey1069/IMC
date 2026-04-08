from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import json

class Trader:

    def bid(self):
        return 15

    def run(self, state: TradingState):
        """
        The main trading logic for the competition.
        Implements a Dual-Pronged Strategy based on data analysis:
        - EMERALDS: Mean-Reverting logic (Hardcoded Fair Value bounds)
        - TOMATOES: Momentum / Moving Average logic (Tracking State)
        """
        result = {}
        
        # Position limits
        POSITION_LIMIT = 20

        # --- MEMORY (STATE TRACKING) ---
        # The IMC environment does not persist variables normally across 'runs'.
        # We must deserialize the system-provided traderData string into a python dictionary!
        if state.traderData == "":
            trader_data_dict = {"tomato_prices": []}
        else:
            try:
                trader_data_dict = json.loads(state.traderData)
            except json.JSONDecodeError:
                trader_data_dict = {"tomato_prices": []}


        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            
            current_position = state.position.get(product, 0)
            
            # Must ensure there is data in the order book before evaluating prices
            if len(order_depth.sell_orders) == 0 or len(order_depth.buy_orders) == 0:
                continue

            # In Python, dictionaries representing orders are sorted by price keys.
            best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
            best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
            
            # -----------------------------------------------
            # 🟢 STRATEGY 1: MARKET MAKING (MEAN-REVERSION)
            # ASSET: EMERALDS
            # -----------------------------------------------
            if product == "EMERALDS":
                # Data showed EMERALDS are perfectly anchored to 10000.
                # No dynamic math needed. We exploit the tight range violently.
                
                # BUY LOGIC: Has the price dropped uncharacteristically low?
                if best_ask < 9998:
                    available_to_buy = POSITION_LIMIT - current_position
                    if available_to_buy > 0:
                        buy_quantity = min(-best_ask_amount, available_to_buy)
                        print(f"EMERALDS: Buying cheap at {best_ask}!")
                        orders.append(Order(product, best_ask, buy_quantity))
                        
                # SELL LOGIC: Has the price shot uncharacteristically high?
                if best_bid > 10002:
                    capacity_to_short = current_position - (-POSITION_LIMIT)
                    if capacity_to_short > 0:
                        sell_quantity = min(best_bid_amount, capacity_to_short)
                        print(f"EMERALDS: Selling high at {best_bid}!")
                        orders.append(Order(product, best_bid, -sell_quantity))

            # -----------------------------------------------
            # 🔴 STRATEGY 2: MOVING AVERAGES (TRENDING)
            # ASSET: TOMATOES
            # -----------------------------------------------
            elif product == "TOMATOES":
                # 1. Update State Memory (We need the history of prices to detect the trend)
                mid_price = (best_ask + best_bid) / 2
                trader_data_dict["tomato_prices"].append(mid_price)
                
                # Limit memory to the last 50 ticks to calculate our Long MA safely and prevent memory leak
                if len(trader_data_dict["tomato_prices"]) > 50:
                    trader_data_dict["tomato_prices"] = trader_data_dict["tomato_prices"][-50:]
                    
                # 2. Trading Logic (Wait until we have gathered at least 50 ticks of data)
                if len(trader_data_dict["tomato_prices"]) == 50:
                    # Calculate Simple Moving Averages (Average over Time)
                    short_ma = sum(trader_data_dict["tomato_prices"][-10:]) / 10
                    long_ma = sum(trader_data_dict["tomato_prices"]) / 50
                    
                    # BUY LOGIC: Is the short-term trend moving upwards past the long-term trend?
                    if short_ma > long_ma:
                        available_to_buy = POSITION_LIMIT - current_position
                        if available_to_buy > 0:
                            buy_quantity = min(-best_ask_amount, available_to_buy)
                            # Additional filter could be added here: if abs(short_ma - long_ma) > spread
                            print(f"TOMATOES: Upward Trend Detected! Buying at {best_ask}")
                            orders.append(Order(product, best_ask, buy_quantity))
                            
                    # SELL LOGIC: Is the short-term trend diving below the long-term trend?
                    elif short_ma < long_ma:
                        capacity_to_short = current_position - (-POSITION_LIMIT)
                        if capacity_to_short > 0:
                            sell_quantity = min(best_bid_amount, capacity_to_short)
                            print(f"TOMATOES: Downward Trend Detected! Shorting at {best_bid}")
                            orders.append(Order(product, best_bid, -sell_quantity))
                            
            # Save our processed orders to the final results dictionary
            result[product] = orders
    
        # --- PREPARE DATA FOR NEXT TICK ---
        # We must package our dictionary back into a raw string before handing it back to the engine
        new_trader_data_string = json.dumps(trader_data_dict)
        
        conversions = 0
        return result, conversions, new_trader_data_string
