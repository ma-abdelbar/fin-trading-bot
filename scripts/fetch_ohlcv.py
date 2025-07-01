import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from ohlcv_downloader import OHLCVDownloader
from config.settings import DATA_PATH
import os

timeframes = ["1d", "4h", "30m", "5m", "1m"]  # start with 1d to test
symbol = "BTC/USDT"
start_date = "2020-04-01"

downloader = OHLCVDownloader(symbol=symbol)


for tf in timeframes:
    print(f"\n📥 Fetching {symbol} {tf} from {start_date}")
    df = downloader.fetch_ohlcv_range(timeframe=tf, start_date=start_date)

    symbol_dir = os.path.join(DATA_PATH, symbol.replace("/", ""))
    filename = f"{symbol.replace('/', '')}_{tf}.parquet"
    full_path = os.path.join(symbol_dir, filename)

    downloader.save_to_parquet(df, full_path)
