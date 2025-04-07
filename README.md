# 🧠 fin-trading-bot

An OO, backtesting and live-trading bot for crypto markets.

---

## 🚀 Features

- Extendable Strategy Base
- Plug-and-play indicators (Implemented: RSI)
- Market and Limit orders with Risk Management (SL/TP)
- Backtest-ready (with PySpark + Parquet) with visualization (matplotlib)
- Live trading (Binance testnet ready)

---

## 🏗️ Project Structure


fin-trading-bot/
│
├── adapters/                # For exchange adapters or data connectors
│
├── backtest/                # Backtesting engine & data stream
│   ├── dataloader.py
│   ├── engine.py
│   ├── snapshot.py
│   └── enriched_snapshot.py
│
├── config/                  # Environment config (API keys, paths)
│   ├── settings.py
│   └── settings.py.bak
│
├── core/                    # Core models, enums, utils
│   ├── enums.py
│   ├── models.py
│   └── utils.py
│
├── domain/                  # Strategies: base + custom
│   ├── strategy_base.py
│   ├── sample_strategies.py
│   └── simple_rsi_strategy.py
│
├── indicators/              # Indicators (RSI, VWAP, etc.)
│   ├── indicator_base.py
│   └── rsi.py
│
├── live/                    # Live trading engine and data feed
│   ├── data_feed.py
│   └── engine.py
│
├── services/                # Broker, executor, trade logger, etc.
│   ├── binance_executor.py
│   ├── mock_executor.py
│   ├── executor.py
│   ├── broker.py
│   ├── bracket.py
│   └── trade_logger.py
│
├── scripts/                 # Utilities (e.g., data fetchers)
│   ├── fetch_ohlcv.py
│   └── ohlcv_downloader.py
│
├── tests/                   # Manual and unit test runners
│   ├── manual_order_test.py
│   ├── run_mock_test.py
│   └── run_strategy_test.py
│
├── .env                     # API keys and config (not tracked)
├── binance_testnet_check.py
├── main.py
├── run_backtest.py
├── run_backtest0.py
└── run_live.py


---

## ⚙️ Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Fill in your Binance API keys



## 📈 Running a Backtest

`python run_backtest.py`



## 💹 Running Live Trading (Binance Testnet)

`python run_live.py`
