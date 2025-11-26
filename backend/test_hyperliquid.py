import os
import time
from dotenv import load_dotenv
from app.infrastructure.hyperliquid.client import HyperliquidClient

def test_integration():
    load_dotenv()
    
    print("Initializing HyperliquidClient...")
    client = HyperliquidClient()
    
    if not client.account:
        print("WARNING: No private key found. Trading tests will be skipped.")
    else:
        print(f"Authenticated with address: {client.account.address}")

    # 1. Fetch Price
    symbol = "BTC"
    print(f"\nFetching price for {symbol}...")
    price = client.get_price(symbol)
    print(f"Current {symbol} price: {price}")
    
    if price == 0:
        print("ERROR: Failed to fetch price.")
        return

    if client.account:
        # 2. Place Order (Limit Buy far below price to avoid fill)
        limit_price = round(price * 0.5, 1) # 50% below current price
        size = 0.001 # Minimum size might vary, check docs
        
        print(f"\nPlacing LIMIT BUY order for {size} {symbol} at {limit_price}...")
        order_result = client.place_order(symbol, True, size, limit_price)
        
        if order_result:
            print("Order placed successfully!")
            print(order_result)
            
            # Extract order ID (this depends on actual response structure)
            # Usually response['response']['data']['statuses'][0]['resting']['oid']
            try:
                statuses = order_result['response']['data']['statuses']
                if statuses and 'resting' in statuses[0]:
                    oid = statuses[0]['resting']['oid']
                    print(f"Order ID: {oid}")
                    
                    # 3. Cancel Order
                    print(f"\nCancelling order {oid}...")
                    time.sleep(2) # Wait a bit
                    cancel_result = client.cancel_order(symbol, oid)
                    print(f"Cancel result: {cancel_result}")
                else:
                    print("Order did not rest (maybe filled or rejected).")
            except Exception as e:
                print(f"Could not parse order result for cancellation: {e}")
        else:
            print("Failed to place order.")

if __name__ == "__main__":
    test_integration()
