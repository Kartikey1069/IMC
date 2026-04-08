from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string

class Trader:

    def bid(self):
        return 15

    def run(self, state: TradingState):
        """
        The main method called by the simulation at every time-step.
        It calculates our 'Fair Value' for the given products and places buy/sell
        orders to capture the difference in prices.
        """
        # A dictionary holding all the orders we want to execute at this time-step
        result = {}

        # Here we set a placeholder position limit of 20 as discussed.
        # This means we won't hold more than 20 items or owe more than 20 items.
        POSITION_LIMIT_EMERALDS = 20
        POSITION_LIMIT_TOMATOES = 20

        # Loop over every product (e.g. EMERALDS, TOMATOES) available in the order book
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            
            # Look up position limit based on product
            position_limit = POSITION_LIMIT_EMERALDS if product == "EMERALDS" else POSITION_LIMIT_TOMATOES

            # Get our current position (how much of the product we currently own)
            # If we don't own any, we default to 0.
            current_position = state.position.get(product, 0)

            # To make informed trades, we must ensure there are both buyers and sellers
            if len(order_depth.sell_orders) != 0 and len(order_depth.buy_orders) != 0:
                
                # Sort and retrieve the best (lowest) ask and the best (highest) bid.
                # In Python, dictionaries representing orders are sorted by price keys.
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                
                # --- DATA METRICS CALCULATION ---
                # Calculate the "Fair Value" (Mid-Price) of the asset.
                # Since EMERALDS acts historically stable and TOMATOES fluctuate, using the
                # true middle of the bid-ask gap serves as a statistically solid anchor price.
                acceptable_price = (best_ask + best_bid) / 2
                
                # --- TRADING LOGIC ---
                # BUY LOGIC: Is there a seller selling the product for LESS than our true Fair Value?
                if int(best_ask) < acceptable_price:
                    # Determine how many items we are allowed to buy without exceeding our limit
                    available_to_buy_capacity = position_limit - current_position
                    
                    if available_to_buy_capacity > 0:
                        # We want to buy at the best_ask. We can only buy what the seller offers (-best_ask_amount)
                        # or whatever we have capacity for, whichever is smaller.
                        buy_quantity = min(-best_ask_amount, available_to_buy_capacity)
                        print("BUY", str(buy_quantity) + "x", best_ask)
                        orders.append(Order(product, best_ask, buy_quantity))
                        
                # SELL LOGIC: Is there a buyer willing to pay MORE than our true Fair Value?
                if int(best_bid) > acceptable_price:
                    # Determine how many items we are allowed to short-sell without violating our negative limit
                    capacity_to_short = current_position - (-position_limit)
                    
                    if capacity_to_short > 0:
                        # We want to sell our asset to the highest bidder.
                        sell_quantity = min(best_bid_amount, capacity_to_short)
                        print("SELL", str(sell_quantity) + "x", best_bid)
                        # Order quantity must be negative when selling
                        orders.append(Order(product, best_bid, -sell_quantity))
            
            # Finalize orders for this product
            result[product] = orders
    
        # The engine expects these return values
        traderData = "SAMPLE" 
        conversions = 0
        return result, conversions, traderData
