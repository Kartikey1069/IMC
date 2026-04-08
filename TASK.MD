I HAVE BEEN GIVEN SOME DATA ITEMS NAMED EMERALDS AND TOMATOES I HAVE BEEN GIVEN A ORDER BOOK AND TRADES OF BOTH .


I AM DESIGNATED TO DESIGIN  A PYTHON SCRIPT WHICH  WOUD EXECUTE THESE ORDERS SO  THAT I CAN GENRATE THE MAXIMUM PROFIT 


FOLLOWING IS THE TEMPLATE I AM USED TO FOLLOW TO MAKE THE SCRIPT 



Below an abstract representation of what the trader class should look like is shown. The class requires a single method called run, which is called by the simulation every time a new TraderState is available. The logic within this run method is written by the player and determines the behaviour of the algorithm. The output of the method is a dictionary, where the key is a product name and the value is a list that contains all the orders that the algorithm decides to send based on this logic. (Again, for Algo Round 2, the Trader class should also define a bid() method. It is fine to have a bid() method in every submission for every round, it will be ignored for all rounds except Round 2.)


from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string

class Trader:

    def bid(self):
        return 15
    
    def run(self, state: TradingState):
        """Only method required. It takes all buy and sell orders for all
        symbols as an input, and outputs a list of orders to be sent."""

        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))

        # Orders to be placed on exchange matching engine
        result = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            acceptable_price = 10  # Participant should calculate this value
            print("Acceptable price : " + str(acceptable_price))
            print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))
    
            if len(order_depth.sell_orders) != 0:
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                if int(best_ask) < acceptable_price:
                    print("BUY", str(-best_ask_amount) + "x", best_ask)
                    orders.append(Order(product, best_ask, -best_ask_amount))
    
            if len(order_depth.buy_orders) != 0:
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                if int(best_bid) > acceptable_price:
                    print("SELL", str(best_bid_amount) + "x", best_bid)
                    orders.append(Order(product, best_bid, -best_bid_amount))
            
            result[product] = orders
    
        # String value holding Trader state data required. 
        # It will be delivered as TradingState.traderData on next execution.
        traderData = "SAMPLE" 
        
        # Sample conversion request. Check more details below. 
        conversions = 1
        return result, conversions, traderData





        The `TradingState` class holds all the important market information that an algorithm needs to make decisions about which orders to send. Below the definition is provided for the `TradingState` class:

    Time = int
Symbol = str
Product = str
Position = int

class TradingState(object):
   def __init__(self,
                 traderData: str,
                 timestamp: Time,
                 listings: Dict[Symbol, Listing],
                 order_depths: Dict[Symbol, OrderDepth],
                 own_trades: Dict[Symbol, List[Trade]],
                 market_trades: Dict[Symbol, List[Trade]],
                 position: Dict[Product, Position],
                 observations: Observation):
        self.traderData = traderData
        self.timestamp = timestamp
        self.listings = listings
        self.order_depths = order_depths
        self.own_trades = own_trades
        self.market_trades = market_trades
        self.position = position
        self.observations = observations
        
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)




The most important properties

- **own_trades**: the trades the algorithm itself has done since the last `TradingState` came in. This property is a dictionary of `Trade` objects with key being a product name. The definition of the `Trade` class is provided in the subsections below.
- **market_trades**: the trades that other market participants have done since the last `TradingState` came in. This property is also a dictionary of `Trade` objects with key being a product name.
- **position**: the long or short position that the player holds in every tradable product. This property is a dictionary with the product as the key for which the value is a signed integer denoting the position, e.g. `{product1: 2, product2: -1}`.
- **order_depths**: all the buy and sell orders per product that other market participants have sent and that the algorithm is able to trade with. This property is a dict where the keys are the products and the corresponding values are instances of the `OrderDepth` class. This `OrderDepth` class then contains all the buy and sell orders. An overview of the `OrderDepth` class is also provided in the subsections below.

## `Trade` class

Both the `own_trades` property and the `market_trades` property provide the traders with a list of trades per products. Every individual trade in each of these lists is an instance of the `Trade` class.




