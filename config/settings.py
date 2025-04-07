import os
from pathlib import Path
from dotenv import load_dotenv

# --- 1. Load `.env` from project root ---
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# --- 2. Global Mode (default: backtest) ---
MODE = os.getenv("MODE", "backtest")  # Options: backtest, testnet, live

# --- 3. API Keys Based on Mode ---
if MODE == "testnet":
    BINANCE_API_KEY = os.getenv("BINANCE_TESTNET_API_KEY")
    BINANCE_API_SECRET = os.getenv("BINANCE_TESTNET_API_SECRET")
elif MODE == "live":
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
    BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
else:
    BINANCE_API_KEY = None
    BINANCE_API_SECRET = None

# --- 4. Backtest Data Location ---
# Use this when loading OHLCV in Spark or Dataloader
DATA_PATH = Path("/mnt/p/trading-data")


