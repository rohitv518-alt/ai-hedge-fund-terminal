import MetaTrader5 as mt5
from config import MT5_LOGIN, MT5_PASSWORD, MT5_PATH, MT5_SERVER


def execute_trade(symbol, decision, lot_size=0.01):
    if decision == "HOLD":
        return "HOLD: No trade executed."

    if decision not in ("BUY", "SELL"):
        return f"ERROR: Invalid decision '{decision}'."

    # 1. Initialize Connection explicitly before trade execution
    mt5.shutdown()
    if not mt5.initialize(
        path=MT5_PATH,
        login=int(MT5_LOGIN),
        password=MT5_PASSWORD,
        server=MT5_SERVER,
    ):
        return f"ERROR: MT5 execution connection failed: {mt5.last_error()}"

    try:
        # 2. Force Symbol Selection in Market Watch (Fixes 'Symbol not found' issue)
        if not mt5.symbol_select(symbol, True):
            return f"ERROR: Symbol '{symbol}' not found in Market Watch or XM Server."

        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return f"ERROR: Symbol '{symbol}' info not found."

        if not symbol_info.visible:
            if not mt5.symbol_select(symbol, True):
                return f"ERROR: Could not select symbol '{symbol}'."

        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return f"ERROR: Could not get market price for '{symbol}'."

        # 3. Determine Order Type and Price
        if decision == "BUY":
            order_type = mt5.ORDER_TYPE_BUY
            price = tick.ask
        else:
            order_type = mt5.ORDER_TYPE_SELL
            price = tick.bid

        # 4. Build Trade Request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(lot_size),
            "type": order_type,
            "price": price,
            "deviation": 20,
            "magic": 10001,
            "comment": "AI Hedge Fund",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # 5. Send Order to Broker
        result = mt5.order_send(request)

        if result is None:
            return f"ERROR: Order failed. {mt5.last_error()}"

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            return f"ERROR: Order failed. Retcode={result.retcode}, Comment={result.comment}"

        return (
            f"SUCCESS: {decision} order executed for {symbol}, "
            f"lot size={lot_size}, price={result.price}"
        )

    finally:
        # Safe disconnect after trade completion
        mt5.shutdown()