Symbol = str
UserId = str

class Trade:
    def __init__(self, symbol: Symbol, price: int, quantity: int, buyer: UserId = None, seller: UserId = None, timestamp: int = 0) -> None:
        self.symbol = symbol
        self.price: int = price
        self.quantity: int = quantity
        self.buyer = buyer
        self.seller = seller
        self.timestamp = timestamp

    def __str__(self) -> str:
        return "(" + self.symbol + ", " + self.buyer + " << " + self.seller + ", " + str(self.price) + ", " + str(self.quantity) + ", " + str(self.timestamp) + ")"

    def __repr__(self) -> str:
        return "(" + self.symbol + ", " + self.buyer + " << " + self.seller + ", " + str(self.price) + ", " + str(self.quantity) + ", " + str(self.timestamp) + ")" + self.symbol + ", " + self.buyer + " << " + self.seller + ", " + str(self.price) + ", " + str(self.quantity) + ")"






These trades have 5 distinct properties (besides the `timestamp` property). On Prosperity’s exchange, like on most real-world exchanges, counterparty information is often not disclosed. Therefore, `self.buyer` and `self.seller` will only be non-empty strings if the algorithm itself is the buyer (`self.buyer = “SUBMISSION”`) or the seller (`self.seller=“SUBMISSION”`).

## `OrderDepth` class

Provided by the `TradingState` class is also the `OrderDepth` per symbol. This object contains the collection of all outstanding buy and sell orders, or “quotes” that were sent by the trading bots, for a certain symbol. 

```python
class OrderDepth:
    def __init__(self):
        self.buy_orders: Dict[int, int] = {}
        self.sell_orders: Dict[int, int] = {}
```

All the orders on a single side (buy or sell) are aggregated in a dict, where the keys indicate the price associated with the order, and the corresponding values indicate the total volume on that price level.





There are two items delivered inside the TradingState instance:

1. Simple product to value dictionary inside plainValueObservations
2. Dictionary of complex **ConversionObservation** values for respective products. Used to place conversion requests from Trader class. Structure visible below.

```python
class ConversionObservation:

    def __init__(self, bidPrice: float, askPrice: float, transportFees: float, exportTariff: float, importTariff: float, sunlight: float, humidity: float):
        self.bidPrice = bidPrice
        self.askPrice = askPrice
        self.transportFees = transportFees
        self.exportTariff = exportTariff
        self.importTariff = importTariff
        self.sugarPrice = sugarPrice
        self.sunlightIndex = sunlightIndex
```

In case you decide to place a conversion request on a product, then the listed integer number should be returned as a “conversions” value from the `run()` method. Based on logic defined inside Prosperity container it will convert positions acquired by submitted code. There is a number of conditions for conversion to happen:

- You need to obtain either long or short position earlier.
- Conversion request cannot exceed possessed items count.





# How to send orders using the `Order` class

After performing logic on the incoming order state, the `run` method defined by the player should output a dictionary containing the orders that the algorithm wants to send. The keys of this dictionary should be all the products that the algorithm wishes to send orders for. These orders should be instances of the `Order` class. Each order has three important properties. These are:

1. The symbol of the product for which the order is sent.
2. The price of the order: the maximum price at which the algorithm wants to buy in case of a BUY order, or the minimum price at which the algorithm wants to sell in case of a SELL order.
3. The quantity of the order: the maximum quantity that the algorithm wishes to buy or sell. If the sign of the quantity is positive, the order is a buy order, if the sign of the quantity is negative it is a sell order.






Symbol = str

class Order:
    def __init__(self, symbol: Symbol, price: int, quantity: int) -> None:
        self.symbol = symbol
        self.price = price
        self.quantity = quantity

    def __str__(self) -> str:
        return "(" + self.symbol + ", " + str(self.price) + ", " + str(self.quantity) + ")"

    def __repr__(self) -> str:
        return "(" + self.symbol + ", " + str(self.price) + ", " + str(self.quantity) + ")"




        If there are active orders from counterparties for the same product against which the algorithms’ orders can be matched, the algorithms’ order will be (partially) executed right away. If no immediate or partial execution is possible, the remaining order quantity will be visible for the bots in the market, and it might be that one of them sees it as a good trading opportunity and will trade against it. If none of the bots decides to trade against the remaining order quantity, it is cancelled. Note that after cancellation of the algorithm’s orders, but before the next `Tradingstate` comes in, bots might also trade with each other.

