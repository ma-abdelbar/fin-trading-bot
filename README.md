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

### 📁 Project Structure

```plaintext
fin-trading-bot/
├── adapters/
├── backtest/
│   ├── dataloader.py
│   ├── engine.py
│   ├── snapshot.py
│   └── enriched_snapshot.py
├── config/
│   ├── settings.py
│   └── settings.py.bak
├── core/
│   ├── enums.py
│   ├── models.py
│   └── utils.py
├── domain/
│   ├── strategy_base.py
│   ├── sample_strategies.py
│   └── simple_rsi_strategy.py
├── indicators/
│   ├── indicator_base.py
│   └── rsi.py
├── live/
│   ├── data_feed.py
│   └── engine.py
├── services/
│   ├── binance_executor.py
│   ├── mock_executor.py
│   ├── executor.py
│   ├── broker.py
│   ├── bracket.py
│   └── trade_logger.py
├── scripts/
│   ├── fetch_ohlcv.py
│   └── ohlcv_downloader.py
├── tests/
│   ├── manual_order_test.py
│   ├── run_mock_test.py
│   └── run_strategy_test.py
├── .env
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
