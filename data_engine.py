import MetaTrader5 as mt5
import pandas as pd

from config import MT5_LOGIN, MT5_PASSWORD, MT5_PATH, MT5_SERVER


def initialize_mt5():
    # Force shutdown previous stale/hanging connections
    mt5.shutdown()

    # Initialize connection with explicit parameters from config
    initialized = mt5.initialize(
        path=MT5_PATH,
        login=MT5_LOGIN,
        password=MT5_PASSWORD,
        server=MT5_SERVER,
    )

    if not initialized:
        raise RuntimeError(
            f"MT5 initialization failed with error: {mt5.last_error()}"
        )

    return True


def get_market_data(symbol):
    # Step 1: Ensure MT5 connection is active
    initialize_mt5()

    # Step 2: Ensure symbol is selected & visible in Market Watch
    if not mt5.symbol_select(symbol, True):
        mt5.shutdown()
        raise RuntimeError(
            f"Symbol '{symbol}' Market Watch me nahi mila ya XM server par available nahi hai."
        )

    timeframes = {
        "4-Hour": mt5.TIMEFRAME_H4,
        "15-Minute": mt5.TIMEFRAME_M15,
    }

    market_data = []

    try:
        for timeframe_name, timeframe in timeframes.items():
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 10)

            if rates is None or len(rates) == 0:
                raise RuntimeError(
                    f"Failed to fetch {timeframe_name} data for {symbol}: {mt5.last_error()}"
                )

            df = pd.DataFrame(rates)
            df["time"] = pd.to_datetime(df["time"], unit="s")

            market_data.append(f"\n{timeframe_name} Timeframe:\n")
            market_data.append(
                df[["time", "open", "high", "low", "close"]].to_string(
                    index=False
                )
            )

    finally:
        # Step 3: Always close connection after fetching to prevent IPC leak/hang
        mt5.shutdown()

    return "\n".join(market_data)