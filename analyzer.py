import csv
from collections import defaultdict

def analyze_data(csv_file_path):
    """
    This script reads a trading data CSV and prints statistical metrics 
    for each product. Please ensure the CSV has column names on the first row!
    """
    try:
        # We need to tell Python to split by semicolon (;) instead of commas!
        with open(csv_file_path, mode='r') as file:
            reader = csv.DictReader(file, delimiter=';')
            
            # We will store all our numerical data in these buckets per product
            products = defaultdict(lambda: {
                "mid_prices": [],
                "spreads": [],
                "imbalances": [],  # (buy volume - sell volume)
                "bids": [],
                "asks": []
            })
            
            row_count = 0
            
            for row in reader:
                try:
                    product = row.get("product")
                    if not product:
                        continue
                        
                    # Standard IMC Prosperity column names
                    bid_price = float(row.get("bid_price_1", 0))
                    ask_price = float(row.get("ask_price_1", 0))
                    bid_volume = float(row.get("bid_volume_1", 0))
                    ask_volume = float(row.get("ask_volume_1", 0))
                    
                    if bid_price == 0 or ask_price == 0:
                        continue # Skip empty data rows
                        
                    # 1. Mid-Price
                    mid_price = (bid_price + ask_price) / 2
                    
                    # 2. Spread (how big the gap is between buyers and sellers)
                    spread = ask_price - bid_price
                    
                    # 3. Order Book Volume Imbalance (positive = more buyers, negative = more sellers)
                    imbalance = bid_volume - ask_volume
                    
                    # Store data
                    products[product]["mid_prices"].append(mid_price)
                    products[product]["spreads"].append(spread)
                    products[product]["imbalances"].append(imbalance)
                    products[product]["bids"].append(bid_price)
                    products[product]["asks"].append(ask_price)
                    
                    row_count += 1
                except ValueError:
                    # Ignore rows with missing or malformed numbers
                    pass
            
            print(f"✅ Successfully read {row_count} rows from {csv_file_path}")
            print("=" * 60)
            
            # Calculate and Print Metrics
            for product, metrics in products.items():
                print(f"📊 DATA METRICS FOR: {product}")
                
                mid_prices = metrics["mid_prices"]
                if not mid_prices:
                    continue
                    
                avg_mid = sum(mid_prices) / len(mid_prices)
                min_mid = min(mid_prices)
                max_mid = max(mid_prices)
                
                avg_spread = sum(metrics["spreads"]) / len(metrics["spreads"])
                avg_imbalance = sum(metrics["imbalances"]) / len(metrics["imbalances"])
                
                # Check for "Pegged" or "Volatile" behavior
                price_volatility = max_mid - min_mid
                
                print(f"  - Average Mid-Price : {avg_mid:.2f}")
                print(f"  - Minimum Price     : {min_mid:.2f}")
                print(f"  - Maximum Price     : {max_mid:.2f}")
                print(f"  - Average Spread    : {avg_spread:.2f} (gap between buyers and sellers)")
                print(f"  - Overall Imbalance : {avg_imbalance:.2f} (Positive = High demand / Negative = Over-supply)")
                
                if price_volatility <= 3:
                    print("  💡 CONCLUSION: This asset is highly STABLE (pegged). Use fixed Fair Value!")
                else:
                    print("  💡 CONCLUSION: This asset is VOLATILE. Use Moving Averages to track it!")
                print("-" * 60)

    except FileNotFoundError:
        print(f"❌ Error: Could not find the file '{csv_file_path}'")
        print("Please place your historical data CSV file in the folder and update the path!")

if __name__ == "__main__":
    # Fixed the missing underscores in the 'trades' filenames!
    FILE_NAMES = [
        "prices_round_0_day_-1.csv",
        "prices_round_0_day_-2.csv"
    ] 
    
    for FILE_NAME in FILE_NAMES:
        print(f"\nSearching for {FILE_NAME}...")
        if "trades" in FILE_NAME:
            print("  ⚠️ Skipping: This script is designed for Order Book analysis using 'prices' files!")
            continue
            
        analyze_data(FILE_NAME)