Note that on Prosperity’s exchange, execution of orders is instantaneous, which means that all their orders arrive in the exchange matching engine without any delay. Therefore, all the orders that a player sends that could be immediately matched with an order from one of the bots, and result in a trade if matched. In other words, none of the bots can send an order that is faster than the player’s order and get the opportunity instead.

See [Trading glossary](https://www.notion.so/Trading-glossary-325e8453a09380febae2cf77bad14f71?pvs=21) for a more elaborate explanation of order execution in financial markets.

## Position Limits

Just like in the real world of trading, there are position limits, i.e. limits to the size of the position that the algorithm can trade into in a single product. These position limits are defined on a per-product basis, and refer to the absolute allowable position size. So for a hypothetical position limit of 10, the position can neither be greater than 10 (long) nor less than -10 (short). On the Prosperity exchange, this position limit is enforced by the exchange. If at any iteration, the player’s algorithm tries to send buy (sell) orders for a product with an aggregated quantity that would cause the player to go over long (short) position limits if all orders would be fully executed, all orders will be rejected automatically.



For an overview of the per-product position limits, please refer to the ‘Rounds’ section on Wiki. The position limits are listed per round.

# Example of Trading

Two example iterations are provided below to give an idea what the simulation behaviour looks like.

For the following example we assume a situation with two products:

- PRODUCT1 with position limit 10
- PRODUCT2 with position limit 20

At the start of the first iteration the run method is called with the `TradingState` generated by the below code. Note: the [datamodel.py](http://datamodel.py) file from which the classes are imported is provided in Appendix B. The code can also be used to test algorithms locally.






from datamodel import Listing, OrderDepth, Trade, TradingState

timestamp = 1000

listings = {
	"PRODUCT1": Listing(
		symbol="PRODUCT1", 
		product="PRODUCT1", 
		denomination= "XIRECS"
	),
	"PRODUCT2": Listing(
		symbol="PRODUCT2", 
		product="PRODUCT2", 
		denomination= "XIRECS"
	),
}

order_depths = {
	"PRODUCT1": OrderDepth(
		buy_orders={10: 7, 9: 5},
		sell_orders={11: -4, 12: -8}
	),
	"PRODUCT2": OrderDepth(
		buy_orders={142: 3, 141: 5},
		sell_orders={144: -5, 145: -8}
	),	
}

own_trades = {
	"PRODUCT1": [],
	"PRODUCT2": []
}

market_trades = {
	"PRODUCT1": [
		Trade(
			symbol="PRODUCT1",
			price=11,
			quantity=4,
			buyer="",
			seller="",
			timestamp=900
		)
	],
	"PRODUCT2": []
}

position = {
	"PRODUCT1": 3,
	"PRODUCT2": -5
}

observations = {}
traderData = ""

state = TradingState(
	traderData,
	timestamp,
  listings,
	order_depths,
	own_trades,
	market_trades,
	position,
	observations
)




Let’s say that at this point in the simulation, the algorithm has the following convictions:

1. PRODUCT1 is worth 13
2. PRODUCT2 is worth 142

It could then potentially decide on the following

1. Since the sell orders in PRODUCT1 at price 11 (qty 4) and price 12 (qty 8) are both below the algorithms calculated fair value, it would like to send a buy order to trade with these sell orders. Given that the position in PRODUCT1 is already 3 long and the position limit is set at 10, sending one or more buy orders with an aggregated quantity of >7 would result in rejection of all buy orders, the algorithm sends a buy order with quantity 7 and a price of 12.
2. Versus the fair value of 142 neither the sell orders nor the buy orders look profitable. The algorithm therefore decides to see if any of the bots is willing to buy at 143, and sends a sell order of quantity 5 at that price level.

Based on the above the `run` method output would then be generated as shown below:

```python
result["PRODUCT1"] = [Order("PRODUCT1", 12, 7)]
result["PRODUCT2"] = [Order("PRODUCT2", 143, -5)]
```

An example of what the next `TradingState` will look like is generated by the code below.Let’s say that at this point in the simulation, the algorithm has the following convictions:

1. PRODUCT1 is worth 13
2. PRODUCT2 is worth 142

It could then potentially decide on the following

1. Since the sell orders in PRODUCT1 at price 11 (qty 4) and price 12 (qty 8) are both below the algorithms calculated fair value, it would like to send a buy order to trade with these sell orders. Given that the position in PRODUCT1 is already 3 long and the position limit is set at 10, sending one or more buy orders with an aggregated quantity of >7 would result in rejection of all buy orders, the algorithm sends a buy order with quantity 7 and a price of 12.
2. Versus the fair value of 142 neither the sell orders nor the buy orders look profitable. The algorithm therefore decides to see if any of the bots is willing to buy at 143, and sends a sell order of quantity 5 at that price level.

Based on the above the `run` method output would then be generated as shown below:

```python
result["PRODUCT1"] = [Order("PRODUCT1", 12, 7)]
result["PRODUCT2"] = [Order("PRODUCT2", 143, -5)]
```

An example of what the next `TradingState` will look like is generated by the code below.



from datamodel import Listing, OrderDepth, Trade, TradingState

timestamp = 1100

listings = {
	"PRODUCT1": Listing(
		symbol="PRODUCT1", 
		product="PRODUCT1", 
		denomination: "XIRECS"
	),
	"PRODUCT2": Listing(
		symbol="PRODUCT2", 
		product="PRODUCT2", 
		denomination: "XIRECS"
	),
}

order_depths = {
	"PRODUCT1": OrderDepth(
		buy_orders={10: 7, 9: 5},
		sell_orders={12: -5, 13: -3}
	),
	"PRODUCT2": OrderDepth(
		buy_orders={142: 3, 141: 5},
		sell_orders={144: -5, 145: -8}
	),	
}

own_trades = {
	"PRODUCT1": [
		Trade(
			symbol="PRODUCT1",
			price=11,
			quantity=4,
			buyer="SUBMISSION",
			seller="",
			timestamp=1000
		),
		Trade(
			symbol="PRODUCT1",
			price=12,
			quantity=3,
			buyer="SUBMISSION",
			seller="",
			timestamp=1000
		)
	],
	"PRODUCT2": [
		Trade(
			symbol="PRODUCT2",
			price=143,
			quantity=2,
			buyer="",
			seller="SUBMISSION",
			timestamp=1000
		),
	]
}

market_trades = {
	"PRODUCT1": [],
	"PRODUCT2": []
}

position = {
	"PRODUCT1": 10,
	"PRODUCT2": -7
}

observations = {}
traderData = ""

state = TradingState(
	traderData,
	timestamp,
  listings,
	order_depths,
	own_trades,
	market_trades,
	position,
	observations
)



from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string

class Trader:

    def bid(self):
        return 15
    
    def run(self, state: TradingState):
        """Only method required. It takes all buy and sell orders for all
        symbols as an input, and outputs a list of orders to be sent."""

        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))

        # Orders to be placed on exchange matching engine
        result = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            acceptable_price = 10  # Participant should calculate this value
            print("Acceptable price : " + str(acceptable_price))
            print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))
    
            if len(order_depth.sell_orders) != 0:
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                if int(best_ask) < acceptable_price:
                    print("BUY", str(-best_ask_amount) + "x", best_ask)
                    orders.append(Order(product, best_ask, -best_ask_amount))
    
            if len(order_depth.buy_orders) != 0:
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                if int(best_bid) > acceptable_price:
                    print("SELL", str(best_bid_amount) + "x", best_bid)
                    orders.append(Order(product, best_bid, -best_bid_amount))
            
            result[product] = orders
    
        traderData = ""  # No state needed - we check position directly
        conversions = 0
        return result, conversions, traderData




        [datamodel.py](http://datamodel.py) file





        import json
from typing import Dict, List
from json import JSONEncoder
import jsonpickle

Time = int
Symbol = str
Product = str
Position = int
UserId = str
ObservationValue = int


class Listing:

    def __init__(self, symbol: Symbol, product: Product, denomination: Product):
        self.symbol = symbol
        self.product = product
        self.denomination = denomination
        
                 
class ConversionObservation:

    def __init__(self, bidPrice: float, askPrice: float, transportFees: float, exportTariff: float, importTariff: float, sunlight: float, humidity: float):
        self.bidPrice = bidPrice
        self.askPrice = askPrice
        self.transportFees = transportFees
        self.exportTariff = exportTariff
        self.importTariff = importTariff
        self.sugarPrice = sugarPrice
        self.sunlightIndex = sunlightIndex
        

class Observation:

    def __init__(self, plainValueObservations: Dict[Product, ObservationValue], conversionObservations: Dict[Product, ConversionObservation]) -> None:
        self.plainValueObservations = plainValueObservations
        self.conversionObservations = conversionObservations
        
    def __str__(self) -> str:
        return "(plainValueObservations: " + jsonpickle.encode(self.plainValueObservations) + ", conversionObservations: " + jsonpickle.encode(self.conversionObservations) + ")"
     

class Order:

    def __init__(self, symbol: Symbol, price: int, quantity: int) -> None:
        self.symbol = symbol
        self.price = price
        self.quantity = quantity

    def __str__(self) -> str:
        return "(" + self.symbol + ", " + str(self.price) + ", " + str(self.quantity) + ")"

    def __repr__(self) -> str:
        return "(" + self.symbol + ", " + str(self.price) + ", " + str(self.quantity) + ")"
    

class OrderDepth:

    def __init__(self):
        self.buy_orders: Dict[int, int] = {}
        self.sell_orders: Dict[int, int] = {}


class Trade:

    def __init__(self, symbol: Symbol, price: int, quantity: int, buyer: UserId=None, seller: UserId=None, timestamp: int=0) -> None:
        self.symbol = symbol
        self.price: int = price
        self.quantity: int = quantity
        self.buyer = buyer
        self.seller = seller
        self.timestamp = timestamp

    def __str__(self) -> str:
        return "(" + self.symbol + ", " + self.buyer + " << " + self.seller + ", " + str(self.price) + ", " + str(self.quantity) + ", " + str(self.timestamp) + ")"

    def __repr__(self) -> str:
        return "(" + self.symbol + ", " + self.buyer + " << " + self.seller + ", " + str(self.price) + ", " + str(self.quantity) + ", " + str(self.timestamp) + ")"


class TradingState(object):

    def __init__(self,
                 traderData: str,
                 timestamp: Time,
                 listings: Dict[Symbol, Listing],
                 order_depths: Dict[Symbol, OrderDepth],
                 own_trades: Dict[Symbol, List[Trade]],
                 market_trades: Dict[Symbol, List[Trade]],
                 position: Dict[Product, Position],
                 observations: Observation):
        self.traderData = traderData
        self.timestamp = timestamp
        self.listings = listings
        self.order_depths = order_depths
        self.own_trades = own_trades
        self.market_trades = market_trades
        self.position = position
        self.observations = observations
        
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

    
class ProsperityEncoder(JSONEncoder):

        def default(self, o):
            return o.__dict__





SO THIS IS ALL THE GUID THAT YOU HAVE TO USE TO IMPLEMENT THIS SCRIPT NOW 




YOUR TASK

IMPLEMENT THE SCRIPT AND HELP ME UNDERSTAND THAT THAT WHAT THOUGHT PROCESS YOU FOLLOWED TO IMPLEMENT IT AND WHY AND HOW YOU IMPLEMENTED IT PREPARE A README EXPLAINING ALL THESE THIGNS IN DETIL EXPLAIN WHICH DATA METRIC YOU USED ASD FEATURES FOR YOUR SCRIPT AND WHAT WERE THE DATA METRICS YOU CINSDIER EXPLAIN THEM IN DETAIL AS I HAVE NO KNOWLEDGE OF TRADING AND STATSITCS MUCH 