from constants import CLOSE_AT_ZSCORE_CROSS, ZSCORE_THRESH
from func_utils import format_number
from func_public import get_candles_recent
from func_cointegration import calculate_zscore
from func_private import place_market_order
from decimal import Decimal
import json
import time 
import pprint as pprint
import os
# Close positions
def manage_trade_exits(client):

    """ 
        Manage exiting open positions
        Based upon criteria set in constants
    
    """
    # Get current file path
    current_file_path = os.path.abspath(__file__)

    json_file_path = os.path.join(current_file_path, "bot_agents.json")
    


    # Initialise saving output
    save_output = []

    # Opening JSON file
    try:
        open_positions_file = open(json_file_path)
        open_positions_dict = json.load(open_positions_file)
    except:
        return "No local dictionary of open positions"
    
   
    
    # Get all open positions per trading platform
    exchange_pos = client.private.get_positions(status="OPEN")
    all_exc_pos = exchange_pos.data["positions"]
    markets_live = []
    
     # Guard Exit if no open positions in file
    if len(open_positions_dict) < 1 or all_exc_pos == []:
        return "Local dictionary or exchange of open positions is empty"
    
    for p in all_exc_pos:
        markets_live.append(p["market"])

    #protect API
    time.sleep(0.5)

    
    # Check all saved positions match order record
    # exit trade according to any exit trade rules
    for position in open_positions_dict:

        # Initialise is_close trigger
        is_close = False

        # Guard: record for any postions that are on or in error on the dictionary but not on the exchange
        # so they can be removed from the dictionary
        missing_position = False

        # Extract position matching information from file = market 1
        position_market_m1 = position["market_1"]
        position_size_m1 = position["order_m1_size"]
        position_side_m1 = position["order_m1_side"]

        # Extract position matching information from file = market 2
        position_market_m2 = position["market_2"]
        position_size_m2 = position["order_m2_size"]
        position_side_m2 = position["order_m2_side"]

        #protect API
        time.sleep(0.5)

        # Get order info m1 per exchange
        order_m1 = client.private.get_order_by_id(position["order_id_m1"])
        order_market_m1 = order_m1.data["order"]["market"]
        order_size_m1 = order_m1.data["order"]["size"]
        order_side_m1 = order_m1.data["order"]["side"]

        #protect API
        time.sleep(0.5)

        # Get order info m2 per exchange
        order_m2 = client.private.get_order_by_id(position["order_id_m2"])
        order_market_m2 = order_m2.data["order"]["market"]
        order_size_m2 = order_m2.data["order"]["size"]
        order_side_m2 = order_m2.data["order"]["side"]        

        # Perform matching check
        check_m1 = position_market_m1 == order_market_m1 and Decimal(position_size_m1) == Decimal(order_size_m1) and position_side_m1 == order_side_m1
        check_m2 = position_market_m2 == order_market_m2 and Decimal(position_size_m2) == Decimal(order_size_m2) and position_side_m2 == order_side_m2
        check_live = position_market_m1 in markets_live and position_market_m2 in markets_live
        
        # Guard: If not all match with error
        if not check_m1 or not check_m2 or not check_live:
            print(f"Warning: No position or error on exchange for {position_market_m1} and {position_market_m2}")
            print(f"removing {position_market_m1} and {position_market_m2} from local dictionary")
            print(f"*** Remove these pairs manually from the exchange ***")
            
            # This position pair will not be saved to the new dictionary
                

            continue

        try:
            # Get prices
            series_1 = get_candles_recent(client, position_market_m1)
            time.sleep(0.2)
            series_2 = get_candles_recent(client, position_market_m2)
            time.sleep(0.2)

        
            # Get markets for reference of tick size
            markets = client.public.get_markets().data
            
            #protect API
            time.sleep(0.5)

        except Exception as e:
            # Handle the error gracefully
            print(f"An error occurred while getting market data: {str(e)}")


        # Trigger close based on Z-score
        if CLOSE_AT_ZSCORE_CROSS:

            # Initialize Z-scores
            hedge_ratio = position["hedge_ratio"]
            z_score_traded = position["z_score"]
            if len(series_1) > 0 and len(series_1) == len(series_2):
                spread = series_1 - (hedge_ratio * series_2)
                z_score_current = calculate_zscore(spread).values.tolist()[-1]

            # Determine trigger
            # for checking operations z_score_level_check = abs(z_score_current) < ZSCORE_THRESH
            #z_score_level_check = abs(z_score_current) >= abs(z_score_traded)
            z_score_level_check = abs(z_score_current) >= abs(ZSCORE_THRESH)
            z_score_cross_check = (z_score_current < 0 and z_score_traded> 0) or (z_score_current > 0 and z_score_traded < 0)

            print(f"Exit check z_score current: {abs(z_score_current)}, z_score traded: {abs(z_score_traded)}" )

            # Close trade
            if z_score_level_check and z_score_cross_check:

                # Initiate trade
                is_close = True

        ### Add any other close logic you want here
        ## trigger is_close

        # Close position if triggered
        
        if is_close:

            # Determine side - m1
            side_m1 = "SELL"
            if position_side_m1 == "SELL":
                side_m1 = "BUY"

            # Determine side - m2
            side_m2 = "SELL"
            if position_side_m2 == "SELL":
                side_m2 = "BUY"

            # Get and format Price
            price_m1 = float(series_1[-1])
            price_m2 = float(series_2[-1])
            accept_price_m1 = price_m1 * 1.05 if side_m1 == "BUY" else price_m1 * 0.95
            accept_price_m2 = price_m2 * 1.05 if side_m2 == "BUY" else price_m2 * 0.95
            tick_size_m1 = markets["markets"][position_market_m1]["tickSize"]
            tick_size_m2 = markets["markets"][position_market_m2]["tickSize"]
            accept_price_m1 = format_number(accept_price_m1, tick_size_m1)
            accept_price_m2 = format_number(accept_price_m2, tick_size_m2)

            # Close positions
            try:

                # Close position for market 1
                print(">>> Closing market 1 <<<")
                print(f"Closing position for {position_market_m1}")

                close_order_m1 = place_market_order(
                    client,
                    market=position_market_m1,
                    side=side_m1,
                    size=position_size_m1,
                    price=accept_price_m1,
                    reduce_only=True,
                )

                print(close_order_m1["order"]["id"])
                print(">>> Closing <<<")

                # Protect API
                time.sleep(1)

                # Close position for market 2
                print(">>> Closing market 2 <<<")
                print(f"Closing position for {position_market_m2}")

                close_order_m2 = place_market_order(
                    client,
                    market=position_market_m2,
                    side=side_m2,
                    size=position_size_m2,
                    price=accept_price_m2,
                    reduce_only=True,
                )

                print(close_order_m2["order"]["id"])
                print(">>> Closing <<<")




            except Exception as e:
                print(f"Exit failed for {position_market_m1} with {position_market_m2} with error: {str(e)}")
                save_output.append(position)

        # Keep record of items and save
        else:
            save_output.append(position)

    # Save remaining items
    print(f"{len(save_output)} Items remaining. Saving file ...")
    with open(json_file_path, "w") as f:
        json.dump(save_output, f)




        

        

    


