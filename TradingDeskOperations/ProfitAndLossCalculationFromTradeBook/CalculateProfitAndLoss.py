import json
from collections import deque
from collections import defaultdict
def p_and_l_calc(json_orders):
    """Calculates the profit and loss valuation from a
    json formatter buy/sell book"""
    orders = []
    with open(json_orders, "r") as json_file:
       orders = json.load(json_file) #json.load converts the json into a list of dictionaries
    #Now that all the orders are captured - let's store them in a dictionary by corresponding symbol
    #Note - if there's nothing in the symbol, and the first order is a buy the p&l associated with that value should be negative
    #O.t - if it contains vol inside of it - we most get rid of it in deque ordering and calculate the p&l
    #If there's nothing in it, and we're buying, we should simply calculate the p&l as negative!
    inventory_by_symbol = {}
    net_position_by_symbol = {}
    realized_p_and_l = 0
    for order in orders:
        order_symbol = order.get("symbol")
        order_type = order.get('side')
        order_quantity = order.get('quantity')
        order_price = order.get('price')

        if inventory_by_symbol.get(order_symbol) is None:
            inventory_by_symbol[order_symbol] = deque() #generate a new deque for the symbol
            #analyze whether the trade is a short or long position and add it to the deque
            if order_type == 'BUY':
                inventory_by_symbol[order_symbol].append({'quantity' : order_quantity, 'price': order_price})
                net_position_by_symbol[order_symbol] = order_quantity
            else:
                #Short position, negative quantity
                inventory_by_symbol[order_symbol].append({'quantity': -1 * order_quantity,'price': order_price})
                net_position_by_symbol[order_symbol] = -1 * order_quantity
        else:
            #Sell case:
            # If already short, append another negative lot
            # If long, deplete long lots FIFO; if sell > long, go short on remainder
            #Buy case:
            # If already long, append another positive lot.
            # If short, deplete short lots FIFO; if buy > short go long on remainder
            queue_status_short = False
            if net_position_by_symbol[order_symbol] < 0:
                queue_status_short = True
            if queue_status_short and order_type == 'SELL':
                inventory_by_symbol[order_symbol].append({'quantity': -1 * order_quantity,'price': order_price})
            elif not queue_status_short and order_type == 'BUY':
                inventory_by_symbol[order_symbol].append({'quantity': order_quantity, 'price': order_price})
                net_position_by_symbol[order_symbol] += order_quantity
            else: #queue status is short and the order symbol is buy, so we must consume
                #consume all the buys we can, calculate p&l and adjust
                while order_quantity > 0 and inventory_by_symbol[order_symbol]: #while there's still order quantity to be processed and there's still orders to match it
                    #pop the deque to get the buy order in FIFO
                    trade_lot = inventory_by_symbol[order_symbol].popleft()
                    lot_qty = abs(trade_lot['quantity'])
                    lot_sign = 1 if trade_lot['quantity'] > 0 else -1
                    matched_qty = min(order_quantity, lot_qty)
                    price_diff = (order_price - trade_lot['price']) * lot_sign
                    realized_p_and_l += price_diff * matched_qty

                    order_quantity -= matched_qty
                    #Adjust our net position - If it's a buy our net position increases and if it's a sell it decreases
                    if order_type == 'BUY':
                        net_position_by_symbol[order_symbol] += matched_qty
                    else:
                        net_position_by_symbol[order_symbol] -= matched_qty
                    remaining_lot_qty = lot_qty - matched_qty
                    #If there is more remaining in the lot after executing the trade - we should bring it back
                    if remaining_lot_qty > 0:
                        # push back remaining unmatched part of lot
                        trade_lot['quantity'] = remaining_lot_qty * lot_sign
                        inventory_by_symbol[order_symbol].appendleft(trade_lot)
                #This case occurs if there is remaining inventory left after short selling for example, so we must update the lot. I.e if we sold 60 shares and we only had 50 in the lot, we must update to -10 shares
                if order_quantity > 0:
                    # append unmatched remainder as a new lot
                    qty_sign = 1 if order_type == 'BUY' else -1
                    inventory_by_symbol[order_symbol].append({
                        'quantity': order_quantity * qty_sign,
                        'price': order_price
                    })
                    net_position_by_symbol[order_symbol] += order_quantity * qty_sign

    print("Realized P&L:", realized_p_and_l)
    print("Net positions:", net_position_by_symbol)
    print("Inventory:")
    for sym, q in inventory_by_symbol.items():
        print(sym, list(q))
def main():
    src = "orders.json"
    p_and_l_calc(src)



if __name__ == "__main__":
    main()