import pandas as pd

# MT5 (MetaTrader 5) Linux/Cloud par available nahi hota, isliye conditional import handling
try:
    import MetaTrader5 as mt5

    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False


def initialize_mt5():
    if not MT5_AVAILABLE:
        return False

    # Attempt importing config dynamically for local Windows setup
    try:
        from config import MT5_LOGIN, MT5_PASSWORD, MT5_PATH, MT5_SERVER
    except ImportError:
        return False

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


def get_market_data(symbol="GOLD"):
    # Streamlit Cloud (Linux) Fallback Data Generation
    if not MT5_AVAILABLE:
        return (
            f"=== Streamlit Cloud Mock Data for {symbol} ===\n\n"
            "4-Hour Timeframe:\n"
            "time                 open     high      low    close\n"
            "2026-03-30 08:00:00  2165.20  2170.10  2162.00  2168.50\n"
            "2026-03-30 12:00:00  2168.50  2175.40  2166.30  2172.10\n\n"
            "15-Minute Timeframe:\n"
            "time                 open     high      low    close\n"
            "2026-03-30 14:15:00  2171.00  2173.20  2170.50  2172.80\n"
            "2026-03-30 14:30:00  2172.80  2174.00  2171.20  2173.50\n"
        )

    # Local Windows Environment MT5 Fetching Logic
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
