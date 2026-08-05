import io
import zipfile
import datetime as dt

import requests
import pandas as pd

BASE_URL = "https://data.binance.vision"

_KLINES_COLUMNS = [
    "OpenTime", "Open", "High", "Low", "Close", "Volume", "CloseTime",
    "QuoteAssetVolume", "NumberOfTrades", "TakerBuyBaseVolume",
    "TakerBuyQuoteVolume", "Ignore",
]

_TRADES_COLUMNS = [
    "TradeId", "TradedPrice", "TradedQty", "QuoteQty", "Time",
    "IsBuyerMaker", "IsBestMatch",
]

_BOOKTICKER_COLUMNS = [
    "UpdateId", "BidPrice", "BidQty", "AskPrice", "AskQty",
    "TransactionTime", "EventTime",
]


def _daterange(start_date: str, end_date: str):
    d0 = dt.date.fromisoformat(start_date)
    d1 = dt.date.fromisoformat(end_date)
    d = d0
    while d <= d1:
        yield d.isoformat()
        d += dt.timedelta(days=1)


def _fetch_zip_csv(url: str, columns: list) -> pd.DataFrame:
    r = requests.get(url, timeout=30)
    if r.status_code != 200:
        return pd.DataFrame(columns=columns)

    with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
        name = zf.namelist()[0]
        with zf.open(name) as f:
            first_line = f.readline().decode()
        first_field = first_line.split(",")[0]
        has_header = not first_field.lstrip("-").replace(".", "", 1).isdigit()

        with zf.open(name) as f:
            if has_header:
                df = pd.read_csv(f)
                df.columns = columns[: len(df.columns)]
            else:
                df = pd.read_csv(f, header=None, names=columns)
    return df


def get_klines(symbol: str, interval: str, start_date: str, end_date: str,
                market: str = "spot") -> pd.DataFrame:
    frames = []
    for date in _daterange(start_date, end_date):
        url = f"{BASE_URL}/data/{market}/daily/klines/{symbol}/{interval}/{symbol}-{interval}-{date}.zip"
        df = _fetch_zip_csv(url, _KLINES_COLUMNS)
        if not df.empty:
            frames.append(df)

    if not frames:
        raise ValueError(f"No klines found for {symbol} between {start_date} and {end_date}")

    out = pd.concat(frames, ignore_index=True)
    out["DateTime"] = pd.to_datetime(out["OpenTime"], unit="ms")
    out = out.set_index("DateTime").sort_index()
    out[["Open", "High", "Low", "Close", "Volume"]] = out[["Open", "High", "Low", "Close", "Volume"]].astype(float)
    return out


def get_tick_data(symbol: str, start_date: str, end_date: str,
                   market: str = "futures/um") -> pd.DataFrame:
    bt_frames, tr_frames = [], []
    for date in _daterange(start_date, end_date):
        bt_url = f"{BASE_URL}/data/{market}/daily/bookTicker/{symbol}/{symbol}-bookTicker-{date}.zip"
        tr_url = f"{BASE_URL}/data/{market}/daily/trades/{symbol}/{symbol}-trades-{date}.zip"

        bt = _fetch_zip_csv(bt_url, _BOOKTICKER_COLUMNS)
        tr = _fetch_zip_csv(tr_url, _TRADES_COLUMNS)

        if not bt.empty:
            bt_frames.append(bt)
        if not tr.empty:
            tr_frames.append(tr)

    if not bt_frames or not tr_frames:
        raise ValueError(f"No tick data found for {symbol} between {start_date} and {end_date}")

    bt = pd.concat(bt_frames, ignore_index=True)
    tr = pd.concat(tr_frames, ignore_index=True)

    bt["DateTime"] = pd.to_datetime(bt["EventTime"], unit="ms")
    tr["DateTime"] = pd.to_datetime(tr["Time"], unit="ms")

    bt = bt.sort_values("DateTime")[["DateTime", "BidPrice", "AskPrice"]].astype(
        {"BidPrice": float, "AskPrice": float}
    )
    tr = tr.sort_values("DateTime")[["DateTime", "TradedPrice", "TradedQty"]].astype(
        {"TradedPrice": float, "TradedQty": float}
    )

    # attach the prevailing best bid/ask (as of the most recent quote update
    # at or before the trade) to every trade
    merged = pd.merge_asof(tr, bt, on="DateTime", direction="backward")
    merged = merged.set_index("DateTime").sort_index()
    return merged[["BidPrice", "AskPrice", "TradedPrice", "TradedQty"]]
