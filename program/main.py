from constants import ABORT_ALL_POSITIONS, FIND_COINTEGRATED, PLACE_TRADES, MANAGE_EXITS
from func_connections import connect_dydx
from func_private import abort_all_positions
from func_public import construct_market_prices
from func_cointegration import store_cointegration_results
from func_entry_pairs import open_positions
from func_exit_pairs import manage_trade_exits

import os
import json

if __name__ == "__main__":

    # Get current file path
    current_file_path = os.path.abspath(__file__)

    json_file_path = os.path.join(current_file_path, "bot_agents.json")
   
    # Connect to client
    try:
        print("Connecting to client...")
        client = connect_dydx()
    except Exception as e:
        print(e)
        print("Error connecting to client: ", e)
        exit(1)

    #Abort all open positions
    if ABORT_ALL_POSITIONS:
        try:
            print("Closing all positions...")
            close_orders = abort_all_positions(client)
            with open(json_file_path, "w") as f:
                json.dump([], f)
        except Exception as e:
            print("Error closing json file positions: ", e)
            exit(1)

    # Find Cointegrated Pairs
    if FIND_COINTEGRATED:

        # Construct market prices
        try:
            print("Fetching market prices, please allow 3 mins...")
            df_market_prices = construct_market_prices(client)
        except Exception as e:
            print("Error constructing market prices: ", e)
            exit(1)

  
        # Store cointegrated pairs
        try:
            print("Storing cointegrated pairs ...")
            stores_result = store_cointegration_results(df_market_prices)
            if stores_result != "saved":
                print("Error saving cointegrated pairs")
                exit(1)
        except Exception as e:
            print("Error saving cointegrated pairs: ", e)
            exit(1)

    while True:

        # Place trades for exiting positions
        if MANAGE_EXITS:
            try:
                print("Managing exits ...")
                manage_trade_exits(client)
            except Exception as e:
                print("Error managing exiting positions: ", e)
                exit(1)


        # Place trades for opening positions
        if PLACE_TRADES:
            try:
                print("Placing trades for opening positions ...")
                open_positions(client)
            except Exception as e:
                print("Error trading pairs: ", e)
                exit(1)